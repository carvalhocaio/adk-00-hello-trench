from google.adk.agents import LlmAgent

from .prompts import DESCRIPTION, INSTRUCTION
from .settings import Settings, get_settings

AGENT_NAME = "hello_trench"


def build_agent(settings: Settings) -> LlmAgent:
    return LlmAgent(
        name=AGENT_NAME,
        model=settings.agent_model,
        description=DESCRIPTION,
        instruction=INSTRUCTION,
    )


root_agent = build_agent(get_settings())
