# BREEZER Chat Implementation Strategy

**Project:** BREEZER IDE by RICHDALE AI  
**Purpose:** AI Chat Interface Integration  
**Target Audience:** Software Engineering Team  
**Date:** November 9, 2025  
**Status:** Planning & Design Phase

---

## Executive Summary

This document outlines two strategic approaches for implementing AI chat functionality in BREEZER IDE. Both leverage our existing multi-agent backend (FastAPI + 9 specialized agents) while differentiating in integration depth and timeline.

**Key Decision Points:**
- **Option 1 (Extension):** 2-4 weeks, bundle with IDE, easier maintenance
- **Option 2 (Core Integration):** 2-3 months, deeper integration, matches Cursor/Windsurf architecture

**Recommendation:** Start with Option 1, migrate to Option 2 in v2.0

---

## Background & Market Context

### Competitive Landscape

**Cursor IDE:**
- VS Code fork with native AI chat (Cmd+L for sidebar, Cmd+K for inline)
- $20/month Pro plan
- Routes to OpenAI, Anthropic APIs
- 500+ fast requests/month

**Windsurf IDE (by Codeium):**
- VS Code fork with "Cascade" chat panel (Ctrl+L)
- $15/month Pro plan
- Proprietary context engine + Write Mode (real-time file updates)
- Deep codebase awareness via AST parsing

**Key Insight:** Both are **VS Code forks with chat built into core**, not extensions. However, both started simpler and evolved deeper integration over time.

### BREEZER's Advantages

Our differentiation:
- ✅ **9 specialized agents** (vs their general-purpose models)
- ✅ **Local LLM option** (Mistral 7B via Llamafile - free tier)
- ✅ **Data sovereignty** (all data stays on-premises)
- ✅ **Existing backend** (FastAPI already built and tested)

**We don't need to copy their UI** - we need to showcase our multi-agent orchestration.

---

## Option 1: VS Code Extension (Bundled)

### Overview

Build BREEZER Chat as a standard VS Code extension, then bundle it with the IDE during the build process. Users get it out-of-the-box without manual installation.

### Architecture

```
BREEZER Chat Extension
├── Extension Host (TypeScript - runs in Node.js)
│   ├── extension.ts              # Activation & command registration
│   ├── chatPanel.ts              # Webview panel manager
│   ├── api/
│   │   ├── agentClient.ts        # FastAPI backend client
│   │   └── contextGatherer.ts    # Collect file/selection context
│   └── commands/
│       ├── openChat.ts           # Ctrl+Shift+B
│       └── inlineAssist.ts       # Quick code edits
│
├── Webview UI (React + TypeScript)
│   ├── src/
│   │   ├── App.tsx               # Main chat interface
│   │   ├── components/
│   │   │   ├── ChatMessage.tsx   # Message bubble
│   │   │   ├── AgentSelector.tsx # Choose which agent
│   │   │   ├── CodeBlock.tsx     # Syntax-highlighted responses
│   │   │   └── ContextPanel.tsx  # Show gathered context
│   │   └── hooks/
│   │       ├── useChat.ts        # Chat state management
│   │       └── useAgent.ts       # Agent API calls
│   └── webview.html              # Entry point
│
└── Build Output
    └── breezer-chat-1.0.0.vsix   # Packaged extension
```

### Key Components

#### 1. Extension Activation (`extension.ts`)

```typescript
import * as vscode from 'vscode';
import { BreezerChatPanel } from './chatPanel';

export function activate(context: vscode.ExtensionContext) {
  // Register main chat command (Ctrl+Shift+B)
  const openChat = vscode.commands.registerCommand(
    'breezer.openChat',
    () => BreezerChatPanel.createOrShow(context.extensionUri)
  );

  // Register inline assist (Ctrl+K)
  const inlineAssist = vscode.commands.registerCommand(
    'breezer.inlineAssist',
    async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) return;
      
      const selection = editor.document.getText(editor.selection);
      // Send to agent, show quick fixes
    }
  );

  context.subscriptions.push(openChat, inlineAssist);
}
```

