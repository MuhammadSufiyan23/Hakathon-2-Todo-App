# OpenAI Agents Integration Skill

## Description
Runs the AI agent that interprets user messages and calls MCP tools, creating an intelligent assistant that can manage tasks through the Model Context Protocol.

## Purpose
- Run the AI agent that interprets user messages and calls MCP tools
- Enable natural language interaction with the todo management system
- Facilitate seamless communication between user requests and backend operations

## Usage
```
/sp.openai-agents-integration
```

## Prerequisites
- OpenAI API key configured
- MCP server running and accessible
- Conversation history storage available

## Responsibilities
- Create agent with system prompt
- Inject conversation history
- Attach MCP tools
- Execute agent runner
- Capture tool calls and responses

## Rules
- Agent must NEVER bypass MCP tools
- All task operations must use tools
- Maintain conversation context across interactions
- Handle errors gracefully and provide informative responses
- Follow security best practices for API key management