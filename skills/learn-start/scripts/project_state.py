"""Validate and summarize learning-project evidence without mutating the project."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path


def valid_date(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        if len(value) == 10:
            date.fromisoformat(value)
        else:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def project_file(root: Path, value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts or ":" in value:
        return False
    try:
        resolved = (root / relative).resolve()
        resolved.relative_to(root.resolve())
        return resolved.is_file()
    except (ValueError, OSError):
        return False


def validate(root: Path, state: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(state, dict):
        return ["state must be an object"]
    if type(state.get("schema_version")) is not int or state["schema_version"] != 1:
        errors.append("schema_version must be 1")
    for field in ("title", "next_action"):
        if not isinstance(state.get(field), str) or not state[field].strip():
            errors.append(f"{field} must be nonempty text")
    for filename in ("README.md", "GOAL.md", "PROFILE.md", "PLAN.md", "SOURCES.md", "RESUME.md"):
        if not project_file(root, filename):
            errors.append(f"missing project file: {filename}")
    for field in ("sections", "evidence", "reviews"):
        if not isinstance(state.get(field), list):
            errors.append(f"{field} must be an array")
    if errors and any(not isinstance(state.get(f), list) for f in ("sections", "evidence", "reviews")):
        return errors

    section_ids: set[str] = set()
    objectives: dict[str, dict] = {}
    graph: dict[str, list[str]] = {}
    for section in state["sections"]:
        if not isinstance(section, dict):
            errors.append("section must be an object")
            continue
        sid = section.get("id")
        if not isinstance(sid, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", sid):
            errors.append("section id must be a lowercase slug")
            continue
        if sid in section_ids:
            errors.append(f"duplicate section: {sid}")
        section_ids.add(sid)
        if not isinstance(section.get("title"), str) or not section["title"].strip():
            errors.append(f"{sid}: missing title")
        if not isinstance(section.get("coverage"), str) or section["coverage"] not in {"planned", "in_progress", "completed", "skipped"}:
            errors.append(f"{sid}: invalid coverage")
        if not isinstance(section.get("materials"), str) or section["materials"] not in {"outline", "ready"}:
            errors.append(f"{sid}: invalid materials status")
        prerequisites = section.get("prerequisites")
        if not isinstance(prerequisites, list) or not all(isinstance(p, str) for p in prerequisites):
            errors.append(f"{sid}: prerequisites must be string IDs")
            prerequisites = []
        graph[sid] = prerequisites
        for filename in ("README.md", "theory.md", "practice.md"):
            if not project_file(root, f"sections/{sid}/{filename}"):
                errors.append(f"{sid}: missing {filename}")
        entries = section.get("objectives")
        if not isinstance(entries, list) or not entries:
            errors.append(f"{sid}: objectives must be a nonempty array")
            continue
        for objective in entries:
            if not isinstance(objective, dict):
                errors.append(f"{sid}: objective must be an object")
                continue
            oid = objective.get("id")
            if not isinstance(oid, str) or not oid.strip():
                errors.append(f"{sid}: objective needs an ID")
                continue
            if oid in objectives:
                errors.append(f"duplicate objective: {oid}")
            objectives[oid] = objective
            if not isinstance(objective.get("text"), str) or not objective["text"].strip():
                errors.append(f"{oid}: missing outcome text")
            refs = objective.get("evidence")
            if not isinstance(refs, list) or not all(isinstance(ref, str) for ref in refs):
                errors.append(f"{oid}: evidence must be string IDs")
            elif len(refs) != len(set(refs)):
                errors.append(f"{oid}: repeated evidence reference")

    for sid, prerequisites in graph.items():
        for prerequisite in prerequisites:
            if prerequisite not in section_ids:
                errors.append(f"{sid}: unknown prerequisite {prerequisite}")
    remaining = {sid: set(ps) & section_ids for sid, ps in graph.items()}
    while remaining:
        ready = {sid for sid, ps in remaining.items() if not ps}
        if not ready:
            errors.append("prerequisites contain a cycle")
            break
        remaining = {sid: ps - ready for sid, ps in remaining.items() if sid not in ready}
    current = state.get("current_section")
    if current is not None and (not isinstance(current, str) or current not in section_ids):
        errors.append("current_section must be a known ID or null")

    evidence: dict[str, dict] = {}
    enums = {
        "kind": {"recall", "explain", "execute", "diagnose", "transfer"},
        "result": {"pass", "partial", "fail", "ungraded"},
        "assistance": {"none", "hint", "worked_solution", "unknown"},
        "assessor": {"model", "deterministic", "learner"},
    }
    for entry in state["evidence"]:
        if not isinstance(entry, dict):
            errors.append("evidence entry must be an object")
            continue
        eid = entry.get("id")
        if not isinstance(eid, str) or not eid.strip():
            errors.append("evidence needs an ID")
            continue
        if eid in evidence:
            errors.append(f"duplicate evidence: {eid}")
        evidence[eid] = entry
        oid = entry.get("objective_id")
        if not isinstance(oid, str) or oid not in objectives:
            errors.append(f"{eid}: unknown objective")
        else:
            refs = objectives[oid].get("evidence")
            if isinstance(refs, list) and eid not in refs:
                errors.append(f"{eid}: missing objective backlink")
        for field, allowed in enums.items():
            value = entry.get(field)
            if not isinstance(value, str) or value not in allowed:
                errors.append(f"{eid}: invalid {field}")
        for field in ("task_id", "note"):
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                errors.append(f"{eid}: missing {field}")
        if not valid_date(entry.get("at")):
            errors.append(f"{eid}: invalid date")
        if not project_file(root, entry.get("artifact")):
            errors.append(f"{eid}: artifact must be an existing project-relative file")
    for oid, objective in objectives.items():
        refs = objective.get("evidence")
        if not isinstance(refs, list):
            continue
        for ref in refs:
            if not isinstance(ref, str) or ref not in evidence:
                errors.append(f"{oid}: unknown evidence reference")
            elif evidence[ref].get("objective_id") != oid:
                errors.append(f"{oid}: evidence belongs to another objective")
    for review in state["reviews"]:
        if not isinstance(review, dict):
            errors.append("review must be an object")
            continue
        oid = review.get("objective_id")
        if not isinstance(oid, str) or oid not in objectives:
            errors.append("review references unknown objective")
        due = review.get("due")
        if not valid_date(due) or len(due) != 10:
            errors.append("review due must be an ISO date")
        if not isinstance(review.get("reason"), str) or not review["reason"].strip():
            errors.append("review needs a reason")
    return errors


def report(state: dict, as_of: date | None = None) -> dict:
    coverage = {key: 0 for key in ("planned", "in_progress", "completed", "skipped")}
    rows = []
    for section in state["sections"]:
        coverage[section["coverage"]] += 1
        for objective in section["objectives"]:
            attempts = [e for e in state["evidence"] if e["objective_id"] == objective["id"]]
            independent = [e for e in attempts if e["result"] == "pass" and e["assistance"] == "none" and e["assessor"] != "learner"]
            rows.append({
                "id": objective["id"], "text": objective["text"],
                "attempt_count": len(attempts),
                "independent_pass_task_count": len({e["task_id"] for e in independent}),
                "independent_evidence": [e["id"] for e in independent],
                "independent_transfer_evidence": [e["id"] for e in independent if e["kind"] == "transfer"],
                "partial_or_failed_evidence": [e["id"] for e in attempts if e["result"] in {"partial", "fail"}],
                "ungraded_evidence": [e["id"] for e in attempts if e["result"] == "ungraded"],
            })
    return {
        "title": state["title"], "current_section": state["current_section"],
        "next_action": state["next_action"], "section_count": len(state["sections"]),
        "coverage": coverage, "objectives": rows,
        "scheduled_reviews": state["reviews"],
        "due_reviews": None if as_of is None else [r for r in state["reviews"] if date.fromisoformat(r["due"]) <= as_of],
        "as_of": as_of.isoformat() if as_of else None,
        "interpretation": "Evidence counts only; mastery, retention and semantic correctness require inspection of the attempts.",
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "report"))
    parser.add_argument("project", type=Path)
    parser.add_argument("--as-of", type=date.fromisoformat, help="Client-local date for due-review reporting")
    args = parser.parse_args()
    try:
        state = json.loads((args.project / "state.json").read_text(encoding="utf-8-sig"))
        errors = validate(args.project, state)
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    result = {"ok": True} if args.command == "validate" else report(state, args.as_of)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
