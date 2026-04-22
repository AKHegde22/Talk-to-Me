import sys
import multiprocessing


def run_agent(agent_name: str):
    agents = {
        "researcher": "agents.researcher.server:main",
        "writer": "agents.writer.server:main",
        "debater": "agents.debater.server:main",
        "philosopher": "agents.philosopher.server:main",
        "explorer": "agents.explorer.server:main",
    }

    if agent_name not in agents:
        print(f"Unknown agent: {agent_name}")
        print(f"Available: {', '.join(agents.keys())}")
        return

    module_path, func_name = agents[agent_name].split(":")
    import importlib

    module = importlib.import_module(module_path)
    func = getattr(module, func_name)
    func()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m agents <agent_name>")
        print("Agents: researcher, writer, debater, philosopher, explorer")
        print("Or use: python -m agents all")
        sys.exit(1)

    if sys.argv[1] == "all":
        processes = []
        for name in ["researcher", "writer", "debater", "philosopher", "explorer"]:
            p = multiprocessing.Process(target=run_agent, args=(name,))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()
    else:
        run_agent(sys.argv[1])
