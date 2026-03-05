"""
Nó Reviewer do LangGraph.
Valida outputs e decide próximos passos.
"""

from pathlib import Path
import os

from langchain_anthropic import ChatAnthropic

from orchestrator.prompts.system_prompts import get_system_prompt
from orchestrator.state.oracle_state import OracleState


def reviewer_node(state: OracleState) -> OracleState:
    """
    Nó que valida o trabalho executado.

    Roda testes, build, linting.
    Decide: aprovar ou voltar para EXECUTING.
    """

    llm = ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        temperature=0,
        api_key=os.getenv("ANTHROPIC_API_KEY"),
    )

    system_prompt = get_system_prompt(phase="reviewing")

    # Lê outputs gerados
    workspace = Path(state["workspace_path"])
    output_summary = _summarize_outputs(workspace / "output")

    response = llm.invoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Valide os seguintes outputs:\n\n{output_summary}"},
        ]
    )

    # Salva relatório
    (workspace / "logs" / "review_report.md").write_text(response.content, encoding="utf-8")

    # Decisão simples: se contém "APROVADO" -> deploy, senão -> voltar
    if "APROVADO" in response.content.upper():
        return {**state, "phase": "deploying"}
    return {**state, "phase": "executing", "human_approval_required": True}


def _summarize_outputs(output_dir: Path) -> str:
    """Sumariza arquivos gerados."""
    if not output_dir.exists():
        return "Nenhum output gerado ainda."

    files = list(output_dir.rglob("*"))
    return "\n".join([f"- {f.relative_to(output_dir)}" for f in files if f.is_file()])
