# Codex surface adapter

- Installed Clade plugin skills are namespaced. Invoke this workflow as
  `$clade:delivery`, and use `$clade:<skill-name>` for companion workflows.
- Read the closest applicable agent instructions. Codex probes
  `AGENTS.override.md` before `AGENTS.md` at each scope and does not merge
  them, so where an override exists that scope's `AGENTS.md` is not in effect.
  `CLAUDE.md` is Clade's legacy fallback rather than a filename Codex resolves;
  read it only when it is trusted repository guidance.
- Codex-managed worktrees may begin at detached HEAD. A local detached commit
  is valid, but create/attach an owned branch or preserve a reachable Clade ref
  before the runtime deletes the worktree.
- Inspect `git worktree list --porcelain` before checkout, rewrite, or cleanup:
  one branch cannot be checked out by multiple worktrees.
- Use Codex native review/worktree/handoff capabilities where available. Do
  not launch Claude Code or a nested Codex CLI to emulate the workflow.
- Project configuration is trust-gated. Provider credentials and user
  connections remain user-scoped and cannot be donated by repository files.
