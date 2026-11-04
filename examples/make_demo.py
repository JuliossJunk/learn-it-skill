"""Create a fictional course and HTML review in a new directory."""

import argparse
import importlib.util
import json
from datetime import date
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="A new directory for fictional demo files")
    args = parser.parse_args()
    root = args.destination.resolve()
    root.mkdir(parents=True, exist_ok=False)
    sections = []
    descriptions = [
        ("foundations", "Foundations of probability", "completed", "Explain conditional probability"),
        ("distributions", "Random variables & distributions", "in_progress", "Choose and justify a probability model"),
        ("inference", "Estimation & uncertainty", "planned", "Interpret an interval estimate"),
        ("simulation", "Simulation lab", "skipped", "Validate a model through simulation"),
    ]
    for index, (sid, title, coverage, outcome) in enumerate(descriptions):
        sections.append({"id": sid, "title": title, "coverage": coverage,
                         "materials": "ready" if index < 2 else "outline",
                         "prerequisites": [] if index == 0 else [descriptions[index - 1][0]],
                         "objectives": [{"id": sid, "text": outcome, "evidence": []}]})
    evidence = []
    observations = [
        ("foundations", "2026-10-12", "partial", "hint", "explain", "Confused the conditioning event; corrected with a diagram."),
        ("foundations", "2026-10-15", "pass", "none", "explain", "Explained the denominator on a different example without a hint."),
        ("foundations", "2026-10-20", "pass", "none", "transfer", "Applied conditional probability in a changed context."),
        ("distributions", "2026-10-23", "fail", "none", "execute", "Selected a model without checking independence."),
        ("distributions", "2026-10-26", "pass", "hint", "execute", "A hint prompted the independence check."),
        ("distributions", "2026-10-30", "pass", "none", "execute", "Justified a model on a new task without help."),
        ("distributions", "2026-11-03", "partial", "none", "transfer", "Missed a boundary case in a changed context."),
        ("distributions", "2026-11-05", "ungraded", "unknown", "explain", "A final explanation is still pending review."),
    ]
    for index, (oid, at, result, assistance, kind, note) in enumerate(observations, 1):
        eid = f"attempt-{index:02}"
        evidence.append({"id": eid, "objective_id": oid, "task_id": f"task-{index:02}", "at": at,
                         "result": result, "assistance": assistance, "kind": kind, "assessor": "model",
                         "artifact": "sessions/demo.md", "note": note})
        next(s for s in sections if s["id"] == oid)["objectives"][0]["evidence"].append(eid)
    state = {"schema_version": 1, "title": "Probability, one idea at a time", "current_section": "distributions",
             "next_action": "Finish the pending explanation, then revisit the boundary-case example.",
             "sections": sections, "evidence": evidence,
             "reviews": [{"objective_id": "foundations", "due": "2026-11-05", "reason": "Check the explanation after a delay."},
                         {"objective_id": "distributions", "due": "2026-11-08", "reason": "Retry the boundary case on a new task."}]}
    files = {name: f"# {name.removesuffix('.md').title()}\n\nFictional demo material; not a real learner record.\n"
             for name in ("README.md", "GOAL.md", "PROFILE.md", "PLAN.md", "SOURCES.md", "RESUME.md")}
    files["state.json"] = json.dumps(state, indent=2)
    files["sessions/demo.md"] = "# Fictional observations\n\nSynthetic metadata for a visual preview, not actual learner answers.\n\n" + "\n".join(f'- {e["id"]}: {e["note"]}' for e in evidence)
    for section in sections:
        for name in ("README.md", "theory.md", "practice.md"):
            files[f'sections/{section["id"]}/{name}'] = f'# {section["title"]}\n\nFictional demo {section["materials"]}.\n'
    for name, content in files.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    script = Path(__file__).resolve().parents[1] / "skills/learn-review/scripts/render_review.py"
    spec = importlib.util.spec_from_file_location("review_demo", script)
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    errors = renderer.ENGINE.validate(root, state)
    if errors:
        raise ValueError(errors)
    output = root / "reports/review.html"
    output.parent.mkdir()
    html = renderer.render(state, root, output, date(2026, 11, 5))
    html = html.replace("Learning journal / Review", "Fictional example / Learning review")
    output.write_text(html, encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
