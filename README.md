# Walk3r 2.0

**Walk3r** is an easy-to-use static analysis tool designed for non-programmers and AI assistant integration. It analyzes your Python projects and creates comprehensive reports perfect for understanding codebases, getting AI coding help, and identifying improvement opportunities.

🎯 **Perfect for**: Code reviews, onboarding, AI assistant context, technical debt analysis

---

## ✨ What's New in 2.0

- 🚀 **Zero-config setup** - Auto-detects projects and creates smart defaults
- 🎨 **Beautiful CLI** - Interactive wizards, progress bars, and rich output
- 🤖 **AI-ready exports** - Optimized files for ChatGPT, Claude, and other assistants
- 📊 **Comprehensive analysis** - Dependencies, complexity, documentation, databases
- 🔧 **One-click install** - Automated setup scripts for all platforms
- 📋 **Plain English reports** - Human-readable summaries alongside technical data

---

## 🚀 Quick Start

### Option 1: One-Click Install (Recommended)

**Linux/macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/elevend0g/walk3r/main/install.sh | bash
```

**Windows:**
```batch
# Download and run install.bat from the repository
```

### Option 2: Manual Install

```bash
# Clone the repository
git clone https://github.com/elevend0g/walk3r.git
cd walk3r

# Run setup
python setup.py

# Start analyzing
python -m app.cli_v2 scan
```

---

## 🎯 Usage

### Interactive Mode (Recommended for beginners)
```bash
python -m app.cli_v2 scan
```
- Auto-detects your project
- Interactive configuration wizard
- Progress indicators and helpful tips
- Opens results when complete

### Quick Analysis
```bash
python -m app.cli_v2 quick /path/to/your/project
```

### Configuration Only
```bash
python -m app.cli_v2 setup
```

---

## 📊 What You Get

Walk3r 2.0 generates comprehensive analysis files:

| File | Description | Use Case |
|------|-------------|----------|
| `summary-YYYYMMDD.json` | Human-readable project overview | Upload to AI assistants |
| `deps-YYYYMMDD.json` | Module dependency graph | Understand code relationships |
| `functions-YYYYMMDD.json` | Function call mapping | Deep code analysis |
| `complexity-YYYYMMDD.json` | Code complexity analysis | Find refactoring opportunities |
| `db-calls-YYYYMMDD.json` | Database operation analysis | Review data access patterns |
| `doc-coverage-YYYYMMDD.json` | Documentation coverage | Improve code documentation |

---

## 🤖 AI Assistant Integration

Walk3r 2.0 is optimized for AI coding assistants:

### ChatGPT/Claude Usage:
1. Run `python -m app.cli_v2 scan --ai-ready`
2. Upload `summary-YYYYMMDD.json` to your AI assistant
3. Ask: *"Analyze this codebase and help me understand it"*

### Common AI Prompts:
- *"Help me refactor the complex functions"* → Upload `complexity-YYYYMMDD.json`
- *"Explain the architecture"* → Upload `deps-YYYYMMDD.json`
- *"Review database usage"* → Upload `db-calls-YYYYMMDD.json`
- *"Add documentation"* → Upload `doc-coverage-YYYYMMDD.json`

---

## 🛠️ Configuration

Walk3r auto-generates configuration, but you can customize `walk3r.toml`:

```bash
# Copy the example configuration
cp walk3r.toml.example walk3r.toml
# Then edit walk3r.toml for your needs
```

```toml
[walk3r]
root_path = "."                    # Your project path
output_dir = "./walk3r_reports"    # Where to save results
formats = ["json", "csv"]          # Export formats

# Analysis features (enable/disable)
enable_complexity = true           # Code complexity analysis
enable_db_detection = true         # Database operation detection
enable_doc_coverage = true         # Documentation coverage
enable_metrics = true              # Code statistics
enable_summary = true              # Human-readable summaries
enable_db_compliance = true        # Database architecture compliance

# Complexity thresholds
max_function_length = 30           # Flag long functions
max_complexity_score = 10          # Flag complex functions
max_parameter_count = 6            # Flag functions with many parameters
```

---

## 🧠 Example Analysis Output

**Human-Readable Summary:**
```json
{
  "project_overview": {
    "description": "Medium-sized Python web application with 45 modules",
    "architecture": "Well-structured with clear separation of concerns",
    "main_components": ["API handlers", "Database models", "Business logic"],
    "key_findings": [
      "✅ Good documentation coverage (78%)",
      "⚠️ 3 functions need complexity reduction",
      "🎯 Database access properly centralized"
    ]
  }
}
```

**AI-Ready Context:**
```json
{
  "for_ai_assistant": {
    "quick_summary": "This is a Flask web app with SQLAlchemy ORM...",
    "help_areas": ["Performance optimization", "Test coverage", "Error handling"],
    "safe_to_modify": ["utils.py", "config.py"],
    "requires_caution": ["core/database.py", "auth/security.py"]
  }
}
```

---

## 🆚 Version Comparison

| Feature | Walk3r 1.x | Walk3r 2.0 |
|---------|-------------|-------------|
| Setup | Manual config required | Auto-setup wizard |
| Output | Technical files only | Human-readable + technical |
| CLI | Basic commands | Interactive, rich interface |
| AI Integration | None | Optimized exports |
| Analysis | Dependencies only | 7 analysis types |
| Documentation | Minimal | Comprehensive |

---

## 🏗️ Architecture Analysis

Walk3r 2.0 includes advanced architecture analysis:

- **Database Compliance**: Checks if database access follows best practices
- **Complexity Hotspots**: Identifies functions that need refactoring
- **Documentation Gaps**: Shows where to add comments and docstrings
- **Dependency Health**: Flags circular dependencies and tight coupling

---

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/elevend0g/walk3r.git
cd walk3r
pip install -e .[dev]
pytest
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🆘 Support

- 📚 **Documentation**: [GitHub Wiki](https://github.com/elevend0g/walk3r/wiki)
- 🐛 **Issues**: [GitHub Issues](https://github.com/elevend0g/walk3r/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/elevend0g/walk3r/discussions)

---

*Walk3r 2.0: Making code analysis accessible to everyone* 🚀