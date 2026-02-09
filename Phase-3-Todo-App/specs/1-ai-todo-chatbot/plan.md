# Implementation Plan: AI Todo Chatbot

**Branch**: `1-ai-todo-chatbot` | **Date**: 2026-02-02 | **Spec**: [specs/1-ai-todo-chatbot/spec.md](../specs/1-ai-todo-chatbot/spec.md)
**Input**: Feature specification from `/specs/1-ai-todo-chatbot/spec.md`

## Summary

Implementation of an AI-powered Todo Chatbot that allows users to manage their tasks through natural language conversations. The system will use OpenAI Agents SDK with Cohere API as the LLM provider, MCP tools for database operations, and maintain a stateless architecture while preserving existing Phase I & II backend functionality.

## Technical Context

**Language/Version**: Python 3.11, TypeScript/JavaScript for frontend
**Primary Dependencies**: FastAPI, SQLModel, OpenAI Agents SDK, Cohere API, MCP SDK, Better Auth, OpenAI ChatKit
**Storage**: Neon Serverless PostgreSQL
**Testing**: pytest for backend, Jest/Vitest for frontend
**Target Platform**: Web application (Next.js frontend with FastAPI backend)
**Project Type**: Web application with AI integration
**Performance Goals**: 95% success rate for task operations, 3-second response times, 90% command accuracy
**Constraints**: <200ms p95 for API calls, stateless architecture, user data isolation
**Scale/Scope**: Individual user task management with conversation history

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] All task operations go through MCP tools?
- [x] Maintained stateless server architecture?
- [x] Used proper user_id in all tool calls?
- [x] Respected Better Auth authentication context?
- [x] MCP tools are stateless and database-only?
- [x] Conversation context reconstructed from database?
- [x] Existing backend logic remains untouched?

## Project Structure

### Documentation (this feature)
```text
specs/1-ai-todo-chatbot/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)
```text
backend/
├── src/
│   ├── models/
│   │   ├── todo.py          # Task model (existing)
│   │   ├── conversation.py  # New: Conversation model
│   │   └── message.py       # New: Message model
│   ├── services/
│   │   ├── auth.py          # Better Auth integration (existing)
│   │   ├── tasks.py         # Task operations (existing)
│   │   ├── conversations.py # New: Conversation operations
│   │   └── messages.py      # New: Message operations
│   ├── tools/
│   │   ├── __init__.py      # New: MCP tools initialization
│   │   ├── task_tools.py    # New: MCP task tools
│   │   └── server.py        # New: MCP server
│   ├── agents/
│   │   ├── __init__.py      # New: Agent definitions
│   │   ├── todo_agent.py    # New: Todo AI agent
│   │   └── runner.py        # New: Agent runner
│   ├── api/
│   │   ├── deps.py          # Dependency injection (existing)
│   │   └── chat.py          # New: Chat endpoint
│   └── main.py              # App entry point (existing)
└── tests/
    ├── unit/
    ├── integration/
    └── contract/

frontend/
├── src/
│   ├── components/
│   │   ├── ChatBot.tsx      # New: ChatKit integration
│   │   └── ChatIcon.tsx     # New: Floating chat icon
│   ├── pages/
│   │   └── dashboard.tsx    # Existing: Dashboard page (updated)
│   ├── services/
│   │   └── api.ts           # API client (existing, updated)
│   └── contexts/
│       └── auth.tsx         # Auth context (existing)
└── tests/
    ├── unit/
    └── integration/
