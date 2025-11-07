# Start Mistral Local LLM Server for BREEZER
# Starts llamafile with your existing mistral.gguf model

$ErrorActionPreference = "Stop"

Write-Host @"
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   🧠 Mistral 7B Local LLM Server                        ║
║      for BREEZER by RICHDALE AI                          ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# Paths
$modelPath = "C:\Users\msira\OneDrive\Documents\AI\Richdale AI\LLM Course Development - LLM Pre Training\llm-knowledge-course"
$llamafile = Join-Path $modelPath "llamafile.exe"
$model = Join-Path $modelPath "mistral.gguf"

Write-Host "📁 Model directory: $modelPath" -ForegroundColor Yellow
Write-Host "🤖 Model file: mistral.gguf" -ForegroundColor Yellow
Write-Host "🌐 Server will run on: http://localhost:8080" -ForegroundColor Green
Write-Host ""

# Check if model exists
if (-not (Test-Path $model)) {
    Write-Host "❌ ERROR: mistral.gguf not found!" -ForegroundColor Red
    Write-Host "Expected location: $model" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Model file found!" -ForegroundColor Green

# Check if llamafile exists
if (-not (Test-Path $llamafile)) {
    Write-Host ""
    Write-Host "⚠️  llamafile.exe not found!" -ForegroundColor Yellow
    Write-Host "Downloading llamafile v0.8.13..." -ForegroundColor Cyan
    
    try {
        $downloadUrl = "https://github.com/Mozilla-Ocho/llamafile/releases/download/0.8.13/llamafile-0.8.13.exe"
        Invoke-WebRequest -Uri $downloadUrl -OutFile $llamafile -UseBasicParsing
        Write-Host "✅ Downloaded llamafile.exe" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to download llamafile!" -ForegroundColor Red
        Write-Host "Please download manually from: https://github.com/Mozilla-Ocho/llamafile/releases" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "✅ llamafile.exe found!" -ForegroundColor Green
Write-Host ""

# Check GPU
Write-Host "🎮 Checking GPU..." -ForegroundColor Cyan
try {
    $gpu = nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>$null
    if ($gpu) {
        Write-Host "✅ GPU detected: $gpu" -ForegroundColor Green
        $useGpu = $true
    } else {
        Write-Host "⚠️  No NVIDIA GPU detected, using CPU mode" -ForegroundColor Yellow
        $useGpu = $false
    }
} catch {
    Write-Host "⚠️  nvidia-smi not found, using CPU mode" -ForegroundColor Yellow
    $useGpu = $false
}

Write-Host ""
Write-Host "🚀 Starting Mistral 7B server..." -ForegroundColor Cyan
Write-Host "   Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

# Build command
$llamaArgs = @(
    "-m", $model,
    "--server",
    "--port", "8080",
    "--host", "0.0.0.0",
    "--ctx-size", "4096"
)

if ($useGpu) {
    $llamaArgs += "--n-gpu-layers", "35"  # RTX 4060 8GB
    Write-Host "⚡ GPU acceleration enabled (35 layers)" -ForegroundColor Green
} else {
    $llamaArgs += "--n-gpu-layers", "0"
    Write-Host "💻 CPU mode" -ForegroundColor Yellow
}

$llamaArgs += "--threads", "8"

Write-Host ""
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host ""

# Start server
try {
    & $llamafile $llamaArgs
} catch {
    Write-Host ""
    Write-Host "❌ Server stopped with error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Mistral server stopped cleanly" -ForegroundColor Green
