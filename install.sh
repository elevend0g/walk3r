#!/bin/bash
# Walk3r 2.0 One-Click Installer for Linux/macOS

set -e

echo "🚀 Walk3r 2.0 One-Click Installer"
echo "================================="

# Check if Python 3.8+ is available
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo "❌ Python not found. Please install Python 3.8+ first."
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    echo "🐍 Found Python $PYTHON_VERSION"
    
    # Compare version (basic check)
    if [[ $(echo "$PYTHON_VERSION < 3.8" | bc -l) -eq 1 ]]; then
        echo "❌ Python 3.8+ required. Found Python $PYTHON_VERSION"
        exit 1
    fi
}

# Install system dependencies
install_system_deps() {
    echo "📦 Installing system dependencies..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            echo "   Detected Ubuntu/Debian"
            sudo apt-get update
            sudo apt-get install -y graphviz
        elif command -v yum &> /dev/null; then
            echo "   Detected CentOS/RHEL"
            sudo yum install -y graphviz
        elif command -v dnf &> /dev/null; then
            echo "   Detected Fedora"
            sudo dnf install -y graphviz
        elif command -v pacman &> /dev/null; then
            echo "   Detected Arch Linux"
            sudo pacman -S --noconfirm graphviz
        else
            echo "⚠️  Unknown Linux distribution. Please install graphviz manually:"
            echo "   Ubuntu/Debian: sudo apt-get install graphviz"
            echo "   CentOS/RHEL: sudo yum install graphviz"
            echo "   Fedora: sudo dnf install graphviz"
            echo "   Arch: sudo pacman -S graphviz"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            echo "   Installing via Homebrew"
            brew install graphviz
        else
            echo "⚠️  Homebrew not found. Please install graphviz manually:"
            echo "   Install Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            echo "   Then run: brew install graphviz"
        fi
    else
        echo "⚠️  Unsupported OS: $OSTYPE"
        echo "   Please install graphviz manually for your system"
    fi
}

# Install Python dependencies
install_python_deps() {
    echo "🐍 Installing Python dependencies..."
    $PYTHON_CMD -m pip install --user toml rich>=12.0.0 graphviz networkx
}

# Run setup script
run_setup() {
    echo "⚙️  Running setup script..."
    $PYTHON_CMD setup.py
}

# Create desktop launcher (optional)
create_launcher() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        read -p "📱 Create desktop launcher? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            DESKTOP_FILE="$HOME/.local/share/applications/walk3r.desktop"
            CURRENT_DIR=$(pwd)
            
            cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Walk3r 2.0
Comment=Easy code analysis tool
Exec=$PYTHON_CMD $CURRENT_DIR/app/cli_v2.py
Icon=code
Terminal=true
Categories=Development;
EOF
            echo "✅ Desktop launcher created: $DESKTOP_FILE"
        fi
    fi
}

# Main installation process
main() {
    check_python
    
    echo
    read -p "🔧 Install system dependencies (requires sudo)? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        install_system_deps
    else
        echo "⚠️  Skipping system dependencies. Visual graphs may not work."
    fi
    
    install_python_deps
    run_setup
    create_launcher
    
    echo
    echo "🎉 Walk3r 2.0 installation complete!"
    echo
    echo "📋 Quick start:"
    echo "   $PYTHON_CMD -m app.cli_v2 scan     # Interactive analysis"
    echo "   $PYTHON_CMD -m app.cli_v2 quick    # Quick analysis"
    echo "   $PYTHON_CMD -m app.cli_v2 setup    # Configure only"
    echo
    echo "📚 Documentation: https://github.com/elevend0g/walk3r"
    echo "🐛 Issues: https://github.com/elevend0g/walk3r/issues"
}

# Run main function
main