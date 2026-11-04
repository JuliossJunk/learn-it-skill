import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "skills/learn-review/scripts/render_review.py"
SPEC = importlib.util.spec_from_file_location("render_review", SCRIPT)
REVIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REVIEW)


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("README.md", "GOAL.md", "PROFILE.md", "PLAN.md", "SOURCES.md", "RESUME.md",
                     "sessions/one.md", "sections/basics/README.md", "sections/basics/theory.md", "sections/basics/practice.md"):
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("Observed record", encoding="utf-8")
        self.state = {"schema_version": 1, "title": "Probability & inference", "current_section": "basics",
                      "next_action": "Explain the pending example", "evidence": [], "reviews": [],
                      "sections": [{"id": "basics", "title": "Foundations", "coverage": "in_progress",
                                    "materials": "ready", "prerequisites": [],
                                    "objectives": [{"id": "solve", "text": "Solve a new example", "evidence": []}]}]}

    def attempt(self, eid, day, **kwargs):
        entry = {"id": eid, "objective_id": "solve", "task_id": eid, "at": day, "kind": "execute",
                 "result": "pass", "assistance": "none", "assessor": "model", "artifact": "sessions/one.md",
                 "note": "Checked against the rubric"}
        entry.update(kwargs)
        self.state["evidence"].append(entry)
        self.state["sections"][0]["objectives"][0]["evidence"].append(eid)

    def test_assisted_and_self_reported_successes_do_not_inflate_chart(self):
        self.attempt("hinted", "2026-10-01", assistance="hint")
        self.attempt("self", "2026-10-02", assessor="learner")
        self.attempt("unknown", "2026-10-03", assistance="unknown")
        data = REVIEW.metrics(self.state)
        self.assertEqual(data["demonstrated"], 0)
        self.assertEqual([x["objectives"] for x in data["daily"].values()], [0, 0, 0])

    def test_repeated_tasks_and_same_day_answers_do_not_imply_growth(self):
        self.attempt("first", "2026-10-01", result="fail", task_id="same")
        self.attempt("repeat", "2026-10-02", task_id="same")
        self.attempt("same-day", "2026-10-01", task_id="new")
        self.assertEqual(REVIEW.metrics(self.state)["transitions"], [])

    def test_transition_requires_same_skill_kind_and_later_distinct_task(self):
        self.attempt("first", "2026-10-01", result="partial")
        self.attempt("recall", "2026-10-02", kind="recall")
        self.assertEqual(REVIEW.metrics(self.state)["transitions"], [])
        self.attempt("later", "2026-10-03")
        data = REVIEW.metrics(self.state)
        self.assertEqual(data["transitions"][0]["after"]["id"], "later")
        self.assertEqual(data["demonstrated"], 1)

    def test_cutoff_excludes_future_attempts_but_preserves_roadmap(self):
        self.attempt("future", "2026-12-01")
        data = REVIEW.metrics(self.state, date(2026, 11, 5))
        self.assertEqual(data["demonstrated"], 0)
        self.assertEqual(data["excluded_future"], 1)
        self.assertEqual(data["summary"]["section_count"], 1)

    def test_failure_remains_visible_after_success(self):
        self.attempt("pass", "2026-10-01")
        self.attempt("fail", "2026-10-02", result="fail")
        data = REVIEW.metrics(self.state)
        self.assertEqual(data["demonstrated"], 1)
        self.assertEqual(data["summary"]["objectives"][0]["partial_or_failed_evidence"], ["fail"])

    def test_html_escapes_learning_content_and_has_offline_links(self):
        self.state["title"] = '<script>alert("title")</script>'
        self.attempt("unsafe", "2026-10-01", note='<img src=x onerror="alert(1)">')
        html = REVIEW.render(self.state, self.root, self.root / "reports/review.html")
        self.assertNotIn("<script>", html)
        self.assertNotIn("<img src=x", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn('href="../sessions/one.md"', html)
        self.assertNotIn('<link ', html)
        self.assertIn("Insufficient comparable evidence", html)

    def test_cli_writes_only_report_and_refuses_to_replace_it(self):
        self.attempt("one", "2026-10-01")
        (self.root / "state.json").write_text(json.dumps(self.state), encoding="utf-8")
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        output = self.root / "reports/review.html"
        command = [sys.executable, "-B", str(SCRIPT), str(self.root), "--output", str(output)]
        run = subprocess.run(command, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertTrue(output.is_file())
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(set(after) - set(before), {Path("reports/review.html")})
        self.assertTrue(all(after[key] == value for key, value in before.items()))
        again = subprocess.run(command, capture_output=True)
        self.assertNotEqual(again.returncode, 0)

    def test_invalid_state_does_not_create_report(self):
        broken = copy.deepcopy(self.state)
        broken["sections"][0]["prerequisites"] = ["unknown"]
        (self.root / "state.json").write_text(json.dumps(broken), encoding="utf-8")
        output = self.root / "reports/review.html"
        run = subprocess.run([sys.executable, "-B", str(SCRIPT), str(self.root), "--output", str(output)], capture_output=True)
        self.assertNotEqual(run.returncode, 0)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
