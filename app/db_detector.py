# db_detector.py

import ast
import os
from typing import Dict, List, Set, Any
from dataclasses import dataclass
from .config import should_ignore

@dataclass
class DatabaseOperation:
    """Represents a detected database operation"""
    module: str
    function: str
    operation_type: str
    call_signature: str
    line_number: int
    purpose_guess: str

class DatabaseCallDetector:
    """Detects database operations and analyzes data access patterns"""
    
    def __init__(self, root_path: str, module_data: Dict[str, Dict], config):
        self.root_path = root_path
        self.module_data = module_data
        self.db_methods = set(getattr(config, 'db_methods', [
            "execute", "query", "find", "insert", "update", "delete",
            "save", "create", "drop", "select", "commit", "rollback"
        ]))
        self.db_modules = set(getattr(config, 'db_modules', [
            "sqlite3", "sqlalchemy", "pymongo", "psycopg2", "mysql",
            "redis", "cassandra", "elasticsearch", "django.db"
        ]))
        
    def detect_db_calls(self) -> Dict[str, Any]:
        """Detect and analyze database operations across all modules"""
        try:
            all_operations = []
            modules_with_db = set()
            
            for module_name in self.module_data.keys():
                operations = self._analyze_module_db_calls(module_name)
                if operations:
                    all_operations.extend(operations)
                    modules_with_db.add(module_name)
            
            # Categorize operations
            read_ops = [op for op in all_operations if self._is_read_operation(op.operation_type)]
            write_ops = [op for op in all_operations if self._is_write_operation(op.operation_type)]
            
            # Group by module
            operations_by_module = self._group_operations_by_module(all_operations)
            
            return {
                "explanation": "This analysis shows all database operations in your codebase. Understanding data flow helps identify performance bottlenecks and ensures proper data handling.",
                "database_summary": {
                    "modules_with_db_access": len(modules_with_db),
                    "total_db_operations": len(all_operations),
                    "read_operations": len(read_ops),
                    "write_operations": len(write_ops),
                    "modules_list": sorted(list(modules_with_db))
                },
                "db_operations_by_module": operations_by_module,
                "architectural_analysis": self._analyze_architecture(operations_by_module),
                "potential_issues": self._identify_potential_issues(all_operations),
                "recommendations": self._generate_recommendations(operations_by_module)
            }
            
        except Exception as e:
            return {
                "error": f"Database detection failed: {str(e)}",
                "explanation": "Unable to complete database analysis, but this won't affect other analysis modes."
            }
    
    def _analyze_module_db_calls(self, module_name: str) -> List[DatabaseOperation]:
        """Analyze database calls in a single module"""
        try:
            file_path = self._module_to_filepath(module_name)
            if not file_path or not os.path.exists(file_path):
                return []
                
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
                
            tree = ast.parse(source)
            visitor = DatabaseVisitor(self.db_methods, self.db_modules, module_name)
            visitor.visit(tree)
            
            return visitor.operations
            
        except Exception as e:
            print(f"Warning: Could not analyze database calls for {module_name}: {e}")
            return []
    
    def _module_to_filepath(self, module_name: str) -> str:
        """Convert module name back to file path"""
        rel_path = module_name.replace('.', os.sep) + '.py'
        return os.path.join(self.root_path, rel_path)
    
    def _is_read_operation(self, op_type: str) -> bool:
        """Check if operation is a read operation"""
        read_ops = {"query", "find", "select", "get", "fetch", "read", "search"}
        return any(read_op in op_type.lower() for read_op in read_ops)
    
    def _is_write_operation(self, op_type: str) -> bool:
        """Check if operation is a write operation"""
        write_ops = {"insert", "update", "delete", "save", "create", "drop", "commit", "write"}
        return any(write_op in op_type.lower() for write_op in write_ops)
    
    def _group_operations_by_module(self, operations: List[DatabaseOperation]) -> Dict[str, Dict]:
        """Group operations by module for reporting"""
        grouped = {}
        
        for op in operations:
            if op.module not in grouped:
                grouped[op.module] = {
                    "operations": [],
                    "operation_count": 0,
                    "read_count": 0,
                    "write_count": 0,
                    "notes": ""
                }
            
            grouped[op.module]["operations"].append({
                "function": op.function,
                "operation_type": op.operation_type,
                "call_signature": op.call_signature,
                "line_number": op.line_number,
                "purpose": op.purpose_guess
            })
            
            grouped[op.module]["operation_count"] += 1
            
            if self._is_read_operation(op.operation_type):
                grouped[op.module]["read_count"] += 1
            elif self._is_write_operation(op.operation_type):
                grouped[op.module]["write_count"] += 1
        
        # Add architectural notes
        for module, data in grouped.items():
            data["notes"] = self._generate_module_notes(module, data)
        
        return grouped
    
    def _generate_module_notes(self, module: str, data: Dict) -> str:
        """Generate notes about module's database usage"""
        notes = []
        
        if data["operation_count"] > 10:
            notes.append("Heavy database usage - consider caching or optimization")
        
        if data["write_count"] == 0:
            notes.append("Read-only module - good for query/reporting functions")
        elif data["read_count"] == 0:
            notes.append("Write-only module - likely data processing or ETL")
        
        if "database" in module.lower() or "db" in module.lower():
            notes.append("Dedicated database module - good separation of concerns")
        
        return "; ".join(notes) if notes else "Standard database usage patterns"
    
    def _analyze_architecture(self, operations_by_module: Dict) -> Dict[str, Any]:
        """Analyze overall database architecture patterns"""
        total_modules = len(operations_by_module)
        
        # Find modules that might be database layers
        db_layer_modules = [
            module for module in operations_by_module.keys()
            if any(keyword in module.lower() for keyword in ["database", "db", "model", "dao", "repository"])
        ]
        
        # Find modules that directly access DB (not through layers)
        direct_db_modules = [
            module for module in operations_by_module.keys()
            if module not in db_layer_modules and operations_by_module[module]["operation_count"] > 0
        ]
        
        return {
            "total_modules_with_db": total_modules,
            "dedicated_db_modules": db_layer_modules,
            "modules_with_direct_access": direct_db_modules,
            "architecture_pattern": self._identify_architecture_pattern(db_layer_modules, direct_db_modules),
            "separation_quality": self._assess_separation_quality(db_layer_modules, direct_db_modules)
        }
    
    def _identify_architecture_pattern(self, db_layers: List[str], direct_access: List[str]) -> str:
        """Identify the database architecture pattern"""
        if len(db_layers) > 0 and len(direct_access) == 0:
            return "Layered architecture - all database access goes through dedicated modules"
        elif len(db_layers) > 0 and len(direct_access) > 0:
            return "Mixed architecture - some modules use database layers, others access directly"
        elif len(direct_access) > 0:
            return "Direct access pattern - modules interact with database directly"
        else:
            return "No clear pattern detected"
    
    def _assess_separation_quality(self, db_layers: List[str], direct_access: List[str]) -> str:
        """Assess the quality of database separation"""
        if len(db_layers) > 0 and len(direct_access) <= 1:
            return "Good - database access is well-centralized"
        elif len(direct_access) <= len(db_layers):
            return "Fair - mostly centralized with some direct access"
        else:
            return "Poor - database access is scattered across many modules"
    
    def _identify_potential_issues(self, operations: List[DatabaseOperation]) -> List[str]:
        """Identify potential database-related issues"""
        issues = []
        
        # Check for SQL injection risks
        sql_operations = [op for op in operations if self._might_be_sql(op.call_signature)]
        if sql_operations:
            issues.append(f"Found {len(sql_operations)} potential SQL operations - ensure proper parameter binding to prevent SQL injection")
        
        # Check for modules with many DB operations
        module_counts = {}
        for op in operations:
            module_counts[op.module] = module_counts.get(op.module, 0) + 1
        
        heavy_modules = [module for module, count in module_counts.items() if count > 15]
        if heavy_modules:
            issues.append(f"Modules with many DB operations: {', '.join(heavy_modules)} - consider performance optimization")
        
        # Check for missing error handling patterns
        if len(operations) > 5:
            issues.append("With multiple database operations, ensure proper error handling and transaction management")
        
        return issues
    
    def _might_be_sql(self, call_signature: str) -> bool:
        """Check if a call signature might involve SQL"""
        sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "FROM", "WHERE"]
        return any(keyword in call_signature.upper() for keyword in sql_keywords)
    
    def _generate_recommendations(self, operations_by_module: Dict) -> List[str]:
        """Generate recommendations for database architecture"""
        recommendations = []
        
        total_modules = len(operations_by_module)
        
        if total_modules > 3:
            recommendations.append("Consider centralizing database operations into a dedicated data access layer")
        
        # Check for mixed read/write patterns
        mixed_modules = [
            module for module, data in operations_by_module.items()
            if data["read_count"] > 0 and data["write_count"] > 0
        ]
        
        if len(mixed_modules) > 2:
            recommendations.append("Consider separating read and write operations for better performance and testing")
        
        if not recommendations:
            recommendations.append("Database access patterns look well-organized")
        
        return recommendations


