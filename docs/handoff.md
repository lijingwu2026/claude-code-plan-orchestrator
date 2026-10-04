# Moving a plan to a new session

When the rest of a plan cannot happen in this session, the route skill writes a handoff instead of carrying on. That means the work needs another environment (a different permission mode, terminal, logged-in browser or machine), an external dependency, or another day. A full context is not a reason: Claude Code compacts on its own and the run resumes from the board.

## What you get

The skill replies with three things: the path of the handoff file, the start block in a fenced block, and plain words saying who picks it up and what they do.

You paste the start block into the new session. It reads:

```text
Read [absolute path of this handoff file]
objective: [one sentence]
Must read: [path + section anchor, ...]
Boundaries: [framing · challenges · settled conclusions]
Start with: [first command, exactly as it runs] — it should return [expected output]
Execute the table under ## Allocation in this file.
```

## The file

It is written to `handoffs/<YYYY-MM-DD>-<slug>.md` in the project root, so it can be traced later. It is written for a session with none of this context, so it points to what to read instead of restating it. It carries:

- the objective, in one sentence
- the paths the new session must read, with section anchors
- boundaries, including settled conclusions that are not reopened
- acceptance for each deliverable: input, expected result, what counts as a pass
- why work stops here and what the next session needs (environment, credentials, dependency, date)
- the state on disk, taken from `git status` and `git log -1` at that moment
- any worker that was interrupted or is still running, or "none"
- every deferred item, with its blocker
- the allocation table copied as it stands, with its `Status` column, and the board location
- for multi-week or cold-start plans, known traps

Every command is written exactly as it runs, with no placeholders.

## Who picks it up

| Recipient | Fits when |
|---|---|
| An agent in a session you start | The default. You paste one thing, the start block |
| A live peer session | Mechanical work a machine can check, and the peer is not busy |
| Cloud or another device | Commit and push first; the handoff points at the pushed branch |
| You | Only real human judgement, a physical action, or a signal only a person can see |

For a peer session: slash commands arrive as plain text and do not run, so they are rewritten as instructions. A receiver in `bypassPermissions`, or a `-p` session started without cross-session input enabled, may never see the message. The skill asks for a receipt and a named output file.

Anything denied in the current session is not sent to a peer to run instead.
