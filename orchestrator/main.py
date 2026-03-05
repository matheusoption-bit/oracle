"""
Ponto de entrada do orquestrador oracle.
"""

import argparse
from pathlib import Path

from openinference.instrumentation.langchain import LangChainInstrumentor
from phoenix.otel import register
from dotenv import load_dotenv

from orchestrator.graph.oracle_graph import create_oracle_graph
from orchestrator.state.oracle_state import create_initial_state


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="oracle orchestrator")
    parser.add_argument("--task", type=str, required=True, help="Task to execute")
    args = parser.parse_args()

    # Cria workspace se não existir
    workspace = Path("workspace")
    workspace.mkdir(exist_ok=True)
    for subdir in ["skills", "memory", "tool_outputs", "output", "logs", "prompts", "index"]:
        (workspace / subdir).mkdir(exist_ok=True)

    # Inicializa estado
    initial_state = create_initial_state(args.task)
    initial_state["workspace_path"] = str(workspace.absolute())

    # Cria e executa grafo
    tracer_provider = register()
    LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
    graph = create_oracle_graph()

    print(f"Starting oracle for: {args.task}")
    print(f"Workspace: {workspace.absolute()}")

    final_state = graph.invoke(initial_state)

    print("\nExecution completed!")
    print(f"Steps executed: {final_state['step_count']}")
    print(f"Outputs generated: {len(final_state['generated_files'])}")
    print(f"Errors found: {len(final_state['errors'])}")
    print(f"\nResults in: {workspace.absolute()}")


if __name__ == "__main__":
    main()
