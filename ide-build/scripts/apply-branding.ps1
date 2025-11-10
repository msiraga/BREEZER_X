# BREEZER IDE Branding Script by RICHDALE AI
# PowerShell Version

param(
    [string]$CodeOssDir = "code-oss"
)

$ErrorActionPreference = "Stop"

$BrandingDir = "ide-build\branding"
$LogosSource = "$BrandingDir\icons"

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

# Ensure directory exists
New-Item -ItemType Directory -Force -Path "$CodeOssDir\resources\win32" | Out-Null

if (Test-Path "$LogosSource\breezer.ico") {
    # Primary icon location (used by VS Code build system)
    Copy-Item "$LogosSource\breezer.ico" "$CodeOssDir\resources\win32\code.ico" -Force
    Write-Host "  SUCCESS: Copied to resources\win32\code.ico" -ForegroundColor Green
    
    # Additional icon locations for Electron packager
    Copy-Item "$LogosSource\breezer.ico" "$CodeOssDir\resources\win32\app.ico" -Force
    Write-Host "  SUCCESS: Copied to resources\win32\app.ico" -ForegroundColor Green
    
    # Verify icon is valid
    $iconSize = (Get-Item "$LogosSource\breezer.ico").Length
    if ($iconSize -lt 1024) {
        Write-Host "  WARNING: Icon file is very small ($($iconSize) bytes) - may be corrupted" -ForegroundColor Yellow
    } else {
        Write-Host "  SUCCESS: Icon validated ($($iconSize) bytes)" -ForegroundColor Green
    }
    
    # Note: Windows tiles (150x150, 70x70) would need conversion from ICO to PNG
    # For now, the main .ico file contains multiple sizes and Windows will use appropriate one
    # If you need explicit PNGs, install ImageMagick and add conversion here
}

# 3. Setup Linux icons
Write-Host "Setting up Linux icons..." -ForegroundColor Yellow

# Ensure directory exists
New-Item -ItemType Directory -Force -Path "$CodeOssDir\resources\linux" | Out-Null

if (Test-Path "$LogosSource\breezer.ico") {
    # Note: Linux needs PNG, not ICO
    # If ImageMagick is available, convert ICO to PNG
    # For PowerShell on Windows build machine, this is handled by bash script
    # This script typically runs on Windows for local testing
    Write-Host "  breezer.ico found (conversion to PNG happens in CI/CD)" -ForegroundColor Yellow
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

---

 2025 RICHDALE AI. All rights reserved.
"@ | Set-Content "$CodeOssDir\README_BREEZER.md"

Write-Host ""
Write-Host "=== Verifying Icon Placement ===" -ForegroundColor Cyan

# Verify all expected icon locations exist
$iconLocations = @(
    "$CodeOssDir\resources\win32\code.ico",
    "$CodeOssDir\resources\win32\app.ico"
)

$allIconsPresent = $true
foreach ($iconPath in $iconLocations) {
    if (Test-Path $iconPath) {
        $size = (Get-Item $iconPath).Length
        Write-Host "SUCCESS: $iconPath ($($size)) bytes" -ForegroundColor Green
    } else {
        Write-Host "MISSING: $iconPath" -ForegroundColor Red
        $allIconsPresent = $false
    }
}

if ($allIconsPresent) {
    Write-Host ""
    Write-Host "SUCCESS: BREEZER IDE branding applied successfully!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "WARNING:  BREEZER IDE branding applied with warnings" -ForegroundColor Yellow
    Write-Host "   Some icon files are missing" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. cd $CodeOssDir" -ForegroundColor White
Write-Host "2. npm ci" -ForegroundColor White
Write-Host "3. npm run compile" -ForegroundColor White
Write-Host "4. npm run gulp vscode-win32-x64" -ForegroundColor White
