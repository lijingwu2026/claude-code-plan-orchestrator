# The board, the hooks and the settings

## The board

The board is a progress table that the route skill keeps on disk, outside the conversation. By default it is `PROGRESS.md` in the project root. Each row has the fields `task, status, evidence`. Status is one of `Todo`, `In Progress`, `Needs Verification`, `Done`, `Blocked`.

The skill adds one row per stage when a plan starts. At each milestone it updates the affected row with observed evidence and reads the board back. After a compaction it reads the board first, so the run picks up from there.

When you enable the plugin, Claude Code asks for two settings:

- `board_location`: a file path (default `PROGRESS.md`), or a board on another platform given as `command:<read command> ;; <write command> [;; <write command> ...]`, for example `command:gh project item-list ;; gh project item-edit ;; gh project item-add`.
- `board_fields`: the comma-separated fields of each row (default `task, status, evidence`).

## What the plugin writes in your project

- The board (`PROGRESS.md` by default), when a plan runs.
- `handoffs/<date>-<slug>.md`, only when the rest of a plan has to move to a new session. See [handoff](handoff.md).

The hooks themselves write nothing.

## The two hooks

Both need `python3`. Neither ever blocks more than described here, and both exit quietly on any error.

| Hook | Triggers on | What it does |
|---|---|---|
| `plan_approved_reminder.py` | `ExitPlanMode` (you approve a plan) | Adds a reminder to run the route skill and print the allocation table before the first change. If `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` is set, it adds a warning that every subagent will run on one model. It reminds only and never blocks. |
| `board_readback.py` | Stop (Claude is about to end its turn) | If Claude wrote the board this turn and has not read it back since, it blocks the stop once and asks for a readback and the board's location. It never blocks twice in a row. If it cannot find the transcript or the board setting, it does nothing. |

## Turn it off or remove it

There is no per-plan switch. To stop the plugin without removing it:

```
claude plugin disable plan-orchestrator
```

To remove it:

```
claude plugin uninstall plan-orchestrator
```

If Claude skips the route skill after you approve a plan, ask it to run the route skill.
