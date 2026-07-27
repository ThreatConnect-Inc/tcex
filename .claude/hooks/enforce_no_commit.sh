#!/usr/bin/env bash
#
# PreToolUse hook for Bash — hard-blocks any git command that would CREATE a
# commit. In this repo, Claude Code must NEVER commit; ALL commits are made by
# the human operator.
#
# Blocked (in the parent repo AND in any submodule via `git -C <path> ...`):
#   git commit ...            (create a commit — always)
#   git commit --amend ...    (rewrite the last commit)
#   git commit -m / -a / ...  (any commit form)
#
# Explicitly ALLOWED (read-only / non-committing):
#   git add / git restore --staged / git reset   (staging is fine — operator commits)
#   git status, git diff, git log, git show, git rev-parse, git fetch, etc.
#   git stash (push/list/show)                    (does not create a branch commit history entry the user cares about)
#
# The check is segment-aware: the command is split on shell separators
# (| || && ; |&) so a `git commit` hidden after a pipe/`&&` is still caught
# (mirrors enforce_no_branch_change.sh).
#
# Stdin: JSON envelope with `.tool_input.command`.
# Exit codes:
#   0 = allow
#   2 = block (stderr shown to the model so it can correct)

set -euo pipefail

PAYLOAD="$(cat)"
CMD="$(printf '%s' "$PAYLOAD" | jq -r '.tool_input.command // ""')"

[[ -z "$CMD" ]] && exit 0

# Split the command into segments on shell separators: | || && ; |&
SEGMENTS="$(printf '%s' "$CMD" | /opt/homebrew/opt/gnu-sed/libexec/gnubin/sed -E 's/\|\||&&|\|&|[|;&]/\n/g')"

block() {
    local segment="$1"
    cat >&2 <<EOF
[enforce_no_commit] BLOCKED: creating a git commit is not allowed.

Claude Code must NEVER commit in this repo — ALL commits are made by the human
operator. This applies to the parent repo and every submodule.
Offending command segment:
  ${segment}

Allowed instead (prepare the change; the operator commits):
  - git add <paths>            (stage changes)
  - git status / git diff      (inspect what will be committed)
  - git restore --staged <p>   (unstage)

Leave the working tree/index staged as needed and report what is ready to
commit — the human operator will run 'git commit' themselves. This hook
intentionally has no override.
EOF
    exit 2
}

# Matches `git`, then any number of git GLOBAL options (e.g. `-C <path>`,
# `-c k=v`, `--no-pager`, `--git-dir=...`), up to (but not including) the
# SUBCOMMAND token. Anchoring this way means the word "commit" inside a commit
# message or a pathspec (`git log --grep 'commit'`) is NOT misread as the
# subcommand.
SUBCMD_PREFIX='(^|[[:space:]])git([[:space:]]+(-[Cc][[:space:]]+[^[:space:]]+|--[^[:space:]=]+(=[^[:space:]]+)?|-[A-Za-z]))*[[:space:]]+'

while IFS= read -r SEG; do
    # Trim leading/trailing whitespace.
    SEG="${SEG#"${SEG%%[![:space:]]*}"}"
    SEG="${SEG%"${SEG##*[![:space:]]}"}"
    [[ -z "$SEG" ]] && continue

    # Only consider segments that invoke git.
    [[ "$SEG" =~ (^|[[:space:]])git([[:space:]]|$) ]] || continue

    # git commit — always block (covers -m, -a, --amend, -C, etc.).
    if [[ "$SEG" =~ ${SUBCMD_PREFIX}commit([[:space:]]|$) ]]; then
        block "$SEG"
    fi
done <<< "$SEGMENTS"

exit 0
