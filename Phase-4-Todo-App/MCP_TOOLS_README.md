# MCP Tools for Todo App

This project implements MCP (Model Context Protocol) tools for managing todo tasks in accordance with the Official MCP SDK specification. The tools provide a stateless interface to the todo application's database.

## Files

- `todo_mcp_tools.py`: Contains the core MCP tool implementations
- `manifest.json`: Defines the available tools and their schemas
- `server.py`: Implements the MCP server that exposes the tools
- `test_mcp_tools.py`: Test script to verify the functionality

## Available Tools

### list_tasks
Retrieve all tasks for the authenticated user.

Parameters: None

### add_task
Add a new task for the user.

Parameters:
- `title` (string, required): The task title
- `description` (string, optional): Task description
- `priority` (enum: low, medium, high, optional): Task priority (defaults to 'medium')

### update_task
Update an existing task for the user.

Parameters:
- `task_id` (string, required): The ID of the task to update
- `title` (string, optional): New task title
- `description` (string, optional): New task description
- `priority` (enum: low, medium, high, optional): New task priority

### delete_task
Delete a task for the user.

Parameters:
- `task_id` (string, required): The ID of the task to delete

### complete_task
Mark a task as completed or not completed for the user.

Parameters:
- `task_id` (string, required): The ID of the task to update
- `completed` (boolean, optional): Whether the task is completed (defaults to true)

## Architecture

The implementation follows the stateless principle required by MCP:
- Each tool operates independently
- Tools only interact with the database through the shared database connection
- No server-side state is maintained between requests
- User authentication is handled through the user_id parameter

## Database

The tools use the same database models and connection as the main todo application, ensuring consistency across the system. The database is automatically initialized when needed.

## Testing

Run the test script to verify all functionality:
```bash
python test_mcp_tools.py
```