#### 2. Chat Panel Manager (`chatPanel.ts`)

```typescript
export class BreezerChatPanel {
  private readonly _panel: vscode.WebviewPanel;
  private _disposables: vscode.Disposable[] = [];

  public static createOrShow(extensionUri: vscode.Uri) {
    const panel = vscode.window.createWebviewPanel(
      'breezerChat',
      'BREEZER AI',
      vscode.ViewColumn.Two,
      {
        enableScripts: true,
        retainContextWhenHidden: true,
        localResourceRoots: [extensionUri]
      }
    );

    return new BreezerChatPanel(panel, extensionUri);
  }

  private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
    this._panel = panel;
    this._panel.webview.html = this._getWebviewContent();

    // Handle messages from webview
    this._panel.webview.onDidReceiveMessage(
      async (message) => {
        switch (message.type) {
          case 'sendPrompt':
            await this._handlePrompt(message.prompt, message.agent);
            break;
          case 'applyCode':
            await this._applyCodeChange(message.code, message.file);
            break;
        }
      },
      null,
      this._disposables
    );
  }

  private async _handlePrompt(prompt: string, agent: string) {
    // Gather context
    const context = await this._gatherContext();
    
    // Call FastAPI backend
    const response = await fetch('http://localhost:8000/api/agent/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt,
        agent,
        context: {
          activeFile: context.activeFile,
          selection: context.selection,
          workspace: context.workspace
        }
      })
    });

    const data = await response.json();
    
    // Send back to webview
    this._panel.webview.postMessage({
      type: 'agentResponse',
      response: data.response,
      agent: data.agent,
      suggestions: data.code_suggestions
    });
  }

  private async _gatherContext() {
    const editor = vscode.window.activeTextEditor;
    return {
      activeFile: editor?.document.fileName,
      selection: editor?.document.getText(editor.selection),
      language: editor?.document.languageId,
      workspace: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath
    };
  }
}
```

#### 3. React Chat UI (`App.tsx`)

```typescript
import React, { useState } from 'react';
import { ChatMessage } from './components/ChatMessage';
import { AgentSelector } from './components/AgentSelector';

const vscode = acquireVsCodeApi();

export const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [selectedAgent, setSelectedAgent] = useState('orchestrator');

  const agents = [
    { id: 'orchestrator', name: 'Orchestrator', icon: '🎭' },
    { id: 'implementation', name: 'Implementation', icon: '⚙️' },
    { id: 'review', name: 'Code Review', icon: '🔍' },
    { id: 'debug', name: 'Debug', icon: '🐛' },
    { id: 'security', name: 'Security', icon: '🔒' }
  ];

  const sendMessage = () => {
    if (!input.trim()) return;

    // Add user message
    setMessages([...messages, { role: 'user', content: input }]);

    // Send to extension
    vscode.postMessage({
      type: 'sendPrompt',
      prompt: input,
      agent: selectedAgent
    });

    setInput('');
  };

  // Listen for responses
  React.useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      const message = event.data;
      if (message.type === 'agentResponse') {
        setMessages(prev => [...prev, {
          role: 'agent',
          content: message.response,
          agent: message.agent,
          suggestions: message.suggestions
        }]);
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  return (
    <div className="chat-container">
      <AgentSelector
        agents={agents}
        selected={selectedAgent}
        onSelect={setSelectedAgent}
      />
      
      <div className="messages">
        {messages.map((msg, i) => (
          <ChatMessage key={i} message={msg} />
        ))}
      </div>

      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder={`Ask ${selectedAgent}...`}
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
};
```

### Bundling with IDE

**In `.github/workflows/build-release.yml`:**

