# Handoff to a new session

Read this when the remaining work cannot happen in this session: it needs another environment, an external dependency, or another day.

## The file

Write `handoffs/<YYYY-MM-DD>-<slug>.md` in the project root (create `handoffs/` if needed). A block that never reached disk cannot be traced later: nobody can tell whether it was sent, and it gets sent twice. The file is for a session with none of this context: point to what to read; do not restate it.

It carries:

- **objective**: one sentence.
- **Must read**: project-relative paths with section anchors — the plan or spec, research, contracts and data models, platform docs the work depends on.
- **Boundaries**: default framing, default challenges, and settled conclusions that are not reopened.
- **Acceptance, per deliverable**: input → expected result → what counts as pass. "Test it end to end" is not a criterion; without one the next session cannot tell when it is done.
- **Why it stops here**: what this session could not do, and what the next one needs (environment, credentials, dependency, date).
- **State on disk**: from `git status` and `git log -1` run now, not from memory.
- **Workers**: every worker interrupted or still running, with what it was dispatched to do; or "none".
- **Carried items**: every deferred item carried, with its blocker.
- **Allocation**: route's allocation table copied verbatim with its `Status` column, under `## Allocation`, and the board location. A new session has no compaction summary to carry it.
- **Traps**, for a multi-week or cold-start plan: precedents that are traps, artifacts that vanish when this session ends, and commands or files confirmed **not** to exist.

Every command runs exactly as written. No placeholders such as `<repo>`, `<path>` or `TBD`; write paths in full. A value the user must supply goes in a table outside the start block, saying where to find it.

The file must end with this section:

~~~markdown
## Start block (paste as-is)

```text
Read [absolute path of this handoff file]
objective: [one sentence]
Must read: [path + section anchor, ...]
Boundaries: [framing · challenges · settled conclusions]
Start with: [first command, exactly as it runs] — it should return [expected output]
Execute the table under ## Allocation in this file.
```
~~~

## The recipient

A different environment does not make the work the user's. Name the recipient and why:

| Recipient | Fits when |
|---|---|
| An agent in a session the user starts | The default. Give the user one thing to paste — the start block — not a list of steps |
| A live peer session (`ListAgents`, `SendMessage`) | Mechanical work whose result a machine can check, and the peer is not busy with something else |
| Cloud or another device | Commit and push first; hand off pointing at the pushed branch |
| The user | Only real human judgement, a physical action, or a signal only a person can see — write why an agent cannot do it |

Sending to a peer session:

- Slash commands arrive as plain text and do not run: rewrite them as instructions.
- A receiver in `bypassPermissions`, or a `-p` session started without `--settings '{"crossSessionInbound":"accept"}'`, may never see the message. Check its mode first.
- Ask for a receipt: "when done, `SendMessage` a summary back", and have the deliverable written to a named file.

You are looking for a different environment, not a more permissive one: anything denied in this session is not sent to a peer to run instead.

## The reply

Three parts: the handoff file's path · the start block pasted in a fenced block · plain words saying this is a handoff, who picks it up, and what they do with it.
