---
id: 2
title: "ai-todo-chatbot-spec"
stage: "spec"
date_iso: "2026-02-02"
surface: "agent"
model: "Claude Sonnet 4.5"
feature: "ai-todo-chatbot"
branch: "1-ai-todo-chatbot"
user: "user"
command: "/sp.specify"
labels: ["spec", "ai", "chatbot", "todo", "mcp"]
spec: "specs/1-ai-todo-chatbot/spec.md"
ticket: null
adr: null
pr: null
---

# PHR: AI Todo Chatbot Specification

## Files Modified
- specs/1-ai-todo-chatbot/spec.md
- specs/1-ai-todo-chatbot/checklists/requirements.md

## Tests
- N/A

## Prompt Text
```
You are Spec-Kit Plus running in `sp.specify` mode.

Your task is to design and specify a COMPLETE Phase III implementation
for an AI-powered Todo Chatbot, fully integrated into an existing
full-stack Todo application where Phase I and Phase II are already complete.

You MUST strictly follow the provided specification and architecture.
Do NOT redesign or replace existing backend logic.
Extend the system safely and cleanly.

────────────────────────────────────────
PROJECT CONTEXT
────────────────────────────────────────

Project: Full-Stack Todo Application (Phase III)
Goal: Add an AI-powered chatbot that manages todos via natural language.

Phase I:
- Auth (Better Auth)
- Todo CRUD
- Database schema already exists

Phase II:
- REST APIs
- Frontend UI (tasks, priority, due date)
- Production deployment (Vercel + Neon)

Phase III (THIS SPEC):
- Conversational AI Chatbot
- MCP-based architecture
- Stateless backend
- AI agent orchestrates tools

────────────────────────────────────────
CRITICAL CONSTRAINTS
────────────────────────────────────────

1. Backend must remain stateless
2. Conversation state must persist in database
3. AI must interact ONLY via MCP tools
4. MCP tools must be stateless
5. Use OpenAI Agents SDK for agent logic
6. Use Cohere API as the LLM provider (NOT Gemini, NOT OpenAI models)
7. Integrate chatbot into existing frontend UI
8. Do not break existing APIs or database models

────────────────────────────────────────
TECHNOLOGY STACK (FIXED)
────────────────────────────────────────

Frontend:
- OpenAI ChatKit
- Existing Next.js / React UI
- Chatbot icon visible on desktop & mobile

Backend:
- Python FastAPI
- SQLModel ORM
- Neon Serverless PostgreSQL
- Better Auth

AI:
- OpenAI Agents SDK
- Cohere API as model provider
- MCP Server using Official MCP SDK

────────────────────────────────────────
HIGH-LEVEL ARCHITECTURE
────────────────────────────────────────

ChatKit UI
   ↓
POST /api/{user_id}/chat   (FastAPI)
   ↓
Conversation Loader (DB)
   ↓
OpenAI Agents SDK Runner
   ↓
MCP Tools (Task Operations)
   ↓
Database (Tasks / Messages / Conversations)

Backend holds NO memory between requests.

────────────────────────────────────────
REQUIRED DATABASE MODELS
────────────────────────────────────────

Task:
- id
- user_id
- title
- description
- completed
- created_at
- updated_at

Conversation:
- id
- user_id
- created_at
- updated_at

Message:
- id
- user_id
- conversation_id
- role (user / assistant)
- content
- created_at

────────────────────────────────────────
MCP TOOL
```

## Response Text
Created a comprehensive specification for the AI Todo Chatbot feature, including user scenarios, functional requirements, and success criteria. The spec defines three priority user stories: natural language todo management (P1), conversation continuity (P2), and secure user isolation (P3). It includes 15 functional requirements covering task operations, conversation persistence, authentication, data isolation, and system integration. Success criteria include 95% success rate for task operations, 3-second response times, 80% user satisfaction, zero cross-user data access, and 90% command accuracy.

## Outcome
Successfully created a complete specification for the AI Todo Chatbot that follows the MCP-based architecture and stateless backend requirements.

## Evaluation
The specification is comprehensive, testable, and aligned with the project constraints. It covers all required functionality while maintaining compatibility with existing Phase I & II components.