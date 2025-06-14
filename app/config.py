# config.py

# Future config structure for Walk3r dependency mapping

DEFAULT_IGNORES = [
    "__init__",
    "tests",
    "site-packages",
    "venv",
    "__pycache__",
    "build",
    "dist"
]

def should_ignore(path: str) -> bool:
    return any(ignored in path for ignored in DEFAULT_IGNORES)
