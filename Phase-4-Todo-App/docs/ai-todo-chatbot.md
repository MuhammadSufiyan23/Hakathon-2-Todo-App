# AI Todo Chatbot Feature

This document describes the AI Todo Chatbot feature that allows users to manage their tasks through natural language conversations.

## Overview

The AI Todo Chatbot enables users to interact with their todo list using natural language. Users can add, list, update, complete, and delete tasks by talking to the AI assistant.

## Architecture

The system follows a stateless architecture where:
- Conversation history is loaded from the database on each request
- The AI agent processes natural language and invokes MCP tools
- MCP tools perform database operations while maintaining user isolation
- Assistant responses are persisted to the database

## User Commands

Users can interact with the chatbot using commands like:
- "Add a task to buy groceries" - adds a new task
- "Show me my pending tasks" - lists incomplete tasks
- "Mark the first task as complete" - marks a task as completed
- "Delete the meeting task" - deletes a task
- "Update the grocery task to include milk" - updates a task

## Security

- All operations are authenticated using Better Auth
- Users can only access their own tasks and conversations
- MCP tools validate user_id on every operation
- Conversation history is isolated by user_id

## Technical Details

- LLM Provider: Cohere API
- AI Framework: OpenAI Agents SDK
- Tool Protocol: MCP (Model Context Protocol)
- Database: Neon Serverless PostgreSQL
- Frontend: OpenAI ChatKit integration