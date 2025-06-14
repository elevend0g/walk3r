# linker.py

from typing import Dict, Set

class DependencyLinker:
    def __init__(self, module_data: Dict[str, Dict]):
        self.module_data = module_data
        self.linked_map: Dict[str, Dict[str, Set[str]]] = {}

    def resolve_links(self) -> Dict[str, Dict[str, Set[str]]]:
        for module, data in self.module_data.items():
            self.linked_map[module] = {
                "imports": set(),
                "calls": set()
            }
            for imported in data.get("imports", []):
                if self._is_local_module(imported):
                    self.linked_map[module]["imports"].add(imported)
            for called in data.get("calls", []):
                mod_guess = self._guess_module(called)
                if mod_guess and mod_guess != module:
                    self.linked_map[module]["calls"].add(mod_guess)
        return self.linked_map

    def _is_local_module(self, module_name: str) -> bool:
        return module_name in self.module_data

    def _guess_module(self, symbol: str) -> str:
        # Heuristic: if a symbol starts with a known module name, return that
        for mod in self.module_data:
            if symbol.startswith(mod.split(".")[-1]):
                return mod
        return ""
