from dataclasses import dataclass
from langgraph_supervisor import create_supervisor
from src.intergrationd.llm import make_chat_model
from src.agents.prompts.supervisor import SUPERVISOR_PROMPT
from langgraph.checkpoint.memory import MemorySaver

@dataclass
class SupervisorResponse:
    message: str
    result: str

def build_subagent() -> list:
    return []

class Supervisor:
    def __init__(self):
        self.grap = create_supervisor(
            agents=build_subagent(),
            model=make_chat_model(),
            prompt= SUPERVISOR_PROMPT,
            supervisor_name="supervisor",
            output_mode="full_history",
        ).compile(checkpointer=MemorySaver)

    async def handle_message():
        pass