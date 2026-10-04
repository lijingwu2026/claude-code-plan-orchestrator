#!/usr/bin/env python3
"""Stop hook: if Claude wrote the progress board this turn and did not read it back
afterwards, block the stop once and ask for a readback plus the board's location.

Board location comes from the plugin option `board_location`
(env CLAUDE_PLUGIN_OPTION_BOARD_LOCATION), in one of two forms:
  PROGRESS.md                                   a file, relative to the project root or absolute
  command:<read> ;; <write> [;; <write> ...]    shell commands that read / write the board

Never blocks twice (stop_hook_active). Fails open: any error, a missing transcript or an
unset option means exit 0 without a block.
"""
import json
import os
import re
import sys

FILE_WRITE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
# Targets of `>`, `>>`, `tee`, `tee -a`.
REDIRECT_RE = re.compile(r"(?:>>?|\btee(?:\s+-a)?)\s*(\"[^\"]+\"|'[^']+'|[^\s;&|]+)")
SED_INPLACE_RE = re.compile(r"\bsed\s+(?:-[A-Za-z]*\s+)*-i")


def parse_location(raw):
    raw = raw.strip()
    if raw.startswith("command:"):
        parts = [" ".join(p.split()) for p in raw[len("command:"):].split(";;")]
        parts = [p for p in parts if p]
        if len(parts) < 2:
            return None
        return {"kind": "command", "read": parts[0], "writes": parts[1:]}
    return {"kind": "file", "path": raw}


def current_turn_tool_uses(transcript_path):
    """Tool calls the main agent made since the last real user message, in order."""
    entries = []
    with open(transcript_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except ValueError:
                continue
    uses = []
    for entry in entries:
        if not isinstance(entry, dict) or entry.get("isSidechain"):
            continue
        msg = entry.get("message") or {}
        content = msg.get("content")
        if entry.get("type") == "user" and not entry.get("isMeta"):
            is_prompt = isinstance(content, str) or (
                isinstance(content, list)
                and any(isinstance(c, dict) and c.get("type") == "text" for c in content)
            )
            if is_prompt:
                uses = []
        elif entry.get("type") == "assistant" and isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    uses.append((c.get("name"), c.get("input") or {}))
    return uses


def file_events(name, inp, board, cwd):
    """Return 'write', 'read', 'write_then_read' or None for one tool call on a file board."""
    def same(p):
        if not p:
            return False
        p = p.strip("\"'")
        return os.path.normpath(os.path.join(cwd, p)) == board

    if name in FILE_WRITE_TOOLS:
        return "write" if same(inp.get("file_path") or inp.get("notebook_path")) else None
    if name == "Read":
        return "read" if same(inp.get("file_path")) else None
    if name == "Bash":
        cmd = inp.get("command") or ""
        base = os.path.basename(board)
        if base not in cmd:
            return None
        if any(same(t) for t in REDIRECT_RE.findall(cmd)) or SED_INPLACE_RE.search(cmd):
            return "write"
        return "read"
    return None


QUOTED_RE = re.compile(r"\"[^\"]*\"|'[^']*'")


def command_events(name, inp, loc):
    if name != "Bash":
        return None
    # Text inside quotes is an argument (echo, grep, a variable), not the board command being run.
    cmd = " ".join(QUOTED_RE.sub(" ", inp.get("command") or "").split())
    write_pos = max((cmd.rfind(w) for w in loc["writes"]), default=-1)
    read_pos = cmd.rfind(loc["read"])
    if write_pos >= 0:
        return "write_then_read" if read_pos > write_pos else "write"
    return "read" if read_pos >= 0 else None


def main():
    data = json.load(sys.stdin)
    if data.get("stop_hook_active"):
        return
    raw = os.environ.get("CLAUDE_PLUGIN_OPTION_BOARD_LOCATION", "")
    loc = parse_location(raw) if raw.strip() else None
    transcript = data.get("transcript_path")
    if not loc or not transcript or not os.path.isfile(transcript):
        return
    cwd = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()

    if loc["kind"] == "file":
        board = os.path.normpath(os.path.join(cwd, loc["path"]))
        how = "Read the file"
        where = board
    else:
        how = "Run `%s`" % loc["read"]
        where = "the board read by `%s`" % loc["read"]

    unread_write = False
    for name, inp in current_turn_tool_uses(transcript):
        if loc["kind"] == "file":
            ev = file_events(name, inp, board, cwd)
        else:
            ev = command_events(name, inp, loc)
        if ev == "write":
            unread_write = True
        elif ev in ("read", "write_then_read"):
            unread_write = False

    if unread_write:
        print(json.dumps({
            "decision": "block",
            "reason": (
                "You wrote the progress board this turn and have not read it back since. "
                "%s now, confirm each row you changed says what you wrote, and name the "
                "board's location (%s) in your reply." % (how, where)
            ),
        }))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
