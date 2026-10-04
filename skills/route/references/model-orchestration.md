# Effort and worker-kind branches

Reference for the `route` skill. Route's body carries what every allocation needs — tier by role, the delegation default, return shape, the effort landing point. Read this file when one of its branches applies: a worker needs a per-role effort setting, or the executor is a teammate or a peer session.

## Setting effort per role

Priority, highest first: the `CLAUDE_CODE_EFFORT_LEVEL` environment variable, then an agent definition's `effort:` frontmatter, then the session level.

- The platform reads subagent definitions only from managed settings, an `--agents` flag, `.claude/agents/`, `~/.claude/agents/`, and a plugin's `agents/` directory. An `effort:` field in a file outside those locations is never read.

## Teammate and peer session

| Form | How it starts | What only it gives | What it cannot give |
|---|---|---|---|
| teammate | a named spawn, while Agent Teams is enabled and the session is interactive (`-p` and Agent SDK sessions are exempt, so a named subagent there stays a subagent) | its own window, automatic completion notice to the lead, direct teammate-to-teammate messaging and a shared task list, and it inherits the lead's effort | its artifact arrives as a message rather than a return value, and late — one measured case took eleven minutes; the model must be named in the prompt or set via `CLAUDE_CODE_SUBAGENT_MODEL` |
| peer session | `ListAgents` to find a live one, or `claude -p --name … --model … --permission-mode …` | a fresh MCP environment (environment is read once at session start), a different permission mode, and a lifetime outlasting the coordinator | a plain text mailbox only — no schema, no handle, no effort control |
