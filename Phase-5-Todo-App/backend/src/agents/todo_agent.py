import os
import json
from typing import Dict, Any, List
import requests
from ..tools.task_tools import (
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task
)

class TodoAgent:
    """
    Todo AI Agent that interprets natural language and orchestrates MCP tools
    to perform task operations
    """

    def __init__(self):
        # Initialize Cohere as the LLM provider
        api_key = os.getenv("COHERE_API_KEY")

        if not api_key:
            # If no API key is provided, set to None to trigger fallback behavior
            self.api_key = None
            print("Warning: COHERE_API_KEY not found in environment. Using fallback responses.")
        else:
            self.api_key = api_key

        self.base_url = "https://api.cohere.ai/v1"

        # Store available tools for the agent
        self.tools = {
            "add_task": add_task,
            "list_tasks": list_tasks,
            "complete_task": complete_task,
            "delete_task": delete_task,
            "update_task": update_task
        }

        # Define the system prompt that guides the agent's behavior
        self.system_prompt = """
        You are a helpful todo management assistant. Your role is to help users manage their tasks through natural language.

        When users ask you to:
        - Add/create/remember a task: Use the add_task tool
        - Show/list/view tasks: Use the list_tasks tool
        - Complete/finish/done a task: Use the complete_task tool
        - Delete/remove/cancel a task: Use the delete_task tool
        - Change/update/rename a task: Use the update_task tool

        IMPORTANT: Each task has a simple number (1, 2, 3...) displayed on the task card. Users can refer to tasks by:
        - Task number (e.g., "Delete task 1" or "Complete task 2")
        - Task title (e.g., "Delete Gym" or "Complete meeting")

        When a user mentions a task by its title (e.g., "Delete Gym"), pass the task title directly as the task_id parameter.
        When a user mentions a task by number (e.g., "Delete task 1"), pass the number as the task_id parameter.

        When you successfully create a task, ALWAYS mention the task number in your response.
        Example: "I've added 'Buy groceries' as task #3 to your list."

        When listing tasks, mention that users can use the task number shown on each card for easy reference.

        Always use the appropriate tool based on the user's request.
        Confirm successful actions to the user in a friendly way.
        If a user asks about something that doesn't relate to task management, politely explain that you're a todo assistant.
        """

    def process_request(self, user_input: str, user_id: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Process a natural language request from the user
        """
        if conversation_history is None:
            conversation_history = []

        # Check if API key is available
        if not self.api_key:
            # Fallback to simple rule-based processing when no API key is available
            return self._fallback_process_request(user_input, user_id)

        # Prepare the messages for the LLM
        # Convert conversation history to Cohere format
        chat_history = []
        for msg in conversation_history:
            role = "USER" if msg["role"] == "user" else "CHATBOT"
            chat_history.append({
                "role": role,
                "message": msg["content"]
            })

        # Call the Cohere API to determine the appropriate action
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # Use Cohere's tool calling capability
            data = {
                "model": "command-r-plus-08-2024",
                "message": user_input,
                "chat_history": chat_history,
                "tools": self._get_tool_definitions(),
                "temperature": 0.1,
                "preamble": self.system_prompt
            }

            response = requests.post(
                f"{self.base_url}/chat",
                headers=headers,
                json=data
            )

            if response.status_code != 200:
                # Instead of returning error message to user, raise exception to be caught by caller
                raise Exception(f"Cohere API error: {response.status_code} - {response.text}")

            response_data = response.json()

            # Check if the model decided to call tools
            if "tool_calls" in response_data and response_data["tool_calls"]:
                tool_calls = response_data["tool_calls"]
                tool_results = []

                for tool_call in tool_calls:
                    function_name = tool_call["name"]
                    function_args = tool_call["parameters"]

                    if function_name in self.tools:
                        # Always override user_id to ensure correct user context
                        function_args["user_id"] = user_id

                        try:
                            result = self.tools[function_name](**function_args)

                            tool_results.append({
                                "name": function_name,
                                "arguments": function_args,
                                "result": result
                            })
                        except Exception as e:
                            error_result = {
                                "success": False,
                                "error": f"Error executing {function_name}: {str(e)}"
                            }
                            tool_results.append({
                                "name": function_name,
                                "arguments": function_args,
                                "result": error_result
                            })
                    else:
                        tool_results.append({
                            "name": function_name,
                            "arguments": function_args,
                            "result": {"success": False, "error": f"Unknown function: {function_name}"}
                        })

                # Send tool results back to the model to generate final response
                data_with_results = {
                    "model": "command-r-plus-08-2024",
                    "chat_history": chat_history + [
                        {"role": "USER", "message": user_input},
                        {"role": "CHATBOT", "message": response_data.get("text", ""), "tool_calls": tool_calls}
                    ],
                    "tools": self._get_tool_definitions(),
                    "tool_results": [
                        {
                            "call": {
                                "name": tr["name"],
                                "parameters": tr["arguments"]
                            },
                            "outputs": [tr["result"]]
                        } for tr in tool_results
                    ],
                    "temperature": 0.1,
                    "preamble": self.system_prompt,
                    "message": ""  # Empty message when providing tool_results
                }

                final_response = requests.post(
                    f"{self.base_url}/chat",
                    headers=headers,
                    json=data_with_results
                )

                if final_response.status_code == 200:
                    final_data = final_response.json()
                    return {
                        "response": final_data.get("text", "Operation completed successfully."),
                        "tool_calls": tool_results,
                        "success": True
                    }
                else:
                    # Instead of returning error message to user, raise exception to be caught by caller
                    raise Exception(f"Cohere API error on second call: {final_response.status_code} - {final_response.text}")
            else:
                # If no tools were called, return the model's response directly
                return {
                    "response": response_data.get("text", "I'm sorry, I couldn't understand your request."),
                    "tool_calls": [],
                    "success": True
                }

        except Exception as e:
            # Instead of returning error to user, re-raise to let the caller handle it appropriately
            raise e

    def _fallback_process_request(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """
        Fallback method when no API key is available - performs simple rule-based processing
        """
        user_input_lower = user_input.lower().strip()

        # Parse the user input to determine the action
        if any(word in user_input_lower for word in ['add', 'create', 'new', 'make']):
            # Extract task title from input (simple parsing)
            parts = user_input_lower.split()
            if len(parts) > 1:
                # Look for the first word that indicates the action and skip it
                start_idx = 1
                for i, word in enumerate(parts):
                    if word in ['add', 'create', 'new', 'make']:
                        start_idx = i + 1
                        break
                task_title = ' '.join(parts[start_idx:]) or "Untitled task"

                # Execute add_task function
                try:
                    result = add_task(user_id=user_id, title=task_title)
                    return {
                        "response": f"I've added the task '{task_title}' to your list.",
                        "tool_calls": [{"name": "add_task", "arguments": {"user_id": user_id, "title": task_title}, "result": result}],
                        "success": True
                    }
                except Exception as e:
                    return {
                        "response": f"Sorry, I couldn't add the task: {str(e)}",
                        "tool_calls": [],
                        "success": False
                    }

        elif any(word in user_input_lower for word in ['list', 'show', 'view', 'display', 'all', 'tasks']):
            # Execute list_tasks function
            try:
                result = list_tasks(user_id=user_id)
                if result and len(result) > 0:
                    task_titles = [task.get('title', 'Untitled') for task in result]
                    task_list_str = ', '.join(task_titles[:5])  # Limit to first 5 tasks
                    if len(result) > 5:
                        task_list_str += f" and {len(result) - 5} more tasks"
                    return {
                        "response": f"You have {len(result)} tasks: {task_list_str}",
                        "tool_calls": [{"name": "list_tasks", "arguments": {"user_id": user_id}, "result": result}],
                        "success": True
                    }
                else:
                    return {
                        "response": "You don't have any tasks yet.",
                        "tool_calls": [{"name": "list_tasks", "arguments": {"user_id": user_id}, "result": result}],
                        "success": True
                    }
            except Exception as e:
                return {
                    "response": f"Sorry, I couldn't retrieve your tasks: {str(e)}",
                    "tool_calls": [],
                    "success": False
                }

        elif any(word in user_input_lower for word in ['complete', 'done', 'finish', 'completed']):
            # Extract task ID (simple parsing - look for numbers)
            import re
            task_ids = re.findall(r'\d+', user_input)
            if task_ids:
                task_id = task_ids[0]
                try:
                    result = complete_task(user_id=user_id, task_id=task_id)
                    return {
                        "response": f"I've marked task {task_id} as completed.",
                        "tool_calls": [{"name": "complete_task", "arguments": {"user_id": user_id, "task_id": task_id}, "result": result}],
                        "success": True
                    }
                except Exception as e:
                    return {
                        "response": f"Sorry, I couldn't complete the task: {str(e)}",
                        "tool_calls": [],
                        "success": False
                    }
            else:
                return {
                    "response": "Please specify which task to complete by its number.",
                    "tool_calls": [],
                    "success": True
                }

        elif any(word in user_input_lower for word in ['delete', 'remove', 'cancel']):
            # Extract task ID (simple parsing - look for numbers)
            import re
            task_ids = re.findall(r'\d+', user_input)
            if task_ids:
                task_id = task_ids[0]
                try:
                    result = delete_task(user_id=user_id, task_id=task_id)
                    return {
                        "response": f"I've deleted task {task_id}.",
                        "tool_calls": [{"name": "delete_task", "arguments": {"user_id": user_id, "task_id": task_id}, "result": result}],
                        "success": True
                    }
                except Exception as e:
                    return {
                        "response": f"Sorry, I couldn't delete the task: {str(e)}",
                        "tool_calls": [],
                        "success": False
                    }
            else:
                return {
                    "response": "Please specify which task to delete by its number.",
                    "tool_calls": [],
                    "success": True
                }

        elif any(word in user_input_lower for word in ['update', 'change', 'modify', 'edit']):
            # Extract task ID and new title (simple parsing)
            import re
            task_ids = re.findall(r'\d+', user_input)
            if task_ids:
                task_id = task_ids[0]

                # Extract new title after the task number
                words = user_input.split()
                start_idx = -1
                for i, word in enumerate(words):
                    if word.isdigit() and word == task_id:
                        start_idx = i + 1
                        break

                if start_idx < len(words):
                    new_title = ' '.join(words[start_idx:])

                    try:
                        result = update_task(user_id=user_id, task_id=task_id, title=new_title)
                        return {
                            "response": f"I've updated task {task_id} to '{new_title}'.",
                            "tool_calls": [{"name": "update_task", "arguments": {"user_id": user_id, "task_id": task_id, "title": new_title}, "result": result}],
                            "success": True
                        }
                    except Exception as e:
                        return {
                            "response": f"Sorry, I couldn't update the task: {str(e)}",
                            "tool_calls": [],
                            "success": False
                        }

            return {
                "response": "Please specify which task to update and the new title. For example: 'Update task 1 to buy groceries'.",
                "tool_calls": [],
                "success": True
            }

        else:
            # Default response for unrecognized commands
            return {
                "response": "I can help you manage your tasks. You can ask me to add, list, complete, delete, or update tasks. For example: 'Add a task to buy groceries' or 'Show my tasks'.",
                "tool_calls": [],
                "success": True
            }

    def _get_tool_definitions(self):
        """
        Define the available tools in the format expected by Cohere API
        """
        return [
            {
                "name": "add_task",
                "description": "Add a new task for the user",
                "parameter_definitions": {
                    "user_id": {
                        "type": "string",
                        "description": "The user's ID",
                        "required": True
                    },
                    "title": {
                        "type": "string",
                        "description": "The task title",
                        "required": True
                    },
                    "description": {
                        "type": "string",
                        "description": "The task description (optional)",
                        "required": False
                    }
                }
            },
            {
                "name": "list_tasks",
                "description": "List tasks for the user",
                "parameter_definitions": {
                    "user_id": {
                        "type": "string",
                        "description": "The user's ID",
                        "required": True
                    },
                    "status": {
                        "type": "string",
                        "description": "Filter by status: 'all', 'pending', or 'completed' (optional)",
                        "required": False
                    }
                }
            },
            {
                "name": "complete_task",
                "description": "Mark a task as completed",
                "parameter_definitions": {
                    "user_id": {
                        "type": "string",
                        "description": "The user's ID",
                        "required": True
                    },
                    "task_id": {
                        "type": "string",
                        "description": "The task identifier - can be: task number (1, 2, 3...), UUID, or task title (e.g., 'Gym', 'Buy groceries'). When user mentions a task by name, use the task title directly.",
                        "required": True
                    }
                }
            },
            {
                "name": "delete_task",
                "description": "Delete a task for the user",
                "parameter_definitions": {
                    "user_id": {
                        "type": "string",
                        "description": "The user's ID",
                        "required": True
                    },
                    "task_id": {
                        "type": "string",
                        "description": "The task identifier - can be: task number (1, 2, 3...), UUID, or task title (e.g., 'Gym', 'Buy groceries'). When user mentions a task by name, use the task title directly.",
                        "required": True
                    }
                }
            },
            {
                "name": "update_task",
                "description": "Update a task for the user",
                "parameter_definitions": {
                    "user_id": {
                        "type": "string",
                        "description": "The user's ID",
                        "required": True
                    },
                    "task_id": {
                        "type": "string",
                        "description": "The task identifier - can be: task number (1, 2, 3...), UUID, or task title (e.g., 'Gym', 'Buy groceries'). When user mentions a task by name, use the task title directly.",
                        "required": True
                    },
                    "title": {
                        "type": "string",
                        "description": "The new task title (optional)",
                        "required": False
                    },
                    "description": {
                        "type": "string",
                        "description": "The new task description (optional)",
                        "required": False
                    }
                }
            }
        ]

    def _generate_final_response(self, user_input: str, tool_results: List[Dict[str, Any]]) -> str:
        """
        Generate a natural language response based on tool execution results
        """
        # Simple response generation based on tool results
        # In a real implementation, this would be more sophisticated

        if not tool_results:
            return "I processed your request, but no specific task operations were needed."

        # Check if there were any errors
        errors = [result for result in tool_results if not result.get("success")]
        if errors:
            error_msgs = [f"- {err.get('error', 'Unknown error')}" for err in errors]
            return f"I encountered some errors while processing your request:\n" + "\n".join(error_msgs)

        # Generate success responses based on tool types
        responses = []
        for result in tool_results:
            if result.get("success"):
                if "task_title" in result:
                    # ✅ Include display_id in response if available
                    display_id = result.get("display_id")
                    if display_id:
                        responses.append(f"I've added '{result['task_title']}' as task #{display_id} to your list.")
                    else:
                        responses.append(f"I've added the task '{result['task_title']}' to your list.")
                elif "tasks" in result:
                    task_count = len(result["tasks"])
                    if task_count == 0:
                        responses.append("You have no tasks matching that criteria.")
                    else:
                        task_titles = [task["title"] for task in result["tasks"]]
                        responses.append(f"You have {task_count} tasks: {', '.join(task_titles[:3])}{'...' if task_count > 3 else ''}")
                elif "completed" in result and result["completed"]:
                    responses.append("I've marked that task as completed.")
                elif "task_id" in result:
                    responses.append("The task has been processed successfully.")

        if responses:
            return " ".join(responses)
        else:
            return "I've processed your request successfully."