```yaml
- name: Build BREEZER Chat Extension
  run: |
    cd extensions/breezer-chat
    npm install
    npm run compile
    npx vsce package --no-dependencies
    
- name: Bundle Extension with IDE
  run: |
    # Windows
    $extDir = "VSCode-win32-x64\resources\app\extensions\breezer-chat"
    New-Item -ItemType Directory -Force -Path $extDir
    
    # Extract .vsix contents to extensions folder
    Expand-Archive extensions\breezer-chat\*.vsix $extDir
    
    Write-Host "✓ Bundled BREEZER Chat extension"
```

### API Integration

**Backend Endpoint (`backend/api/routes/chat.py`):**

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.agents.orchestrator import OrchestratorAgent

router = APIRouter(prefix="/api/agent")

class ChatRequest(BaseModel):
    prompt: str
    agent: str
    context: dict

@router.post("/chat")
async def chat(request: ChatRequest):
    # Route to appropriate agent
    agent_map = {
        'orchestrator': OrchestratorAgent(),
        'implementation': ImplementationAgent(),
        # ... other agents
    }
    
    agent = agent_map.get(request.agent)
    if not agent:
        raise HTTPException(404, "Agent not found")
    
    # Process request
    response = await agent.process(
        prompt=request.prompt,
        context=request.context
    )
    
    return {
        "response": response.text,
        "agent": request.agent,
        "code_suggestions": response.code_blocks,
        "confidence": response.confidence
    }
```

### Advantages

✅ **Fast Development:** 2-4 weeks  
✅ **Standard VS Code APIs:** Well-documented, stable  
✅ **Easy Updates:** Iterate independently of IDE core  
✅ **Familiar Patterns:** React + TypeScript stack  
✅ **Portable:** Could publish to marketplace later  
✅ **Low Risk:** Doesn't modify Code-OSS source  

### Limitations

⚠️ **Extension API Constraints:**
- Limited access to editor internals
- Can't modify status bar/title bar natively
- Webview performance overhead

⚠️ **Not "Native" Feel:**
- Chat appears in panel, not sidebar tree
- Can't deeply integrate with VS Code UI themes

---

## Option 2: Core Integration

### Overview

Modify Code-OSS source code directly to add chat as a native workbench contribution, similar to how Terminal, Debug, and Output panels work. This matches Cursor/Windsurf's architecture.

### Architecture

```
Code-OSS Source Modifications
└── src/vs/workbench/
    ├── contrib/
    │   └── breezer/                    # New contribution
    │       ├── browser/
    │       │   ├── breezerChatView.ts        # Sidebar chat panel
    │       │   ├── breezerInlineWidget.ts    # Inline editing widget
    │       │   ├── breezerStatusBar.ts       # Status bar integration
    │       │   └── breezerService.ts         # Core service
    │       ├── common/
    │       │   ├── breezerApi.ts             # Backend API client
    │       │   ├── breezerContext.ts         # Context gathering
    │       │   ├── breezerModels.ts          # TypeScript interfaces
    │       │   └── IBreezerService.ts        # Service interface
    │       └── electron-main/
    │           └── breezerMain.ts            # Main process integration
    │
    └── services/
        └── breezer/
            └── common/
                └── breezerService.ts         # DI service registration
```

### Integration Points

#### 1. Sidebar View (`breezerChatView.ts`)

```typescript
import { ViewPane } from 'vs/workbench/browser/parts/views/viewPane';
import { IInstantiationService } from 'vs/platform/instantiation/common/instantiation';

export class BreezerChatView extends ViewPane {
  static readonly ID = 'workbench.view.breezer.chat';

  constructor(
    options: IViewPaneOptions,
    @IInstantiationService instantiationService: IInstantiationService,
    @IBreezerService private breezerService: IBreezerService
  ) {
    super(options, instantiationService);
  }

