# Tooling Platform Rollout Plan

This document captures the phased plan for delivering a full tooling platform across the backend and UI.

## Phase 1 – Backend Foundation

1. **Tool-call schema in `AgentResponse`**  
   - Add `tool_calls` (array of OpenAI-style function calls) and `requires_tool` flags to `AgentResponse`.  
   - Each entry carries: `id`, `function.name`, `function.arguments` (JSON string), and optional `status`.
2. **LLMRouter support for function calling**  
   - Switch completion requests to use the OpenAI-compatible schema (`functions` + `function_call`).  
   - Normalize responses from providers, ensuring we can surface pending tool calls and continue the conversation after tool execution.
3. **Tool-result callback endpoint**  
   - Introduce `POST /agent/tool-result` that accepts `{ request_id, call_id, output }`.  
   - Orchestrator stores pending tool calls, resumes the associated agent pipeline when results arrive.
4. **State management**  
   - Persist pending tool calls (in-memory map to start; later Redis).  
   - Include timeout/cleanup logic to avoid orphaned tool requests.

## Phase 2 – Minimal UI Loop

1. **Tool Shelf (MVP)**  
   - Sidebar card with File Ops + Git tools.  
   - Trigger simple read/write or `git status` actions.
2. **Command Palette hooks**  
   - Register commands (`Breezer: File Ops`, `Breezer: Git Tools`) that open the Tool Shelf panel.  
   - Allow power users to launch tool dialogs quickly.
3. **Chat tool mentions**  
   - Support `@file.read` / `@git.status` syntax that raises a confirmation modal and calls the backend tool endpoint.  
   - Stream tool results back into the chat transcript.
4. **Backend ↔ UI wiring**  
   - The extension calls `/agent/tool-result` as soon as a tool finishes, letting the agent continue.

## Phase 3 – Feature Build-out

1. **Tool Shelf expansion**  
   - Add Terminal Runner (whitelisted commands), Web Lookup, Diagnostics & Symbols.  
   - Provide inline descriptions and confirmation flows.
2. **Advanced tabs in webview**  
   - Streaming toggle + indicator.  
   - Context manager (active mentions/resources).  
   - Template gallery (common workflows).  
   - Performance dashboard (latency, token counts, success rates).  
   - MCP connections panel (list servers, reconnect/manage).
3. **All Tools modal**  
   - Summarize capabilities, quick actions, and inline help/tooltips.
4. **Attachment ingestion**  
   - Drag-and-drop zone for images and other file types; surface them as tool calls or context items.

## Phase 4 – Polish & Telemetry

1. **Inline execution feedback**  
   - Success/error states, retries, and step traces in the UI.  
2. **Saved presets and history**  
   - Persist frequently used commands/templates per workspace.  
3. **Metrics & auditing**  
   - Log tool usage, confirmations, denials, and command outputs (with redaction where needed).  
   - Surface aggregated insights in the performance dashboard.
4. **Security hardening**  
   - Periodic review of whitelists, sandbox configurations, and permission scopes.  
   - Alerts for suspicious tool usage or repeated failures.

---

This roadmap should be revisited after completing each phase to incorporate lessons learned and shifting priorities.

Here’s the sequencing I’d recommend from a purely engineering perspective:

Baseline functionality (done) – finish the non-streaming tool-call support and callback endpoint.
Frontend wiring (current focus) – hook the UI to the new tool APIs (Tool Shelf, palette commands, chat workflow) so we have end-to-end functionality.
Streaming upgrade – once the UI can execute tools reliably, extend the SSE generator to emit event: tool_call blocks and update the client to react to them. Implement queueing, pausing, and resuming logic with good telemetry.
Polish & guardrails – add tests, timeout handling, and broader provider support, then refine the UX (status indicators, retries, audit logging).
