from typing import Dict, Any, List
from .todo_agent import TodoAgent


class AgentRunner:
    """
    Runs the Todo AI Agent and manages its execution
    """

    def __init__(self):
        self.agent = TodoAgent()

    def run_agent(self, user_input: str, user_id: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Run the agent with the given user input and context
        """
        return self.agent.process_request(
            user_input=user_input,
            user_id=user_id,
            conversation_history=conversation_history
        )


# Singleton instance for the agent runner
agent_runner = AgentRunner()


def get_agent_runner() -> AgentRunner:
    """
    Get the singleton agent runner instance
    """
    return agent_runner