# Conversation DB Management Skill

## Description
Persists conversation history in a stateless architecture by managing conversation and message records in the database.

## Purpose
- Persist conversation history in a stateless architecture
- Enable retrieval of conversation context for AI interactions
- Maintain historical record of user-assistant exchanges

## Usage
```
/sp.conversation-db-management
```

## Prerequisites
- Database connection configured
- Conversation and Message models defined
- Proper database schema in place

## Responsibilities
- Create conversations if not provided
- Store user messages
- Store assistant responses
- Retrieve history for each request
- Manage conversation lifecycle
- Handle database transactions safely

## Data Models
- Conversation: Contains conversation metadata (ID, created_at, updated_at, user_id)
- Message: Contains individual messages (ID, conversation_id, role, content, timestamp, message_type)

## Features
- Automatic conversation creation for new sessions
- Message sequencing and ordering
- Conversation history retrieval
- Data integrity and transaction safety
- Efficient querying for conversation history