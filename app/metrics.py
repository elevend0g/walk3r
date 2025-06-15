# metrics.py

import ast
import os
from typing import Dict, List, Any
from pathlib import Path
from .config import should_ignore

class MetricsAnalyzer:
    """Analyzes basic code metrics like LOC, function counts, etc."""
    
    def __init__(self, root_path: str, module_data: Dict[str, Dict]):
        self.root_path = root_path
        self.module_data = module_data
        
    def analyze_metrics(self) -> Dict[str, Any]:
        """Analyze code metrics for all modules"""
        try:
            module_metrics = {}
            total_lines = 0
            total_functions = 0
            total_classes = 0
            total_files = 0
            
            for module_name, data in self.module_data.items():
                metrics = self._analyze_module_metrics(module_name)
                if metrics:
                    module_metrics[module_name] = metrics
                    total_lines += metrics['lines_of_code']
                    total_functions += metrics['function_count']
                    total_classes += metrics['class_count']
                    total_files += 1
            
            project_summary = self._generate_project_summary(
                total_files, total_lines, total_functions, total_classes, module_metrics
            )
            
            return {
                "explanation": "This analysis shows code size and structure metrics for each module, helping you understand the scope and complexity of different parts of your codebase.",
                "project_summary": project_summary,
                "module_metrics": module_metrics,
                "insights": self._generate_insights(module_metrics)
            }
            
        except Exception as e:
            return {
                "error": f"Metrics analysis failed: {str(e)}",
                "explanation": "Unable to complete metrics analysis, but this won't affect other analysis modes."
            }
    
    def _analyze_module_metrics(self, module_name: str) -> Dict[str, Any]:
        """Analyze metrics for a single module"""
        try:
            # Convert module name back to file path
            file_path = self._module_to_filepath(module_name)
            if not file_path or not os.path.exists(file_path):
                return {}
                
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
                
            tree = ast.parse(source)
            visitor = MetricsVisitor()
            visitor.visit(tree)
            
            lines_of_code = len([line for line in source.split('\n') if line.strip() and not line.strip().startswith('#')])
            total_lines = len(source.split('\n'))
            comment_lines = total_lines - lines_of_code
            
            return {
                "lines_of_code": lines_of_code,
                "total_lines": total_lines,
                "comment_lines": comment_lines,
                "comment_ratio": round(comment_lines / max(total_lines, 1), 2),
                "function_count": visitor.function_count,
                "class_count": visitor.class_count,
                "import_count": len(self.module_data.get(module_name, {}).get('imports', [])),
                "complexity_score": self._calculate_basic_complexity(visitor)
            }
            
        except Exception as e:
            print(f"Warning: Could not analyze metrics for {module_name}: {e}")
            return {}
    
    def _module_to_filepath(self, module_name: str) -> str:
        """Convert module name back to file path"""
        rel_path = module_name.replace('.', os.sep) + '.py'
        return os.path.join(self.root_path, rel_path)
    
    def _calculate_basic_complexity(self, visitor) -> int:
        """Calculate a basic complexity score"""
        # Simple heuristic: functions + classes + nested structures
        return visitor.function_count + visitor.class_count + visitor.nested_count
    
    def _generate_project_summary(self, total_files: int, total_lines: int, 
                                 total_functions: int, total_classes: int,
                                 module_metrics: Dict) -> Dict[str, Any]:
        """Generate human-readable project summary"""
        
        # Find largest modules
        largest_modules = sorted(
            [(name, metrics['lines_of_code']) for name, metrics in module_metrics.items()],
            key=lambda x: x[1], reverse=True
        )[:5]
        
        # Calculate averages
        avg_lines_per_file = round(total_lines / max(total_files, 1))
        avg_functions_per_file = round(total_functions / max(total_files, 1))
        
        return {
            "total_files": total_files,
            "total_lines_of_code": total_lines,
            "total_functions": total_functions,
            "total_classes": total_classes,
            "average_lines_per_file": avg_lines_per_file,
            "average_functions_per_file": avg_functions_per_file,
            "largest_modules": [{"name": name, "lines": lines} for name, lines in largest_modules],
            "project_size_category": self._categorize_project_size(total_lines, total_functions)
        }
    
    def _categorize_project_size(self, total_lines: int, total_functions: int) -> str:
        """Categorize project size for non-programmers"""
        if total_lines < 500:
            return "Small project - easy to understand and modify"
        elif total_lines < 2000:
            return "Medium project - moderate complexity, well-structured modules recommended"
        elif total_lines < 10000:
            return "Large project - significant codebase requiring careful organization"
        else:
            return "Very large project - enterprise-scale codebase requiring team coordination"
    
    def _generate_insights(self, module_metrics: Dict) -> List[str]:
        """Generate actionable insights from metrics"""
        insights = []
        
        # Check for very large modules
        large_modules = [name for name, metrics in module_metrics.items() 
                        if metrics['lines_of_code'] > 300]
        if large_modules:
            insights.append(f"Large modules detected: {', '.join(large_modules[:3])}. Consider breaking these into smaller, focused modules.")
        
        # Check for modules with low comment ratios
        poorly_commented = [name for name, metrics in module_metrics.items()
                           if metrics['comment_ratio'] < 0.1 and metrics['lines_of_code'] > 50]
        if poorly_commented:
            insights.append(f"Modules with few comments: {', '.join(poorly_commented[:3])}. Adding comments would improve maintainability.")
        
        # Check for modules with many functions
        function_heavy = [name for name, metrics in module_metrics.items()
                         if metrics['function_count'] > 20]
        if function_heavy:
            insights.append(f"Modules with many functions: {', '.join(function_heavy[:3])}. Consider grouping related functions into classes.")
        
        if not insights:
            insights.append("Code metrics look healthy - good balance of module sizes and documentation.")
            
        return insights


class MetricsVisitor(ast.NodeVisitor):
    """AST visitor to collect basic metrics"""
    
    def __init__(self):
        self.function_count = 0
        self.class_count = 0
        self.nested_count = 0
        self.depth = 0
        
    def visit_FunctionDef(self, node):
        self.function_count += 1
        if self.depth > 0:
            self.nested_count += 1
        self.depth += 1
        self.generic_visit(node)
        self.depth -= 1
        
    def visit_AsyncFunctionDef(self, node):
        self.function_count += 1
        if self.depth > 0:
            self.nested_count += 1
        self.depth += 1
        self.generic_visit(node)
        self.depth -= 1
        
    def visit_ClassDef(self, node):
        self.class_count += 1
        if self.depth > 0:
            self.nested_count += 1
        self.depth += 1
        self.generic_visit(node)
        self.depth -= 1