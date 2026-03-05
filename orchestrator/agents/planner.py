"""
Nó Planner do LangGraph.
Responsável por decompor tarefas em planos executáveis.
"""

import re
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
        model="claude-sonnet-4-5-20250929",
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
    response_text = _coerce_response_text(response.content)
    if not response_text.strip():
        response_text = (
            f"Objetivo: {state['current_task']}\n\n"
            "1. Entender o objetivo\n"
            "2. Definir passos executáveis\n"
            "3. Executar os passos\n"
            "4. Revisar resultados\n"
        )

    # Extrai plan.md e todo.md do response (assumindo que o LLM retorna markdown)
    plan_content = _extract_section(response_text, "plan.md")
    todo_content = _extract_section(response_text, "todo.md")
    decisions_content = _extract_section(response_text, "decisions.md")

    # Fallbacks: evita arquivos vazios quando o modelo não segue o template esperado.
    if not plan_content:
        plan_content = response_text.strip()
    if not todo_content:
        todo_content = _build_fallback_todo(response_text, state["current_task"])
    if not decisions_content:
        decisions_content = "Sem decisões de arquitetura registradas nesta execução."

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


def _coerce_response_text(content: object) -> str:
    """
    Normaliza o conteúdo retornado pelo LLM para texto.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                maybe_text = item.get("text")
                if isinstance(maybe_text, str):
                    parts.append(maybe_text)
            elif hasattr(item, "text"):
                parts.append(str(item.text))
            else:
                parts.append(str(item))
        return "\n".join(parts)
    return str(content)


def _build_fallback_todo(response_text: str, current_task: str) -> str:
    """
    Gera um todo.md mínimo e válido quando não há seção `todo.md` explícita.
    """
    steps: list[str] = []
    for line in response_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        match = re.match(r"^(\d+[\.\)]|-)\s+(.*)$", stripped)
        if not match:
            continue
        step = match.group(2).strip()
        if step and not step.lower().startswith(("objetivo", "premissas", "restrições")):
            steps.append(step)
    if not steps:
        steps = [f"Executar a tarefa: {current_task}"]
    return "\n".join([f"- [ ] {step}" for step in steps[:10]])
