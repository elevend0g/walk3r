# config.py

from dataclasses import dataclass, field
from typing import List, Dict

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

@dataclass
class Walk3rConfig:
    """Configuration for Walk3r analysis modes"""
    root_path: str
    output_dir: str
    formats: List[str]
    
    # Long walk mode settings
    enable_complexity: bool = True
    enable_db_detection: bool = True
    enable_db_compliance: bool = True
    enable_doc_coverage: bool = True
    enable_metrics: bool = True
    enable_summary: bool = True
    
    # Database detection customization
    db_methods: List[str] = field(default_factory=lambda: [
        "execute", "query", "find", "insert", "update", "delete",
        "save", "create", "drop", "select", "commit", "rollback"
    ])
    db_modules: List[str] = field(default_factory=lambda: [
        "sqlite3", "sqlalchemy", "pymongo", "psycopg2", "mysql",
        "redis", "cassandra", "elasticsearch", "django.db"
    ])
    
    # Complexity thresholds
    max_function_length: int = 30
    max_complexity_score: int = 10
    max_parameter_count: int = 6
    
    # Database compliance patterns
    violation_patterns: Dict[str, List[str]] = field(default_factory=dict)
    service_patterns: Dict[str, List[str]] = field(default_factory=dict)

def should_ignore(path: str) -> bool:
    return any(ignored in path for ignored in DEFAULT_IGNORES)
