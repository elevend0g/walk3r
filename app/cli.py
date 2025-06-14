# cli.py

import argparse
import sys
from .scanner import ModuleScanner
from .linker import DependencyLinker
from .exporter import export_json, export_csv, export_dot

def main():
    parser = argparse.ArgumentParser(description="Walk3r - Python Dependency Mapper")
    parser.add_argument("--path", required=True, help="Path to source directory")
    parser.add_argument("--format", choices=["json", "csv", "dot"], default="json", help="Export format")
    parser.add_argument("--output", default="dependency_graph", help="Output file name without extension")
    args = parser.parse_args()

    scanner = ModuleScanner(args.path)
    raw_data = scanner.scan()

    linker = DependencyLinker(raw_data)
    mapped = linker.resolve_links()

    output_path = f"{args.output}.{args.format}"
    if args.format == "json":
        export_json(mapped, output_path)
    elif args.format == "csv":
        export_csv(mapped, output_path)
    elif args.format == "dot":
        export_dot(mapped, output_path)

    print(f"✅ Dependency graph written to {output_path}")

if __name__ == "__main__":
    sys.exit(main())
