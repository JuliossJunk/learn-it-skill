# Validation results

## Teaching workflow update — 2026-11-08

Added proportionate feedback, an adaptive pre-plan diagnostic with decision rationale, explicit lesson competencies, and full sourced theory saved in linked Markdown lesson files. Updated behavioral scenarios specify these expectations, including accepting equivalent correct answers and waiting for practice readiness. These are instruction changes; script regression tests do not establish conversational compliance, and independent behavioral evaluation remains pending.

## Curriculum approval update — 2026-11-08

The instructions now require explicit approval of the presented plan before course-file creation or teaching. Baseline recommendations require inspected sources and an explicit rationale; extensions remain separately optional. New behavioral scenarios cover pending approval, revisions, acceptance, source uncertainty, declined extensions, and cross-skill continuation. These scenarios specify expected behavior; an independent conversational evaluation of this update has not yet been run. Python regression tests check the existing scripts, not compliance with this instruction-level gate.

Date: 2026-11-05.

## Repository checks

- All 17 Python tests passed: nine for shared project state and eight for the HTML review.
- All five skills passed the bundled `quick_validate.py`. UI metadata parsed as YAML; description lengths and explicit skill mentions in default prompts were checked.
- The HTML review tests cover assisted and self-reported answers, repeated tasks, same-day comparisons, differing task kinds, future evidence cutoffs, later failures, HTML escaping, local source links, invalid state, read-only course handling, and refusal to overwrite a report.
- A fictional example was generated with `examples/make_demo.py` and opened in headless Microsoft Edge at 1440 and 390 pixels wide. Screenshots were inspected at both sizes; neither viewport had page-level horizontal overflow. The evidence table scrolls horizontally on narrow screens.
- Only `README.ru.md` contains Russian text. Local installation logs and private learner transcripts were excluded from the repository.

PyYAML was used for the external skill-format validator only. The course helper, review renderer, demo generator, and test suite require no third-party Python packages.

## Installation checks

- The expanded suite ran 31 tests: 30 passed and one symlink-creation test was skipped because this Windows host does not grant symlink creation. Fourteen tests cover the installer; the earlier 17 state and review tests still pass.
- Project installation and file checks passed for all five agent destinations: Codex, Claude Code, Cursor, GitHub Copilot, and OpenCode. Tests include full-bundle copying, shared resources, user-path selection, paths containing spaces, dry runs, idempotence, adoption of identical manual copies, explicit updates, conflict preservation, obsolete-file removal, uninstall boundaries, and restoration after a simulated filesystem failure.
- The Skills CLI discovered all five skills and installed the local checkout into an isolated project for the five selected agents with `--copy`. Installed files matched the sources in both its shared `.agents/skills` directory and its `.claude/skills` copies. The installed review renderer produced an HTML report, and the installed state helper validated the fictional example course.
- The same five-agent installation also succeeded directly from `JuliossJunk/learn-it-skill` on GitHub into a second isolated project with `--skill '*' --copy --yes`. Its installed renderer and validator also ran successfully. Text assets explicitly use LF in Git checkouts to keep installation hashes consistent across platforms.
- Agent directory and invocation instructions were checked against the vendor documentation linked in [the installation guide](../docs/installation.md). These checks verify packaging, paths, and scripts; they do not claim an interactive tutoring session was run inside all five agent applications.

The Python installer uses only the standard library. Its integration tests ran on Windows; macOS and Linux were not exercised in this session. Real linked-directory refusal was not exercised because the symlink setup test was skipped.

## Earlier behavioral evidence

Before repository packaging, an independent agent exercised `learn-progress` on a legacy Markdown course. The recorded result distinguished assisted practice from retention, preserved a learner correction about two different formulas, listed pending questions, and did not start a lesson. The agent reported no writes to the course. That private transcript and its machine-specific installation record are not distributed here; this is a historical summary, not a new validation of the five-skill bundle.

## Limits

- Full tutoring loops for `learn-start`, `learn-next`, and `learn-test` have not received independent behavioral evaluation.
- `learn-review` has script tests and visual checks; its agent-authored narrative and legacy-course branch have not received independent behavioral evaluation.
- Script tests establish bookkeeping and artifact behavior, not semantic grading accuracy, lesson quality, or actual learning gains.
- The renderer identifies candidate transitions, not comparable difficulty or verified retention. Those claims require inspecting source attempts.
- Browser inspection covered desktop and narrow-screen HTML, not PDF export or all browsers.

Additional scenarios remain listed in [scenarios.md](scenarios.md) as evaluation criteria.
