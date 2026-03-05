"""
Estado central do oracle.
Implementa princípios de Context Engineering do Manus.
"""

from typing import Annotated, Literal, Sequence, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
import json
from datetime import datetime


class OracleState(TypedDict):
    """
    Estado principal do grafo LangGraph.

    REGRAS DE CONTEXT ENGINEERING:
    1. Serialização SEMPRE determinística (sort_keys=True)
    2. Append-only: nunca modificar histórico
    3. Tool outputs NUNCA vão aqui (vão para filesystem)
    """

    # Conversação
    messages: Annotated[Sequence[BaseMessage], add_messages]

    # Planejamento
    plan: str  # Conteúdo do plan.md
    todo: str  # Conteúdo do todo.md (atualizado a cada step)
    decisions: str  # Decisões de arquitetura

    # Fase atual (para logit masking)
    phase: Literal["planning", "executing", "reviewing", "deploying"]

    # Contexto
    current_task: str
    workspace_path: str  # Sempre /workspace/

    # Memória
    repo_map: str  # Resumo da estrutura do repo
    skills_loaded: list[str]  # Ex: ["frontend", "backend", "rag"]

    # Outputs (PATHS, não conteúdo)
    tool_output_paths: list[str]  # Ex: ["/workspace/tool_outputs/2026-03-05_12-30-45_shell_exec.json"]
    generated_files: list[str]  # Ex: ["/workspace/output/frontend/page.tsx"]

    # Erros (MANTER no contexto - Princípio 5)
    errors: list[dict]  # {"step": 3, "tool": "shell_exec", "error": "...", "observation": "..."}

    # Controle
    step_count: int
    max_steps: int
    human_approval_required: bool

    # KV-Cache optimization
    system_prompt_prefix: str  # Prefixo ESTÁVEL (sem timestamp)
    last_cache_breakpoint: str  # Última posição de cache


def serialize_state(state: OracleState) -> str:
    """
    Serializa estado de forma DETERMINÍSTICA.
    Princípio 1: KV-Cache precisa de JSON idêntico.
    """
    return json.dumps(state, sort_keys=True, ensure_ascii=False, indent=2)


def create_initial_state(task: str) -> OracleState:
    """
    Cria estado inicial com prefixo estável.
    """
    return OracleState(
        messages=[],
        plan="",
        todo="",
        decisions="",
        phase="planning",
        current_task=task,
        workspace_path="/workspace/",
        repo_map="",
        skills_loaded=[],
        tool_output_paths=[],
        generated_files=[],
        errors=[],
        step_count=0,
        max_steps=50,
        human_approval_required=False,
        system_prompt_prefix=_create_stable_prefix(),
        last_cache_breakpoint="",
    )


def _create_stable_prefix() -> str:
    """
    Prefixo do system prompt SEM timestamps.
    Princípio 1: precisa ser IDÊNTICO entre chamadas.
    """
    return """Você é o oracle, um agente autônomo de desenvolvimento.

REGRAS ABSOLUTAS:
1. Tool outputs vão para /workspace/tool_outputs/, NUNCA no contexto
2. Reescreva /workspace/todo.md a cada step
3. Erros permanecem no contexto - nunca os remova
4. JSON sempre com keys ordenadas
5. Nunca modifique histórico de actions/observations

FASE ATUAL: {phase}
WORKSPACE: /workspace/
"""
