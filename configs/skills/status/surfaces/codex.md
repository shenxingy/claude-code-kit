# Codex status adapter

- Invoke the installed plugin workflow explicitly as `$clade:status`; bare
  `$status` is not the Clade plugin identity.
- Use Codex task/tool activity exposed in the current conversation.
- Codex TUI status-line configuration is an ordered list of native fields, not
  an arbitrary command renderer. Do not claim Claude-style custom rendering.
- Use `$clade:codex-usage --json` when installed for authenticated native limit
  observations; otherwise report limits as unavailable/unknown.
- Read the applicable agent instructions before interpreting
  repository-specific progress. `AGENTS.override.md` wins over `AGENTS.md` at
  each scope with no merge, so do not report a shadowed `AGENTS.md` as in
  effect; trusted legacy `CLAUDE.md` is Clade's own fallback rather than a
  filename Codex resolves.
- Do not launch a nested Codex CLI to discover status.
