"""MCP Server for Todo Tools

This script creates an MCP server that exposes the todo management tools.
It follows the Official MCP SDK specification and implements stateless operations
that only interact with the database.
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any, List, Optional, Callable
from pydantic import BaseModel
from todo_mcp_tools import (
    list_tasks, add_task, update_task, delete_task, complete_task
)


class MCPServer:
    def __init__(self):
        self.tools = {
            "list_tasks": self._handle_list_tasks,
            "add_task": self._handle_add_task,
            "update_task": self._handle_update_task,
            "delete_task": self._handle_delete_task,
            "complete_task": self._handle_complete_task
        }

    def _handle_list_tasks(self, user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list_tasks request"""
        try:
            result = list_tasks(user_id=user_id)
            return {
                "result": result
            }
        except Exception as e:
            return {
                "error": {
                    "type": "llm_call_failed",
                    "message": f"Error listing tasks: {str(e)}"
                }
            }

    def _handle_add_task(self, user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle add_task request"""
        try:
            title = params.get('title')
            description = params.get('description')
            priority = params.get('priority', 'medium')

            if not title:
                raise ValueError("Missing required parameter: title")

            result = add_task(
                user_id=user_id,
                title=title,
                description=description,
                priority=priority
            )
            return {
                "result": result
            }
        except Exception as e:
            return {
                "error": {
                    "type": "llm_call_failed",
                    "message": f"Error adding task: {str(e)}"
                }
            }

    def _handle_update_task(self, user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle update_task request"""
        try:
            task_id = params.get('task_id')
            if task_id is None:
                raise ValueError("Missing required parameter: task_id")

            result = update_task(
                task_id=task_id,
                user_id=user_id,
                title=params.get('title'),
                description=params.get('description'),
                priority=params.get('priority')
            )
            return {
                "result": result
            }
        except Exception as e:
            return {
                "error": {
                    "type": "llm_call_failed",
                    "message": f"Error updating task: {str(e)}"
                }
            }

    def _handle_delete_task(self, user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle delete_task request"""
        try:
            task_id = params.get('task_id')
            if task_id is None:
                raise ValueError("Missing required parameter: task_id")

            result = delete_task(task_id=task_id, user_id=user_id)
            return {
                "result": result
            }
        except Exception as e:
            return {
                "error": {
                    "type": "llm_call_failed",
                    "message": f"Error deleting task: {str(e)}"
                }
            }

    def _handle_complete_task(self, user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle complete_task request"""
        try:
            task_id = params.get('task_id')
            if task_id is None:
                raise ValueError("Missing required parameter: task_id")

            completed = params.get('completed', True)

            result = complete_task(task_id=task_id, user_id=user_id, completed=completed)
            return {
                "result": result
            }
        except Exception as e:
            return {
                "error": {
                    "type": "llm_call_failed",
                    "message": f"Error completing task: {str(e)}"
                }
            }

    async def run(self):
        """Run the MCP server, reading requests from stdin and writing responses to stdout"""
        buffer = ""
        try:
            while True:
                line = await self._read_line()
                if not line.strip():
                    continue

                # Handle header lines and body
                if line.startswith("Content-Length:"):
                    content_length = int(line.split(":")[1].strip())
                    # Read the empty line after headers
                    await self._read_line()
                    # Read the body
                    body = await self._read_json(content_length)

                    # Process the request
                    response = await self._process_request(body)

                    # Send the response
                    await self._write_response(response)
                else:
                    # Accumulate lines until we find Content-Length
                    buffer += line + "\n"

        except KeyboardInterrupt:
            pass
        except Exception as e:
            error_response = {
                "error": {
                    "type": "llm_call_failed",
                    "message": f"Server error: {str(e)}"
                }
            }
            await self._write_response(error_response)

    async def _read_line(self) -> str:
        """Read a line from stdin"""
        return await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)

    async def _read_json(self, length: int) -> Dict[str, Any]:
        """Read JSON body with specified length"""
        body_str = ""
        remaining = length
        while remaining > 0:
            chunk = sys.stdin.read(remaining)
            if not chunk:
                break
            body_str += chunk
            remaining -= len(chunk.encode('utf-8'))

        return json.loads(body_str)

    async def _process_request(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single MCP request"""
        request_type = body.get('method')

        if request_type == 'initialize':
            # Send initialization response with tool definitions
            return {
                "id": body.get('id'),
                "result": {
                    "capabilities": {
                        "tools": {
                            "list": {
                                "type": "function",
                                "function": {
                                    "name": "list_tools",
                                    "description": "List all available tools"
                                }
                            }
                        }
                    },
                    "protocolVersion": "2.0.0"
                }
            }
        elif request_type == 'call_tool':
            # Process tool call
            tool_name = body.get('params', {}).get('name')
            tool_arguments = body.get('params', {}).get('arguments', {})

            if tool_name not in self.tools:
                return {
                    "id": body.get('id'),
                    "error": {
                        "type": "llm_call_failed",
                        "message": f"Unknown tool: {tool_name}"
                    }
                }

            # Extract user_id from the environment or arguments
            user_id = os.environ.get('USER_ID') or tool_arguments.get('user_id')
            if not user_id:
                return {
                    "id": body.get('id'),
                    "error": {
                        "type": "llm_call_failed",
                        "message": "Missing user_id in environment or arguments"
                    }
                }

            # Call the appropriate handler
            handler = self.tools[tool_name]
            result = handler(user_id, tool_arguments)
            result['id'] = body.get('id')
            return result
        else:
            return {
                "id": body.get('id'),
                "error": {
                    "type": "llm_call_failed",
                    "message": f"Unsupported request type: {request_type}"
                }
            }

    async def _write_response(self, response: Dict[str, Any]):
        """Write response to stdout with proper MCP formatting"""
        response_str = json.dumps(response)
        headers = f"Content-Type: application/json\nContent-Length: {len(response_str.encode('utf-8'))}\n\n"
        output = headers + response_str
        sys.stdout.write(output)
        sys.stdout.flush()


async def main():
    server = MCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())