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
    cfg = toml.load("walk3r.toml")["walk3r"]
    # Convert relative paths to absolute before directory change
    root = os.path.abspath(os.path.join(os.getcwd(), cfg["root_path"]))
    out_dir = Path(os.path.abspath(os.path.join(os.getcwd(), cfg["output_dir"])))
    formats = cfg.get("formats", ["json"])

    out_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(out_dir)

    scanner = ModuleScanner(root)
    raw_data = scanner.scan()

    linker = DependencyLinker(raw_data)
    mapped = linker.resolve_links()
    function_map = linker.get_function_map()

    date_tag = datetime.now().strftime("%Y%m%d")

    for fmt in formats:
        out_path = Path(f"deps-{date_tag}.{fmt}")
        if fmt == "json":
            export_json(mapped, out_path)
        elif fmt == "csv":
            export_csv(mapped, out_path)
        elif fmt == "dot":
            export_dot(mapped, out_path)
            render_dot_to_images(out_path)

        print(f"✅ Wrote {fmt.upper()} to {out_path}")

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
