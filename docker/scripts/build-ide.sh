#!/bin/bash
# BREEZER IDE Docker Build Script

set -e

PLATFORM=${1:-all}
VERSION=${2:-1.95}
OUTPUT_DIR=${3:-/output}

echo "🏄 Building BREEZER IDE for $PLATFORM (Code-OSS $VERSION)"

# If platform is "all", build all platforms sequentially
if [ "$PLATFORM" == "all" ]; then
    echo "📦 Building ALL platforms (Linux, Windows, macOS)"
    
    for plat in linux windows darwin; do
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Building $plat..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        bash $0 $plat $VERSION $OUTPUT_DIR
    done
    
    echo ""
    echo "✅ All platforms built successfully!"
    echo "📁 Output: $OUTPUT_DIR"
    ls -lh $OUTPUT_DIR/
    exit 0
fi

# Clone Code-OSS
if [ ! -d "code-oss" ]; then
    echo "📥 Cloning Code-OSS release/$VERSION..."
    git clone --depth 1 --branch release/$VERSION \
        https://github.com/microsoft/vscode.git code-oss
fi

cd code-oss

# Apply BREEZER branding
echo "🎨 Applying BREEZER branding..."
bash /build/scripts/apply-branding.sh $(pwd)

# Install dependencies
echo "📦 Installing dependencies..."
npm ci

# Compile
echo "🔨 Compiling BREEZER IDE..."
npm run compile

# Build for platform
echo "📦 Building for $PLATFORM..."
case $PLATFORM in
    linux)
        npm run gulp vscode-linux-x64
        echo "✅ Linux build complete"
        if [ -d ".build/linux/VSCode-linux-x64" ]; then
            mkdir -p "$OUTPUT_DIR"
            tar -czf "$OUTPUT_DIR/breezer-ide-linux-x64.tar.gz" -C .build/linux VSCode-linux-x64
            echo "📦 Package: $OUTPUT_DIR/breezer-ide-linux-x64.tar.gz"
        fi
        ;;
    
    windows)
        npm run gulp vscode-win32-x64
        echo "✅ Windows build complete"
        if [ -d ".build/win32-x64/VSCode-win32-x64" ]; then
            mkdir -p "$OUTPUT_DIR"
            cd .build/win32-x64
            zip -r "$OUTPUT_DIR/breezer-ide-windows-x64.zip" VSCode-win32-x64
            echo "📦 Package: $OUTPUT_DIR/breezer-ide-windows-x64.zip"
        fi
        ;;
    
    darwin)
        npm run gulp vscode-darwin-x64
        echo "✅ macOS build complete"
        if [ -d ".build/darwin/VSCode-darwin-x64" ]; then
            mkdir -p "$OUTPUT_DIR"
            cd .build/darwin
            tar -czf "$OUTPUT_DIR/breezer-ide-darwin-x64.tar.gz" VSCode-darwin-x64
            echo "📦 Package: $OUTPUT_DIR/breezer-ide-darwin-x64.tar.gz"
        fi
        ;;
    
    *)
        echo "❌ Unknown platform: $PLATFORM"
        echo "Usage: $0 [linux|windows|darwin] [version] [output_dir]"
        exit 1
        ;;
esac

echo ""
echo "✅ BREEZER IDE build complete!"
echo "📁 Output directory: $OUTPUT_DIR"
