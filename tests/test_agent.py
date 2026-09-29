from google.adk.agents import LlmAgent

from adk_00_hello_trench import agent
from adk_00_hello_trench.prompts import DESCRIPTION, INSTRUCTION
from adk_00_hello_trench.settings import Settings


def test_build_agent_wires_settings_and_prompts() -> None:
    settings = Settings(_env_file=None, GOOGLE_API_KEY="key", HELLO_TRENCH_MODEL="m")

    built = agent.build_agent(settings)

    assert isinstance(built, LlmAgent)
    assert built.name == agent.AGENT_NAME
    assert built.model == "m"
    assert built.description == DESCRIPTION
    assert built.instruction == INSTRUCTION


def test_root_agent_is_exposed_for_adk() -> None:
    assert isinstance(agent.root_agent, LlmAgent)
    assert agent.root_agent.name == agent.AGENT_NAME