  protected renderBody(container: HTMLElement): void {
    // Render chat UI
    const chatContainer = DOM.append(container, DOM.$('.breezer-chat'));
    
    // Create message list
    this.messageList = this.instantiationService.createInstance(
      MessageList,
      chatContainer
    );

    // Create input area
    this.inputArea = this.instantiationService.createInstance(
      ChatInput,
      chatContainer,
      (text) => this.sendMessage(text)
    );
  }

  private async sendMessage(text: string): Promise<void> {
    const context = await this.gatherContext();
    const response = await this.breezerService.sendPrompt(text, context);
    this.messageList.addMessage(response);
  }
}
```

#### 2. Service Registration (`breezerService.ts`)

```typescript
import { registerSingleton } from 'vs/platform/instantiation/common/extensions';
import { createDecorator } from 'vs/platform/instantiation/common/instantiation';

export const IBreezerService = createDecorator<IBreezerService>('breezerService');

export interface IBreezerService {
  sendPrompt(prompt: string, context: IBreezerContext): Promise<string>;
  selectAgent(agent: string): void;
}

class BreezerService implements IBreezerService {
  private apiBase = 'http://localhost:8000/api/agent';

  async sendPrompt(prompt: string, context: IBreezerContext): Promise<string> {
    const response = await fetch(`${this.apiBase}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, context })
    });
    return (await response.json()).response;
  }
}

registerSingleton(IBreezerService, BreezerService, InstantiationType.Delayed);
```

#### 3. Workbench Contribution (`breezer.contribution.ts`)

```typescript
import { Registry } from 'vs/platform/registry/common/platform';
import { IWorkbenchContributionsRegistry, Extensions } from 'vs/workbench/common/contributions';
import { LifecyclePhase } from 'vs/workbench/services/lifecycle/common/lifecycle';

// Register view container
const VIEW_CONTAINER = Registry.as<IViewContainersRegistry>(ViewContainerExtensions.ViewContainersRegistry)
  .registerViewContainer({
    id: 'workbench.view.breezer',
    title: 'BREEZER AI',
    icon: 'breezer-icon',
    order: 2,
    ctorDescriptor: new SyncDescriptor(ViewPaneContainer)
  }, ViewContainerLocation.Sidebar);

// Register chat view
Registry.as<IViewsRegistry>(ViewExtensions.ViewsRegistry)
  .registerViews([{
    id: BreezerChatView.ID,
    name: 'Chat',
    containerIcon: 'breezer-icon',
    canToggleVisibility: true,
    ctorDescriptor: new SyncDescriptor(BreezerChatView)
  }], VIEW_CONTAINER);

// Register keybindings
KeybindingsRegistry.registerCommandAndKeybindingRule({
  id: 'breezer.openChat',
  weight: KeybindingWeight.WorkbenchContrib,
  when: undefined,
  primary: KeyMod.CtrlCmd | KeyMod.Shift | KeyCode.KeyB,
  handler: (accessor) => {
    const viewsService = accessor.get(IViewsService);
    viewsService.openView(BreezerChatView.ID, true);
  }
});
```

### Build Integration

**Modify `build/gulpfile.vscode.js`:**

```javascript
// Add BREEZER contributions to compilation
const breezerContributions = [
  'src/vs/workbench/contrib/breezer/**',
  'src/vs/workbench/services/breezer/**'
];

compilation.src = compilation.src.concat(breezerContributions);
```

### Advantages

✅ **Native Integration:** Indistinguishable from built-in features  
✅ **Full Access:** All VS Code internals available  
✅ **Better Performance:** No webview overhead for UI  
✅ **Deeper Context:** Access to language services, workspace state  
✅ **Professional Feel:** Matches Cursor/Windsurf quality  
✅ **Branding:** Complete UI control  

### Challenges

⚠️ **Longer Development:** 2-3 months initial build  
⚠️ **Code-OSS Updates:** Must merge upstream changes  
⚠️ **Build Complexity:** Requires gulp/webpack knowledge  
⚠️ **Testing Burden:** Full IDE rebuild for each change  

---

## Comparison Matrix

| Aspect | Option 1 (Extension) | Option 2 (Core) |
|--------|----------------------|-----------------|
| **Timeline** | 2-4 weeks | 2-3 months |
| **Complexity** | Low | High |
| **Maintenance** | Easy (independent updates) | Complex (merge upstream) |
| **User Experience** | Good (webview panel) | Excellent (native) |
| **Performance** | Good | Excellent |
| **Flexibility** | Limited by Extension API | Full control |
| **Code Changes** | None to Code-OSS | Modify core source |
| **Testing** | Fast (npm run watch) | Slow (full rebuild) |
| **Marketability** | Good | Best (premium feel) |
| **Risk** | Low | Medium |

---

## Recommended Implementation Plan

### Phase 1: Extension MVP (Weeks 1-4)

**Goal:** Working chat in users' hands quickly

**Deliverables:**
- Basic chat panel (Ctrl+Shift+B)
- Agent selector (9 agents)
- Context gathering (active file, selection)
- Code block rendering
- Apply code suggestions

**Acceptance Criteria:**
- User can open chat
- Select agent
- Send prompt with file context
- Receive response from FastAPI backend
- Apply code changes to files

### Phase 2: Extension Polish (Weeks 5-8)

**Enhancements:**
- Inline assist (Ctrl+K)
- Chat history persistence
- Streaming responses (SSE)
- Syntax highlighting
- Multi-file context (@file mentions)
- Terminal output awareness

### Phase 3: Core Migration Planning (Month 3)

**Analysis:**
- User feedback from extension
- Performance metrics
- Feature requests
- ROI assessment for core integration

### Phase 4: Core Integration (Months 4-6) - If Justified

**Only proceed if:**
- Extension has >1000 active users
- Premium tier launched
- Engineering bandwidth available
- Clear competitive advantage needed

---

## Technical Requirements

### Development Environment

**Extension Development:**
- Node.js 20.18.0
- npm 10.x
- VS Code Extension API knowledge
- React 18+ experience
- TypeScript 5.x

**Core Integration:**
- All of above, plus:
- Code-OSS source build experience
- Gulp/Webpack understanding
- VS Code contribution patterns knowledge

### Backend Requirements

**API Endpoints Needed:**

```python
# Required endpoints
POST /api/agent/chat           # Main chat endpoint
POST /api/agent/stream         # Streaming responses (SSE)
GET  /api/agent/list           # List available agents
POST /api/agent/context        # Validate/process context
POST /api/agent/apply          # Apply code changes

# Response format
{
  "response": "Agent's text response",
  "code_blocks": [{
    "language": "python",
    "code": "def hello():\n    pass",
    "file": "main.py",
    "line_start": 10
  }],
  "agent": "implementation",
  "confidence": 0.95,
  "suggestions": ["refactor", "add tests"]
}
```

### Infrastructure

**For Extension:**
- FastAPI backend running on `localhost:8000`
- No additional infrastructure

**For Core Integration:**
- Same backend
- Potentially: WebSocket server for better streaming
- Monitoring/telemetry (optional)

---

## Success Metrics

### Extension (Phase 1-2)

- **Adoption:** 80% of BREEZER users activate chat within first week
- **Engagement:** Average 10+ messages per day per active user
- **Satisfaction:** >4.5/5 star rating in feedback
- **Performance:** <500ms average response time (backend)
- **Stability:** <1% crash rate

### Core Integration (Phase 4)

- **All above, plus:**
- **Perceived Quality:** "Feels native" in user surveys (>90%)
- **Competitive:** Feature parity with Cursor/Windsurf
- **Upsell:** 20% conversion to premium tier

---

## Cost-Benefit Analysis

### Option 1: Extension

**Development Cost:**
- 1 senior engineer: 4 weeks @ $12k = **$12,000**
- Infrastructure: $0 (use existing backend)
- **Total: $12,000**

**Ongoing:**
- Maintenance: 5 hours/month @ $150/hr = **$750/month**

### Option 2: Core Integration

**Development Cost:**
- 1 senior engineer: 3 months @ $36k = **$36,000**
- Testing/QA: 2 weeks @ $6k = **$6,000**
- **Total: $42,000**

**Ongoing:**
- Maintenance: 10 hours/month = **$1,500/month**
- Merge upstream: 2 days/quarter = **$2,400/quarter**

### ROI Break-Even

**Assumptions:**
- Premium tier: $10/month
- Chat is primary value driver

**Extension Path:**
- Need 100 premium users to break even (Month 2)

**Core Path:**
- Need 350 premium users to break even (Month 5)

**Recommendation:** Start with extension, prove value, then invest in core.

---

## Risk Analysis

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| FastAPI backend latency | Medium | High | Add caching, optimize queries |
| Extension API limitations | Low | Medium | Prototype early, validate capabilities |
| Code-OSS merge conflicts | High (Option 2) | High | Dedicate time quarterly for merges |
| Agent reliability | Medium | High | Fallback to default responses, monitoring |

### Market Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Cursor/Windsurf add multi-agent | Medium | High | Patent agents, emphasize local LLM |
| VS Code adds native AI | Low | Critical | Differentiate on privacy/agents |
| User adoption below target | Medium | High | User testing, iterate quickly |

---

## Decision Framework

**Choose Extension (Option 1) if:**
- ✅ Need to ship in Q1 2025
- ✅ Limited engineering bandwidth
- ✅ Want to validate market first
- ✅ Prioritize low risk

**Choose Core (Option 2) if:**
- ✅ Have 3+ months runway
- ✅ Need competitive differentiation NOW
- ✅ Have experienced Code-OSS developers
- ✅ Premium tier already launched

**Recommended:** Extension first, core later.

---

## Next Steps

### Immediate (This Week)

1. **Decision:** Confirm Option 1 (Extension) approach
2. **Setup:** Create `extensions/breezer-chat/` directory
3. **Prototype:** Basic chat panel in 2 days
4. **Test:** Validate API integration with backend

### Week 2-3

1. Implement React UI
2. Add agent selector
3. Context gathering
4. Code application logic

### Week 4

1. Bundle with IDE builds
2. Internal testing
3. Documentation
4. Launch to early access users

---

## Appendix: Code Samples

### Extension package.json

```json
{
  "name": "breezer-chat",
  "displayName": "BREEZER AI Chat",
  "version": "1.0.0",
  "engines": {
    "vscode": "^1.95.0"
  },
  "categories": ["Other"],
  "activationEvents": ["onStartupFinished"],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [{
      "command": "breezer.openChat",
      "title": "Open BREEZER Chat",
      "category": "BREEZER"
    }],
    "keybindings": [{
      "command": "breezer.openChat",
      "key": "ctrl+shift+b",
      "mac": "cmd+shift+b"
    }],
    "viewsContainers": {
      "activitybar": [{
        "id": "breezer",
        "title": "BREEZER AI",
        "icon": "resources/icon.svg"
      }]
    },
    "views": {
      "breezer": [{
        "id": "breezerChat",
        "name": "Chat"
      }]
    }
  },
  "scripts": {
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./",
    "package": "vsce package"
  },
  "devDependencies": {
    "@types/vscode": "^1.95.0",
    "@vscode/vsce": "^2.22.0",
    "typescript": "^5.3.0"
  }
}
```

---

## References

- **VS Code Extension API:** https://code.visualstudio.com/api
- **Cursor IDE:** https://cursor.com
- **Windsurf IDE:** https://windsurf.com
- **Code-OSS Repository:** https://github.com/microsoft/vscode
- **BREEZER Backend:** `backend/agents/` (existing)

---

**Document Version:** 1.0  
**Last Updated:** November 9, 2025  
**Owner:** RICHDALE AI Engineering Team  
**Status:** Planning Phase - Pending Engineering Review
