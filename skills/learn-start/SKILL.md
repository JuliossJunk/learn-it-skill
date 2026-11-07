---
name: learn-start
description: Start or redesign a sustained personal learning project through goal clarification, background diagnosis, source selection, a prerequisite-aware curriculum, and persistent course files. Use for learning a subject over multiple sessions; a standalone explanation does not require a course project.
---

# Start a learning project

Read [the shared project contract](references/project-contract.md) before creating or updating course files. It defines persistence and evidence for all five learning skills. The bundle's companion skills are `learn-progress`, `learn-next`, `learn-test`, and `learn-review`.

## Establish the learning brief

Inspect the selected workspace for existing learning files first. Reuse known goals, prior attempts, books, time budget, language, and accessibility preferences. If several courses could be intended, ask which one.

Interview in short rounds. Ask questions whose answers affect the next decision: desired capabilities and use cases, boundaries, actual background, time and deadline, preferred practice, and existing materials. Give a recommendation for decisions, not invented answers about the learner. Questions that depend on an unanswered question belong in a later round. A short interview should lead to learning rather than become a barrier to it.

Explicitly ask whether the learner has books, notes, courses, links, example tasks, or project code they want included. Offer to find suitable primary materials yourself. Inspect supplied accessible resources before asking the learner to restate their contents. Record inaccessible sources honestly and request only the missing information needed to use them. Identify book editions before assigning chapters. Resource discovery supplements, rather than replaces, the learner's chosen book.

Use a small diagnostic appropriate to the learner's claimed background. Request reasoning, allow “I don't know”, and separate arithmetic slips, notation gaps, and conceptual mistakes. Self-reported confidence and professional seniority guide question choice; actual responses establish the starting point.

Summarize the brief and reuse decisions already agreed with the learner. Agreement on goals or background is not approval of a curriculum. Interview, diagnostic questions, and source discovery may proceed before plan approval; course creation and teaching follow the approval gate below.

## Design the curriculum

Work backward from observable outcomes. Each section has stable IDs, prerequisites, a realistic time estimate, relevant sources, practice, and an exit check. Sequence missing foundations before dependent topics. Include explanation, routine execution, error diagnosis, and application to a changed problem where relevant. Reserve time for review and checks inside the agreed budget.

Read [baseline and extension planning](references/curriculum-planning.md) when drafting the curriculum. Present a recognizable baseline appropriate to the learner's goal and explain which verified standards, curricula, practices, or recommendations support it. Include a separate optional block of useful, less obvious extensions with their benefits and prerequisites.

Draft the broad route and describe the proposed first section; prepare full lesson materials only after approval. Later sections can remain concise outlines. Keep the route adaptable to evidence and resource discoveries. A deadline or page count is a planning constraint, not evidence of mastery.

## Stop for explicit plan approval

Show the complete proposed plan in the conversation, clearly labelled as a draft. Include the intended capabilities and baseline level, cited rationale, section sequence and prerequisites, time estimates within the budget, practice and exit checks, and the optional extensions. State which extensions, if any, the proposal includes; unselected extensions remain outside the core route and its time estimate.

Ask the learner to approve this specific plan or request changes, then end the response and wait for their reply. Before approval, do not create course files or directories, initialize Git, prepare full lessons, begin teaching, or advance to a section. A request to start learning, agreement with the brief, silence, or elapsed time does not approve a plan that has not yet been presented. If the learner explicitly requests a saved draft, clarify that this workflow presents the draft in chat and saves course files after approval.

Accept an explicit affirmative reply to the presented plan, such as approval to proceed with that plan. If the reply only answers a question or requests changes, resolve it, show the revised proposal, and wait for approval again. Reuse approval already given to the same unchanged plan; do not ask repeatedly. Changes to agreed goals, scope, baseline, extension selection, or time commitment require approval of the revised plan before implementation.

## Create the project

Enter this phase only after the approval gate is satisfied. Record the accepted plan and a faithful note of the learner's approval in `PLAN.md`, including the date and any conditions. Prepare the first executable lesson and label later materials as outlines until prepared.

Create a dedicated local project directory, using the agreed path or a clearly named folder in the selected workspace. A requested repository means local Git by default: initialize only that dedicated directory if it is not already part of a repository. Remote creation, publication, and pushes require a separate user request. Keep unrelated workspace data outside the new project.

Write the contract's goal, profile, plan, source register, section files, resume note, and state. Preserve existing learner work; adapt legacy Markdown projects without resetting their history. Add a small root `AGENTS.md` pointing learning requests to `RESUME.md`, `state.json`, and the current section. Scope it to tutoring in this project; it must not redirect unrelated coding requests.

Use the bundled `scripts/project_state.py` to validate the structure after changes. Return links to the goal and plan, distinguish prepared lessons from outlines, and state the first learning action. If the user requested a course but not an immediate lesson, finish with the concrete project rather than starting an unsolicited assessment.
