# go_walk3r.py

import toml
import subprocess
from datetime import datetime
from app.scanner import ModuleScanner
from app.linker import DependencyLinker
from app.exporter import export_json, export_csv, export_dot, export_function_map_json
from app.exporter import export_function_dot
from pathlib import Path
import os

def render_dot_to_images(dot_path: Path):
    svg_path = dot_path.with_suffix(".svg")
    png_path = dot_path.with_suffix(".png")

    subprocess.run(["dot", "-Tsvg", str(dot_path), "-o", str(svg_path)], check=True)
    subprocess.run(["dot", "-Tpng", str(dot_path), "-o", str(png_path)], check=True)

    print(f"🖼️  Rendered SVG: {svg_path}")
    print(f"🖼️  Rendered PNG: {png_path}")


def main():
    print(f"🔍 Starting from directory: {os.getcwd()}")
    
    cfg = toml.load("walk3r.toml")["walk3r"]
    print(f"🔍 Config loaded - root_path: '{cfg['root_path']}'")
    
    # Convert relative paths to absolute before directory change
    root = os.path.abspath(os.path.join(os.getcwd(), cfg["root_path"]))
    print(f"🔍 Resolved absolute path: {root}")
    print(f"🔍 Expected path: /home/jay/ag1/padma")
    print(f"🔍 Paths match: {root == '/home/jay/ag1/padma'}")
    print(f"🔍 Path exists: {os.path.exists(root)}")
    
    if os.path.exists(root):
        py_files = [f for f in os.listdir(root) if f.endswith('.py') or os.path.isdir(os.path.join(root, f))]
        print(f"🔍 Python files/dirs in target: {py_files[:5]}")
    
    out_dir = Path(os.path.abspath(os.path.join(os.getcwd(), cfg["output_dir"])))
    formats = cfg.get("formats", ["json"])

    out_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(out_dir)
    
    print(f"🔍 Changed to output dir: {os.getcwd()}")
    print(f"🔍 About to scan: {root}")

    scanner = ModuleScanner(root)
    raw_data = scanner.scan()
    
    print(f"🔍 Scanner found {len(raw_data)} modules:")
    for module in sorted(raw_data.keys())[:10]:
        print(f"   📁 {module}")
    
    # Rest of function continues...
    # Export function-level JSON
    fn_json_path = Path(f"functions-{date_tag}.json")
    export_function_map_json(function_map, fn_json_path)
    print(f"📎 Wrote function-level map to {fn_json_path}")

    # Export function-level DOT
    fn_dot_path = Path(f"functions-{date_tag}.dot")
    export_function_dot(function_map, fn_dot_path)
    render_dot_to_images(fn_dot_path)
    print(f"🧠 Wrote function-level graph to {fn_dot_path}")

if __name__ == "__main__":
    main()
