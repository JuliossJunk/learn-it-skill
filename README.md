# Learn It

Five skills for a personal learning project that carries across sessions: set a goal, build a curriculum, practice, check understanding, and see what the evidence supports.

[Russian README](README.ru.md) · [MIT license](LICENSE)

## Skills

| Skill | Example prompt | Result |
| --- | --- | --- |
| `learn-start` | `$learn-start I want to learn probability` | A brief, diagnostic, sources, curriculum, and persistent course files |
| `learn-progress` | `$learn-progress Where did we stop?` | A concise, read-only account of demonstrated skills, gaps, and the next action |
| `learn-next` | `$learn-next Continue my course` | Resume the pending task or prepare a prerequisite-ready topic |
| `learn-test` | `$learn-test Check my understanding` | Questions, feedback on real answers, and a record of assistance |
| `learn-review` | `$learn-review Create an HTML learning report` | An offline visual report with all topics, evidence over time, review needs, and qualified findings about growth |

Instructions and skill-selector metadata are in English. Lessons, feedback, and the entire HTML report follow the learner's communication language by default: an explicit preference, then the saved profile, then the current request. This includes report headings, chart labels, and conclusions. In language courses, the target language and explanation language are separate preferences. Skills may also be selected when a request matches their descriptions. They do not run in the background.

## What persists

Each course has its own local directory:

```text
GOAL.md        Desired capabilities and scope
PROFILE.md     Background, preferences, and time budget
PLAN.md        Sections, prerequisites, and revision reasons
SOURCES.md     Books, editions, links, access, and topic mapping
RESUME.md      Exact stopping point and next action
state.json     Structured progress and links to evidence
sections/      Theory, practice, solutions, and exit checks
sessions/      Actual attempts and corrections
assessments/   Questions, responses, grading, and assistance
reports/       Generated HTML reviews, when requested
```

Coverage, independent performance, and delayed retention are separate. A hinted answer stays assisted; a skipped topic stays skipped. The skills work with existing Markdown courses without resetting their history. New courses prepare the first lesson in detail and keep later sections as outlines until needed.

## Install locally in Codex

Clone this repository, then copy all five directories under `skills/` into `~/.agents/skills/`. Keep them together: the skills share the contract and validator in `learn-start`. Compare any existing directories with the same names before replacing them.

The user-level location and discovery behavior are documented in [OpenAI's skill guide](https://learn.chatgpt.com/docs/build-skills). If a newly installed skill does not appear, restart Codex. This repository provides skill folders for local installation.

Python 3.10+ is required for the state helper and HTML renderer. Both use only the standard library. The teaching, source selection, and assessment of open answers are performed by the agent.

## HTML reviews

Ask for `$learn-review` in a course workspace. The skill reads the plan and attempts, creates a local HTML artifact, and explains what the record says about growth. The report includes the full roadmap, current stopping point, evidence timeline, assistance, failures, pending answers, and scheduled reviews. Expandable topics, embedded styles, and a responsive layout work offline.

To render a structured course directly, from this repository's root:

```sh
python skills/learn-review/scripts/render_review.py /path/to/course --output /path/to/course/reports/review.html --as-of 2026-11-05
```

Use the learner's actual local date. Omit `--as-of` when unknown; reviews will be shown without overdue labels. The cutoff applies to attempts; topic statuses remain the current saved roadmap. Choose a fresh output filename for each report. Direct script output is an English visual baseline; the skill localizes the entire artifact, inspects source attempts, and adds the interpretive narrative. Legacy Markdown courses are reviewed directly by the agent without a state migration.

The chart counts outcomes with independent evidence. An upward line alone does not establish growth. Changes in task difficulty, assistance, or grading need inspection, and sparse records are labelled insufficient. No overall mastery probability is calculated. Reports stay local unless publication is requested.

To preview the layout with explicitly fictional data, choose a new destination directory:

```sh
python examples/make_demo.py /path/to/new-demo
```

Open `reports/review.html` inside that directory. The example keeps all source links local and includes completed, current, planned, and skipped topics.

## Validate

```sh
python -B -X utf8 -m unittest discover -s tests -v
python skills/learn-start/scripts/project_state.py validate /path/to/course
python skills/learn-start/scripts/project_state.py report /path/to/course --as-of 2026-11-05
```

The validator checks IDs, prerequisite cycles, evidence links, dates, and required files. It does not establish that a lesson or grading judgement is correct. See [evaluation results](evals/RESULTS.md) and [behavioral scenarios](evals/scenarios.md) for what has and has not been checked.

## License

[MIT](LICENSE), copyright 2026 JuliossJunk.
