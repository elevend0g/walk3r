# Walk3r

**Walk3r** is a Python static dependency mapper that scans your project and builds a module-level map of imports and call relationships. Outputs are exportable as `.json`, `.csv`, or Graphviz `.dot` files — perfect for visualization, knowledge graph ingestion, or LLM fine-tuning.

---

## 📦 Features

- 🧠 Static analysis via `ast`
- 📎 Maps both `imports` and `calls`
- 🔍 Ignores noise (`venv`, `__pycache__`, etc.)
- 🧾 Exports to `json`, `csv`, or `dot`
- 🧩 Modular CLI-ready architecture

---

## 🚀 Usage

From project root:

```bash
python3 -m app.cli --path ../padma/app --format json --output padma_graph
