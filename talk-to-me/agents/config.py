import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class AgentConfig:
    name: str
    description: str
    personality: str
    skills: list[dict]
    model_provider: str
    model_name: str
    port: int
    fallback_model_name: Optional[str] = None


def get_openai_key() -> str:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY not set in environment")
    return key


def get_anthropic_key() -> str:
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError("ANTHROPIC_API_KEY not set in environment")
    return key


def get_ollama_url() -> str:
    return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


def load_agent_config(agent_type: str) -> AgentConfig:
    import yaml
    from pathlib import Path

    config_path = Path(__file__).parent.parent / "config" / "agents.yaml"
    with open(config_path) as f:
        data = yaml.safe_load(f)

    agent_data = data["agents"].get(agent_type)
    if not agent_data:
        raise ValueError(f"Agent '{agent_type}' not found in config")

    return AgentConfig(
        name=agent_data["name"],
        description=agent_data["description"],
        personality=agent_data["personality"],
        skills=agent_data["skills"],
        model_provider=agent_data["model_provider"],
        model_name=agent_data["model_name"],
        port=agent_data["port"],
        fallback_model_name=agent_data.get("fallback_model_name"),
    )


def get_available_agents() -> list[str]:
    import yaml
    from pathlib import Path

    config_path = Path(__file__).parent.parent / "config" / "agents.yaml"
    with open(config_path) as f:
        data = yaml.safe_load(f)

    return list(data["agents"].keys())
