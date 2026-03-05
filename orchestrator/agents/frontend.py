"""
Agente especializado em geração de frontend.
"""

from pathlib import Path
import os
import subprocess

from langchain_anthropic import ChatAnthropic

from orchestrator.state.oracle_state import OracleState


def frontend_agent_node(state: OracleState) -> OracleState:
    """
    Gera frontend completo do zero.

    Usa SKILL.md como base de conhecimento.
    """

    workspace = Path(state["workspace_path"])
    skill_path = workspace / "skills" / "frontend.md"

    # Lê skill se existir
    skill_content = ""
    if skill_path.exists():
        skill_content = skill_path.read_text(encoding="utf-8")

    llm = ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        temperature=0.3,
        api_key=os.getenv("ANTHROPIC_API_KEY"),
    )

    prompt = f"""Você é um especialista em Next.js.

SKILL CARREGADA:
{skill_content}

TAREFA: {state['current_task']}

PROCESSO:
1. Crie plan.md com lista de componentes
2. Scaffold: npx create-next-app@latest no /workspace/output/frontend
3. Init shadcn
4. Implemente componentes
5. Build e corrija erros (max 3 tentativas)

Retorne o plano em formato markdown.
"""

    response = llm.invoke([{"role": "user", "content": prompt}])

    # Salva plan
    (workspace / "plan.md").write_text(response.content, encoding="utf-8")

    # Executa scaffold (placeholder - implementar com aider)
    output_dir = workspace / "output" / "frontend"
    output_dir.mkdir(parents=True, exist_ok=True)

    # TODO: Chamar aider para gerar código

    return {
        **state,
        "generated_files": state["generated_files"] + [str(output_dir)],
        "step_count": state["step_count"] + 1,
    }
