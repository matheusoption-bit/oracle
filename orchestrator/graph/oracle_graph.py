"""
Grafo principal do oracle.
Define fluxo: planner → executor → reviewer.
"""

from langgraph.graph import END, StateGraph

from orchestrator.agents.executor import executor_node
from orchestrator.agents.planner import planner_node
from orchestrator.agents.reviewer import reviewer_node
from orchestrator.state.oracle_state import OracleState, create_initial_state


def create_oracle_graph():
    """
    Cria o grafo de estados do oracle.

    Fluxo:
    START → planner → executor → reviewer → END
           └─────────────┬───────────┘
                   (loop se reprovar)
    """

    workflow = StateGraph(OracleState)

    # Adicionar nós
    workflow.add_node("planner", planner_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("reviewer", reviewer_node)

    # Definir edges
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "executor")

    # Executor pode ir para reviewer OU continuar (se mais steps)
    workflow.add_conditional_edges(
        "executor",
        _should_continue_executing,
        {"continue": "executor", "review": "reviewer"},
    )

    # Reviewer pode aprovar (END) ou reprovar (volta pro executor)
    workflow.add_conditional_edges(
        "reviewer",
        _should_deploy,
        {"deploy": END, "retry": "executor"},
    )

    return workflow.compile()


def _should_continue_executing(state: OracleState) -> str:
    """Decide se executor deve continuar ou ir para review."""
    if state["phase"] == "reviewing":
        return "review"
    if state["step_count"] >= state["max_steps"]:
        return "review"
    return "continue"


def _should_deploy(state: OracleState) -> str:
    """Decide se reviewer aprovou ou reprovou."""
    if state["phase"] == "deploying":
        return "deploy"
    return "retry"
