---
id: 3
title: "ai-todo-chatbot-impl-plan"
stage: "plan"
date_iso: "2026-02-02"
surface: "agent"
model: "Claude Sonnet 4.5"
feature: "ai-todo-chatbot"
branch: "1-ai-todo-chatbot"
user: "user"
command: "/sp.plan"
labels: ["plan", "ai", "chatbot", "todo", "implementation"]
spec: "specs/1-ai-todo-chatbot/spec.md"
plan: "specs/1-ai-todo-chatbot/plan.md"
ticket: null
adr: null
pr: null
---

# PHR: AI Todo Chatbot Implementation Plan

## Files Modified
- specs/1-ai-todo-chatbot/plan.md
- specs/1-ai-todo-chatbot/research.md
- specs/1-ai-todo-chatbot/data-model.md
- specs/1-ai-todo-chatbot/contracts/api-contract.yaml
- specs/1-ai-todo-chatbot/quickstart.md

## Tests
- N/A

## Prompt Text
```
You are Spec-Kit Plus running in `sp.plan` mode.

Based on the previously approved `sp.specify` specification,
create a DETAILED, STEP-BY-STEP IMPLEMENTATION PLAN
for Phase III: AI-powered Todo Chatbot.

The plan must be executable by a team or a single developer
using Claude Code, and must strictly follow the approved architecture.

────────────────────────────────────────
PLANNING OBJECTIVE
────────────────────────────────────────

Produce a clear, ordered implementation plan that covers:

1. Backend AI chatbot integration
2. MCP server & tools
3. OpenAI Agents SDK with Cohere
4. Stateless conversation flow
5. Database persistence
6. Frontend chatbot UI integration
7. Deployment & verification

Do NOT write code.
Do NOT redesign architecture.
Only define WHAT to build and IN WHAT ORDER.

────────────────────────────────────────
PHASE BREAKDOWN REQUIREMENTS
────────────────────────────────────────

Organize the plan into the following phases:

PHASE A — Foundations & Setup
PHASE B — Database & Persistence Layer
PHASE C — MCP Server & Tools
PHASE D — AI Agent (OpenAI Agents SDK + Cohere)
PHASE E — Chat API (Stateless Flow)
PHASE F — Frontend Chatbot UI
PHASE G — Integration, Testing & Deployment

Each phase MUST include:
- Purpose
- Inputs
- Outputs
- Key responsibilities
- Validation checklist

────────────────────────────────────────
PHASE A — FOUNDATIONS & SETUP
────────────────────────────────────────

Plan steps to:
- Add Cohere API key to backend environment
- Configure OpenAI Agents SDK to use Cohere as LLM provider
- Prepare MCP SDK dependencies
- Ensure Better Auth user identity is accessible in chat flow

────────────────────────────────────────
PHASE B — DATABASE & PERSISTENCE
────────────────────────────────────────

Plan steps to:
- Confirm Task schema compatibility with AI tools
- Create Conversation table
- Create Message table
- Define conversation lifecycle rules
- Ensure stateless request behavior with DB hydration

────────────────────────────────────────
PHASE C — MCP SERVER & TOOLS
────────────────────────────────────────

Plan steps to:
- Initialize MCP Server
- Register MCP tools:
  - add_task
  - list_tasks
  - complete_task
  - delete_task
  - update_task
- Define tool schemas & validation
- Ensure tools ONLY interact with DB
- Ensure tools NEVER store memory

────────────────────────────────────────
PHASE D — AI AGENT (COHERE + AGENTS SDK)
────────────────────────────────────────

Plan steps to:
- Define Todo AI Agent role & behavior
- Configure Agent Runner
- Connect agent to MCP tools
- Define natural-language → tool mapping rules
- Add confirmation & error-handling behaviors
- Ensure user email/context awareness

────────────────────────────────────────
PHASE E — CHAT API (STATELESS)
────────────────────────────────────────

Plan steps to:
- Design POST /api/{user_id}/chat endpoint
- Fetch conversation history from DB
- Append new user message
- Invoke agent runner
- Capture tool calls
- Persist assistant response
- Return response + tool_calls to frontend

────────────────────────────────────────
PHASE F — FRONTEND CHATBOT UI
────────────────────────────────────────

Plan steps to:
- Add floating chatbot icon (desktop + mobile)
- Integrate OpenAI ChatKit
- Connect ChatKit to backend chat endpoint
- Handle conversation_id lifecycle
- Display confirmations & task updates
- Ensure responsive UI/UX

────────────────────────────────────────
PHASE G — INTEGRATION, TESTING & DEPLOYMENT
────────────────────────────────────────

Plan steps to:
- Validate all natural language commands
- Test multi-step tool chaining
- Test error scenarios
- Ensure stateless behavior across restarts
- Deploy backend
- Redeploy frontend on Vercel
- Verify production domain functionality

────────────────────────────────────────
FINAL OUTPUT FORMAT
────────────────────────────────────────

- Use clear headings
- Use numbered steps
- Be concise but complete
- No code blocks
- No assumptions beyond the specification

This plan must be production-ready and executable without ambiguity.
```

## Response Text
Created a comprehensive implementation plan for the AI Todo Chatbot, organizing development into 7 sequential phases: Foundations & Setup (A), Database & Persistence Layer (B), MCP Server & Tools (C), AI Agent (D), Chat API (E), Frontend Chatbot UI (F), and Integration/Testing/Deployment (G). Each phase includes purpose, inputs, outputs, key responsibilities, and validation checklists. Also created supporting documents: research.md (resolving technical unknowns), data-model.md (database schema), contracts/api-contract.yaml (API specifications), and quickstart.md (setup guide). All components align with the constitutional requirements for stateless architecture, MCP-first operations, and user data isolation.

## Outcome
Successfully created a complete implementation plan that follows the MCP-based architecture and stateless backend requirements while maintaining compatibility with existing Phase I & II components.

## Evaluation
The plan is comprehensive, follows the required phase structure, includes all validation checkpoints, and provides clear guidance for implementation without specifying code details. All constitutional requirements are addressed in the validation checklists.