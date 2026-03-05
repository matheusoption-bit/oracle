"""
Tool para chamar aider.
"""

from pathlib import Path
import subprocess


def aider_edit(
    files: list[str], instruction: str, model: str = "claude-sonnet-4-5-20250929"
) -> str:
    """
    Chama aider para editar arquivos.

    Tool: aider_edit
    """

    cmd = [
        "aider",
        "--model",
        model,
        "--message",
        instruction,
        "--yes",  # Auto-aceita mudanças
        *files,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())

    return f"Exit code: {result.returncode}\n{result.stdout}\n{result.stderr}"
