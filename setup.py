#!/usr/bin/env python3
"""
Walk3r 2.0 Easy Setup Script
Automatically installs dependencies and sets up Walk3r for first-time users
"""

import os
import sys
import subprocess
import platform

def run_command(cmd, description=""):
    """Run a command and handle errors gracefully"""
    try:
        print(f"🔧 {description}...")
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {e}")
        print(f"   Command: {cmd}")
        if e.stdout:
            print(f"   Output: {e.stdout}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. You have Python {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_pip():
    """Check if pip is available"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("✅ pip is available")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip is not available. Please install pip first.")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Core dependencies
    deps = [
        "toml",
        "rich>=12.0.0",
        "graphviz",
        "networkx"
    ]
    
    for dep in deps:
        if not run_command(f"{sys.executable} -m pip install {dep}", 
                          f"Installing {dep}"):
            return False
    
    return True

def check_graphviz_system():
    """Check if Graphviz system package is installed"""
    try:
        subprocess.run(["dot", "-V"], check=True, capture_output=True)
        print("✅ Graphviz system package is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Graphviz system package not found")
        return False

def suggest_graphviz_install():
    """Suggest how to install Graphviz system package"""
    system = platform.system().lower()
    
    print("\n📋 To generate visual graphs, install Graphviz:")
    
    if system == "windows":
        print("   • Download from: https://graphviz.org/download/")
        print("   • Or use chocolatey: choco install graphviz")
    elif system == "darwin":  # macOS
        print("   • Using Homebrew: brew install graphviz")
        print("   • Using MacPorts: port install graphviz")
    else:  # Linux
        print("   • Ubuntu/Debian: sudo apt-get install graphviz")
        print("   • CentOS/RHEL: sudo yum install graphviz")
        print("   • Fedora: sudo dnf install graphviz")
        print("   • Arch: sudo pacman -S graphviz")

def create_example_config():
    """Create an example configuration file"""
    config_content = """# Walk3r 2.0 Configuration Example
# Copy this to your project directory and customize

[walk3r]
# Path to your Python project (relative to config file)
root_path = "."

# Where to save analysis results
output_dir = "./walk3r_reports"

# Output formats: json, csv, dot
formats = ["json", "csv"]

# Analysis features (set to false to disable)
enable_complexity = true      # Code complexity analysis
enable_db_detection = true    # Database operation detection
enable_db_compliance = true   # Database architecture compliance
enable_doc_coverage = true    # Documentation coverage analysis
enable_metrics = true         # Code metrics and statistics
enable_summary = true         # Human-readable summaries

# Complexity analysis thresholds
max_function_length = 30      # Flag functions longer than this
max_complexity_score = 10     # Flag functions more complex than this
max_parameter_count = 6       # Flag functions with more parameters

# Database detection patterns (customize for your project)
db_methods = ["execute", "query", "find", "insert", "update", "delete", "save", "create"]
db_modules = ["sqlite3", "sqlalchemy", "pymongo", "psycopg2", "mysql", "redis", "django.db"]

# Database compliance patterns (for architectural analysis)
[walk3r.violation_patterns]
direct_sql = [
    "cursor\\.execute\\(",
    "\\.execute\\s*\\(",
    "SELECT\\s+.*FROM",
    "INSERT\\s+INTO",
    "UPDATE\\s+.*SET",
    "DELETE\\s+FROM",
]

[walk3r.service_patterns]
repository_pattern = [
    "Repository\\(",
    "\\.repository\\.",
    "_repo\\.",
]
"""
    
    try:
        with open("walk3r-example.toml", "w") as f:
            f.write(config_content)
        print("✅ Created walk3r-example.toml configuration template")
        return True
    except Exception as e:
        print(f"⚠️  Could not create example config: {e}")
        return False

def test_installation():
    """Test if Walk3r can be imported and run"""
    try:
        # Test basic import
        import app.cli_v2
        print("✅ Walk3r modules can be imported")
        
        # Test basic functionality
        from app.scanner import ModuleScanner
        from app.config import Walk3rConfig
        print("✅ Core components are working")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Walk3r 2.0 Setup Script")
    print("=" * 40)
    
    # Check system requirements
    if not check_python_version():
        return 1
    
    if not check_pip():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        return 1
    
    # Check optional Graphviz
    if not check_graphviz_system():
        suggest_graphviz_install()
        print("   (Visual graphs will not work without Graphviz, but analysis will still run)")
    
    # Create example configuration
    create_example_config()
    
    # Test installation
    if not test_installation():
        print("❌ Installation test failed")
        return 1
    
    # Success message
    print("\n🎉 Walk3r 2.0 setup complete!")
    print("\n📋 Next steps:")
    print("   1. Copy walk3r-example.toml to your project directory")
    print("   2. Rename it to walk3r.toml and customize settings")
    print("   3. Run: python -m app.cli_v2 scan")
    print("   4. Or run: python -m app.cli_v2 setup (for interactive configuration)")
    
    print("\n💡 Quick start:")
    print("   python -m app.cli_v2 quick    # Quick analysis with defaults")
    print("   python -m app.cli_v2 scan     # Full interactive analysis")
    
    print("\n🤖 For AI assistants:")
    print("   Upload the generated summary-YYYYMMDD.json file to ChatGPT or Claude")
    print("   Ask: 'Analyze this codebase and help me understand it'")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())