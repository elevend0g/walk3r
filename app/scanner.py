# scanner.py

import ast
import os
from typing import List, Dict, Set
from .config import should_ignore

class ModuleScanner:
    def __init__(self, root_path: str):
        self.root_path = os.path.abspath(root_path)
        self.module_map: Dict[str, Dict] = {}

    def scan(self) -> Dict[str, Dict]:
        for dirpath, _, filenames in os.walk(self.root_path):
            if should_ignore(dirpath):
                continue
            for filename in filenames:
                if filename.endswith(".py"):
                    filepath = os.path.join(dirpath, filename)
                    if should_ignore(filepath):
                        continue
                    module_name = self._module_name_from_path(filepath)
                    self.module_map[module_name] = self._parse_file(filepath)
        return self.module_map

    def _module_name_from_path(self, path: str) -> str:
        rel_path = os.path.relpath(path, self.root_path)
        module = rel_path.replace(os.sep, ".")
        return module[:-3] if module.endswith(".py") else module

    def _parse_file(self, filepath: str) -> Dict:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=filepath)

        imports: Set[str] = set()
        calls: Set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    calls.add(f"{ast.unparse(node.func.value)}.{node.func.attr}")
                elif isinstance(node.func, ast.Name):
                    calls.add(node.func.id)

        return {
            "imports": sorted(imports),
            "calls": sorted(calls),
        }
