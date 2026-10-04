# How the route skill decides

After you approve a plan, the route skill fills in one table row per remaining stage, plus one row per check a stage needs. It prints the table in its reply before the first file change or dispatch. Each row fixes a split, an executor, a model and a check. This page explains how each is chosen.

Before the table, the skill scopes the run. It writes down the files or records involved, the number of subtasks, where the output lands, and a check for every stage (a runnable command, a pass criterion, and where the evidence lands). If a slot is empty or it cannot write a stage's check, it stops and asks you.

## Split: how a stage runs relative to the others

The skill picks the split from something it can observe.

| Split | Used when |
|---|---|
| spawn N | The subtasks are independent and share no state |
| batch | 5 or more independent units of the same pattern, and the project already uses pull requests |
| goal | The stop condition can be decided by a machine: `pass_rate >= X`, `count == 0`, every box ticked, a `grep -q` |
| loop | One artifact is revised until a measure passes a threshold, or there are 3 or more similar targets |
| serial | One of three holds: the same file is edited repeatedly, the workers must talk to each other while running, or a later step consumes new data an earlier step produced |

If no serial condition holds, stages run in parallel. A shared prerequisite orders stages but does not make them serial. Deterministic mechanical work becomes a script.

A spawn can be upgraded to a dynamic workflow only when the flow will run again and has dozens of independent units. The skill asks you first, with the unit count and a cost estimate, and starts it only if you agree.

## Executor: who does the work

| Executor | Used when |
|---|---|
| inline | The work needs context unique to this session that cannot be passed by reference, or it is a one-off of 2 or fewer tool calls |
| subagent | The default for delegated work, because its result returns to the main window |
| teammate (agent team) | Only when the parties must question each other; their output arrives as messages, and late |
| peer session | Only for a different environment or lifecycle |
| script | Deterministic mechanical work |

If the skill cannot say why a worker is not a subagent, it is a subagent. If it cannot name why a row is inline, the row is delegated.

## Model tier

Judgment goes to the highest available tier, for example Opus. Mechanical execution goes to the lowest sufficient tier, for example Sonnet. The skill sets `model` on every subagent call, because a call without it runs on the agent definition's model or the session's, which is usually the top tier. A review never runs on the same model as the output it reviews. After two rounds of rework, the row moves one tier up.

If `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` is `1`, every subagent runs on one model whatever the skill passes. The skill checks this before the first dispatch and says so in the table.

## Check

Every stage has a check: a command, a pass criterion, and where the evidence lands. When a worker returns, its row waits at `Needs Verification` until the skill runs the check itself. A worker's report that it passed does not count. A failed check reopens the row.

Each delegated worker gets a brief with a target, the check, the paths to read, a write boundary, and what to return. The return always includes the raw output of the check.

## After Claude Code compacts

Compaction is Claude Code's own. What the route skill adds is the board, which lives outside the conversation, and four rules:

1. Record each result on the board as it returns.
2. After a compaction, read the board first. Where the board and the table disagree on status, the board wins.
3. Do not restart a subagent that Claude Code says is still running; act on its result when it returns.
4. Do not rerun a finished step unless a later check finds its output wrong.

A six-stage plan got through 3 to 4 compactions in 6 of 6 test runs, with no step started twice. See [evidence](evidence.md).
