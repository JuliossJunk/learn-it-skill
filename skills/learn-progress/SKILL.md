---
name: learn-progress
description: Show progress, evidence of understanding, pending exercises and review needs in an existing personal learning project. Use for where we stopped or what has been learned; do not start a new curriculum or a test just to show status.
---

# Show learning progress

Read the sibling [shared project contract](../learn-start/references/project-contract.md). Locate the intended project and read its resume note, plan and state. For a legacy project, use its existing progress and diagnostic notes without changing the layout.

This operation is read-only unless the learner explicitly asks to correct or save something. Run the sibling `learn-start/scripts/project_state.py report <project> --as-of <client-local-date>` when structured state exists. Without a reliable client date, omit `--as-of` and show scheduled reviews without labelling them overdue. Verify important claims against the underlying attempts, especially if a summary says “mastered” without evidence.

Lead with the current section and exact stopping point. Then show:

- What the learner has independently demonstrated, with a concrete example and date.
- What has only been introduced or completed with assistance.
- Open errors, ungraded answers, pending tasks, and due reviews.
- The next useful action and why it fits the prerequisites and time budget.

Keep coverage separate from independent evidence and delayed retention. Use deterministic counts with a clear denominator; do not invent a general percentage of subject mastery. If an old failure was corrected, include the correction rather than presenting the failure as current fact. Missing or contradictory evidence stays uncertain.

Link the detailed record and stop. Showing progress does not authorize advancing a section, administering a test, or rewriting the plan. If the learner asks to fix a record, preserve the original attempt, append the correction, update its derived summary and validate state.
