#!/usr/bin/env bash
# Spin up a parallel worktree for a track/agent so a swarm can run at once.
# Usage: scripts/new-agent-worktree.sh <track>   e.g. science | infra | design | writeup
set -euo pipefail

TRACK="${1:-}"
case "$TRACK" in
  science|infra|design|writeup) ;;
  *) echo "usage: $0 <science|infra|design|writeup>"; exit 1 ;;
esac

# must be run from inside the main repo, which needs at least one commit on main
if ! git rev-parse --verify main >/dev/null 2>&1; then
  echo "error: 'main' branch not found. After kickoff (12:30 ET) run:"
  echo "  git init && git add -A && git commit -m 'chore: scaffold' && git branch -M main"
  echo "  git config core.hooksPath scripts/git-hooks   # enforces the no-attribution commit-msg hook"
  exit 1
fi

BRANCH="track/${TRACK}"
DIR="../$(basename "$PWD")-${TRACK}"

if git rev-parse --verify "$BRANCH" >/dev/null 2>&1; then
  git worktree add "$DIR" "$BRANCH"
else
  git worktree add -b "$BRANCH" "$DIR" main
fi

# .claude/ is gitignored, so worktrees do not inherit it from git.
# Copy it in so the subagents, hooks, and commands are available in this worktree.
if [ -d .claude ]; then
  cp -r .claude "$DIR"/ 2>/dev/null || true
  echo "copied .claude/ into the worktree (agents, hooks, commands)"
fi

echo
echo "worktree ready: $DIR  (branch $BRANCH)"
echo "next:  cd $DIR && claude    # then delegate to the '$TRACK' subagent"
echo "list:  git worktree list"
echo "remove when done:  git worktree remove $DIR"
