---
id: 2
title: Create Beautiful Todo Frontend Spec
stage: spec
date: 2026-01-14
surface: agent
model: claude-sonnet-4-5-20250929
feature: ui
branch: 1-ui
user: king
command: /sp.specify
labels: ["ui", "spec", "frontend", "todo-app", "design"]
links:
  spec: "@specs/ui/todo-frontend-beautiful.md"
  ticket: null
  adr: null
  pr: null
files:
  - "specs/ui/todo-frontend-beautiful.md"
  - "specs/ui/checklists/requirements.md"
tests: []
---

# Prompt

```
Focus STRICTLY on creating a complete, ultra-beautiful, professional frontend specification for the Hackathon II Phase 2 Todo Web Application. Ignore backend, database, agents, skills – only frontend UI/UX + Next.js implementation details.

Project references (ALWAYS reference these):
@specs/overview.md
@specs/features/task-crud.md
@specs/api/rest-endpoints.md (for data shape: tasks with id, title, description, completed, created_at, updated_at)
@specs/ui/components.md (or create if needed)
root CLAUDE.md and /frontend/CLAUDE.md for Next.js + Tailwind patterns

Core Goal: The frontend MUST look premium, modern, and visually stunning – like top 2025 professional todo/dashboard apps (inspired by Horizon UI, Tailwind UI templates, Aceternity components, shadcn/ui + Framer Motion examples). Use clean design, subtle gradients, glassmorphism/soft shadows if fits, full dark/light mode support, and smooth animations everywhere.

Key Non-Negotiable Requirements for Beauty & Professionalism:
- Full dark mode + light mode support (use next-themes or Tailwind dark: prefix)
- Responsive on all devices (mobile-first, beautiful on phone/tablet/desktop)
- Use shadcn/ui components as base (for buttons, cards, modals, inputs, toasts, dropdowns – install via CLI if needed)
- Add beautiful animations with Framer Motion (install framer-motion):
  - Fade-in / slide-up on page load and task list items
  - Smooth hover scale + shadow lift on task cards
  - Checkbox toggle with spring animation
  - Modal open/close with scale + opacity transition
  - Loading skeletons with pulse animation
  - Success/error toasts with slide-in from bottom
- Modern color palette: Primary blue/indigo accents, neutral grays, soft gradients (e.g. from-indigo-500 to-purple-600)
- Typography: Use modern sans-serif (e.g. Inter or default system), proper hierarchy (headings bold, tasks readable)
- No inline styles – pure Tailwind classes + cn() helper from shadcn
- Subtle effects: Hover glow, focus rings, transitions (duration-300 ease-out)

Pages & Routes (Protected under auth layout):
- /signup → Beautiful auth form (gradient background, centered card, animated inputs)
- /signin → Similar to signup, with forgot password link
- / (or /dashboard) → Main Todo Dashboard:
  - Header: App name + theme toggle + logout + user avatar
  - Sidebar (collapsible on mobile): Filters (All/Pending/Completed), Sort (Date/Title), New Task button
  - Main content: Task list as animated grid/cards
    - Each TaskCard: Title bold, description truncated + expand on click, checkbox (animated checkmark), delete icon (trash with confirm tooltip), edit button
    - Empty state: Nice illustration/message + "Add your first task" CTA
  - Floating action button (mobile) for new task
- /tasks/new or modal: Task creation form (title input, description textarea, submit with loading spinner)
- Task edit: Modal with pre-filled form
- Use modals for create/edit/delete confirm (shadcn Dialog + Framer Motion)

Components to Define (Beautiful & Animated):
- TaskCard.tsx → Card with border, hover:shadow-xl hover:scale-[1.02] transition, completed strike-through + opacity fade
- TaskList.tsx → AnimatePresence for adding/removing tasks with layout animation
- TaskForm.tsx → Inputs with shake on error, animated label float
- AuthForm.tsx → Gradient button with hover shine, loading dots
- ThemeToggle.tsx → Sun/moon icon with rotate animation
- EmptyState.tsx → Centered SVG/illustration + animated fade-in text

Data Flow & Integration:
- Use Better Auth hooks for session (useSession, signIn, signOut)
- Centralized api client: /lib/api.ts with fetch + JWT auto-attach from session.token
- Optimistic updates: Update UI first, rollback on error
- Error handling: Sonner toasts (install sonner) for success/error
- Loading: Skeleton cards with animate-pulse

Acceptance Criteria for Premium Look:
- Feels like a paid product (e.g. Todoist/Notion style polish)
- 60fps smooth animations (no jank)
- WCAG accessible (contrast, keyboard nav)
- Performance: No heavy libs beyond framer-motion + shadcn
- Mobile: Sidebar collapses, cards stack vertically

Generate a detailed, comprehensive specification markdown file:
Place in: specs/ui/todo-frontend-beautiful.md

Sections:
- Overview & Design Vision
- Color Palette & Typography
- Pages & Routes
- Key Components with Animation Descriptions
- Auth & Protected Flow
- Data Fetching & State Management
- Styling & Animation Guidelines
- Edge Cases & Polish Touches

After spec, suggest next: sp.clarify if needed, then sp.plan for frontend implementation.

Execute now – make this the most beautiful todo frontend spec possible!
```

# Response

Created a comprehensive specification for the Beautiful Todo Frontend Application with detailed sections covering design vision, color palette, typography, pages and routes, key components with animations, auth flow, data fetching, styling guidelines, and edge cases. The specification includes all required elements with a focus on premium aesthetics, smooth animations, and responsive design.

# Outcome & Impact

Successfully created a detailed frontend specification that captures all requirements for a beautiful, professional todo application with premium design elements, smooth animations, and responsive behavior. The specification is ready for implementation planning.

# Tests Summary

None

# Files Summary

- specs/ui/todo-frontend-beautiful.md: Comprehensive frontend specification
- specs/ui/checklists/requirements.md: Quality checklist for specification validation

# Next Prompts

Suggest running sp.plan for frontend implementation planning

# Reflection Note

The specification captures all design requirements including animations, color schemes, and responsive behavior needed for a premium todo application.

# Evaluation

## Failure Modes Observed

None

## Next Experiment to Improve Prompt Quality

N/A