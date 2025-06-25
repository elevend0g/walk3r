@echo off
REM Walk3r 2.0 One-Click Installer for Windows

echo 🚀 Walk3r 2.0 One-Click Installer
echo =================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo 🐍 Found Python %PYTHON_VERSION%

REM Check Python version compatibility
python -c "import sys; exit(0 if (sys.version_info.major == 3 and sys.version_info.minor >= 8) or sys.version_info.major > 3 else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 3.8+ required. Found Python %PYTHON_VERSION%
    pause
    exit /b 1
)

REM Check if pip is available
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip not found. Please ensure Python is properly installed with pip
    pause
    exit /b 1
)

echo 📦 Installing Python dependencies...
python -m pip install --user toml rich>=12.0.0 graphviz networkx

if %errorlevel% neq 0 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)

echo ⚙️ Running setup script...
python setup.py

if %errorlevel% neq 0 (
    echo ❌ Setup failed
    pause
    exit /b 1
)

echo.
echo ⚠️ NOTE: For visual graphs, install Graphviz:
echo    • Download from: https://graphviz.org/download/
echo    • Or use chocolatey: choco install graphviz
echo.

echo 🎉 Walk3r 2.0 installation complete!
echo.
echo 📋 Quick start:
echo    python -m app.cli_v2 scan     # Interactive analysis
echo    python -m app.cli_v2 quick    # Quick analysis
echo    python -m app.cli_v2 setup    # Configure only
echo.
echo 📚 Documentation: https://github.com/elevend0g/walk3r
echo 🐛 Issues: https://github.com/elevend0g/walk3r/issues
echo.
pause