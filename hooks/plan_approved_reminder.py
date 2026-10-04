#!/usr/bin/env python3
"""PostToolUse hook for ExitPlanMode: remind Claude to run route before the first change, and warn when
CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1 makes the table's Model column ineffective.

Reminds only. Always exits 0 and never blocks.
"""
import json
import os
import sys

REMINDER = (
    "The plan was approved. Before the first change, run the route skill: print the "
    "allocation table (Stage | Split | Executor | Model | Check | Why | Status) covering every "
    "stage of the plan. "
    "This is a reminder, not a block."
)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    if not isinstance(data, dict) or data.get("tool_name") != "ExitPlanMode":
        return
    text = REMINDER
    if os.environ.get("CLAUDE_CODE_SUBAGENT_MODEL_FORCE") == "1":
        forced = os.environ.get("CLAUDE_CODE_SUBAGENT_MODEL") or "the main conversation's model"
        text += (f" CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1 is set: every subagent runs on {forced}, whatever "
                 "model you pass. Write that model in every delegated row's Model cell and say so in your reply.")
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": text,
        }
    }))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
