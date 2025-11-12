# Agent Execution Flow: Weather UI Request

This guide explains what happens in *agent mode* when a user asks the system:

> "Create a project of a weather website UI using a free weather API. A user enters the name of a city and the output is the weather conditions live in that city."

The goal is to demystify how the orchestration pipeline, agents, and local LLM work together to fulfill the request.

---

## 1. Entry Point (IDE → Backend API)
1. The user types the prompt inside the Breezer IDE agent panel.
2. The IDE POSTs the request to the backend endpoint `POST /api/agent/query` with a payload shaped like [`AgentRequest` in @backend/api/routes/agent.py#18-27](../../backend/api/routes/agent.py#18-27).
3. FastAPI validates the payload and constructs an `AgentContext`, bundling:
   - `workspace_path` (typically `/app` inside the container)
   - Current/open files (if any)
   - User prompt text
   - Any additional metadata

## 2. Orchestrator Routing
1. The API calls `orchestrator.process_request(context)` (@backend/api/routes/agent.py#64-66).
2. Inside `AgentOrchestrator.process_request` (@backend/agents/orchestrator.py#49-95), the system classifies the query via `_classify_request` (@backend/agents/orchestrator.py#97-144):
   - It scans the lowercased prompt for keywords. "Create" and "project" map to `RequestType.IMPLEMENT`.
3. The orchestrator routes the context to the **Implementation Agent** (`self.agents["implementation"].process(context)`).

### Why only the Implementation Agent?
- The prompt is about building a new feature/UI.
- No hints trigger review, debug, or documentation paths.
- Other requests ("review", "debug", "explain") would dynamically select different agents using the same keyword heuristic.

## 3. Implementation Agent Workflow
1. `ImplementationAgent.process` (@backend/agents/implementation.py#43-85) starts by searching for related snippets in Qdrant using `search_code` (@backend/agents/implementation.py#87-98).
   - This provides contextual examples from the workspace (if indexed) to inform generation.
2. The agent builds a prompt for the LLM:
   - **System message**: a role definition enumerating implementation responsibilities (@backend/agents/implementation.py#19-41).
   - **User message**: formatted context + related code + instruction to deliver a complete implementation (@backend/agents/implementation.py#102-114).
3. Calls `self.get_completion(...)` to obtain LLM output (@backend/agents/base.py#55-79).

## 4. LLM Routing & Local Model
1. `BaseAgent.get_completion` delegates to the global `llm_router.complete` (@backend/core/llm_router.py#34-128).
2. `LLMRouter` maps `AgentType.IMPLEMENTATION` to `settings.MODEL_IMPLEMENTATION` (@backend/core/llm_router.py#37-50).
   - Env defaults: DeepSeek models for primary tasks, fallback `llamafile/mistral-7b-instruct` (@backend/core/config.py#31-42).
3. Because `LLAMAFILE_ENABLED=true` and `MODEL_FALLBACK` references `llamafile`, the router passes `api_base=http://llamafile:8080` to LiteLLM (@backend/core/llm_router.py#90-99).
4. LiteLLM performs an OpenAI-compatible request to the local llama.cpp HTTP server (docker service `breezer-llamafile`).
   - The server is the llama.cpp build described in @llama_server/Dockerfile.llamafile#1-25.
   - It loads `mistral.gguf` and exposes `/v1/chat/completions` (confirmed via README instructions).
5. The server generates code/content tailored to the weather UI prompt and returns it through LiteLLM → router → agent.

## 5. Agent Response Packaging
1. The Implementation Agent extracts markdown code blocks from the response (@backend/agents/implementation.py#116-128).
2. It constructs `AgentResponse` with:
   - `content`: full natural-language and code output from the LLM
   - `metadata`: counts for code blocks & related examples used
   - `actions`: structured suggestions (`create_file`, `edit_file`) for the IDE to apply (@backend/agents/implementation.py#130-145)
3. The agent logs the interaction for telemetry/debugging.
4. The orchestrator returns the `AgentResponse` back to the API handler.

## 6. HTTP Response to Client
1. `/api/agent/query` wraps the agent result inside `AgentResponseModel` (@backend/api/routes/agent.py#67-74).
2. The IDE receives JSON similar to:
   ```json
   {
     "request_id": "uuid",
     "success": true,
     "content": "...markdown...",
     "metadata": {"code_blocks": 2, "related_examples": 0},
     "actions": [
       {"type": "create_file", "language": "python", "code": "..."}
     ],
     "confidence": 0.9
   }
   ```
3. The UI renders the natural-language explanation and exposes the `actions` (e.g., buttons to create files or apply code).

---

## Sequence Overview
```
User Prompt
  ↓
IDE POST /api/agent/query
  ↓
FastAPI ⇒ AgentOrchestrator
  ↓ (classify: IMPLEMENT)
Implementation Agent
  ↓ (vector search + prompt building)
LLMRouter (LiteLLM)
  ↓ (api_base=http://llamafile:8080)
Local llama.cpp (Mistral 7B)
  ↓
Agent parses response → actions/metadata
  ↓
Orchestrator returns AgentResponse
  ↓
API sends AgentResponseModel → IDE
```

---

## Key Components to Know
| Component | File(s) | Purpose |
|-----------|---------|---------|
| API Route | @backend/api/routes/agent.py#39-118 | Accepts agent requests & returns results |
| Orchestrator | @backend/agents/orchestrator.py#33-171 | Classifies prompt, selects agent |
| Implementation Agent | @backend/agents/implementation.py#13-146 | Generates feature code |
| LLM Router | @backend/core/llm_router.py#34-194 | Maps agent types to models, injects llama.cpp base URL |
| Local LLM Dockerfile | @llama_server/Dockerfile.llamafile#1-25 | Builds llama.cpp server with mistral.gguf |
| README Ops | @documentation/operations/README.md#149-163 | Commands to rebuild & test the service |

---

## FAQ
**Q: Are multiple agents ever involved automatically?**  
Not for this prompt. The orchestrator picks exactly one agent whose request type best matches. However, other keywords like "review" or "debug" would choose different agents. Future enhancements could chain agents via `process_multi_agent` (@backend/agents/orchestrator.py#146-171).

**Q: How do actions become file changes?**  
The IDE interprets `actions` from the response. For example, a `create_file` action includes `language` and `code`, which the UI can present as an "Apply" button.

**Q: What if the local LLM is offline?**  
`LLMRouter` would try the configured fallback. If llamafile is unreachable, errors propagate back through the agent response and the API returns an HTTP 500.

---

## Testing the Flow Manually
1. **Backend query**
   ```powershell
   $body = @{ query = "Create a project of a weather website UI using a free weather API"; workspace_path = "/app" } | ConvertTo-Json
   Invoke-RestMethod -Uri "http://localhost:8000/api/agent/query" -Method Post -ContentType "application/json" -Body $body
   ```
2. **Verify llama.cpp logs**
   ```powershell
   docker-compose logs -f llamafile
   ```
3. **Confirm model availability**
   ```powershell
   docker-compose exec backend python -c "import requests; print(requests.get('http://llamafile:8080/v1/models').json())"
   ```

This walk-through should make it clear how Breezer’s agent mode orchestrates the request from the UI down to LLM execution and back.
