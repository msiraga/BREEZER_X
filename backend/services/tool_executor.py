"""Backend tool execution services with safety guards."""

from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.config import settings


class ToolExecutionError(Exception):
    """Raised when a tool execution request is invalid or fails."""


class ToolExecutionService:
    """Executes workspace-scoped tools with safety checks."""

    def __init__(self, workspace_path: str) -> None:
        base = settings.TOOL_FILE_ROOT or workspace_path
        if not base:
            raise ToolExecutionError("Workspace path is required")
        self.workspace_root = Path(base).resolve()
        if not self.workspace_root.exists():
            raise ToolExecutionError("Workspace root does not exist")

    def _resolve_path(self, relative: str) -> Path:
        candidate = (self.workspace_root / relative).resolve()
        if not str(candidate).startswith(str(self.workspace_root)):
            raise ToolExecutionError("Path escapes workspace root")
        return candidate

    def file_read(self, path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        target = self._resolve_path(path)
        if not target.is_file():
            raise ToolExecutionError("File not found")
        size = target.stat().st_size
        if size > settings.TOOL_MAX_FILE_SIZE_BYTES:
            raise ToolExecutionError("File exceeds maximum readable size")
        content = target.read_text(encoding=encoding)
        return {"path": str(target.relative_to(self.workspace_root)), "content": content}

    def file_write(
        self,
        path: str,
        content: str,
        mode: str = "overwrite",
        confirm: Optional[bool] = None,
        encoding: str = "utf-8"
    ) -> Dict[str, Any]:
        if settings.TOOL_REQUIRE_CONFIRMATION and not confirm:
            raise ToolExecutionError("Write operation requires user confirmation")
        target = self._resolve_path(path)
        if target.exists() and target.stat().st_size > settings.TOOL_MAX_FILE_SIZE_BYTES:
            raise ToolExecutionError("Target file exceeds maximum allowable size")
        target.parent.mkdir(parents=True, exist_ok=True)
        if mode == "append" and target.exists():
            target.write_text(target.read_text(encoding=encoding) + content, encoding=encoding)
        else:
            target.write_text(content, encoding=encoding)
        return {"path": str(target.relative_to(self.workspace_root)), "written_bytes": len(content)}

    def file_list(self, path: str, max_entries: int = 50) -> Dict[str, Any]:
        max_entries = max(1, min(max_entries, 500))
        target = self._resolve_path(path)
        if not target.exists():
            raise ToolExecutionError("Directory not found")
        if not target.is_dir():
            raise ToolExecutionError("Path is not a directory")
        entries: List[Dict[str, Any]] = []
        for idx, child in enumerate(target.iterdir()):
            if idx >= max_entries:
                break
            entries.append({
                "name": child.name,
                "is_dir": child.is_dir(),
                "size": None if child.is_dir() else child.stat().st_size
            })
        return {"path": str(target.relative_to(self.workspace_root)), "entries": entries}

    def git_status(self, detailed: bool = False) -> Dict[str, Any]:
        cmd = ["git", "status"]
        if detailed:
            cmd.extend(["--porcelain", "-b"])
        return self._run_command(cmd)

    def git_diff(self, path: Optional[str] = None, staged: bool = False) -> Dict[str, Any]:
        cmd = ["git", "diff"]
        if staged:
            cmd.append("--cached")
        if path:
            cmd.append(path)
        return self._run_command(cmd)

    def terminal_command(self, command: str) -> Dict[str, Any]:
        whitelist = settings.TOOL_TERMINAL_WHITELIST
        command_map = settings.TOOL_TERMINAL_COMMAND_MAP
        if command not in whitelist:
            raise ToolExecutionError("Command not permitted")
        mapped = command_map.get(command)
        if not mapped:
            raise ToolExecutionError("Command mapping missing")
        cmd = shlex.split(mapped)
        return self._run_command(cmd, timeout=120)

    def web_lookup(self, query: str) -> Dict[str, Any]:
        if not settings.TOOL_WEB_LOOKUP_ENABLED:
            raise ToolExecutionError("Web lookup is disabled")
        # Placeholder implementation. Integration point for approved providers.
        return {"query": query, "results": []}

    def workspace_diagnostics(self, limit: int = 50) -> Dict[str, Any]:
        # Placeholder until LSP integration is available.
        raise ToolExecutionError("Workspace diagnostics not yet implemented")

    def _run_command(self, cmd: List[str], timeout: int = 60) -> Dict[str, Any]:
        try:
            completed = subprocess.run(
                cmd,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
        except FileNotFoundError as exc:
            raise ToolExecutionError("Command executable not found") from exc
        except subprocess.TimeoutExpired as exc:
            raise ToolExecutionError("Command timed out") from exc
        return {
            "command": " ".join(cmd),
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr
        }

    def execute(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if not hasattr(self, name):
            raise ToolExecutionError("Unknown tool")
        method = getattr(self, name)
        if not callable(method):
            raise ToolExecutionError("Invalid tool handler")
        return method(**arguments)
