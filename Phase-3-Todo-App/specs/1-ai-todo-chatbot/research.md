# Research: AI Todo Chatbot Implementation

**Feature**: 1-ai-todo-chatbot
**Date**: 2026-02-02
**Status**: Completed

## Overview

Research conducted to resolve unknowns and establish best practices for implementing the AI Todo Chatbot with OpenAI Agents SDK, Cohere API, and MCP tools.

## Technology Decisions

### Decision: Use OpenAI Assistant API with Cohere adapter
**Rationale**: The OpenAI Agents SDK can be configured to work with Cohere API as the LLM provider by using the appropriate API adapter. This allows us to leverage the familiar OpenAI Agents SDK while meeting the requirement to use Cohere as the LLM provider.

**Alternatives considered**:
- Direct Cohere API calls with custom orchestration - Would require building our own agent framework
- LangChain with Cohere - Adds additional complexity and dependencies

### Decision: Implement MCP Server as a separate service component
**Rationale**: MCP tools need to be registered with an MCP server that can be accessed by the OpenAI Agents SDK. Implementing this as a component within our FastAPI application ensures tight integration while maintaining the required architecture.

**Alternatives considered**:
- Standalone MCP server - Would add network complexity and potential failure points
- Third-party MCP server - Would reduce control over the tool implementations

### Decision: Use Neon Serverless PostgreSQL for conversation persistence
**Rationale**: Consistent with existing architecture and requirements. Neon provides serverless scaling which is appropriate for conversation data that may have variable access patterns.

**Alternatives considered**:
- Redis for session storage - Would violate statelessness requirement by storing conversation context in memory
- File-based storage - Would not scale well and wouldn't integrate well with existing SQLModel patterns

## Best Practices Applied

### Security Best Practices
- All API keys stored in environment variables
- Database queries always filtered by user_id
- Input validation on all user inputs
- Rate limiting considerations for API calls

### Performance Best Practices
- Connection pooling for database operations
- Efficient indexing on user_id and conversation_id
- Caching of frequently accessed data patterns
- Asynchronous operations where appropriate

### Architecture Best Practices
- Stateless design maintained throughout
- Clear separation of concerns between components
- Proper error handling and logging
- Comprehensive testing at all levels

## Unknowns Resolved

### Cohere API Integration
**Unknown**: How to configure OpenAI Agents SDK to use Cohere API
**Resolution**: Through API adapters that map OpenAI API calls to Cohere API calls, maintaining the same interface while using Cohere as the underlying provider.

### MCP Tool Registration
**Unknown**: How to properly register MCP tools with the agent
**Resolution**: MCP tools are registered with an MCP server which is then connected to the OpenAI Agents SDK. The tools are defined with proper schemas and validation.

### Conversation State Management
**Unknown**: How to maintain conversation context while keeping the system stateless
**Resolution**: Conversation history is loaded from the database on each request and passed to the agent. The agent operates on this history without maintaining its own state.

## Implementation Patterns

### Database Patterns
- Use SQLModel for all database interactions to maintain consistency
- Implement proper foreign key relationships between conversations, messages, and tasks
- Apply proper indexing for efficient querying by user_id

### API Patterns
- RESTful API design for the chat endpoint
- Proper authentication using Better Auth
- Consistent error response format
- Request/response validation

### AI Integration Patterns
- Natural language to tool mapping through agent configuration
- Tool chaining for complex operations
- Proper error handling and user feedback
- Confirmation flows for destructive operations

## Risk Mitigation

### API Availability
- Implement retry mechanisms for Cohere API calls
- Graceful degradation when API is unavailable
- Proper error messaging to users

### Data Privacy
- Strict user data isolation enforced at database level
- No sharing of conversation data between users
- Proper authentication on all endpoints

### Performance
- Monitor API response times and implement caching where appropriate
- Optimize database queries with proper indexing
- Consider pagination for long conversation histories