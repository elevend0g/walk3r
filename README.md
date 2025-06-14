# Walk3r

**Walk3r** is a Python static dependency mapper that scans your project and builds both module-level and function-level maps of imports and call relationships. Output is available in `.json`, `.csv`, and Graphviz `.dot`, `.svg`, `.png` formats — ideal for visualization, LLM ingestion, or architectural audits.

---

## 🔍 v0.1.1 Highlights

- 🧠 **Function-to-function call mapping** per module
- 📎 `functions-*.json` for structured analysis or AI ingestion
- 🗺️ Graph output: `functions-*.dot`, `.svg`, `.png`
- 🔗 Symlinks like `deps-latest.json`, `functions-latest.svg` for easy integration
- 🧾 Timestamped output like `deps-YYYYMMDD.json` to preserve history

---

## 📦 Features

- AST-based static module + function scanner
- Import + function call tracking
- Clean exports for:
  - Module-level: `deps-*.json`, `deps-*.csv`, `deps-*.dot`
  - Function-level: `functions-*.json`, `functions-*.dot`
- Auto-generated images: `.svg` and `.png`
- Config-driven CLI + Docker support
- `make run` or `python3 app/go_walk3r.py` for single-command analysis

---

## 🧠 Example Output

**Module Map:**
```json
"core.padma_api": {
  "imports": [...],
  "calls": [...],
  "functions": {
    "handle_request": ["parse_input", "store_memory"]
  }
}
```

**DOT Sample:**
```
"core.padma_api.handle_request" -> "memory.store_event"
```

---

## 🚀 Quick Start

```bash
make run
# or manually:
python3 app/go_walk3r.py
```

---

## 🛠️ Configuration

Edit `walk3r.toml`:

```toml
[walk3r]
root_path = "../padma/app"
output_dir = "../padma/walk3r"
formats = ["json", "csv", "dot"]
```

---

MIT License. Built for long-term insight with limited shenanigans.