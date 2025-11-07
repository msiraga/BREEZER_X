#!/bin/bash
# BREEZER IDE Branding Script by RICHDALE AI

set -e

CODE_OSS_DIR=${1:-"code-oss"}
BRANDING_DIR="ide-build/branding"
LOGOS_SOURCE="C:/Users/msira/Downloads/breezer_ico"

echo "🏄 Applying BREEZER IDE branding..."

# Check if Code-OSS directory exists
if [ ! -d "$CODE_OSS_DIR" ]; then
    echo "❌ Code-OSS directory not found: $CODE_OSS_DIR"
    exit 1
fi

# 1. Merge product metadata (preserve original fields)
echo "📝 Updating product.json..."
if command -v jq &> /dev/null; then
    # Merge our branding with original product.json
    jq -s '.[0] * .[1]' "$CODE_OSS_DIR/product.json" "$BRANDING_DIR/product.json" > "$CODE_OSS_DIR/product.json.tmp"
    mv "$CODE_OSS_DIR/product.json.tmp" "$CODE_OSS_DIR/product.json"
else
    echo "⚠️  jq not found, using full replacement (may cause build issues)"
    cp "$BRANDING_DIR/product.json" "$CODE_OSS_DIR/product.json"
fi

# 2. Convert and copy icons for Linux
echo "🐧 Setting up Linux icons..."
if [ -f "$LOGOS_SOURCE/splash.png" ]; then
    # Use splash as base, resize for Linux icon
    convert "$LOGOS_SOURCE/splash.png" -resize 512x512 "$CODE_OSS_DIR/resources/linux/code.png" 2>/dev/null || \
    cp "$LOGOS_SOURCE/splash.png" "$CODE_OSS_DIR/resources/linux/code.png"
fi

# 3. Setup Windows icons
echo "🪟 Setting up Windows icons..."
if [ -f "$LOGOS_SOURCE/breezer.ico" ]; then
    cp "$LOGOS_SOURCE/breezer.ico" "$CODE_OSS_DIR/resources/win32/code.ico"
fi

if [ -f "$LOGOS_SOURCE/splash.png" ]; then
    # Resize for Windows tiles
    convert "$LOGOS_SOURCE/splash.png" -resize 256x256 "$CODE_OSS_DIR/resources/win32/code_150x150.png" 2>/dev/null || \
    cp "$LOGOS_SOURCE/splash.png" "$CODE_OSS_DIR/resources/win32/code_150x150.png"
    
    convert "$LOGOS_SOURCE/splash.png" -resize 70x70 "$CODE_OSS_DIR/resources/win32/code_70x70.png" 2>/dev/null || \
    cp "$LOGOS_SOURCE/splash.png" "$CODE_OSS_DIR/resources/win32/code_70x70.png"
fi

# 4. Setup macOS icons
echo "🍎 Setting up macOS icons..."
if [ -f "$LOGOS_SOURCE/breezer.ico" ]; then
    # Convert ICO to ICNS for macOS (requires imagemagick)
    convert "$LOGOS_SOURCE/breezer.ico" "$CODE_OSS_DIR/resources/darwin/code.icns" 2>/dev/null || \
    echo "⚠️  Could not convert to ICNS, manual conversion needed"
fi

# 5. Update package.json
echo "📦 Updating package.json..."
if command -v jq &> /dev/null; then
    jq '.name = "breezer-ide" | 
        .productName = "BREEZER IDE" | 
        .description = "AI-Powered Development Platform by RICHDALE AI"' \
        "$CODE_OSS_DIR/package.json" > "$CODE_OSS_DIR/package.json.tmp"
    mv "$CODE_OSS_DIR/package.json.tmp" "$CODE_OSS_DIR/package.json"
else
    echo "⚠️  jq not found, skipping package.json update"
fi

# 6. Disable telemetry in source code
echo "🔒 Disabling telemetry..."
# Find and replace telemetry settings (macOS compatible)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS requires empty string after -i
    find "$CODE_OSS_DIR/src" -type f -name "*.ts" -exec sed -i '' 's/enableTelemetry: true/enableTelemetry: false/g' {} \; 2>/dev/null || true
else
    # Linux
    find "$CODE_OSS_DIR/src" -type f -name "*.ts" -exec sed -i 's/enableTelemetry: true/enableTelemetry: false/g' {} \; 2>/dev/null || true
fi

# 7. Update README
echo "📄 Creating custom README..."
cat > "$CODE_OSS_DIR/README_BREEZER.md" << 'EOF'
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

- 🤖 Multi-agent AI system
- 🔒 Privacy-first (no telemetry)
- 🐳 Integrated sandbox execution
- 🚀 GPU-accelerated semantic search
- 🎨 Beautiful, modern interface

## License

MIT License - See LICENSE file

---

© 2025 RICHDALE AI. All rights reserved.
EOF

echo "✅ BREEZER IDE branding applied successfully!"
echo ""
echo "Next steps:"
echo "1. cd $CODE_OSS_DIR"
echo "2. yarn install"
echo "3. yarn compile"
echo "4. yarn gulp vscode-<platform>-x64"
