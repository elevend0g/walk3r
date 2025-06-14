# scanner.py

import ast
import os
from typing import Dict, Set, List, Tuple
from .config import should_ignore

class FunctionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.imports: Set[str] = set()
        self.calls: Set[str] = set()
        self.functions: Dict[str, Set[str]] = {}
        self.current_function: str = ""

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.add(node.module)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.current_function = node.name
        self.functions[self.current_function] = set()
        self.generic_visit(node)
        self.current_function = ""

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            call_str = f"{ast.unparse(node.func.value)}.{node.func.attr}"
        elif isinstance(node.func, ast.Name):
            call_str = node.func.id
        else:
            call_str = ast.unparse(node.func)

        self.calls.add(call_str)
        if self.current_function:
            self.functions[self.current_function].add(call_str)
        self.generic_visit(node)

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
        visitor = FunctionVisitor()
        visitor.visit(tree)

        return {
            "imports": sorted(visitor.imports),
            "calls": sorted(visitor.calls),
            "functions": {fn: sorted(calls) for fn, calls in visitor.functions.items()}
        }
