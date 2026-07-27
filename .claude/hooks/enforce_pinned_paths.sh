#!/usr/bin/env bash
#
# PreToolUse hook for Bash — rejects commands that contain a bare-name
# invocation of a system utility that should be invoked via its absolute path.
#
# Stdin: a JSON envelope with `.tool_input.command` set to the proposed command.
# Exit codes:
#   0  = allow the tool call
#   2  = block the tool call; stderr is shown to the model so it can correct
#
# Rationale: Claude Code permission rules in settings.local.json match by
# literal command-string prefix. `Bash(grep *)` and
# `Bash(/opt/homebrew/opt/grep/libexec/gnubin/grep *)` are different rules.
# Picking one form per command and enforcing it keeps the allowlist small and
# deterministic. See $CLAUDE_PROJECT_DIR/CLAUDE.md →
# "Tool Invocation — Absolute Paths Only" for the convention.
#
# Scope: this hook checks the FIRST TOKEN of EACH COMMAND SEGMENT — segments
# are split on the operators | || && ; |&. So `cmd | tail -30` blocks because
# the `tail` segment uses a bare name, even though the leading `cmd` is fine.
# Mid-argument bare names (e.g. the `cat` in `xargs cat ...`) are not rewritten.
#
# Edge case: pipes inside quoted strings (`grep "a|b"`) will be split, which
# may produce a false positive. Quote elsewhere or escape the literal pipe.

set -euo pipefail

PAYLOAD="$(cat)"
CMD="$(printf '%s' "$PAYLOAD" | jq -r '.tool_input.command // ""')"

# Pinned utilities: bare-name → required absolute path.
# These are the Homebrew GNU builds standardized for all tcex projects on this
# workstation. Keep this list in sync with $CLAUDE_PROJECT_DIR/CLAUDE.md →
# "System utilities — pinned to Homebrew GNU paths".
declare -A PINNED=(
    # coreutils → /opt/homebrew/opt/coreutils/libexec/gnubin/
    [cat]=/opt/homebrew/opt/coreutils/libexec/gnubin/cat
    [head]=/opt/homebrew/opt/coreutils/libexec/gnubin/head
    [tail]=/opt/homebrew/opt/coreutils/libexec/gnubin/tail
    [sort]=/opt/homebrew/opt/coreutils/libexec/gnubin/sort
    [uniq]=/opt/homebrew/opt/coreutils/libexec/gnubin/uniq
    [wc]=/opt/homebrew/opt/coreutils/libexec/gnubin/wc
    [cut]=/opt/homebrew/opt/coreutils/libexec/gnubin/cut
    [tr]=/opt/homebrew/opt/coreutils/libexec/gnubin/tr
    [ls]=/opt/homebrew/opt/coreutils/libexec/gnubin/ls
    [cp]=/opt/homebrew/opt/coreutils/libexec/gnubin/cp
    [mv]=/opt/homebrew/opt/coreutils/libexec/gnubin/mv
    [rm]=/opt/homebrew/opt/coreutils/libexec/gnubin/rm
    [mkdir]=/opt/homebrew/opt/coreutils/libexec/gnubin/mkdir
    [chmod]=/opt/homebrew/opt/coreutils/libexec/gnubin/chmod
    [touch]=/opt/homebrew/opt/coreutils/libexec/gnubin/touch
    [ln]=/opt/homebrew/opt/coreutils/libexec/gnubin/ln
    [stat]=/opt/homebrew/opt/coreutils/libexec/gnubin/stat
    [env]=/opt/homebrew/opt/coreutils/libexec/gnubin/env
    [date]=/opt/homebrew/opt/coreutils/libexec/gnubin/date
    [basename]=/opt/homebrew/opt/coreutils/libexec/gnubin/basename
    [dirname]=/opt/homebrew/opt/coreutils/libexec/gnubin/dirname
    [tee]=/opt/homebrew/opt/coreutils/libexec/gnubin/tee
    [echo]=/opt/homebrew/opt/coreutils/libexec/gnubin/echo
    [printf]=/opt/homebrew/opt/coreutils/libexec/gnubin/printf
    [du]=/opt/homebrew/opt/coreutils/libexec/gnubin/du
    # grep → /opt/homebrew/opt/grep/libexec/gnubin/
    [grep]=/opt/homebrew/opt/grep/libexec/gnubin/grep
    # findutils → /opt/homebrew/opt/findutils/libexec/gnubin/
    [find]=/opt/homebrew/opt/findutils/libexec/gnubin/find
    [xargs]=/opt/homebrew/opt/findutils/libexec/gnubin/xargs
    # gnu-sed → /opt/homebrew/opt/gnu-sed/libexec/gnubin/
    [sed]=/opt/homebrew/opt/gnu-sed/libexec/gnubin/sed
    # gawk → /opt/homebrew/opt/gawk/libexec/gnubin/
    [awk]=/opt/homebrew/opt/gawk/libexec/gnubin/awk
    # gnu-tar → /opt/homebrew/opt/gnu-tar/libexec/gnubin/
    [tar]=/opt/homebrew/opt/gnu-tar/libexec/gnubin/tar
    # diffutils → /opt/homebrew/opt/diffutils/bin/
    [diff]=/opt/homebrew/opt/diffutils/bin/diff
    # homebrew bin → /opt/homebrew/bin/
    [gzip]=/opt/homebrew/bin/gzip
    [gunzip]=/opt/homebrew/bin/gunzip
    [zcat]=/opt/homebrew/bin/zcat
    [jq]=/opt/homebrew/bin/jq
    [wget]=/opt/homebrew/bin/wget
    # native (no GNU build installed — stays /usr/bin)
    [file]=/usr/bin/file
)

# Normalize all command separators to newlines so we can iterate segments.
# Order: replace 2-char operators FIRST so they don't get half-replaced by
# the 1-char rules (e.g. `&&` must be replaced before `&`).
NORMALIZED="$CMD"
NORMALIZED="${NORMALIZED//&&/$'\n'}"
NORMALIZED="${NORMALIZED//||/$'\n'}"
NORMALIZED="${NORMALIZED//|&/$'\n'}"
NORMALIZED="${NORMALIZED//|/$'\n'}"
NORMALIZED="${NORMALIZED//;/$'\n'}"

while IFS= read -r segment; do
    # Trim leading whitespace
    segment="${segment#"${segment%%[![:space:]]*}"}"
    [[ -z "$segment" ]] && continue

    # Skip segments that begin with a special construct (substitution, paren, etc.)
    case "$segment" in
        '$'*|'('*|'{'*|'!'*) continue ;;
    esac

    first="${segment%%[[:space:]]*}"
    PINNED_PATH="${PINNED[$first]:-}"

    if [[ -z "$PINNED_PATH" ]]; then
        continue
    fi

    cat >&2 <<EOF
[enforce_pinned_paths] BLOCKED: bare-name invocation of \`$first\`.

Per ${CLAUDE_PROJECT_DIR:-the project}/CLAUDE.md → "Tool Invocation — Absolute Paths Only":
- Standard system utilities must be invoked via their pinned absolute path.
- This applies to ALL command segments, including those after | || && ; |&

Replace \`$first\` with \`$PINNED_PATH\` in this segment:
    ${segment:0:120}

Why: \`Bash($first *)\` and \`Bash($PINNED_PATH *)\` are distinct
permission rules. Mixing forms doubles the rules and re-prompts the user.
EOF
    exit 2
done <<< "$NORMALIZED"

exit 0
