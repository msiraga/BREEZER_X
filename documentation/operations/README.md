# BREEZER 🏄

**AI-Powered Development Platform by RICHDALE AI**

A fully customizable, enterprise-grade coding assistant built on Code-OSS with multi-agent orchestration, intelligent code understanding, and sandboxed execution.

> **Privacy-First**: No telemetry, all data stays on-premise, local LLM support for sensitive operations.

## Features

- 🤖 **Multi-Agent System**: Specialized agents for implementation, review, architecture, testing, and debugging
- 🎨 **Custom Branded IDE**: Built on Code-OSS with full Microsoft extension compatibility
- 🐳 **Docker Sandbox**: Safe code execution and debugging environment
- 🔒 **Privacy First**: No telemetry, all processing on your infrastructure
- 🚀 **GPU Accelerated**: Local embeddings using RTX GPU for fast semantic search
- 🌐 **Multi-Platform**: Linux, Windows, macOS builds via Docker

## Architecture

```
BREEZER IDE (Code-OSS + Extensions)
    ↓
Agent Orchestrator (FastAPI + LangGraph)
    ├─ Implementation Agent
    ├─ Review Agent
    ├─ Architect Agent
    ├─ QA Agent
    └─ Debug Agent
    ↓
Services Layer
    ├─ Vector DB (Qdrant) - Code search
    ├─ PostgreSQL - Task/memory storage
    ├─ Redis - Caching
    └─ Docker Sandbox - Safe execution
    ↓
LLM Router (OpenAI, Anthropic, Local)
```

## Quick Start

### Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Node.js 18+
- Python 3.11+
- 16GB+ RAM recommended
- NVIDIA GPU RTX 4060 (for local embeddings)
- DeepSeek API key (for testing/building)

### Installation

```bash
# Clone repository
git clone https://github.com/msiraga/BREEZER_X.git
cd BREEZER_X

# Setup environment
cp .env.example .env
# Edit .env with your DeepSeek API key

# Start backend services
docker-compose up -d

# Build IDE for all platforms (Linux, Windows, macOS)
docker-compose -f docker/docker-compose.build.yml up

# Built IDE will be in: builds/
# - breezer-ide-linux-x64.tar.gz
# - breezer-ide-windows-x64.zip
# - breezer-ide-darwin-x64.tar.gz
```

### Development Setup

```bash
# Install dependencies
cd backend && pip install -r requirements.txt
cd ../extension && npm install

# Run in development mode
npm run dev
```

## Project Structure

```
BREEZER/
├── ide-build/              # Code-OSS custom build
│   ├── branding/          # RICHDALE AI logos, product.json
│   └── scripts/           # Branding automation
├── extension/             # VSCode extension (UI)
├── backend/               # Agent orchestrator (Python/FastAPI)
│   ├── agents/           # 9 specialized AI agents
│   │   ├── implementation.py
│   │   ├── review.py
│   │   ├── debug.py
│   │   ├── documentation.py
│   │   ├── refactoring.py
│   │   ├── security.py
│   │   └── devops.py
│   ├── services/         # Vector DB, sandbox, embeddings
│   ├── api/              # REST endpoints
│   └── core/             # LLM router, config
├── docker/               # Multi-platform IDE builds
└── .github/              # CI/CD workflows
```

## Configuration

### API Keys

Edit `.env`:
```bash
# Primary LLM (DeepSeek)
DEEPSEEK_API_KEY=sk-your-deepseek-key

# Optional: Add more providers later
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Local LLM (Mistral 7B via Llamafile)
LLAMAFILE_ENABLED=true
LLAMAFILE_BASE_URL=http://localhost:8080
```

**Privacy**: Sensitive operations automatically use local LLM when `USE_LOCAL_FOR_SENSITIVE=true`

### Agent Settings

Edit `backend/config/agents.yaml` to customize agent behavior.

## Usage

### Via IDE

1. Open BREEZER IDE
2. Press `Ctrl+Shift+B` to open agent panel
3. Type your request: "Create a REST API with authentication"
4. Agents collaborate to complete the task

### Via API

```bash
curl -X POST http://localhost:8000/api/task \
  -H "Content-Type: application/json" \
  -d '{"task": "Refactor this function", "context": {...}}'
```

## Building for Production

```bash
# Build all platforms
docker-compose -f docker/docker-compose.build.yml up

# Output:
# - builds/breezer-ide-windows.exe
# - builds/breezer-ide-linux.AppImage
# - builds/breezer-ide-macos.dmg
```

## Documentation

- [Architecture Guide](docs/architecture.md)
- [Agent Development](docs/agents.md)
- [Deployment Guide](docs/deployment.md)
- [API Reference](docs/api.md)

## Agents Overview

### Priority 1 (Core)
- **Implementation**: Code generation & feature development
- **Review**: Code quality & best practices analysis
- **Architect**: System design & architecture decisions
- **QA**: Test generation & coverage analysis
- **Debug**: Error analysis & troubleshooting

### Priority 2 (Extended)
- **Documentation**: Technical writing & API docs
- **Refactoring**: Code improvement & optimization
- **Security**: Vulnerability detection & OWASP compliance
- **DevOps**: CI/CD, infrastructure, deployment

## License

MIT License - See LICENSE file

---

<div align="center">

**BREEZER** by **RICHDALE AI**

Built with ❤️ for developers who demand more

© 2025 RICHDALE AI. All rights reserved.

</div>
