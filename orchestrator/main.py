"""
Ponto de entrada do orquestrador oracle.
"""

import argparse
from pathlib import Path

import phoenix as px
from phoenix.trace.langchain import LangChainInstrumentor

from orchestrator.graph.oracle_graph import create_oracle_graph
from orchestrator.state.oracle_state import create_initial_state


def main():
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
    px.launch_app()
    LangChainInstrumentor().instrument()
    graph = create_oracle_graph()

    print(f"🚀 Iniciando oracle para: {args.task}")
    print(f"📁 Workspace: {workspace.absolute()}")

    final_state = graph.invoke(initial_state)

    print("\n✅ Execução concluída!")
    print(f"📊 Steps executados: {final_state['step_count']}")
    print(f"📝 Outputs gerados: {len(final_state['generated_files'])}")
    print(f"❌ Erros encontrados: {len(final_state['errors'])}")
    print(f"\n📂 Resultados em: {workspace.absolute()}")


if __name__ == "__main__":
    main()
