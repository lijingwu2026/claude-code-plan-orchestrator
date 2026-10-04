---
name: route
description: Staffs every remaining stage of an approved plan (split, executor, model tier, check) in a table before work starts, then dispatches, checks and records each stage on a progress board. Use when executing or resuming an approved plan (including after an automatic compaction), when a batch of 3 or more similar tool calls is about to start, when 2 or more independent outputs are due, before spawning a subagent or picking a model tier, when the rest of an active plan has to move to a new session (handoff), and when reporting the status of an active plan. Not for drafting a plan the user has not approved, or for status questions about anything other than an active plan.
---

# Route

## Overview

Decide who runs every remaining stage of an approved plan, at which model tier, against which check — and emit that decision as a filled-in table before the first file change or the first dispatch. Every step below ends in a template: fill each named slot.

## When to Use

- Executing or resuming an approved plan
- A batch of 3 or more tool calls of the same shape is about to start
- 2 or more independent outputs are due
- About to spawn a subagent or pick a model tier
- The rest of an active plan cannot happen in this session and has to be handed to a new one

Asked only for an active plan's status: read the board, report it, and create or write nothing.

**When NOT to use:** drafting a plan the user has not approved; status questions about anything other than an active plan.

## After a compaction

Claude Code compacts the conversation on its own.

- Read the board first. Where the board and the table's `Status` disagree, the board wins: rewrite the table's `Status` from it.
- A worker Claude Code reminds you is still running is not dispatched again; act on its result when it returns.
- A row marked `Done` is not run again because of the compaction. A later check that finds its output wrong reopens it like any failed check (Step 3). Re-allocate only rows whose Why no longer holds, and name them.

## Step 1: Scope the run

Read the plan, the spec, the project instructions, and the current state. Confirm four things: the acceptance criteria, that every prerequisite artifact exists, the authorization boundary, and that nobody else is writing the paths you will write.

Design each stage's check before allocating it. A check is a runnable command, a pass criterion, and where its evidence lands. When the plan already states one, that command is the check.

Three slots must be fillable, and each value must point at where it came from in the user's words or in the plan. If any slot is empty, or you cannot write some stage's check, stop and ask — before running the remaining decisions, not after.

Read the board at `${user_config.board_location}` before starting work. If it has no rows for this plan yet, add one row per stage at `Todo`, then read it back (Step 4).

```markdown
scope
- objects: [specific files or records] — from [the user's message / plan section]
- subtasks: [countable N] — from [where]
- output: [what] lands at [path or record] — from [where]
- stage [n] check: [command + pass criterion] → evidence returns as [raw output / file path + count]
- board: [location; rows for this plan already present / added now]
```

## Step 2: Allocate every remaining stage

Resuming after a compaction: see After a compaction.

Write the allocation as visible text in your reply, before the first file change and before the first dispatch, covering all remaining stages. A table that exists only in your reasoning does not count: the user, the board and a later compaction can carry only what is in the reply. One row per remaining stage, plus one row per check a stage needs. Allocating only the next cell and starting leaves every later stage unrouted, and a table produced after the work is a report, not an allocation.


Pick each row's split from an observable property. Splits nest, and only a form this host actually exposes is on the menu:

| Split | Use it when |
|---|---|
| spawn N | Subtasks are independent and share no state |
| batch | 5 or more independent same-pattern units **and** the project already uses pull requests |
| goal | The stop condition is machine-decidable: `pass_rate >= X`, `count == 0`, every box ticked, `grep -q` |
| loop | One artifact is revised until a measure passes a threshold, or there are 3 or more similar targets |
| serial | One of exactly three holds: the same file is edited repeatedly · the workers must talk to each other once running · a later step consumes new data an earlier step produced, where a value fixed at planning time does not count |

No serial condition holds → run the stages in parallel. A shared prerequisite orders stages; it does not serialize them. Deterministic mechanical work → write a script, which is neither a serial reason nor an inline reason.

