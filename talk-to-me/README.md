# Talk-to-Me: A2A Multi-Agent Communication System

A2A-powered multi-agent conversation system where 5 AI agents with distinct personalities can communicate and collaborate.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Talk-to-Me System                       │
│  ┌──────────┐     A2A      ┌──────────┐               │
│  │Researcher│◄────────────►│  Writer  │               │
│  │(GPT-4)   │              │(Claude)  │               │
│  └──────────┘              └──────────┘               │
│        │                         │                         │
│        │    ┌──────────┐       │    ┌──────────┐        │
│        └───►│ Debater  │◄──────└───►│Philosopher│        │
│             │(Claude)  │             │(Ollama)   │        │
│             └──────────┘             └──────────┘        │
│                   │                      │               │
│                   └──────► Explorer ◄────┘               │
│                         (GPT-4o-mini)                      │
└─────────────────────────────────────────────────────────────┘
```

## Agents

| Agent | Personality | Skills | Model |
|-------|-------------|--------|-------|
| **Researcher** | Curious, analytical | Research, analyze, gather info | OpenAI GPT-4 |
| **Writer** | Creative, expressive | Writing, editing, storytelling | Anthropic Claude |
| **Debater** | Critical, persuasive | Debate, argue, persuade | Anthropic Claude |
| **Philosopher** | Deep-thinking, questioning | Philosophize, ethics, critique | Ollama (local) |
| **Explorer** | Adventurous, curious | Explore, brainstorm, discover | OpenAI GPT-4o-mini |

## Prerequisites

- Python 3.10+
- API Keys (see below)

## Installation

```bash
cd talk-to-me
pip install -e .
```

## Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Add your API keys to `.env`:
```
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=sk-ant-your-key
```

3. For Philosopher (Ollama), install and run Ollama:
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3
```

## Running the Agents

### Start Individual Agents

```bash
# Terminal 1: Start Researcher (port 9991)
python -m agents.researcher

# Terminal 2: Start Writer (port 9992)  
python -m agents.writer

# Terminal 3: Start Debater (port 9993)
python -m agents.debater

# Terminal 4: Start Philosopher (port 9994)
python -m agents.philosopher

# Terminal 5: Start Explorer (port 9995)
python -m agents.explorer
```

### Start All Agents

```bash
python -m agents all
```

## Using the Chat Client

Start the chat client:

```bash
python -m client.chat_client
```

### Commands

| Command | Description |
|---------|-------------|
| `/list` | List all available agents |
| `/use <agent>` | Switch to an agent (researcher/writer/debater/philosopher/explorer) |
| `/consult <agent> <message>` | Have current agent consult another |
| `/discuss <topic> <agent1> <agent2> ...` | Have multiple agents discuss a topic |
| `/help` | Show help |
| `/quit` | Exit |

### Example Session

```
> /list
[Shows all available agents]

> /use researcher
[Now talking to Researcher]

> What are the key benefits of renewable energy?
[Researcher responds with analysis]

> /use writer  
[Switching to Writer]

> Can you turn this into a compelling story?
[Writer creates creative content]

> /discuss AI ethics researcher writer debater
[All three agents discuss AI ethics]
```

## Agent-to-Agent Communication

Agents communicate via A2A protocol:

```python
from client.chat_client import AgentOrchestrator

orchestrator = AgentOrchestrator()
await orchestrator.setup()

# Have researcher consult philosopher
response = await orchestrator.consult_agent(
    "philosopher",
    "What is the ethical implications of AGI?",
    context="You are an AI ethics researcher."
)
```

## Project Structure

```
talk-to-me/
├── agents/
│   ├── base.py           # Base executor & LLM factory
│   ├── config.py         # Agent configuration
│   ├── llm_factory.py    # LLM client factory
│   ├── researcher/       # Researcher agent
│   ├── writer/         # Writer agent
│   ├── debater/        # Debater agent
│   ├── philosopher/   # Philosopher agent
│   └── explorer/     # Explorer agent
├── client/
│   └── chat_client.py   # CLI chat client
├── config/
│   └── agents.yaml     # Agent configurations
└── pyproject.toml
```

## License

MIT