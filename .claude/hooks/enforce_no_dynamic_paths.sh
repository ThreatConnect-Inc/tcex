#!/usr/bin/env bash
#
# PreToolUse hook for Bash — rejects commands that resolve paths dynamically
# via shell substitutions like $(git rev-parse), $(pwd), $(realpath ...).
#
# The workspace root is fixed per project ($CLAUDE_PROJECT_DIR) and the venv at
# <root>/.venv; both must be written as literal absolute paths in commands.
# Dynamic resolution defeats the consistency we just established and re-introduces
# the variant-explosion problem (each unique substitution becomes its own
# permission rule because the literal command string differs).
#
# Stdin: a JSON envelope with `.tool_input.command` set to the proposed command.
# Exit codes:
#   0  = allow the tool call
#   2  = block the tool call; stderr is shown to the model so it can correct

set -euo pipefail

PAYLOAD="$(cat)"
CMD="$(printf '%s' "$PAYLOAD" | jq -r '.tool_input.command // ""')"

# Match $(...) substitutions whose first token is a path-resolution tool.
# Pattern: literal "$(", optional whitespace, then git|pwd|realpath|readlink|cd,
# then a word boundary (whitespace or close-paren).
DYN_PARENS='\$\([[:space:]]*(git|pwd|realpath|readlink|cd)([[:space:]]|\))'

# Same pattern via backticks.
DYN_TICKS='`[[:space:]]*(git|pwd|realpath|readlink|cd)([[:space:]]|`)'

if [[ "$CMD" =~ $DYN_PARENS ]] || [[ "$CMD" =~ $DYN_TICKS ]]; then
    ROOT="${CLAUDE_PROJECT_DIR:-the workspace root}"
    {
        printf '[enforce_no_dynamic_paths] BLOCKED: dynamic path resolution detected.\n\n'
        printf 'The workspace root is fixed at %s. Do NOT use:\n' "$ROOT"
        cat <<'EOF'
  $(git rev-parse --show-toplevel)
  $(pwd)
  $(realpath ...)
  $(readlink -f ...)
  $(cd ... && pwd)
  `git rev-parse ...`   (backticks)
EOF
        printf '\nSubstitute the literal absolute workspace path directly. Examples:\n\n'
        printf '    # WRONG — resolves dynamically\n'
        printf '    "$(git rev-parse --show-toplevel)/.venv/bin/python" ...\n'
        printf '    cd "$(pwd)" && ...\n\n'
        printf '    # CORRECT — hardcoded absolute path\n'
        printf '    %s/.venv/bin/python ...\n' "$ROOT"
        printf '\nWhy: every unique substitution becomes a distinct permission rule.\n'
        printf 'Writing the absolute workspace path collapses those into single rules.\n'
        printf 'See %s/CLAUDE.md → "Tool Invocation — Absolute Paths Only".\n' "$ROOT"
    } >&2
    exit 2
fi

exit 0