```

**Structure Decision**: Web application with backend/ and frontend/ directories following the existing structure. New AI-related components will be added to both backend and frontend while maintaining existing functionality.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [None] | [All constitution checks passed] | [No violations identified] |

## PHASE A — Foundations & Setup

**Purpose**: Set up the foundational components and dependencies required for the AI Todo Chatbot system, including Cohere API integration, OpenAI Agents SDK configuration, and MCP SDK preparation.

**Inputs**:
- Cohere API key (to be added to environment)
- Existing Better Auth user identity system
- OpenAI Agents SDK library
- MCP SDK dependencies

**Outputs**:
- Backend configured with Cohere API access
- OpenAI Agents SDK properly configured to use Cohere as LLM provider
- MCP SDK dependencies installed and ready
- Better Auth user identity accessible in chat flow

**Key Responsibilities**:
1. Add Cohere API key to backend environment variables
2. Configure OpenAI Agents SDK to use Cohere as LLM provider
3. Install and prepare MCP SDK dependencies
4. Ensure Better Auth user identity is accessible in chat flow

**Validation Checklist**:
- [ ] Cohere API key properly configured in backend
- [ ] OpenAI Agents SDK successfully uses Cohere as LLM provider
- [ ] MCP SDK dependencies installed and importable
- [ ] Better Auth user identity accessible in backend context
- [ ] Environment variables properly secured

## PHASE B — Database & Persistence Layer

**Purpose**: Establish the database schema and persistence layer for conversation history, ensuring stateless operation with proper hydration from database on each request.

**Inputs**:
- Existing Task schema (from Phase I)
- Conversation lifecycle requirements
- Message entity requirements
- User isolation requirements

**Outputs**:
- Conversation table schema
- Message table schema
- Database models for conversations and messages
- Proper relationship mappings between entities

**Key Responsibilities**:
1. Confirm Task schema compatibility with AI tools
2. Create Conversation table with proper fields
3. Create Message table with proper fields
4. Define conversation lifecycle rules
5. Ensure stateless request behavior with DB hydration

**Validation Checklist**:
- [ ] Task schema confirmed compatible with AI tools
- [ ] Conversation table properly created with id, user_id, created_at, updated_at
- [ ] Message table properly created with id, user_id, conversation_id, role, content, created_at
- [ ] Proper foreign key relationships established
- [ ] User isolation maintained at database level
- [ ] Indexes created for efficient querying by user_id and conversation_id

## PHASE C — MCP Server & Tools

**Purpose**: Implement the MCP (Model Context Protocol) server and register the required tools for task operations, ensuring all database interactions occur through properly defined tools.

**Inputs**:
- Task database models and operations
- MCP SDK framework
- Tool schema definitions
- User authentication context

**Outputs**:
- MCP server initialized and running
- Five MCP tools registered: add_task, list_tasks, complete_task, delete_task, update_task
- Tool schemas and validation properly defined
- Tools configured to interact only with database
- Tools configured to never store memory

**Key Responsibilities**:
1. Initialize MCP Server
2. Register MCP tools: add_task, list_tasks, complete_task, delete_task, update_task
3. Define tool schemas and validation
4. Ensure tools ONLY interact with DB
5. Ensure tools NEVER store memory

**Validation Checklist**:
- [ ] MCP Server successfully initialized
- [ ] All five task tools properly registered
- [ ] Tool schemas properly defined with required parameters
- [ ] Tools restricted to database-only interactions
- [ ] Tools configured without any memory storage
- [ ] User_id properly validated in all tools
- [ ] Tools return appropriate responses

## PHASE D — AI Agent (Cohere + Agents SDK)

**Purpose**: Create and configure the AI agent that will interpret natural language and orchestrate the MCP tools to perform task operations.

**Inputs**:
- MCP tools from Phase C
- Cohere API configuration
- OpenAI Agents SDK
- Natural language → tool mapping rules
- User context and email awareness

**Outputs**:
- Todo AI Agent with proper role and behavior
- Agent runner configured
- Agent connected to MCP tools
- Natural-language → tool mapping rules implemented
- Confirmation and error-handling behaviors
- User email/context awareness

**Key Responsibilities**:
1. Define Todo AI Agent role and behavior
2. Configure Agent Runner
3. Connect agent to MCP tools
4. Define natural-language → tool mapping rules
5. Add confirmation and error-handling behaviors
6. Ensure user email/context awareness

**Validation Checklist**:
- [ ] Todo AI Agent properly defined with appropriate role
- [ ] Agent Runner configured and operational
- [ ] Agent successfully connects to all MCP tools
- [ ] Natural language mapping correctly implemented
- [ ] Error handling behaviors properly configured
- [ ] User context awareness implemented
- [ ] Agent responds appropriately to various natural language inputs

## PHASE E — Chat API (Stateless)

**Purpose**: Implement the stateless chat API endpoint that will handle conversation flow, interact with the AI agent, and manage request/response cycles.

**Inputs**:
- Conversation persistence layer from Phase B
- AI Agent from Phase D
- User authentication context
- Better Auth integration

**Outputs**:
- POST /api/{user_id}/chat endpoint implemented
- Conversation history fetching logic
- User message appending functionality
- Agent runner invocation
- Tool call capturing
- Assistant response persistence
- Proper response structure returned to frontend

**Key Responsibilities**:
1. Design POST /api/{user_id}/chat endpoint
2. Fetch conversation history from DB
3. Append new user message
4. Invoke agent runner
5. Capture tool calls
6. Persist assistant response
7. Return response + tool_calls to frontend

**Validation Checklist**:
- [ ] POST /api/{user_id}/chat endpoint properly implemented
- [ ] Conversation history correctly fetched from database
- [ ] User messages properly appended to conversation
- [ ] Agent runner successfully invoked
- [ ] Tool calls properly captured and returned
- [ ] Assistant responses persisted to database
- [ ] Endpoint returns appropriate response structure
- [ ] Stateless behavior verified (no server-side session storage)

## PHASE F — Frontend Chatbot UI

**Purpose**: Integrate the OpenAI ChatKit UI component and connect it to the backend chat API, ensuring seamless user experience across devices.

**Inputs**:
- Backend chat API from Phase E
- OpenAI ChatKit library
- Existing frontend structure
- Responsive design requirements

**Outputs**:
- Floating chatbot icon added to UI (desktop + mobile)
- OpenAI ChatKit integrated into application
- Connection between ChatKit and backend chat endpoint
- Proper conversation_id lifecycle management
- Confirmation and task update displays
- Responsive UI/UX across devices

**Key Responsibilities**:
1. Add floating chatbot icon (desktop + mobile)
2. Integrate OpenAI ChatKit
3. Connect ChatKit to backend chat endpoint
4. Handle conversation_id lifecycle
5. Display confirmations and task updates
6. Ensure responsive UI/UX

**Validation Checklist**:
- [ ] Floating chatbot icon visible on desktop and mobile
- [ ] OpenAI ChatKit properly integrated
- [ ] Connection established with backend chat API
- [ ] Conversation_id properly managed
- [ ] Task confirmations and updates properly displayed
- [ ] UI responsive across device sizes
- [ ] User experience smooth and intuitive

## PHASE G — Integration, Testing & Deployment

**Purpose**: Conduct comprehensive testing of the integrated system, validate all requirements, and deploy to production.

**Inputs**:
- Complete backend implementation (Phases A-F)
- Complete frontend implementation (Phases A-F)
- All functional and non-functional requirements
- Production deployment environment

**Outputs**:
- All natural language commands validated
- Multi-step tool chaining tested
- Error scenarios validated
- Stateless behavior verified across restarts
- Backend deployed to production
- Frontend redeployed on Vercel
- Production domain functionality verified

**Key Responsibilities**:
1. Validate all natural language commands
2. Test multi-step tool chaining
3. Test error scenarios
4. Ensure stateless behavior across restarts
5. Deploy backend
6. Redeploy frontend on Vercel
7. Verify production domain functionality

**Validation Checklist**:
- [ ] All natural language commands properly handled
- [ ] Multi-step tool chaining works correctly
- [ ] Error scenarios handled gracefully
- [ ] Stateless behavior maintained across server restarts
- [ ] Backend successfully deployed
- [ ] Frontend successfully redeployed on Vercel
- [ ] Production domain functionality verified
- [ ] All success criteria from spec validated
- [ ] Cross-user data isolation confirmed