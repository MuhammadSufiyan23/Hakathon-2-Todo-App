from mcp.server import Server
from mcp.types import Tool
import asyncio
from typing import Dict, Any
from pydantic import Field
from .task_tools import (
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task
)

# Initialize the MCP server
server = Server("todo-mcp-server")


def initialize_mcp_server():
    """Initialize and return the MCP server with all tools registered"""

    # Register add_task tool
    @server.tool(
        "add_task",
        description="Add a new task for the user",
    )
    def handle_add_task(context, user_id: str = Field(..., description="The user's ID"),
                       title: str = Field(..., description="The task title"),
                       description: str = Field(None, description="The task description (optional)")) -> Dict[str, Any]:
        """Handle add_task requests"""
        return add_task(user_id=user_id, title=title, description=description)

    # Register list_tasks tool
    @server.tool(
        "list_tasks",
        description="List tasks for the user",
    )
    def handle_list_tasks(context, user_id: str = Field(..., description="The user's ID"),
                         status: str = Field("all", description="Filter by status: 'all', 'pending', or 'completed' (optional)")) -> Dict[str, Any]:
        """Handle list_tasks requests"""
        return list_tasks(user_id=user_id, status=status)

    # Register complete_task tool
    @server.tool(
        "complete_task",
        description="Mark a task as completed",
    )
    def handle_complete_task(context, user_id: str = Field(..., description="The user's ID"),
                            task_id: str = Field(..., description="The ID of the task to complete")) -> Dict[str, Any]:
        """Handle complete_task requests"""
        return complete_task(user_id=user_id, task_id=task_id)

    # Register delete_task tool
    @server.tool(
        "delete_task",
        description="Delete a task for the user",
    )
    def handle_delete_task(context, user_id: str = Field(..., description="The user's ID"),
                          task_id: str = Field(..., description="The ID of the task to delete")) -> Dict[str, Any]:
        """Handle delete_task requests"""
        return delete_task(user_id=user_id, task_id=task_id)

    # Register update_task tool
    @server.tool(
        "update_task",
        description="Update a task for the user",
    )
    def handle_update_task(context, user_id: str = Field(..., description="The user's ID"),
                          task_id: str = Field(..., description="The ID of the task to update"),
                          title: str = Field(None, description="The new task title (optional)"),
                          description: str = Field(None, description="The new task description (optional)")) -> Dict[str, Any]:
        """Handle update_task requests"""
        return update_task(user_id=user_id, task_id=task_id, title=title, description=description)

    return server


# If running as a standalone server
if __name__ == "__main__":
    import sys

    async def main():
        server_instance = initialize_mcp_server()

        # Start the server based on transport method
        if len(sys.argv) > 1:
            transport_method = sys.argv[1]
            if transport_method == "stdio":
                await server_instance.run_stdio()
            elif transport_method == "tcp":
                port = int(sys.argv[2]) if len(sys.argv) > 2 else 7667
                await server_instance.run_tcp(port=port)
            else:
                print(f"Unknown transport method: {transport_method}")
                sys.exit(1)
        else:
            # Default to stdio
            await server_instance.run_stdio()

    asyncio.run(main())