class DatabaseVisitor(ast.NodeVisitor):
    """AST visitor to detect database operations"""
    
    def __init__(self, db_methods: Set[str], db_modules: Set[str], module_name: str):
        self.db_methods = db_methods
        self.db_modules = db_modules
        self.module_name = module_name
        self.operations = []
        self.current_function = "module_level"
        self.imports = set()
        
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.add(node.module)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function
    
    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)
    
    def visit_Call(self, node):
        call_str = self._get_call_string(node)
        
        # Check if this looks like a database operation
        if self._is_database_call(call_str, node):
            operation = DatabaseOperation(
                module=self.module_name,
                function=self.current_function,
                operation_type=self._extract_operation_type(call_str),
                call_signature=call_str,
                line_number=node.lineno,
                purpose_guess=self._guess_purpose(call_str, self.current_function)
            )
            self.operations.append(operation)
        
        self.generic_visit(node)
    
    def _get_call_string(self, node) -> str:
        """Extract call signature as string"""
        try:
            return ast.unparse(node)
        except:
            # Fallback for older Python versions
            if isinstance(node.func, ast.Attribute):
                return f"{ast.unparse(node.func.value) if hasattr(ast, 'unparse') else 'object'}.{node.func.attr}"
            elif isinstance(node.func, ast.Name):
                return node.func.id
            else:
                return "unknown_call"
    
    def _is_database_call(self, call_str: str, node) -> bool:
        """Determine if a call is likely a database operation"""
        # Check method names
        for method in self.db_methods:
            if method in call_str.lower():
                return True
        
        # Check if calling methods on imported database modules
        for db_module in self.db_modules:
            if any(imp.startswith(db_module) for imp in self.imports):
                return True
        
        # Check for SQL-like strings in arguments
        if hasattr(node, 'args'):
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    if any(keyword in arg.value.upper() for keyword in ["SELECT", "INSERT", "UPDATE", "DELETE"]):
                        return True
        
        return False
    
    def _extract_operation_type(self, call_str: str) -> str:
        """Extract the type of database operation"""
        call_lower = call_str.lower()
        
        # Try to identify specific operation types
        for method in self.db_methods:
            if method in call_lower:
                return method
        
        # Check for SQL keywords
        sql_keywords = {
            "select": "query",
            "insert": "insert", 
            "update": "update",
            "delete": "delete",
            "create": "create",
            "drop": "drop"
        }
        
        for keyword, op_type in sql_keywords.items():
            if keyword in call_lower:
                return op_type
        
        return "unknown_db_operation"
    
    def _guess_purpose(self, call_str: str, function_name: str) -> str:
        """Guess the purpose of the database operation"""
        call_lower = call_str.lower()
        func_lower = function_name.lower()
        
        # Common patterns
        if any(word in func_lower for word in ["login", "auth", "verify"]):
            return "User authentication or verification"
        elif any(word in func_lower for word in ["create", "add", "insert"]):
            return "Creating new records"
        elif any(word in func_lower for word in ["update", "modify", "edit"]):
            return "Updating existing data"
        elif any(word in func_lower for word in ["delete", "remove"]):
            return "Removing data"
        elif any(word in func_lower for word in ["get", "find", "fetch", "load"]):
            return "Retrieving data"
        elif "user" in call_lower:
            return "User data operations"
        elif any(word in call_lower for word in ["product", "item", "order"]):
            return "Business data operations"
        else:
            return "General database operation"