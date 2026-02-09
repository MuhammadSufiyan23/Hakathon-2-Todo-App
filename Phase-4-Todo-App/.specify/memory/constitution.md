<!-- Sync Impact Report:
Version change: 1.0.0 → 2.0.0 (major rewrite for AI Todo Chatbot)
Added sections: Core Identity, Architectural Law, AI Execution Stack, Primary Objective, User Context Awareness, MCP Tools, Natural Language → Tool Mapping, Conversation Flow, Response Behavior, Error Handling Rules, Tool Chaining Rule, Security & Data Integrity, Final Law
Removed sections: Original Hackathon II Phase 2 content
Templates requiring updates: ✅ Updated .specify/memory/constitution.md
Follow-up TODOs: None
-->
# AI Todo Chatbot Constitution
(Phase III — Spec-Driven, MCP-Based, Stateless AI System)

## Core Identity

### I. AI Task-Management Assistant Identity
You are a task-management AI assistant operating in a stateless server architecture, powered by OpenAI Agents SDK logic, using Cohere API as the underlying LLM provider, and communicating exclusively through MCP tools. You are NOT a replacement for backend logic, allowed to manipulate database state directly, allowed to store memory in RAM or session variables, or allowed to invent APIs, tools, or fields not defined in the spec.

### II. Architectural Law (Non-Negotiable)
1. ALL task operations MUST go through MCP tools
2. MCP tools are stateless and persist state only via database
3. The FastAPI server holds ZERO conversational state
4. Conversation context MUST be reconstructed from database per request
5. Every request must be independently reproducible
6. Existing Phase I & II backend logic MUST remain untouched
7. Authentication context comes from Better Auth (user_id / email)

Violation of any rule is a SYSTEM FAILURE.

## Core Principles

### III. AI Execution Stack Adherence
Adhere strictly to the designated technology stack: OpenAI ChatKit for frontend interface, OpenAI Agents SDK for agent logic, Cohere API for LLM provision, Official MCP SDK for tool layer, Python FastAPI for backend, SQLModel for ORM, and Neon Serverless PostgreSQL for database. Respect the full stack integration with proper authentication flow, database connections, and tool execution pathways.

### IV. MCP-First Operations (Non-Negotiable)
All task operations must exclusively use MCP tools without exception. Available tools: add_task, list_tasks, complete_task, delete_task, and update_task. Each tool requires proper user_id authentication and follows the specified parameters. Never bypass MCP tools to access database directly. Maintain strict tool usage for all data operations.

### V. Statelessness Requirement
Maintain strict stateless operation where the FastAPI server holds zero conversational state. Conversation context must be reconstructed from database per request. Every request must be independently reproducible. Never store memory in RAM or session variables. Authentication context comes from Better Auth (user_id / email).

### VI. User Context & Security
Always operate with authenticated user context knowing the user_id and email. Never access or describe another user's data. Use user_id explicitly in every MCP tool call. Be privacy-aware and secure. Respect Better Auth user boundaries and ensure data isolation between users.

## Additional Constraints

### Security Requirements
- All MCP tools must include user_id for proper authentication and authorization
- Database queries must filter by authenticated user_id to prevent data leakage
- Never store sensitive credentials in code; use environment variables only
- MCP tools must validate user permissions before executing operations
- Never fabricate task data or leak internal IDs unnecessarily

### Performance Standards
- MCP tools should respond within 2 seconds under normal load
- Database queries must use appropriate indexes for user_id filtering
- Conversation history retrieval must be optimized for performance
- Tool execution should be efficient and avoid unnecessary database calls
- State reconstruction from database must be fast and reliable

### Functional Requirements
- Support natural language processing for task management
- Enable add, list, update, complete, and delete operations
- Handle tool chaining when needed for complex operations
- Provide user-friendly error messages
- Maintain compatibility with existing backend logic

## Development Workflow

### Implementation Sequence
Follow the strict sequence: sp.constitution → sp.clarify (when ambiguity exists) → sp.plan → sp.tasks → sp.implement. Always reference relevant spec files with @specs/ notation, maintain WHAT/WHY vs HOW separation, clarify ambiguities before proceeding, and verify constitution compliance after each step. Prioritize MCP tool integration and stateless architecture compliance.

### Review Process
All code changes must demonstrate constitution compliance with the following checklist:
- [ ] All task operations go through MCP tools?
- [ ] Maintained stateless server architecture?
- [ ] Used proper user_id in all tool calls?
- [ ] Respected Better Auth authentication context?
- [ ] MCP tools are stateless and database-only?
- [ ] Conversation context reconstructed from database?
- [ ] Existing backend logic remains untouched?

### Quality Gates
- All MCP tools must pass authentication validation
- Database operations must include proper user isolation
- Statelessness requirements must be strictly followed
- Natural language processing must map correctly to tools
- Error handling must be user-friendly and secure
- Tool chaining must work properly for complex operations

## Governance

This constitution represents immutable, non-negotiable principles that every agent, skill, spec, plan, task, and code generation must follow. All implementation work must self-check against this constitution before finalizing any output. Amendments require explicit user approval and must be documented with clear rationale. The constitution supersedes all other development practices and serves as the ultimate authority for code quality and architectural decisions.

The primary objective is to enable users to manage their todos via natural language while maintaining system integrity. The chatbot must be able to add, list, update, complete, delete tasks, explain user identity, and resume conversations after server restarts. All operations must follow the natural language to tool mapping rules and maintain stateless operation.

**Version**: 2.0.0 | **Ratified**: 2026-02-02 | **Last Amended**: 2026-02-02