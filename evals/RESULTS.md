# Validation results

Date: 2026-11-05.

## Repository checks

- All 17 Python tests passed: nine for shared project state and eight for the HTML review.
- All five skills passed the bundled `quick_validate.py`. UI metadata parsed as YAML; description lengths and explicit skill mentions in default prompts were checked.
- The HTML review tests cover assisted and self-reported answers, repeated tasks, same-day comparisons, differing task kinds, future evidence cutoffs, later failures, HTML escaping, local source links, invalid state, read-only course handling, and refusal to overwrite a report.
- A fictional example was generated with `examples/make_demo.py` and opened in headless Microsoft Edge at 1440 and 390 pixels wide. Screenshots were inspected at both sizes; neither viewport had page-level horizontal overflow. The evidence table scrolls horizontally on narrow screens.
- Only `README.ru.md` contains Russian text. Local installation logs and private learner transcripts were excluded from the repository.

PyYAML was used for the external skill-format validator only. The course helper, review renderer, demo generator, and test suite require no third-party Python packages.

## Earlier behavioral evidence

Before repository packaging, an independent agent exercised `learn-progress` on a legacy Markdown course. The recorded result distinguished assisted practice from retention, preserved a learner correction about two different formulas, listed pending questions, and did not start a lesson. The agent reported no writes to the course. That private transcript and its machine-specific installation record are not distributed here; this is a historical summary, not a new validation of the five-skill bundle.

## Limits

- Full tutoring loops for `learn-start`, `learn-next`, and `learn-test` have not received independent behavioral evaluation.
- `learn-review` has script tests and visual checks; its agent-authored narrative and legacy-course branch have not received independent behavioral evaluation.
- Script tests establish bookkeeping and artifact behavior, not semantic grading accuracy, lesson quality, or actual learning gains.
- The renderer identifies candidate transitions, not comparable difficulty or verified retention. Those claims require inspecting source attempts.
- Browser inspection covered desktop and narrow-screen HTML, not PDF export or all browsers.

Additional scenarios remain listed in [scenarios.md](scenarios.md) as evaluation criteria.
