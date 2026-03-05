"""
Registro central de tools.
Implementa naming com prefixos para logit masking.
"""

TOOL_PERMISSIONS = {
    "planning": [
        "mcp_fs_read",
        "mcp_fs_write",
        "mcp_fs_list",
    ],
    "executing": [
        "mcp_fs_read",
        "mcp_fs_write",
        "e2b_shell_exec",
        "e2b_browser_navigate",
        "e2b_file_write",
        "aider_edit",
    ],
    "reviewing": [
        "mcp_fs_read",
        "e2b_shell_exec",  # Apenas leitura
    ],
    "deploying": ["e2b_shell_exec"],
}


def get_allowed_tools(phase: str) -> list[str]:
    """
    Retorna tools permitidas para a fase.
    Usado para logit masking (Princípio 2).
    """
    return TOOL_PERMISSIONS.get(phase, [])


def get_tool_prefix(phase: str) -> str:
    """
    Retorna prefixo para response prefill.
    Força modelo a chamar tools do grupo correto.
    """
    if phase == "planning":
        return '{"name": "mcp_fs_'
    if phase == "executing":
        return '{"name": "'  # Qualquer tool
    if phase == "reviewing":
        return '{"name": "mcp_fs_'
    return '{"name": "'
