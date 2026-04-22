import asyncio
import sys
from typing import Optional

import httpx

from a2a.client import Client


AGENT_PORTS = {
    "researcher": 9991,
    "writer": 9992,
    "debater": 9993,
    "philosopher": 9994,
    "explorer": 9995,
}


class AgentDiscovery:
    def __init__(self):
        self.agents = {}
        self.clients = {}

    async def discover_agent(self, agent_type: str, port: int):
        url = f"http://localhost:{port}"
        async with httpx.AsyncClient() as http_client:
            try:
                client = Client(httpx_client=http_client, base_url=url)
                self.agents[agent_type] = client.agent_card
                self.clients[agent_type] = client
                return client
            except Exception as e:
                print(f"Failed to discover {agent_type} at {url}: {e}")
                return None

    async def discover_all(self):
        tasks = [self.discover_agent(name, port) for name, port in AGENT_PORTS.items()]
        results = await asyncio.gather(*tasks)
        return {k: v for k, v in zip(AGENT_PORTS.keys(), results) if v}

    def list_agents(self):
        print("\n" + "=" * 60)
        print("Available Agents")
        print("=" * 60)
        for name, card in self.agents.items():
            print(f"\n{name.upper()}")
            print(f"  Name: {card.name}")
            print(f"  Description: {card.description}")
            print(f"  Skills:")
            for skill in card.skills or []:
                print(f"    - {skill.name}: {skill.description}")
        print("\n" + "=" * 60)


class ChatSession:
    def __init__(self, client: Client, agent_name: str):
        self.client = client
        self.agent_name = agent_name
        self.session_id = f"chat-{agent_name}"

    async def send_message(self, message: str, stream: bool = False) -> str:
        try:
            if stream:
                return await self._stream_message(message)
            else:
                response = await self.client.send_message(
                    message=message,
                    session_id=self.session_id,
                )
                return (
                    response.message.parts[0].text
                    if response.message.parts
                    else "No response"
                )
        except Exception as e:
            return f"Error: {e}"

    async def _stream_message(self, message: str) -> str:
        full_response = []
        async for event in self.client.send_message_streaming(
            message=message,
            session_id=self.session_id,
        ):
            if event.message and event.message.parts:
                for part in event.message.parts:
                    if hasattr(part, "text"):
                        full_response.append(part.text)
        return "".join(full_response)


class AgentOrchestrator:
    def __init__(self):
        self.discovery = AgentDiscovery()
        self.clients = {}

    async def setup(self):
        self.clients = await self.discovery.discover_all()

    async def consult_agent(
        self, agent_type: str, message: str, context: Optional[str] = None
    ) -> str:
        if agent_type not in self.clients:
            return f"Agent '{agent_type}' not found"

        client = self.clients[agent_type]
        session = ChatSession(client, agent_type)

        if context:
            full_message = f"Context: {context}\n\nQuestion: {message}"
        else:
            full_message = message

        return await session.send_message(full_message)

    async def collaborative_discussion(self, topic: str, agent_types: list):
        results = {}
        for agent_type in agent_types:
            if agent_type in self.clients:
                client = self.clients[agent_type]
                session = ChatSession(client, agent_type)
                response = await session.send_message(f"Let's discuss: {topic}")
                results[agent_type] = response
        return results


class ChatClient:
    def __init__(self):
        self.orchestrator = AgentOrchestrator()
        self.current_session: Optional[ChatSession] = None
        self.current_agent: Optional[str] = None

    async def start(self):
        print("\n" + "=" * 60)
        print("Talk-to-Me: A2A Multi-Agent Chat System")
        print("=" * 60)
        print("\nDiscovering agents...")
        await self.orchestrator.setup()

        if not self.orchestrator.clients:
            print("No agents found! Make sure agent servers are running.")
            return

        print(f"Discovered {len(self.orchestrator.clients)} agents!\n")
        self.show_help()

        await self.main_loop()

    def show_help(self):
        print("\nCommands:")
        print("  /list        - List all available agents")
        print("  /use <name> - Switch to an agent")
        print("  /consult <agent> <message> - Consult another agent")
        print("  /discuss <topic> <agents...> - Multi-agent discussion")
        print("  /help        - Show this help")
        print("  /quit       - Exit the chat")
        print()

    async def main_loop(self):
        while True:
            if self.current_agent:
                prompt = f"[{self.current_agent}] "
            else:
                prompt = "> "

            try:
                user_input = input(prompt).strip()
            except EOFError:
                break

            if not user_input:
                continue

            if user_input.startswith("/"):
                await self.handle_command(user_input)
            elif self.current_session:
                try:
                    response = await self.current_session.send_message(user_input)
                    print(f"\n{self.current_agent}: {response}\n")
                except Exception as e:
                    print(f"\nError: {e}\n")
            else:
                print("Use /use <agent> to select an agent first.")

    async def handle_command(self, command: str):
        parts = command.split()
        cmd = parts[0].lower()

        if cmd == "/list":
            self.orchestrator.discovery.list_agents()

        elif cmd == "/use":
            if len(parts) < 2:
                print("Usage: /use <agent_name>")
                return
            agent_name = parts[1].lower()
            if agent_name in self.orchestrator.clients:
                client = self.orchestrator.clients[agent_name]
                self.current_session = ChatSession(client, agent_name)
                self.current_agent = agent_name
                print(f"Switched to {agent_name}")
            else:
                print(
                    f"Agent '{agent_name}' not found. Use /list to see available agents."
                )

        elif cmd == "/consult":
            if len(parts) < 3:
                print("Usage: /consult <target_agent> <message>")
                return
            target_agent = parts[1].lower()
            message = " ".join(parts[2:])
            if not self.current_agent:
                print("No agent selected. Use /use <agent> first.")
                return
            context = f"You are consulting {target_agent} as the {target_agent} agent."
            try:
                response = await self.orchestrator.consult_agent(
                    target_agent, message, context
                )
                print(f"\n{target_agent}: {response}\n")
            except Exception as e:
                print(f"Error: {e}")

        elif cmd == "/discuss":
            if len(parts) < 3:
                print("Usage: /discuss <topic> <agent1> <agent2> ...")
                return
            topic = parts[1]
            agents = parts[2:]
            try:
                results = await self.orchestrator.collaborative_discussion(
                    topic, agents
                )
                for agent, response in results.items():
                    print(f"\n{agent}: {response}\n")
            except Exception as e:
                print(f"Error: {e}")

        elif cmd == "/help":
            self.show_help()

        elif cmd == "/quit":
            print("Goodbye!")
            sys.exit(0)

        else:
            print(f"Unknown command: {cmd}. Use /help for available commands.")


async def main():
    client = ChatClient()
    await client.start()


if __name__ == "__main__":
    asyncio.run(main())
