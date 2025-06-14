# exporter.py

import json
import csv
from pathlib import Path
from typing import Dict, Set

def export_json(dependency_map: Dict[str, Dict[str, Set[str]]], output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({k: {ik: list(iv) for ik, iv in v.items()} for k, v in dependency_map.items()}, f, indent=2)

def export_csv(dependency_map: Dict[str, Dict[str, Set[str]]], output_path: str):
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Source", "Type", "Target"])
        for source, links in dependency_map.items():
            for target in links.get("imports", []):
                writer.writerow([source, "import", target])
            for target in links.get("calls", []):
                writer.writerow([source, "call", target])

def export_dot(dependency_map: Dict[str, Dict[str, Set[str]]], output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("digraph G {\n")
        f.write("  rankdir=LR;\n  node [shape=box, style=rounded, fontname=Courier, fontsize=10];\n")
        for source, links in dependency_map.items():
            for target in links.get("imports", []):
                f.write(f'  "{source}" -> "{target}" [label="import"];\n')
            for target in links.get("calls", []):
                f.write(f'  "{source}" -> "{target}" [label="call"];\n')
        f.write("}\n")

def export_function_map_json(function_map: Dict[str, Dict[str, Set[str]]], output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({k: {fn: list(calls) for fn, calls in v.items()} for k, v in function_map.items()}, f, indent=2)

def export_function_dot(function_map: Dict[str, Dict[str, Set[str]]], output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("digraph FunctionGraph {\n")
        f.write("  rankdir=LR;\n  node [shape=ellipse, style=filled, fillcolor=lightgray, fontname=Courier, fontsize=10];\n")
        for module, functions in function_map.items():
            for func, calls in functions.items():
                full_func = f"{module}.{func}"
                for call in calls:
                    f.write(f'  "{full_func}" -> "{call}";\n')
        f.write("}\n")
