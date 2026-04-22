from typing import Any, Dict, List, Union

from a2a.helpers import new_text_artifact, new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import AgentCard, AgentSkill

from agents.config import AgentConfig
from agents.llm_factory import Provider, get_llm_client
from langchain_core.messages import HumanMessage, SystemMessage


class LLMAgentExecutor(AgentExecutor):
    def __init__(self, config: AgentConfig, provider: Provider):
        self.config = config
        self.provider = provider
        self.system_prompt = config.personality

        try:
            self.llm = get_llm_client(provider, config.model_name)
        except Exception:
            if config.fallback_model_name:
                self.llm = get_llm_client(provider, config.fallback_model_name)
            else:
                self.llm = None

        self._message_history: Dict[str, List[Dict[str, str]]] = {}

    def _get_history(self, session_id: str) -> List[Dict[str, str]]:
        if session_id not in self._message_history:
            self._message_history[session_id] = []
        return self._message_history[session_id]

    def _add_to_history(self, session_id: str, role: str, content: str):
        history = self._get_history(session_id)
        history.append({"role": role, "content": content})
        if len(history) > 10:
            history.pop(0)

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        session_id = context.context_id or "default"
        user_input = self._extract_text(context.message)

        self._add_to_history(session_id, "user", user_input)

        response = await self._generate_response(session_id, user_input)

        self._add_to_history(session_id, "assistant", response)

        await event_queue.enqueue_event(
            new_text_artifact(name="response", text=response)
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        await event_queue.enqueue_event(new_text_message(text="Task cancelled."))

    def _extract_text(self, message: Any) -> str:
        if hasattr(message, "parts") and message.parts:
            for part in message.parts:
                if hasattr(part, "text"):
                    return part.text
        if hasattr(message, "text"):
            return message.text
        return str(message)

    async def _generate_response(self, session_id: str, user_input: str) -> str:
        if not self.llm:
            return "LLM not configured."

        history = self._get_history(session_id)

        messages = [SystemMessage(content=self.system_prompt)]
        for msg in history:
            messages.append(HumanMessage(content=msg["content"]))
        messages.append(HumanMessage(content=user_input))

        response = await self.llm.ainvoke(messages)
        return response.content


def create_agent_card(config: AgentConfig) -> AgentCard:
    skills = [
        AgentSkill(id=skill["id"], name=skill["name"], description=skill["description"])
        for skill in config.skills
    ]

    return AgentCard(
        name=config.name,
        description=config.description,
        skills=skills,
    )
