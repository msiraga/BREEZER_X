#!/bin/bash
# BREEZER IDE Branding Script by RICHDALE AI

set -e

CODE_OSS_DIR=${1:-"code-oss"}
BRANDING_DIR="ide-build/branding"
LOGOS_SOURCE="$BRANDING_DIR/icons"

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
mkdir -p "$CODE_OSS_DIR/resources/linux"
if [ -f "$LOGOS_SOURCE/breezer.ico" ]; then
    # Convert ICO to PNG for Linux (extract largest size from multi-resolution ICO)
    if convert "$LOGOS_SOURCE/breezer.ico[0]" -resize 512x512 "$CODE_OSS_DIR/resources/linux/code.png" 2>/dev/null; then
        echo "✓ Converted breezer.ico to Linux PNG icon (512x512)"
    else
        echo "⚠️  ImageMagick conversion failed, trying fallback..."
        # Fallback: try without [0] index
        convert "$LOGOS_SOURCE/breezer.ico" -resize 512x512 "$CODE_OSS_DIR/resources/linux/code.png" 2>/dev/null || \
        echo "❌ Could not convert ICO to PNG for Linux"
    fi
fi

# 3. Setup Windows icons
echo "🪟 Setting up Windows icons..."
mkdir -p "$CODE_OSS_DIR/resources/win32"
if [ -f "$LOGOS_SOURCE/breezer.ico" ]; then
    cp "$LOGOS_SOURCE/breezer.ico" "$CODE_OSS_DIR/resources/win32/code.ico"
    echo "✓ Copied Windows icon"
fi

if [ -f "$LOGOS_SOURCE/breezer.ico" ]; then
    # Convert ICO to PNG for Windows tiles (Start menu tiles)
    convert "$LOGOS_SOURCE/breezer.ico[0]" -resize 150x150 "$CODE_OSS_DIR/resources/win32/code_150x150.png" 2>/dev/null || \
    convert "$LOGOS_SOURCE/breezer.ico" -resize 150x150 "$CODE_OSS_DIR/resources/win32/code_150x150.png" 2>/dev/null || \
    echo "⚠️  Could not create 150x150 tile"
    
    convert "$LOGOS_SOURCE/breezer.ico[0]" -resize 70x70 "$CODE_OSS_DIR/resources/win32/code_70x70.png" 2>/dev/null || \
    convert "$LOGOS_SOURCE/breezer.ico" -resize 70x70 "$CODE_OSS_DIR/resources/win32/code_70x70.png" 2>/dev/null || \
    echo "⚠️  Could not create 70x70 tile"
    
    echo "✓ Created Windows tile icons from breezer.ico"
fi

# 4. Setup macOS icons
echo "🍎 Setting up macOS icons..."
mkdir -p "$CODE_OSS_DIR/resources/darwin"
if [ -f "$LOGOS_SOURCE/breezer.ico" ]; then
    # Convert ICO to ICNS for macOS (requires imagemagick)
    if convert "$LOGOS_SOURCE/breezer.ico" "$CODE_OSS_DIR/resources/darwin/code.icns" 2>/dev/null; then
        echo "✓ Converted and copied macOS icon"
    else
        echo "⚠️  Could not convert to ICNS, manual conversion needed"
    fi
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
