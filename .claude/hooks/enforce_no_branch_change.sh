#!/usr/bin/env bash
#
# PreToolUse hook for Bash — hard-blocks any git command that would CHANGE
# (switch to / create / detach onto) a git branch. Claude Code must NEVER change
# branches in this repo.
#
# Blocked:
#   git switch ...            (branch switch/create — always)
#   git switch -c/-C ...      (create + switch)
#   git checkout <branch>     (switch)
#   git checkout -b/-B ...    (create + switch)
#   git checkout <sha>        (detached HEAD)
#   git checkout --detach ... (detached HEAD)
#   git worktree add ...      (creates a new branch/worktree checkout)
#
# Explicitly ALLOWED (read-only / non-branch-changing):
#   git branch ...            (list/create-without-switch — listing is read-only)
#   git status, git rev-parse, git log, git diff, git fetch, git pull, etc.
#   git checkout -- <path>    (file restore; the "--" pathspec separator)
#   git checkout <ref> -- <p> (file restore from a ref)
#   git restore ...           (modern file restore — never matched)
#
# The check is segment-aware: the command is split on shell separators
# (| || && ; |&) so a blocked git invocation hidden after a pipe/`&&` is still
# caught (mirrors enforce_pinned_paths.sh).
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
# Replace each separator with a newline, then iterate segment-by-segment.
SEGMENTS="$(printf '%s' "$CMD" | /opt/homebrew/opt/gnu-sed/libexec/gnubin/sed -E 's/\|\||&&|\|&|[|;&]/\n/g')"

block() {
    local reason="$1" segment="$2"
    cat >&2 <<EOF
[enforce_no_branch_change] BLOCKED: ${reason}

Claude Code must NEVER change git branches in this repo.
Offending command segment:
  ${segment}

Allowed instead:
  - git branch                 (list branches)
  - git status / git rev-parse (inspect state)
  - git checkout -- <path>     (restore a file; note the "--" separator)
  - git restore <path>         (modern file restore)

If a branch change is genuinely required, the human operator must run it
themselves — this hook intentionally has no override.
EOF
    exit 2
}

# Matches `git`, then any number of git GLOBAL options (e.g. `-C <path>`,
# `-c k=v`, `--no-pager`, `--git-dir=...`), up to (but not including) the
# SUBCOMMAND token. The subcommand the caller wants follows immediately after.
# Anchoring this way means words like "switch"/"checkout" inside a commit
# message (`git commit -m 'switch to ...'`) are NOT misread as the subcommand.
SUBCMD_PREFIX='(^|[[:space:]])git([[:space:]]+(-[Cc][[:space:]]+[^[:space:]]+|--[^[:space:]=]+(=[^[:space:]]+)?|-[A-Za-z]))*[[:space:]]+'

while IFS= read -r SEG; do
    # Trim leading/trailing whitespace.
    SEG="${SEG#"${SEG%%[![:space:]]*}"}"
    SEG="${SEG%"${SEG##*[![:space:]]}"}"
    [[ -z "$SEG" ]] && continue

    # Only consider segments that invoke git.
    [[ "$SEG" =~ (^|[[:space:]])git([[:space:]]|$) ]] || continue

    # git worktree add — creates a new checkout/branch.
    if [[ "$SEG" =~ ${SUBCMD_PREFIX}worktree[[:space:]]+add([[:space:]]|$) ]]; then
        block "git worktree add creates a new branch/worktree checkout." "$SEG"
    fi

    # git switch — its sole purpose is switching/creating branches. Always block.
    if [[ "$SEG" =~ ${SUBCMD_PREFIX}switch([[:space:]]|$) ]]; then
        block "git switch changes the current branch." "$SEG"
    fi

    # git checkout — block UNLESS it is a file-restore using the "--" pathspec
    # separator (" -- " between args, or a trailing " --").
    if [[ "$SEG" =~ ${SUBCMD_PREFIX}checkout([[:space:]]|$) ]]; then
        if [[ "$SEG" =~ [[:space:]]--[[:space:]] ]] || [[ "$SEG" =~ [[:space:]]--$ ]]; then
            # File-restore form (git checkout [<ref>] -- <path>) — allowed.
            continue
        fi
        block "git checkout switches/creates/detaches a branch." "$SEG"
    fi
done <<< "$SEGMENTS"

exit 0
