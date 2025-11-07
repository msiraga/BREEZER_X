# Running Local Mistral with Llamafile

You already have `mistral.gguf` - here's how to use it with BREEZER.

---

## Quick Start

### 1. Download Llamafile Executable

```powershell
# Download llamafile (one-time)
cd C:\Users\msira\OneDrive\Documents\AI\Richdale AI\LLM Course Development - LLM Pre Training\llm-knowledge-course

# Download from: https://github.com/Mozilla-Ocho/llamafile/releases
# Get: llamafile-0.8.13.exe (or latest version)
```

**Or use PowerShell:**
```powershell
Invoke-WebRequest -Uri "https://github.com/Mozilla-Ocho/llamafile/releases/download/0.8.13/llamafile-0.8.13.exe" -OutFile "llamafile.exe"
```

---

### 2. Run Mistral as a Server

```powershell
# Navigate to model directory
cd "C:\Users\msira\OneDrive\Documents\AI\Richdale AI\LLM Course Development - LLM Pre Training\llm-knowledge-course"

# Run llamafile server
.\llamafile.exe -m mistral.gguf --server --port 8080 --host 0.0.0.0
```

**What this does:**
- Starts HTTP server on `http://localhost:8080`
- Compatible with OpenAI API format
- BREEZER can connect automatically

---

### 3. Configure BREEZER

Your `.env` file already has:
```bash
LLAMAFILE_ENABLED=true
LLAMAFILE_BASE_URL=http://localhost:8080
LLAMAFILE_MODEL=mistral-7b-instruct
USE_LOCAL_FOR_SENSITIVE=true
```

**That's it!** BREEZER will use local Mistral for sensitive operations.

---

## Create Startup Script

**Create: `start-mistral.ps1`**

```powershell
# Start Mistral Local LLM Server
# Location: C:\Users\msira\OneDrive\Documents\AI\Richdale AI\...

$modelPath = "C:\Users\msira\OneDrive\Documents\AI\Richdale AI\LLM Course Development - LLM Pre Training\llm-knowledge-course"
$llamafile = Join-Path $modelPath "llamafile.exe"
$model = Join-Path $modelPath "mistral.gguf"

Write-Host "🚀 Starting Mistral 7B Local Server..." -ForegroundColor Cyan
Write-Host "📁 Model: $model" -ForegroundColor Yellow
Write-Host "🌐 Server: http://localhost:8080" -ForegroundColor Green
Write-Host ""

# Check if files exist
if (-not (Test-Path $llamafile)) {
    Write-Host "❌ llamafile.exe not found!" -ForegroundColor Red
    Write-Host "Download from: https://github.com/Mozilla-Ocho/llamafile/releases" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $model)) {
    Write-Host "❌ mistral.gguf not found!" -ForegroundColor Red
    exit 1
}

# Start server
& $llamafile -m $model --server --port 8080 --host 0.0.0.0 `
    --ctx-size 4096 `
    --n-gpu-layers 35 `
    --threads 8

Write-Host ""
Write-Host "✅ Mistral server stopped" -ForegroundColor Green
```

**Save to:** `C:\Users\msira\Downloads\breezer_sonnet\start-mistral.ps1`

---

## Usage

### Start Everything

```powershell
# Terminal 1: Start Mistral
.\start-mistral.ps1

# Terminal 2: Start BREEZER Backend
docker-compose up -d
```

---

## Test Llamafile Connection

```powershell
# Test if Mistral is running
Invoke-RestMethod -Uri "http://localhost:8080/v1/models" -Method Get

# Expected response:
# {
#   "data": [
#     {
#       "id": "mistral-7b-instruct",
#       ...
#     }
#   ]
# }
```

---

## What Operations Use Local LLM?

When `USE_LOCAL_FOR_SENSITIVE=true`:

**Uses Local Mistral:**
- 🔒 Analyzing proprietary code
- 🔒 Processing sensitive data
- 🔒 Security audits
- 🔒 Fallback when API down

**Uses DeepSeek (Cloud):**
- 📝 Documentation generation
- 🐛 General debugging
- 💡 Code suggestions
- 🎨 Refactoring

---

## Performance Notes

**Your System (RTX 4060):**
```
GPU: NVIDIA RTX 4060 (8GB VRAM)
├─ Recommended: --n-gpu-layers 35
├─ Context size: --ctx-size 4096
└─ Expected speed: 30-50 tokens/sec
```

**Adjust for performance:**
```powershell
# More GPU layers = faster but needs more VRAM
--n-gpu-layers 35  # Good for RTX 4060 8GB

# Smaller context if needed
--ctx-size 2048    # Use less memory
```

---

## Advantages of Local LLM

✅ **Privacy**: No data leaves your machine  
✅ **Cost**: Free (no API calls)  
✅ **Speed**: No network latency  
✅ **Offline**: Works without internet  
✅ **Control**: Full ownership of inference  

---

## Alternative: Quick Test Without Script

```powershell
# One-line test
cd "C:\Users\msira\OneDrive\Documents\AI\Richdale AI\LLM Course Development - LLM Pre Training\llm-knowledge-course"
.\llamafile.exe -m mistral.gguf --server --port 8080
```

Then in browser: http://localhost:8080

---

## Troubleshooting

### Port Already in Use
```powershell
# Check what's using port 8080
netstat -ano | findstr :8080

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### GPU Not Detected
```powershell
# Check CUDA
nvidia-smi

# Run CPU-only (slower)
.\llamafile.exe -m mistral.gguf --server --port 8080 --n-gpu-layers 0
```

### Out of Memory
```powershell
# Reduce context size
--ctx-size 2048

# Or reduce GPU layers
--n-gpu-layers 20
```

---

## Summary

**You have:**
✅ `mistral.gguf` model (already downloaded)  
⏳ Need: `llamafile.exe` (download once)  

**To run:**
1. Download llamafile.exe
2. Run: `.\llamafile.exe -m mistral.gguf --server --port 8080`
3. BREEZER automatically connects via `.env` config

**Result:**
- Local AI for sensitive code
- No data sent to cloud
- Free inference on your GPU

---

© 2025 RICHDALE AI - BREEZER Platform
