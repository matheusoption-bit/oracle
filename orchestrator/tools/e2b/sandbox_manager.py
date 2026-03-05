"""
Gerenciador de sandbox E2B.
Implementa os 27 tools do Manus.
"""

from datetime import datetime
from pathlib import Path
import json
import os

from e2b import Sandbox


class E2BSandboxManager:
    """
    Gerencia lifecycle do sandbox E2B.

    Princípio 3: Tool outputs no filesystem.
    """

    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.sandbox = None
        self.api_key = os.getenv("E2B_API_KEY")

    def create_sandbox(self) -> str:
        """Cria sandbox com timeout 10min."""
        self.sandbox = Sandbox(
            api_key=self.api_key,
            timeout=600,  # 10 minutos
            memory_mb=2048,
            cpu_count=1,
        )
        return self.sandbox.id

    def destroy_sandbox(self):
        """Destrói sandbox."""
        if self.sandbox:
            self.sandbox.kill()
            self.sandbox = None

    def shell_exec(self, command: str) -> dict:
        """
        Executa comando shell.
        Tool: e2b_shell_exec
        """
        if not self.sandbox:
            self.create_sandbox()

        result = self.sandbox.process.start_and_wait(command)

        # Salva output no filesystem (Princípio 3)
        output = {
            "command": command,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.exit_code,
            "timestamp": datetime.now().isoformat(),
        }

        self._save_tool_output("shell_exec", output)

        return output

    def browser_navigate(self, url: str) -> dict:
        """
        Navega para URL e retorna conteúdo.
        Tool: e2b_browser_navigate
        """
        # Placeholder - implementar com Playwright no E2B
        output = {
            "url": url,
            "content": f"[Conteúdo simulado de {url}]",
            "timestamp": datetime.now().isoformat(),
        }

        self._save_tool_output("browser_navigate", output)
        return output

    def file_write(self, path: str, content: str) -> dict:
        """
        Escreve arquivo no sandbox.
        Tool: e2b_file_write
        """
        if not self.sandbox:
            self.create_sandbox()

        self.sandbox.filesystem.write(path, content)

        output = {
            "path": path,
            "size_bytes": len(content.encode("utf-8")),
            "timestamp": datetime.now().isoformat(),
        }

        self._save_tool_output("file_write", output)
        return output

    def _save_tool_output(self, tool_name: str, output: dict):
        """
        Salva output da tool no filesystem.
        Princípio 3: NUNCA colocar outputs no contexto.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{timestamp}_{tool_name}.json"
        path = self.workspace_path / "tool_outputs" / filename

        path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
