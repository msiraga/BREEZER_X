# BREEZER IDE Branding Script by RICHDALE AI
# PowerShell Version

param(
    [string]$CodeOssDir = "code-oss"
)

$ErrorActionPreference = "Stop"

$BrandingDir = "ide-build\branding"
$LogosSource = "C:\Users\msira\Downloads\breezer_ico"

Write-Host "Applying BREEZER IDE branding..." -ForegroundColor Cyan

# Check if Code-OSS directory exists
if (!(Test-Path $CodeOssDir)) {
    Write-Host "ERROR: Code-OSS directory not found: $CodeOssDir" -ForegroundColor Red
    exit 1
}

# 1. Merge product metadata (preserve original fields)
Write-Host "Updating product.json..." -ForegroundColor Yellow
$originalProduct = Get-Content "$CodeOssDir\product.json" -Raw | ConvertFrom-Json
$brandingProduct = Get-Content "$BrandingDir\product.json" -Raw | ConvertFrom-Json

# Merge: branding overrides take precedence
$brandingProduct.PSObject.Properties | ForEach-Object {
    $originalProduct | Add-Member -MemberType NoteProperty -Name $_.Name -Value $_.Value -Force
}

$originalProduct | ConvertTo-Json -Depth 100 | Set-Content "$CodeOssDir\product.json"

# 2. Setup Windows icons
Write-Host "Setting up Windows icons..." -ForegroundColor Yellow

if (Test-Path "$LogosSource\breezer.ico") {
    Copy-Item "$LogosSource\breezer.ico" "$CodeOssDir\resources\win32\code.ico" -Force
    Write-Host "  Copied breezer.ico" -ForegroundColor Green
}

if (Test-Path "$LogosSource\splash.png") {
    # For now, just copy splash.png directly
    # In production, you'd want to resize these properly
    Copy-Item "$LogosSource\splash.png" "$CodeOssDir\resources\win32\code_150x150.png" -Force
    Copy-Item "$LogosSource\splash.png" "$CodeOssDir\resources\win32\code_70x70.png" -Force
    Write-Host "  Copied splash images" -ForegroundColor Green
}

# 3. Setup Linux icons
Write-Host "Setting up Linux icons..." -ForegroundColor Yellow
if (Test-Path "$LogosSource\splash.png") {
    Copy-Item "$LogosSource\splash.png" "$CodeOssDir\resources\linux\code.png" -Force
}

# 4. Update package.json
Write-Host "Updating package.json..." -ForegroundColor Yellow
$packageJson = Get-Content "$CodeOssDir\package.json" -Raw | ConvertFrom-Json
$packageJson | Add-Member -MemberType NoteProperty -Name "name" -Value "breezer-ide" -Force
$packageJson | Add-Member -MemberType NoteProperty -Name "productName" -Value "BREEZER IDE" -Force
$packageJson | Add-Member -MemberType NoteProperty -Name "description" -Value "AI-Powered Development Platform by RICHDALE AI" -Force
$packageJson | ConvertTo-Json -Depth 100 | Set-Content "$CodeOssDir\package.json"

# 5. Disable telemetry in source code
Write-Host "Disabling telemetry..." -ForegroundColor Yellow
Get-ChildItem -Path "$CodeOssDir\src" -Filter "*.ts" -Recurse | ForEach-Object {
    (Get-Content $_.FullName) -replace 'enableTelemetry: true', 'enableTelemetry: false' | Set-Content $_.FullName
}

# 6. Create custom README
Write-Host "Creating custom README..." -ForegroundColor Yellow
@"
# BREEZER IDE

**AI-Powered Development Platform by RICHDALE AI**

BREEZER is a next-generation IDE built on Code-OSS with integrated AI agents for:
- Intelligent code generation
- Automated code review
- Advanced debugging
- Architecture design
- Security auditing
- And much more...

## Features

- Multi-agent AI system
- Privacy-first (no telemetry)
- Integrated sandbox execution
- GPU-accelerated semantic search
- Beautiful, modern interface

## License

MIT License - See LICENSE file

---

© 2025 RICHDALE AI. All rights reserved.
"@ | Set-Content "$CodeOssDir\README_BREEZER.md"

Write-Host ""
Write-Host "BREEZER IDE branding applied successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. cd $CodeOssDir" -ForegroundColor White
Write-Host "2. yarn install" -ForegroundColor White
Write-Host "3. yarn compile" -ForegroundColor White
Write-Host "4. yarn gulp vscode-win32-x64" -ForegroundColor White
