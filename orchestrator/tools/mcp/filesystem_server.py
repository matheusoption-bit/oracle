"""
MCP Filesystem Server.
Baseado em modelcontextprotocol/servers/filesystem.
"""

from pathlib import Path
import json


class MCPFilesystemServer:
    """
    Servidor MCP para operações de arquivo.
    Tools: mcp_fs_read, mcp_fs_write, mcp_fs_list, mcp_fs_delete
    """

    def __init__(self, allowed_paths: list[str]):
        self.allowed_paths = [Path(p).resolve() for p in allowed_paths]

    def read_file(self, path: str) -> str:
        """Tool: mcp_fs_read"""
        file_path = Path(path).resolve()
        self._check_allowed(file_path)
        return file_path.read_text(encoding="utf-8")

    def write_file(self, path: str, content: str) -> str:
        """Tool: mcp_fs_write"""
        file_path = Path(path).resolve()
        self._check_allowed(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return f"Arquivo {path} escrito com sucesso"

    def list_directory(self, path: str) -> list[str]:
        """Tool: mcp_fs_list"""
        dir_path = Path(path).resolve()
        self._check_allowed(dir_path)
        return [str(p.relative_to(dir_path)) for p in dir_path.iterdir()]

    def delete_file(self, path: str) -> str:
        """Tool: mcp_fs_delete"""
        file_path = Path(path).resolve()
        self._check_allowed(file_path)
        file_path.unlink()
        return f"Arquivo {path} deletado"

    def _check_allowed(self, path: Path):
        """Verifica se path está nas pastas permitidas."""
        if not any(path.is_relative_to(allowed) for allowed in self.allowed_paths):
            raise PermissionError(f"Acesso negado: {path}")