Upgrade a spawn to a dynamic workflow when this flow will run again and it has dozens of independent units, where 11–23 does not qualify on its own; a conclusion that needs another set of agents to rebut it, with that rebuttal running again, also qualifies. A count alone is not an answer. Four exemptions, any one of which keeps it a spawn: the user must decide inside a batch, and a running workflow accepts no input — a decision the user makes between batches is not an exemption: split the work at that decision and upgrade each batch · the check is deterministic, so a script suffices · the units must talk to each other · a cheaper mechanism already exists — a one-off cross-source review takes ONE independent reviewer, not a fan-out. To upgrade, ask the user, giving the unit count, the cost estimate and "run it as a Workflow", and start the Workflow only on their explicit agreement. On an upgrade, run one slice first to measure real cost; the scale figures are advice, not a cap.

Keep a row inline only for one of two kinds of work: it needs context unique to this session that cannot be passed by reference, or it is genuinely one-off at 2 or fewer tool calls with nothing to batch it with. "The user is waiting" is an instance of the second kind, not a reason of its own. Cannot name the kind → delegate.

Fix five things for every delegated row:

| What | Fix it to |
|---|---|
| Brief | Scope · the acceptance check · required reference paths · write boundary · return. A worker inherits neither this conversation nor the skills already loaded here. Use the brief template in Step 3. |
| Model | Judgment → highest available tier (for example Opus); mechanical execution → lowest sufficient tier (for example Sonnet). Set `model` on every subagent call: a call without it runs on the agent definition's model or, failing that, the session's, which is usually the top tier. Before the first dispatch, run `printenv CLAUDE_CODE_SUBAGENT_MODEL_FORCE CLAUDE_CODE_SUBAGENT_MODEL`: when the first is `1`, every subagent runs on the second (or, unset, the session's model) whatever `model` you pass — write that model in every delegated row's Model cell and say so in the reply. Two rounds of rework or a backlog of problems → go one tier up, or start an isolated thinker. A review never runs on the same model as the output it reviews. Spawn overhead is not a reason to stay inline: pass paths, batch 3–5 items, or hand one worker the whole chain. |
| Return | One record per work item, always including the raw output of running the check. Long lists, full text, or bulk output → write a file, and reply with the path, the count, and the raw output of the self-check command. A worker's default is to return markdown and not Write. |
| Worker kind | subagent by default, because its result returns to this window. teammate only when the parties must interrogate each other, and then artifacts travel as messages and arrive late. peer session only for a different environment or lifecycle. Cannot say why it is not a subagent → it is a subagent. With Agent Teams on, giving a subagent a name makes it a teammate. |
| Effort | The dispatch tool has no per-invocation effort argument. The Workflow tool's `agent()` accepts one. The only carrier that persists per role is an `effort:` field in an agent definition (for example `.claude/agents/<role>.md`, with `model:` beside it), dispatched with that `subagent_type`. Never call effort set without naming that file, and never raise a global or session default to serve one stage. If the user asks for an effort level, say in your reply how it is applied: through which agent definition file, or that the session's own level applies. |

Read `references/model-orchestration.md` when a worker needs a per-role effort setting, or when choosing teammate or peer session.

Executor values: `inline` · `subagent: <type>` (for example `subagent: general-purpose`) · `teammate` · `peer session` · `script`.

```markdown
routing: [split] × [executor] — [one-line reason]

| Stage | Split | Executor | Model | Check | Why | Status |
|---|---|---|---|---|---|---|
| [stage n] | [spawn N / batch / goal / loop / serial] | [inline / subagent: <type> / teammate / peer session / script] | [tier; inline → the session's model by name, e.g. Opus; script → —] | [stage n check from Step 1] | [reason] | [board status] |
| [check for stage n] | [split] | [executor] | [tier, not the producer's model when it reviews] | [pass criterion] | [reason] | [board status] |

board: [location]

workflow: N=[units] — [keep spawn: which condition fails or which exemption holds / upgrade: asked the user "[request text]" → their words: [quote / waiting]]
effort: [not set / `effort: [value]` in [agent definition file]]
```

## Step 3: Execute and verify each stage

Every brief carries these lines, filled in. A brief with a blank line is not ready to send; write `none` for References when there are none.

```
Target: <the files or outputs this worker produces — its scope>
Check: <the exact command and pass criterion from the table's Check cell>
References: <paths it must read>
Write boundary: <the only paths it may modify; everything else is read-only>
Return: the raw output of running the check, plus <anything else you need back>
```

Per stage: execute, look at the real result, run the check from Step 1 yourself, and decide the next step from what the check returned. A worker's report that the check passed is not the check. A returned worker's row waits at `Needs Verification` until your check passes. Record each returned result on the board before starting other work: a result that exists only as chat text is lost if a compaction comes first.

- Passed → record the meaningful state change (Step 4), then take the next ready stage.
- Recoverable failure → inspect the mechanism, fix it in place or re-dispatch with the failing output, re-verify. Repeated failure means the hypothesis is wrong: change it, and keep the unaffected work moving.
- An assumption turned out false → change the affected steps, dependencies, allocation, or checks, and record why. A changed deliverable, a material tradeoff, or a new permission is the user's to decide.

Pause only where the user explicitly asked for a review. A milestone, a worker returning, and a recoverable failure are not pauses.

```markdown
stage [n]: ran [what] → observed [the actual result]
check: [command] → [raw output] → [pass / recoverable failure / assumption false]
next: [next ready stage / fixed [what] and re-verified / changed [steps] because ... / the user's to decide: ...]
```

## Step 4: Record progress on the board

The board keeps progress on disk, so a handoff can point to it instead of copying it.

- Location: `${user_config.board_location}`
- Fields per row: `${user_config.board_fields}`
- Status values: `Todo` · `In Progress` · `Needs Verification` · `Done` · `Blocked`. `Needs Verification` = the work is done and its check has not passed yet, including a check that waits on someone else; `Blocked` = the work itself cannot proceed.

The location takes one of two forms:

- **A file path** (default `PROGRESS.md`, relative to the project root): write it with Edit or Write, read it back with Read.
- **`command:<read> ;; <write> [;; <write> ...]`**: a board on another platform, reached through shell commands. The first command reads the board; each later one writes to it. For GitHub Projects, for example: `command:gh project item-list ;; gh project item-edit ;; gh project item-add`. Write with a write command, then read back by running the read command. Run a command's `--help` before an operation you have not used.

Mark a row `In Progress` only when its work actually starts.

At a milestone, a material plan change, a change in what is blocked, and at completion:

1. Read the board, and copy the row's task text verbatim — one character off creates a second row instead of updating the first.
2. Update only the affected row, with observed evidence and one of the five status values.
3. Read the board again. The value you read back is the current state; a write that returned is not.

Leave a row at `Needs Verification` until its verification passes. Name the board's location in your reply. The plugin's Stop hook blocks a stop once when the board was written this turn without a readback afterwards.

```markdown
row: "[task text copied from the board read]"
status: [one of the five]
evidence: [observed evidence]
readback: [value from the second read]
board: [location]
```

## Step 5: Finish or hand back

Finish when four hold: the deliverable exists, its required verification passed, the project's wrap-up procedure ran, and integration is authorized. When one is missing for a reason you can act on, return to Step 3.

Hand back only because the user must decide, the user must supply information or a permission, an action is the user's to take, or an external blocker stands. Never ask whether to continue work that is already authorized.

Before finishing or handing back, list every item set aside earlier in this run ("later", "after X") and give each one disposition: done now · done and reported · carried, naming its blocker. Anything doable now is done now: an earlier "not now" is not a blocker. An item with no disposition is dropped.

The remaining work cannot happen in this session — it needs another environment (permission mode, terminal, logged-in browser, another machine), an external dependency, or another day → read `references/handoff.md` and write the handoff it describes. A full context is not such a reason: Claude Code compacts on its own and the run resumes from the board.

```markdown
finish: deliverable [evidence] · verification [command → output] · wrap-up [what ran] · integration [authorized by ...]

hand back
- completed: [outcome] · evidence: [readings] · board status: [row statuses]
- remaining: [...] · restart point: [exact command / file + line]
- board: [board location]
- deferred: [item → disposition] / none found after listing
- needed from the user: [decision / information / permission / external action / none]
```

## Checkpoint: before the first file change or dispatch

- [ ] The allocation table is visible text in the reply, not only in reasoning
- [ ] Every remaining stage has a row, and every check a stage needs has its own row
- [ ] No row has a blank split or executor — blank is unrouted, not inline
- [ ] Every `serial` row names which of the three conditions it meets
- [ ] Every set of independent subtasks is allocated to run in parallel
- [ ] Every subagent call will set `model`
- [ ] Every effort claim names the agent definition file the setting lives in

Nothing machine-checks this allocation, so run this checkpoint yourself.
