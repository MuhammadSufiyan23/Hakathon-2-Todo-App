---
id: 0001
title: Fix-dueDate-priority-display
stage: red
date: 2026-01-21
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: Muhammad Sufiyan
command: /sp.phr
labels: ["bug-fix", "frontend", "api", "task-card", "data-mapping"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - frontend/lib/api.ts
 - frontend/components/tasks/TaskCard.tsx
tests:
 - none
---

## Prompt

--title "Fix-dueDate-priority-display" --stage "red"

## Response snapshot

Fixed the issue where dueDate and priority fields were blank on task cards by updating the transformTask function in frontend/lib/api.ts to properly map backend snake_case fields (due_date, priority) to frontend camelCase fields (dueDate, priority).

## Outcome

- ✅ Impact: Fixed data mapping issue causing dueDate and priority to appear blank on task cards
- 🧪 Tests: none
- 📁 Files: frontend/lib/api.ts, frontend/components/tasks/TaskCard.tsx
- 🔁 Next prompts: none
- 🧠 Reflection: Proper field mapping between backend and frontend is crucial for data display

## Evaluation notes (flywheel)

- Failure modes observed: None - the fix was straightforward and successful
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): none