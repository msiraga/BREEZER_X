# BREEZER Setup Guide

**Complete setup instructions for BREEZER IDE by RICHDALE AI**

## Prerequisites

### Required
- Docker Desktop (Windows 11/macOS) or Docker Engine (Linux)
- Git
- 16GB+ RAM
- 20GB+ free disk space

### For Backend Development
- Python 3.11+
- Node.js 18+
- PostgreSQL 16+ (or use Docker)

### For GPU Acceleration
- NVIDIA RTX 4060 (or similar)
- CUDA drivers installed
- NVIDIA Container Toolkit (for Docker GPU support)

## Step 1: Clone Repository

```bash
git clone https://github.com/msiraga/BREEZER_X.git
cd BREEZER_X
```

## Step 2: Configuration

### 2.1 Copy Environment Template

```bash
cp .env.example .env
```

### 2.2 Edit `.env` File

```bash
# Minimum required configuration
DEEPSEEK_API_KEY=sk-your-key-here

# Optional: Local LLM for sensitive operations
LLAMAFILE_ENABLED=true
USE_LOCAL_FOR_SENSITIVE=true

# Database (default values work with Docker)
POSTGRES_PASSWORD=change-me-in-production
```

### 2.3 Get DeepSeek API Key

1. Visit https://platform.deepseek.com/
2. Sign up / Login
3. Generate API key
4. Add to `.env`: `DEEPSEEK_API_KEY=sk-...`

## Step 3: Start Backend Services

### Option A: Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

Services will be available at:
- **Backend API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Qdrant**: http://localhost:6333

### Option B: Local Development

```bash
# Install PostgreSQL, Redis, Qdrant manually
# Then:
cd backend
pip install -r requirements.txt
python main.py
```

## Step 4: Build BREEZER IDE

### Using Docker (Recommended - Builds All Platforms)

```bash
# Build for all platforms (Linux, Windows, macOS)
docker-compose -f docker/docker-compose.build.yml up

# Builds will be in: builds/
# - breezer-ide-linux-x64.tar.gz
# - breezer-ide-windows-x64.zip
# - breezer-ide-darwin-x64.tar.gz
```

**Build Time:**
- First build: 1-3 hours (all platforms)
- Subsequent builds: 25-50 minutes (cached)

### Alternative: Use GitHub Actions (No Local Build)

Push to GitHub and builds happen automatically:
```bash
git push origin main
# Wait 30-60 minutes → Builds appear as artifacts
```

### Advanced: Native Build (Not Recommended)

**Windows (PowerShell):**
```powershell
# Install Node.js 18, Python 3.11, Visual Studio Build Tools
git clone --depth 1 --branch release/1.95 https://github.com/microsoft/vscode.git code-oss
cd code-oss
..\ide-build\scripts\apply-branding.ps1 .
yarn install
yarn compile
yarn gulp vscode-win32-x64
```

**Linux/macOS:**
```bash
# Install build dependencies
git clone --depth 1 --branch release/1.95 https://github.com/microsoft/vscode.git code-oss
cd code-oss
bash ../ide-build/scripts/apply-branding.sh .
yarn install
yarn compile
yarn gulp vscode-linux-x64  # or vscode-darwin-x64
```

## Step 5: Optional - Local LLM (Llamafile)

For sensitive data operations, install local Mistral 7B:

```bash
# Download Llamafile
curl -L https://huggingface.co/Mozilla/Mistral-7B-Instruct-v0.2-llamafile/resolve/main/mistral-7b-instruct-v0.2.Q4_0.llamafile -o mistral.llamafile

# Make executable (Linux/macOS)
chmod +x mistral.llamafile

# Run
./mistral.llamafile --server --port 8080
```

**Windows**: Download `.exe` version from the same URL.

## Step 6: Verify Installation

### 6.1 Check Backend

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 6.2 Check Detailed Health

```bash
curl http://localhost:8000/health/detailed
```

Should show:
- GPU status
- Vector store status
- Embeddings provider

### 6.3 Test Agent

```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Write a hello world function",
    "workspace_path": "/tmp/test"
  }'
```

## Step 7: Run BREEZER IDE

### Windows
```powershell
cd builds
Expand-Archive breezer-ide-windows-x64.zip
cd VSCode-win32-x64
.\Code.exe
```

### Linux
```bash
cd builds
tar -xzf breezer-ide-linux-x64.tar.gz
cd VSCode-linux-x64
./code
```

### macOS
```bash
cd builds
tar -xzf breezer-ide-darwin-x64.tar.gz
cd VSCode-darwin-x64
open Code.app
```

## Troubleshooting

### Issue: Docker GPU not working

**Solution**:
```bash
# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

### Issue: Out of memory during IDE build

**Solution**:
```bash
# Increase Node.js memory
export NODE_OPTIONS="--max-old-space-size=8192"
```

Or edit `docker-compose.build.yml`:
```yaml
environment:
  - NODE_OPTIONS=--max_old_space_size=8192
```

### Issue: DeepSeek API errors

**Check**:
1. API key is correct
2. Account has credits
3. Check rate limits: https://platform.deepseek.com/usage

### Issue: Vector store connection fails

**Solution**:
```bash
# Restart Qdrant
docker-compose restart qdrant

# Check Qdrant health
curl http://localhost:6333/healthz
```

### Issue: Sandbox execution fails

**Solution**:
```bash
# Ensure Docker socket is accessible
sudo chmod 666 /var/run/docker.sock  # Linux
# Or add user to docker group:
sudo usermod -aG docker $USER
```

## Next Steps

1. **Configure IDE**: Open BREEZER IDE and install extensions
2. **Test Agents**: Try different agent commands
3. **Index Codebase**: Let BREEZER index your projects
4. **Customize**: Edit agent prompts in `backend/agents/`

## Advanced Configuration

### Add More LLM Providers

Edit `.env`:
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

Edit `.env` model routing:
```bash
MODEL_IMPLEMENTATION=gpt-4-turbo-preview
MODEL_ARCHITECT=claude-3-opus-20240229
```

### Custom Agent Prompts

Edit agent system prompts in:
- `backend/agents/implementation.py`
- `backend/agents/review.py`
- etc.

### Company-wide Deployment

See [DEPLOYMENT.md](docs/deployment.md) for:
- Multi-user setup
- Authentication
- Shared knowledge base
- Enterprise configuration

## Support

- **Issues**: https://github.com/msiraga/BREEZER_X/issues
- **Discussions**: https://github.com/msiraga/BREEZER_X/discussions

---

© 2025 RICHDALE AI
