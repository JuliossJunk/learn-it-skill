import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "skills/learn-start/scripts/project_state.py"
SPEC = importlib.util.spec_from_file_location("project_state", SCRIPT)
ENGINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENGINE)


class ProjectStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("README.md", "GOAL.md", "PROFILE.md", "PLAN.md", "SOURCES.md", "RESUME.md", "sessions/one.md", "sections/01-base/README.md", "sections/01-base/theory.md", "sections/01-base/practice.md"):
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("Observed learner material\n", encoding="utf-8")
        self.state = {
            "schema_version": 1, "title": "Test course", "current_section": "01-base",
            "next_action": "Continue the pending question",
            "sections": [{"id": "01-base", "title": "Basics", "prerequisites": [],
                          "coverage": "in_progress", "materials": "ready",
                          "objectives": [{"id": "solve", "text": "Solve a new task", "evidence": []}]}],
            "evidence": [], "reviews": [],
        }

    def add_attempt(self, eid="a1", **changes):
        attempt = {"id": eid, "objective_id": "solve", "task_id": "task-one", "at": "2026-11-05",
                   "kind": "execute", "result": "pass", "assistance": "none", "assessor": "model",
                   "artifact": "sessions/one.md", "note": "Correct method and checked result"}
        attempt.update(changes)
        self.state["evidence"].append(attempt)
        self.state["sections"][0]["objectives"][0]["evidence"].append(eid)

    def test_assistance_and_self_report_do_not_become_independent_passes(self):
        self.add_attempt("a1", assistance="hint")
        self.add_attempt("a2", assistance="worked_solution")
        self.add_attempt("a3", assistance="unknown")
        self.add_attempt("a4", assessor="learner")
        self.assertEqual(ENGINE.validate(self.root, self.state), [])
        row = ENGINE.report(self.state)["objectives"][0]
        self.assertEqual(row["attempt_count"], 4)
        self.assertEqual(row["independent_pass_task_count"], 0)

    def test_repeated_task_is_not_counted_as_distinct_skill_evidence(self):
        self.add_attempt("a1")
        self.add_attempt("a2")
        self.assertEqual(ENGINE.report(self.state)["objectives"][0]["independent_pass_task_count"], 1)

    def test_failure_and_pending_answer_remain_visible_after_success(self):
        self.add_attempt("a1")
        self.add_attempt("a2", result="fail", task_id="new-task")
        self.add_attempt("a3", result="ungraded", task_id="ambiguous-answer")
        row = ENGINE.report(self.state)["objectives"][0]
        self.assertEqual(row["independent_evidence"], ["a1"])
        self.assertEqual(row["partial_or_failed_evidence"], ["a2"])
        self.assertEqual(row["ungraded_evidence"], ["a3"])

    def test_cycle_and_unknown_prerequisite_rejected(self):
        self.state["sections"][0]["prerequisites"] = ["01-base", "unknown"]
        errors = ENGINE.validate(self.root, self.state)
        self.assertTrue(any("cycle" in e for e in errors))
        self.assertTrue(any("unknown prerequisite" in e for e in errors))

    def test_evidence_must_have_real_artifact_inside_project(self):
        self.add_attempt(artifact="../outside.md")
        self.assertTrue(any("artifact" in e for e in ENGINE.validate(self.root, self.state)))
        self.state["evidence"][0]["artifact"] = "sessions/missing.md"
        self.assertTrue(any("artifact" in e for e in ENGINE.validate(self.root, self.state)))

    def test_broken_evidence_links_rejected(self):
        self.add_attempt()
        self.state["sections"][0]["objectives"][0]["evidence"] = ["nonexistent"]
        errors = ENGINE.validate(self.root, self.state)
        self.assertTrue(any("backlink" in e for e in errors))
        self.assertTrue(any("unknown evidence" in e for e in errors))

    def test_due_reviews_use_explicit_client_date(self):
        self.state["reviews"] = [{"objective_id": "solve", "due": "2026-11-06", "reason": "Delayed check"}]
        self.assertEqual(ENGINE.validate(self.root, self.state), [])
        self.assertIsNone(ENGINE.report(self.state)["due_reviews"])
        self.assertEqual(ENGINE.report(self.state, date(2026, 11, 5))["due_reviews"], [])
        self.assertEqual(len(ENGINE.report(self.state, date(2026, 11, 6))["due_reviews"]), 1)

    def test_malformed_state_returns_errors_instead_of_certifying_progress(self):
        bad_cases = [[], {}, {**self.state, "sections": None}]
        for field in ("coverage", "materials"):
            broken = copy.deepcopy(self.state)
            broken["sections"][0][field] = []
            bad_cases.append(broken)
        for broken in bad_cases:
            with self.subTest(state=broken):
                self.assertTrue(ENGINE.validate(self.root, broken))

    def test_cli_report_is_read_only_and_does_not_claim_mastery(self):
        self.add_attempt()
        (self.root / "state.json").write_text(json.dumps(self.state, ensure_ascii=False), encoding="utf-8")
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        run = subprocess.run([sys.executable, "-B", "-X", "utf8", str(SCRIPT), "report", str(self.root), "--as-of", "2026-11-05"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(result["objectives"][0]["independent_pass_task_count"], 1)
        self.assertNotIn("mastery_score", result)
        after = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
