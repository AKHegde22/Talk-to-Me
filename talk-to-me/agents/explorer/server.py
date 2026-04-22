import uvicorn
from starlette.applications import Starlette

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill

from agents.base import LLMAgentExecutor
from agents.config import load_agent_config


def main():
    config = load_agent_config("explorer")
    executor = LLMAgentExecutor(config, "openai")

    skills = [
        AgentSkill(
            id=skill["id"],
            name=skill["name"],
            description=skill["description"],
            tags=["explorer", skill["id"]],
            examples=[f"{skill['id']} example"],
        )
        for skill in config.skills
    ]

    agent_card = AgentCard(
        name=config.name,
        description=config.description,
        version="1.0.0",
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        capabilities=AgentCapabilities(streaming=True),
        supported_interfaces=[
            AgentInterface(
                protocol_binding="JSONRPC", url=f"http://localhost:{config.port}"
            )
        ],
        skills=skills,
    )

    request_handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )

    routes = []
    routes.extend(create_agent_card_routes(agent_card))
    routes.extend(create_jsonrpc_routes(request_handler, "/"))

    app = Starlette(routes=routes)
    uvicorn.run(app, host="0.0.0.0", port=config.port)


if __name__ == "__main__":
    main()
