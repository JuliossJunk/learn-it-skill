---
name: learn-review
description: Create a polished HTML review of an existing learning project with a topic roadmap, evidence timeline, learning process, gaps, and observed changes over time. Use for visual learning reports or a review dashboard; use learn-progress for a short conversational status update.
---

# Create a learning review

Read the sibling [shared project contract](../learn-start/references/project-contract.md). Reuse the intended project's goals, plan, resume, sources, and relevant attempts. This skill extends the evidence rules of `learn-progress` into a standalone report. It reviews existing learning; it does not teach a new lesson or administer a test.

## Establish what the record supports

Read `state.json` when present and validate it with the sibling helper. Inspect the underlying attempts before describing improvement, regression, or retention. Keep all planned topics visible, including skipped sections and unprepared outlines. Determine the report language using the shared contract. Localize the entire report by default, not only the narrative: headings, labels, legends, tables, status names, empty states, chart titles, accessibility text, and conclusions. English source instructions and the renderer's English baseline do not override the learner's language.

Separate coverage, independent evidence, assistance, and delayed checks. Compare attempts on the same outcome and skill kind across different dates and tasks. Check task difficulty, tools, and grading before claiming growth. An increase in cumulative evidence is evidence accumulation; it alone does not establish improvement. A later failure remains visible even after earlier successes. Label sparse or incomparable history as insufficient evidence of a trend. The report must answer “is there growth?” with a qualified finding supported by specific attempts, or explicitly say why it cannot yet be determined.

Explain how learning has actually proceeded: explanation, practice, assistance, feedback, assessments, and review where recorded. Distinguish this history from the method merely proposed in the plan. Show dates of recorded activity without inventing study duration or streaks. Mark retention as unverified unless an actual delayed attempt supports it. Respect the client-local date for due reviews and temporal cutoffs.

## Build the artifact

For structured projects, run from this skill's directory:

```text
python scripts/render_review.py <project> --output <project>/reports/review.html --as-of <client-local-date>
```

Choose a fresh output filename if one already exists. The renderer validates the shared schema, escapes source text, and produces responsive HTML with embedded styles, no network dependencies, an evidence chart, expandable topics, the next action, review dates, and links to source records. `--as-of` filters future attempts and labels due reviews; roadmap statuses remain the current snapshot, not reconstructed historical states. Without a reliable client date, omit it; scheduled reviews remain undated relative to today.

Read the generated report, localize its learner-facing text into the chosen language, and set the HTML `lang` attribute accordingly. This is part of every report request and needs no separate translation request. Keep counts, dates, source links, IDs, and CSS classes intact. Add a concise, evidence-linked narrative about growth, obstacles, and learning process in the same language. Label your interpretation separately from recorded facts. Use HTML-escaped text and safe local links. The bundled renderer is the visual starting point; preserve its accessible headings, responsive layout, and print styles when adding narrative.

For legacy Markdown projects, use existing files without migrating them. Author the same report sections directly in standalone HTML, using [the bundled styles](assets/report.css). Link claims to the actual records. Preserve unknown dates, assistance, and grading as unknown; omit quantitative charts that cannot be reconstructed faithfully. State that the report uses a partial legacy record.

Write only the requested report and any required report assets; keep course state, attempts, and resume unchanged. Never replace an evidence artifact with a report. The generated artifact may contain private learning records; deliver it locally unless publication is explicitly requested.

## Verify and deliver

Check all topics against the plan, denominators against state, chart labels against their metric, and every trend claim against attempts. Verify that all learner-facing report text follows the chosen language, including empty states and accessibility labels. Open the HTML with an available browser or renderer to inspect a desktop and narrow layout; check printing when a PDF or print version is requested. If visual inspection is unavailable, report that limitation. For a schema error, explain the blocker instead of presenting an invalid state as a successful report.

Return a link to the HTML and a short finding about the current position, growth evidence, and next useful action. Report creation is the completion criterion; it does not authorize changing the curriculum or starting the next lesson.
