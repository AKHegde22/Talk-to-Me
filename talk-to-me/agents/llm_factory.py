from typing import TYPE_CHECKING, Literal

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama

from agents.config import get_openai_key, get_anthropic_key, get_ollama_url

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel


Provider = Literal["openai", "anthropic", "ollama"]


def get_llm_client(
    provider: Provider, model_name: str, temperature: float = 0.7
) -> "BaseChatModel":
    """Factory function to create LLM clients based on provider."""

    if provider == "openai":
        return ChatOpenAI(
            model=model_name,
            api_key=get_openai_key(),
            temperature=temperature,
        )

    elif provider == "anthropic":
        return ChatAnthropic(
            model=model_name,
            anthropic_api_key=get_anthropic_key(),
            temperature=temperature,
        )

    elif provider == "ollama":
        return ChatOllama(
            model=model_name,
            base_url=get_ollama_url(),
            temperature=temperature,
        )

    else:
        raise ValueError(f"Unknown provider: {provider}")


def get_fallback_client(
    provider: Provider, fallback_model: str, temperature: float = 0.7
) -> "BaseChatModel":
    """Get fallback client if primary model fails."""
    return get_llm_client(provider, fallback_model, temperature)
