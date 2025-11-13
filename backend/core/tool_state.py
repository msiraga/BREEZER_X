"""In-memory manager for pending tool-call conversations."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional
from datetime import datetime, timedelta


class ToolStateManager:
    """Tracks pending tool-call conversations keyed by request ID."""

    def __init__(self, ttl_seconds: int = 600) -> None:
        self._lock = asyncio.Lock()
        self._state: Dict[str, Dict[str, Any]] = {}
        self._ttl = timedelta(seconds=ttl_seconds)

    async def set_state(self, request_id: str, state: Dict[str, Any]) -> None:
        async with self._lock:
            if not state:
                self._state.pop(request_id, None)
                return
            state["updated_at"] = datetime.utcnow().isoformat()
            self._state[request_id] = state

    async def get_state(self, request_id: str) -> Optional[Dict[str, Any]]:
        async with self._lock:
            state = self._state.get(request_id)
            if not state:
                return None

            if self._is_expired(state):
                self._state.pop(request_id, None)
                return None

            return state

    async def pop_state(self, request_id: str) -> Optional[Dict[str, Any]]:
        async with self._lock:
            state = self._state.pop(request_id, None)
            if not state:
                return None

            if self._is_expired(state):
                return None

            return state

    async def clear_state(self, request_id: str) -> None:
        async with self._lock:
            if request_id in self._state:
                del self._state[request_id]

    def _is_expired(self, state: Dict[str, Any]) -> bool:
        timestamp = state.get("updated_at")
        if not timestamp:
            return False

        try:
            updated_at = datetime.fromisoformat(timestamp)
        except (TypeError, ValueError):
            return False

        return datetime.utcnow() - updated_at > self._ttl


# Global instance
tool_state_manager = ToolStateManager()
