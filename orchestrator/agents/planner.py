"""
Nó Planner do LangGraph.
Responsável por decompor tarefas em planos executáveis.
"""

from pathlib import Path
import os

from langchain_anthropic import ChatAnthropic

from orchestrator.prompts.system_prompts import get_system_prompt
from orchestrator.state.oracle_state import OracleState


def planner_node(state: OracleState) -> OracleState:
    """
    Nó que cria o plano inicial.

    Princípio 4: Recitação - cria todo.md
    Princípio 3: Filesystem-as-context - salva plan.md
    """

    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        temperature=0.1,
        api_key=os.getenv("ANTHROPIC_API_KEY"),
    )

    # System prompt estável
    system_prompt = get_system_prompt(phase="planning", current_task=state["current_task"])

    # Chama LLM
    response = llm.invoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Crie um plano para: {state['current_task']}"},
        ]
    )

    # Extrai plan.md e todo.md do response (assumindo que o LLM retorna markdown)
    plan_content = _extract_section(response.content, "plan.md")
    todo_content = _extract_section(response.content, "todo.md")
    decisions_content = _extract_section(response.content, "decisions.md")

    # Salva no filesystem (Princípio 3)
    workspace = Path(state["workspace_path"])
    (workspace / "plan.md").write_text(plan_content, encoding="utf-8")
    (workspace / "todo.md").write_text(todo_content, encoding="utf-8")
    (workspace / "decisions.md").write_text(decisions_content, encoding="utf-8")

    # Atualiza estado (append-only)
    return {
        **state,
        "plan": plan_content,
        "todo": todo_content,
        "decisions": decisions_content,
        "phase": "executing",
        "step_count": state["step_count"] + 1,
    }


def _extract_section(content: str, filename: str) -> str:
    """
    Extrai seção do markdown retornado pelo LLM.
    """
    lines = content.split("\n")
    capturing = False
    section = []

    for line in lines:
        if line.strip().startswith(f"## {filename}") or line.strip().startswith(f"# {filename}"):
            capturing = True
            continue
        if capturing:
            if line.strip().startswith("##") or line.strip().startswith("#"):
                break
            section.append(line)

    return "\n".join(section).strip()
