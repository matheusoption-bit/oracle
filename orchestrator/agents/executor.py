"""
Nó Executor do LangGraph.
Executa steps do todo.md usando tools.
"""

from datetime import datetime
from pathlib import Path
import json
import os

from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool

from orchestrator.prompts.system_prompts import get_system_prompt
from orchestrator.state.oracle_state import OracleState
from orchestrator.tools.e2b.sandbox_manager import E2BSandboxManager
from orchestrator.tools.mcp.filesystem_server import MCPFilesystemServer


# Placeholder de tools (implementar depois)
@tool
def mcp_fs_read(path: str) -> str:
    """Lê arquivo do filesystem via MCP."""
    return Path(path).read_text(encoding="utf-8")


@tool
def mcp_fs_write(path: str, content: str) -> str:
    """Escreve arquivo no filesystem via MCP."""
    Path(path).write_text(content, encoding="utf-8")
    return f"Arquivo {path} criado com sucesso"


@tool
def e2b_shell_exec(command: str) -> str:
    """Executa comando shell no sandbox E2B."""
    # Placeholder - implementar com E2B SDK
    return f"Executando: {command}\n[output simulado]"


def executor_node(state: OracleState) -> OracleState:
    """
    Nó que executa o próximo step do todo.md.

    Princípio 2: Logit masking por fase
    Princípio 3: Tool outputs no filesystem
    Princípio 4: Atualiza todo.md a cada step
    Princípio 5: Erros mantidos no estado
    """

    # Lê todo.md
    workspace = Path(state["workspace_path"])
    todo_content = (workspace / "todo.md").read_text(encoding="utf-8")

    # Identifica próximo step não marcado
    next_step = _find_next_unchecked_step(todo_content)

    if not next_step:
        return {**state, "phase": "reviewing"}

    # Tools permitidas na fase EXECUTING
    allowed_tools = ["mcp_fs_read", "mcp_fs_write", "e2b_shell_exec"]
    sandbox = E2BSandboxManager(state["workspace_path"])
    mcp_server = MCPFilesystemServer([state["workspace_path"]])

    @tool
    def mcp_fs_read_real(path: str) -> str:
        """Lê arquivo do filesystem via MCP."""
        return mcp_server.read_file(path)

    @tool
    def mcp_fs_write_real(path: str, content: str) -> str:
        """Escreve arquivo no filesystem via MCP."""
        return mcp_server.write_file(path, content)

    # Criar tool real
    @tool
    def e2b_shell_exec_real(command: str) -> str:
        """Executa comando shell no sandbox E2B."""
        result = sandbox.shell_exec(command)
        return f"Exit code: {result['exit_code']}\nOutput: {result['stdout']}"

    tools = [mcp_fs_read_real, mcp_fs_write_real, e2b_shell_exec_real]

    llm = ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        temperature=0,
        api_key=os.getenv("ANTHROPIC_API_KEY"),
    ).bind_tools(tools)

    system_prompt = get_system_prompt(
        phase="executing",
        allowed_tools=", ".join(allowed_tools),
        next_step=next_step,
    )

    try:
        response = llm.invoke(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Execute: {next_step}"},
            ]
        )

        # Salva tool output no filesystem (Princípio 3)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_path = workspace / "tool_outputs" / f"{timestamp}_executor.json"
        output_path.write_text(
            json.dumps({"step": next_step, "response": response.content}, indent=2),
            encoding="utf-8",
        )

        # Marca step como completo no todo.md (Princípio 4)
        updated_todo = _mark_step_complete(todo_content, next_step)
        (workspace / "todo.md").write_text(updated_todo, encoding="utf-8")

        return {
            **state,
            "todo": updated_todo,
            "tool_output_paths": state["tool_output_paths"] + [str(output_path)],
            "step_count": state["step_count"] + 1,
        }

    except Exception as e:
        # Princípio 5: erros no estado
        error_entry = {
            "step": state["step_count"],
            "tool": "executor",
            "error": str(e),
            "observation": next_step,
        }

        return {
            **state,
            "errors": state["errors"] + [error_entry],
            "step_count": state["step_count"] + 1,
        }


def _find_next_unchecked_step(todo_content: str) -> str:
    """Encontra primeiro step com [ ]."""
    for line in todo_content.split("\n"):
        if line.strip().startswith("- [ ]"):
            return line.replace("- [ ]", "").strip()
    return ""


def _mark_step_complete(todo_content: str, completed_step: str) -> str:
    """Marca step como [x]."""
    lines = []
    for line in todo_content.split("\n"):
        if completed_step in line and "- [ ]" in line:
            lines.append(line.replace("- [ ]", "- [x]"))
        else:
            lines.append(line)
    return "\n".join(lines)
