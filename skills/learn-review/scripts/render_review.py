"""Render a validated learning project as a standalone, offline HTML review."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from collections import Counter
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import quote


SKILL = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "learning_project_state", SKILL.parent / "learn-start/scripts/project_state.py"
)
ENGINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENGINE)


def metrics(state: dict, as_of: date | None = None) -> dict:
    """Count evidence and expose transitions without declaring causal growth."""
    attempts = sorted(
        (e for e in state["evidence"] if as_of is None or e["at"][:10] <= as_of.isoformat()),
        key=lambda e: (e["at"][:10], e["at"], e["id"]),
    )
    snapshot = {**state, "evidence": attempts}
    summary = ENGINE.report(snapshot, as_of)
    independent_ids = {eid for row in summary["objectives"] for eid in row["independent_evidence"]}
    seen: set[str] = set()
    daily: dict[str, dict] = {}
    for entry in attempts:
        day = entry["at"][:10]
        bucket = daily.setdefault(day, {"attempts": 0, "objectives": 0})
        bucket["attempts"] += 1
        if entry["id"] in independent_ids:
            seen.add(entry["objective_id"])
        bucket["objectives"] = len(seen)
    transitions = []
    for objective in summary["objectives"]:
        entries = [e for e in attempts if e["objective_id"] == objective["id"]]
        for later in entries:
            if later["id"] not in independent_ids:
                continue
            earlier = [e for e in entries
                       if e["at"][:10] < later["at"][:10]
                       and e["kind"] == later["kind"] and e["task_id"] != later["task_id"]
                       and e["assessor"] != "learner"
                       and (e["result"] in {"fail", "partial"}
                            or (e["result"] == "pass" and e["assistance"] in {"hint", "worked_solution"}))]
            if earlier:
                transitions.append({"objective": objective["text"], "before": earlier[-1], "after": later})
                break
    return {"summary": summary, "attempts": attempts, "daily": daily,
            "independent_ids": independent_ids, "transitions": transitions,
            "objective_count": len(summary["objectives"]), "demonstrated": len(seen),
            "excluded_future": len(state["evidence"]) - len(attempts)}


def chart(daily: dict, total: int) -> str:
    if not daily:
        return '<p class="empty">No dated attempts recorded. A trend cannot yet be assessed.</p>'
    days = list(daily)
    start, end = date.fromisoformat(days[0]), date.fromisoformat(days[-1])
    span = max(1, (end - start).days)
    points = [(54 + (date.fromisoformat(day) - start).days / span * 590,
               184 - daily[day]["objectives"] / max(1, total) * 140) for day in days]
    coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    area = f'54,184 {coords} {points[-1][0]:.1f},184'
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4"><title>{day}: '
                   f'{daily[day]["objectives"]} objectives; {daily[day]["attempts"]} attempts</title></circle>'
                   for day, (x, y) in zip(days, points))
    return (f'<svg class="chart" viewBox="0 0 700 230" role="img" '
            f'aria-label="Cumulative objectives with independent evidence, out of {total}">'
            f'<path class="axis" d="M54 40 V184 H650"/><text x="15" y="48">{total}</text>'
            f'<text x="28" y="188">0</text><polygon class="area" points="{area}"/>'
            f'<polyline class="line" points="{coords}"/>{dots}'
            f'<text x="54" y="216">{days[0]}</text>'
            f'<text x="650" y="216" text-anchor="end">{days[-1]}</text></svg>')


def source_link(project: Path, output: Path, artifact: str, label: str) -> str:
    if not ENGINE.project_file(project, artifact):
        return escape(label) + " (source unavailable)"
    target = (project / artifact).resolve()
    try:
        href = quote(Path(os.path.relpath(target, output.parent)).as_posix(), safe="/.-_")
    except ValueError:  # A report on another Windows drive needs a file URI.
        href = target.as_uri()
    return f'<a href="{escape(href, quote=True)}">{escape(label)}</a>'


def render(state: dict, project: Path, output: Path, as_of: date | None = None) -> str:
    data = metrics(state, as_of)
    summary, attempts = data["summary"], data["attempts"]
    rows = {row["id"]: row for row in summary["objectives"]}
    topic_html = []
    for section in state["sections"]:
        outcomes = []
        for objective in section["objectives"]:
            row = rows[objective["id"]]
            outcomes.append(f'<li>{escape(objective["text"])}<br><small>'
                            f'{row["independent_pass_task_count"]} distinct independently passed tasks; '
                            f'{row["attempt_count"]} recorded attempts; '
                            f'{len(row["ungraded_evidence"])} ungraded.</small></li>')
        prereqs = ", ".join(section["prerequisites"]) or "None"
        source = source_link(project, output, f'sections/{section["id"]}/README.md', "Section plan and exit check")
        topic_html.append(f'<details open><summary>{escape(section["title"])} '
                          f'<span class="tag {section["coverage"]}">{section["coverage"].replace("_", " ")}</span>'
                          f'</summary><p class="subtle">Prerequisites: {escape(prereqs)}. '
                          f'Materials: {section["materials"]}.</p><ul>{"".join(outcomes)}</ul>{source}</details>')
    evidence_rows = []
    for entry in reversed(attempts):
        source = source_link(project, output, entry["artifact"], entry["id"])
        evidence_rows.append(f'<tr><td>{escape(entry["at"])}<br>{source}</td>'
                             f'<td>{escape(entry["objective_id"])}<br><small>{entry["kind"]}</small></td>'
                             f'<td>{entry["result"]}<br><small>Assistance: {entry["assistance"]}; '
                             f'assessor: {entry["assessor"]}</small></td><td>{escape(entry["note"])}</td></tr>')
    changes = []
    for transition in data["transitions"]:
        before, after = transition["before"], transition["after"]
        changes.append(f'<li>{escape(transition["objective"])}: '
                       f'{source_link(project, output, before["artifact"], before["id"])} '
                       f'({escape(before["at"][:10])}, {before["result"]}, {before["assistance"]}) to '
                       f'{source_link(project, output, after["artifact"], after["id"])} '
                       f'({escape(after["at"][:10])}, independent pass on a different task).</li>')
    growth = (f'<ul>{"".join(changes)}</ul><p>These transitions suggest possible improvement. '
              'Task difficulty, tools, and rubric comparability still need inspection; later difficulties remain in the ledger.</p>'
              if changes else '<p>Insufficient comparable evidence to establish growth. This does not imply no learning occurred.</p>')
    reviews = []
    for review in state["reviews"]:
        status = "Scheduled"
        if as_of is not None:
            status = "Due" if date.fromisoformat(review["due"]) <= as_of else "Upcoming"
        reviews.append(f'<li><strong>{status} · {review["due"]}</strong><br>'
                       f'{escape(review["objective_id"])}: {escape(review["reason"])}</li>')
    process = Counter(entry["assistance"] for entry in attempts)
    kinds = Counter(entry["kind"] for entry in attempts)
    current = next((s["title"] for s in state["sections"] if s["id"] == state["current_section"]), "No current section selected")
    coverage = summary["coverage"]
    coverage_tags = "".join(f'<span class="tag {key}">{key.replace("_", " ")}: {value}</span>' for key, value in coverage.items())
    stat_items = [(f'{coverage["completed"]}/{summary["section_count"]}', "Sections covered"),
                  (f'{data["demonstrated"]}/{data["objective_count"]}', "Outcomes with independent evidence"),
                  (str(len(attempts)), "Recorded attempts"), (str(len(data["daily"])), "Dates with recorded attempts")]
    stats = "".join(f'<div class="stat"><span class="number">{number}</span><small>{label}</small></div>' for number, label in stat_items)
    cutoff = as_of.isoformat() if as_of else "No reference date supplied"
    future = f'<p>{data["excluded_future"]} future-dated attempts excluded.</p>' if data["excluded_future"] else ""
    css = (SKILL / "assets/report.css").read_text(encoding="utf-8")
    ledger = ('<div class="scroll"><table><thead><tr><th>Date / source</th><th>Outcome / kind</th>'
              '<th>Result / support</th><th>Recorded judgement</th></tr></thead>'
              f'<tbody>{"".join(evidence_rows)}</tbody></table></div>' if evidence_rows else '<p class="empty">No attempts recorded.</p>')
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(state["title"])} — Learning review</title><style>{css}</style></head>
<body><main><header><div class="eyebrow">Learning journal / Review</div><h1>{escape(state["title"])}</h1>
<p class="intro">A map of the work so far, the evidence behind it, and the road ahead.</p>
<small>Evidence through: {cutoff}. Roadmap: current saved state.</small></header>
<div class="stats">{stats}</div><div class="grid"><section class="panel"><div class="eyebrow">01 / Evidence over time</div>
<h2>Building a record</h2>{chart(data["daily"], data["objective_count"])}
<p class="legend"><span><span class="dot"></span>Cumulative outcomes with at least one independent pass</span></p>
<p class="subtle">Evidence accumulation, not a mastery or growth score. Earlier successes stay counted after later failures.</p>{future}</section>
<aside class="panel accent"><div class="eyebrow">02 / Your next step</div><h2>{escape(current)}</h2>
<p>{escape(state["next_action"])}</p><small>Follow the saved stopping point; check prerequisites before advancing.</small></aside></div>
<section class="panel"><div class="eyebrow">03 / Full roadmap</div><h2>Covered, current, and ahead</h2>
<p>{coverage_tags}</p><p class="subtle">Coverage describes activity. Skipped sections and prepared outlines do not certify understanding.</p>
{"".join(topic_html) or '<p class="empty">No sections recorded.</p>'}</section>
<div class="grid"><section class="panel"><div class="eyebrow">04 / Observed changes</div><h2>Is there growth?</h2>{growth}
<!-- Add an evidence-linked interpretation here after inspecting the source attempts. -->
</section><section class="panel"><div class="eyebrow">05 / Learning process</div><h2>How the work happens</h2>
<p>Recorded assistance: {escape(", ".join(f"{key}: {value}" for key, value in sorted(process.items())) or "No attempts")}.</p>
<p>Recorded task types: {escape(", ".join(f"{key}: {value}" for key, value in sorted(kinds.items())) or "No attempts")}.</p>
<p class="subtle">These counts describe recorded practice. Explanation history and study duration require session records.</p></section></div>
<section class="panel"><div class="eyebrow">06 / Revisit</div><h2>Review and retention</h2>
<ul>{"".join(reviews)}</ul><p>{'Review dates are plans, not evidence of retention.' if reviews else 'No reviews scheduled.'}
 Delayed retention requires inspecting actual later attempts; this renderer does not certify it.</p></section>
<section class="panel"><div class="eyebrow">07 / Source ledger</div><h2>Attempts, support, and open questions</h2>{ledger}</section>
<footer>Local, offline report · No course records changed · Model judgements remain judgements.
Source links work while the report and project retain their relative locations.</footer></main></body></html>'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--as-of", type=date.fromisoformat, help="Client-local evidence cutoff and review date")
    args = parser.parse_args()
    try:
        project, output = args.project.resolve(), args.output.resolve()
        if output.suffix.lower() != ".html":
            raise ValueError("Output must have an .html extension")
        if output.exists():
            raise ValueError("Output exists; choose a new report filename")
        if output.is_relative_to(project) and not output.is_relative_to(project / "reports"):
            raise ValueError("Reports inside the project must be saved under reports/")
        state = json.loads((project / "state.json").read_text(encoding="utf-8-sig"))
        errors = ENGINE.validate(project, state)
        if errors:
            raise ValueError("Invalid project: " + "; ".join(errors))
        html = render(state, project, output, args.as_of)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as destination:
            destination.write(html)
        print(json.dumps({"ok": True, "output": str(output)}, ensure_ascii=True))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
