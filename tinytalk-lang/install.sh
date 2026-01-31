#!/bin/bash
# Auto-install script for TinyTalk on Linux/macOS

echo "🚀 TinyTalk Language Installer"
echo "================================"

# Check for GCC or Clang
if command -v gcc &> /dev/null; then
    CC=gcc
elif command -v clang &> /dev/null; then
    CC=clang
else
    echo "❌ Error: No C compiler found (GCC or Clang required)"
    echo "📦 Install options:"
    echo "   macOS:   brew install gcc"
    echo "   Ubuntu:  sudo apt-get install build-essential"
    echo "   Fedora:  sudo dnf install gcc make"
    exit 1
fi

# Check for Make
if ! command -v make &> /dev/null; then
    echo "❌ Error: Make not found"
    echo "📦 Install: sudo apt-get install make (or equivalent)"
    exit 1
fi

# Build
echo "🔨 Building TinyTalk with $CC..."
make clean
make

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    
    # Install to /usr/local/bin (optional)
    read -p "Install to /usr/local/bin for system-wide access? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo cp tinytalk /usr/local/bin/
        echo "✅ Installed to /usr/local/bin/tinytalk"
        echo "   You can now run 'tinytalk' from anywhere!"
    else
        echo "ℹ️  TinyTalk binary: $(pwd)/tinytalk"
        echo "   Run with: ./tinytalk run examples/hello_world.tt"
    fi
    
    # Test
    echo ""
    echo "🧪 Testing installation..."
    ./tinytalk run examples/hello_world.tt
    
else
    echo "❌ Build failed"
    exit 1
fi
