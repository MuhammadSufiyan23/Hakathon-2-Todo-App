# Quickstart Guide: AI Todo Chatbot

**Feature**: 1-ai-todo-chatbot
**Date**: 2026-02-02
**Status**: Complete

## Overview

This guide provides the essential steps to get the AI Todo Chatbot up and running in your development environment.

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (or Neon Serverless PostgreSQL)
- Better Auth credentials
- Cohere API key
- OpenAI API key (for OpenAI Agents SDK)
- MCP SDK

## Setup Instructions

### 1. Environment Configuration

Create `.env` file in the backend directory with the following variables:

```env
DATABASE_URL="postgresql://username:password@host:port/database"
COHERE_API_KEY="your-cohere-api-key"
OPENAI_API_KEY="your-openai-api-key"  # For OpenAI Agents SDK
AUTH_SECRET="your-better-auth-secret"
```

### 2. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the database:
   ```bash
   # Run database migrations to create tables
   python -m alembic upgrade head
   ```

   Or if using direct SQLModel:
   ```bash
   python create_tables.py
   ```

4. Install MCP SDK:
   ```bash
   pip install mcp
   ```

5. Install OpenAI Agents SDK:
   ```bash
   pip install openai
   ```

### 3. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Install OpenAI ChatKit:
   ```bash
   npm install @openai/chatkit
   ```

### 4. Run the Application

#### Backend:
```bash
cd backend
uvicorn main:app --reload --port 8000
```

#### Frontend:
```bash
cd frontend
npm run dev
```

## Key Components

### MCP Server
Located in `backend/src/tools/server.py`, this component registers and serves the MCP tools that the AI agent will use to interact with the database.

### AI Agent
Located in `backend/src/agents/todo_agent.py`, this component processes natural language and orchestrates the appropriate MCP tools.

### Chat API
Located in `backend/src/api/chat.py`, this endpoint handles conversation flow and connects user input to the AI agent.

### Frontend Chat Component
Located in `frontend/src/components/ChatBot.tsx`, this component integrates the OpenAI ChatKit with the backend chat API.

## Configuration Points

1. **Cohere Integration**: The OpenAI Agents SDK needs to be configured to use Cohere as the LLM provider
2. **User Authentication**: Ensure Better Auth integration passes user_id to the chat endpoint
3. **Database Models**: Conversation and Message models need to be properly defined
4. **Tool Registration**: MCP tools (add_task, list_tasks, etc.) must be properly registered

## Testing the Integration

1. Start both backend and frontend servers
2. Authenticate with Better Auth
3. Click the chatbot icon in the UI
4. Try natural language commands like:
   - "Add a task to buy groceries"
   - "Show me my pending tasks"
   - "Mark the first task as complete"
   - "Delete the meeting task"

## Troubleshooting

### Common Issues

1. **Cohere API Not Working**: Verify COHERE_API_KEY is set and the OpenAI Agents SDK is configured correctly
2. **Database Connection**: Check DATABASE_URL and ensure required tables are created
3. **Authentication Issues**: Ensure Better Auth is properly configured and user_id is passed correctly
4. **MCP Tools Not Found**: Verify MCP server is running and tools are properly registered

### Logs to Check

- Backend logs for API and agent operations
- Database logs for query execution
- Frontend browser console for UI issues
- MCP server logs for tool execution

## Next Steps

1. Customize the AI agent's personality and response format
2. Enhance the natural language processing capabilities
3. Add advanced features like task categorization or reminders
4. Implement comprehensive error handling and user feedback
5. Deploy to production environment with proper monitoring