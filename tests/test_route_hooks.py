"""Mock tests for the route hooks: synthetic stdin JSON and synthetic transcripts."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HOOKS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hooks")
REMINDER = os.path.join(HOOKS, "plan_approved_reminder.py")
READBACK = os.path.join(HOOKS, "board_readback.py")


def run(script, payload, env_extra=None):
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("CLAUDE_PLUGIN_OPTION_", "CLAUDE_CODE_SUBAGENT_MODEL")) and k != "CLAUDE_PROJECT_DIR"}
    env.update(env_extra or {})
    p = subprocess.run([sys.executable, script], input=json.dumps(payload),
                       capture_output=True, text=True, env=env, timeout=10)
    return p.returncode, p.stdout.strip()


def user(text):
    return {"type": "user", "message": {"role": "user", "content": text}}


def tool_result():
    return {"type": "user", "message": {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": "t", "content": "ok"}]}}


def tool(name, **inp):
    return {"type": "assistant", "message": {"role": "assistant", "content": [
        {"type": "tool_use", "id": "t", "name": name, "input": inp}]}}


class ReminderTest(unittest.TestCase):
    def test_fires_on_exit_plan_mode(self):
        code, out = run(REMINDER, {"hook_event_name": "PostToolUse", "tool_name": "ExitPlanMode",
                                   "tool_input": {}, "tool_response": {"plan": "x"}})
        self.assertEqual(code, 0)
        hso = json.loads(out)["hookSpecificOutput"]
        self.assertEqual(hso["hookEventName"], "PostToolUse")
        self.assertIn("route", hso["additionalContext"])
        self.assertIn("Stage | Split | Executor | Model | Check | Why | Status", hso["additionalContext"])
        self.assertNotIn("decision", json.loads(out))

    def test_no_force_warning_by_default(self):
        _, out = run(REMINDER, {"hook_event_name": "PostToolUse", "tool_name": "ExitPlanMode"})
        self.assertNotIn("MODEL_FORCE", json.loads(out)["hookSpecificOutput"]["additionalContext"])

    def test_force_warning_names_forced_model(self):
        _, out = run(REMINDER, {"hook_event_name": "PostToolUse", "tool_name": "ExitPlanMode"},
                     {"CLAUDE_CODE_SUBAGENT_MODEL_FORCE": "1", "CLAUDE_CODE_SUBAGENT_MODEL": "haiku"})
        ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1", ctx)
        self.assertIn("every subagent runs on haiku", ctx)

    def test_force_without_model_names_main_model(self):
        _, out = run(REMINDER, {"hook_event_name": "PostToolUse", "tool_name": "ExitPlanMode"},
                     {"CLAUDE_CODE_SUBAGENT_MODEL_FORCE": "1"})
        self.assertIn("the main conversation's model", json.loads(out)["hookSpecificOutput"]["additionalContext"])

    def test_silent_on_other_tools(self):
        for name in ("Edit", "Bash", "Write"):
            code, out = run(REMINDER, {"hook_event_name": "PostToolUse", "tool_name": name})
            self.assertEqual((code, out), (0, ""), name)

    def test_bad_stdin_fails_open(self):
        p = subprocess.run([sys.executable, REMINDER], input="not json",
                           capture_output=True, text=True, timeout=10)
        self.assertEqual((p.returncode, p.stdout.strip()), (0, ""))


class ReadbackTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        self.board = os.path.join(self.dir, "PROGRESS.md")
        self.cmd_loc = "command:gh project item-list ;; gh project item-edit ;; gh project item-add"

    def tearDown(self):
        self.tmp.cleanup()

    def transcript(self, entries):
        path = os.path.join(self.dir, "t.jsonl")
        with open(path, "w") as fh:
            for e in entries:
                fh.write(json.dumps(e) + "\n")
        return path

    def stop(self, entries, location="PROGRESS.md", active=False, transcript=None):
        payload = {"hook_event_name": "Stop", "cwd": self.dir, "stop_hook_active": active,
                   "transcript_path": transcript or self.transcript(entries)}
        env = {"CLAUDE_PLUGIN_OPTION_BOARD_LOCATION": location} if location is not None else {}
        code, out = run(READBACK, payload, env)
        self.assertEqual(code, 0)
        return json.loads(out) if out else None

    def assertBlocks(self, result):
        self.assertIsNotNone(result)
        self.assertEqual(result["decision"], "block")
        self.assertIn("read", result["reason"].lower())

    # --- file location ---
    def test_file_written_not_read_blocks(self):
        r = self.stop([user("go"), tool("Edit", file_path=self.board, old_string="a", new_string="b"),
                       tool_result()])
        self.assertBlocks(r)
        self.assertIn(self.board, r["reason"])

    def test_file_relative_path_and_write_tool(self):
        self.assertBlocks(self.stop([user("go"), tool("Write", file_path="PROGRESS.md", content="x")]))

    def test_file_bash_redirect_counts_as_write(self):
        self.assertBlocks(self.stop([user("go"), tool("Bash", command="echo '| a | Done |' >> PROGRESS.md")]))

    def test_file_read_after_write_passes(self):
        self.assertIsNone(self.stop([user("go"), tool("Edit", file_path=self.board), tool_result(),
                                     tool("Read", file_path=self.board), tool_result()]))

    def test_file_bash_cat_after_write_passes(self):
        self.assertIsNone(self.stop([user("go"), tool("Write", file_path=self.board),
                                     tool("Bash", command="cat PROGRESS.md")]))

    def test_file_read_before_write_still_blocks(self):
        self.assertBlocks(self.stop([user("go"), tool("Read", file_path=self.board),
                                     tool("Edit", file_path=self.board)]))

    def test_nothing_written_passes(self):
        self.assertIsNone(self.stop([user("go"), tool("Edit", file_path=os.path.join(self.dir, "other.md")),
                                     tool("Bash", command="echo hi > notes.txt")]))

    def test_write_in_earlier_turn_ignored(self):
        self.assertIsNone(self.stop([user("first"), tool("Edit", file_path=self.board), tool_result(),
                                     user("second"), tool("Bash", command="ls")]))

    def test_stop_hook_active_passes(self):
        self.assertIsNone(self.stop([user("go"), tool("Edit", file_path=self.board)], active=True))

    def test_missing_transcript_passes(self):
        self.assertIsNone(self.stop([], transcript=os.path.join(self.dir, "missing.jsonl")))

    def test_unset_location_passes(self):
        self.assertIsNone(self.stop([user("go"), tool("Edit", file_path=self.board)], location=None))
        self.assertIsNone(self.stop([user("go"), tool("Edit", file_path=self.board)], location=""))

    def test_garbage_stdin_fails_open(self):
        p = subprocess.run([sys.executable, READBACK], input="{broken",
                           capture_output=True, text=True, timeout=10,
                           env=dict(os.environ, CLAUDE_PLUGIN_OPTION_BOARD_LOCATION="PROGRESS.md"))
        self.assertEqual((p.returncode, p.stdout.strip()), (0, ""))

    # --- command location ---
    def test_command_written_not_read_blocks(self):
        r = self.stop([user("go"), tool("Bash", command="gh project item-edit --id X --field-id S --text Done")],
                      location=self.cmd_loc)
        self.assertBlocks(r)
        self.assertIn("gh project item-list", r["reason"])

    def test_command_named_inside_quotes_is_not_a_write(self):
        # echo / grep / a variable that only mentions the write command does not run it
        self.assertIsNone(self.stop([user("go"),
                                     tool("Bash", command="LOC='gh project item-edit'; grep -n \"gh project item-add\" notes.md")],
                                    location=self.cmd_loc))

    def test_command_read_after_write_passes(self):
        self.assertIsNone(self.stop([user("go"), tool("Bash", command="gh project item-add 3 --url U"),
                                     tool("Bash", command="gh project item-list 3 --owner me")],
                                    location=self.cmd_loc))

    def test_command_write_then_read_in_one_call_passes(self):
        self.assertIsNone(self.stop([user("go"), tool("Bash",
                                     command="gh project item-edit --id X && gh project item-list 3")],
                                    location=self.cmd_loc))

    def test_command_nothing_written_passes(self):
        self.assertIsNone(self.stop([user("go"), tool("Bash", command="gh project item-list 3"),
                                     tool("Edit", file_path=self.board)], location=self.cmd_loc))

    def test_command_stop_hook_active_passes(self):
        self.assertIsNone(self.stop([user("go"), tool("Bash", command="gh project item-edit --id X")],
                                    location=self.cmd_loc, active=True))

    def test_command_missing_transcript_passes(self):
        self.assertIsNone(self.stop([], location=self.cmd_loc,
                                    transcript=os.path.join(self.dir, "missing.jsonl")))


if __name__ == "__main__":
    unittest.main()
