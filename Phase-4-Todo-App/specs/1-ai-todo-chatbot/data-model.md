# Data Model: AI Todo Chatbot

**Feature**: 1-ai-todo-chatbot
**Date**: 2026-02-02
**Status**: Defined

## Overview

This document describes the data models required for the AI Todo Chatbot implementation, including the relationships between entities and validation rules.

## Entities

### Task (Existing)
**Description**: Represents a user's todo item with title, description, completion status, and timestamps
**Location**: backend/src/models/todo.py (existing)

**Fields**:
- id: Integer (Primary Key, Auto-generated)
- user_id: String (Foreign Key to user, required)
- title: String (required, max 255 characters)
- description: String (optional, max 1000 characters)
- completed: Boolean (default False)
- created_at: DateTime (Auto-generated)
- updated_at: DateTime (Auto-generated, updates on modification)

**Relationships**:
- Belongs to: User (via user_id)
- Referenced by: Messages (in content references)

**Validation Rules**:
- user_id must match authenticated user
- title must not be empty
- completed must be boolean value

### Conversation (New)
**Description**: Represents a chat session between user and AI assistant with metadata
**Location**: backend/src/models/conversation.py

**Fields**:
- id: Integer (Primary Key, Auto-generated)
- user_id: String (Foreign Key to user, required)
- created_at: DateTime (Auto-generated)
- updated_at: DateTime (Auto-generated, updates on modification)

**Relationships**:
- Belongs to: User (via user_id)
- Has Many: Messages (via conversation_id)

**Validation Rules**:
- user_id must match authenticated user
- created_at is set on creation only
- updated_at is updated when messages are added

### Message (New)
**Description**: Represents individual exchanges in a conversation with role (user/assistant) and content
**Location**: backend/src/models/message.py

**Fields**:
- id: Integer (Primary Key, Auto-generated)
- user_id: String (Foreign Key to user, required)
- conversation_id: Integer (Foreign Key to conversation, required)
- role: String (required, values: "user", "assistant")
- content: String (required, max 5000 characters)
- created_at: DateTime (Auto-generated)

**Relationships**:
- Belongs to: User (via user_id)
- Belongs to: Conversation (via conversation_id)

**Validation Rules**:
- user_id must match authenticated user
- conversation_id must exist and belong to user
- role must be either "user" or "assistant"
- content must not be empty

## Relationships

```
User (1) -> (Many) Task
User (1) -> (Many) Conversation
User (1) -> (Many) Message
Conversation (1) -> (Many) Message
```

## Database Indexes

### Task Table
- Index on user_id (for efficient user-based queries)
- Index on (user_id, completed) (for efficient status filtering)
- Index on created_at (for chronological ordering)

### Conversation Table
- Index on user_id (for efficient user-based queries)
- Index on created_at (for chronological ordering)

### Message Table
- Index on user_id (for efficient user-based queries)
- Index on conversation_id (for conversation-based queries)
- Index on (conversation_id, created_at) (for chronological conversation history)

## Data Lifecycle

### Conversation Lifecycle
1. Conversation created when user starts new chat
2. Messages added as user and AI interact
3. Conversation remains accessible for ongoing reference
4. Conversation updated when new messages are added
5. Conversation archived after extended inactivity (future feature)

### Message Lifecycle
1. User message created when request received
2. Assistant message created after AI response
3. Messages immutable after creation
4. Messages retrieved in chronological order for conversation context

## Access Control
- All queries must be filtered by user_id
- Users can only access their own conversations and messages
- Task operations via MCP tools must respect user_id boundaries
- Authentication required for all data operations