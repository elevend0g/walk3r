# doc_coverage.py

import ast
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from .config import should_ignore

@dataclass
class DocumentationIssue:
    """Represents a documentation issue"""
    location: str
    issue_type: str
    severity: str
    description: str
    suggestion: str

class DocCoverageAnalyzer:
    """Analyzes documentation coverage including docstrings, type hints, and comments"""
    
    def __init__(self, root_path: str, module_data: Dict[str, Dict]):
        self.root_path = root_path
        self.module_data = module_data
        
    def analyze_documentation(self) -> Dict[str, Any]:
        """Analyze documentation coverage across all modules"""
        try:
            all_issues = []
            module_coverage = {}
            total_functions = 0
            documented_functions = 0
            total_classes = 0
            documented_classes = 0
            
            for module_name in self.module_data.keys():
                coverage, issues = self._analyze_module_documentation(module_name)
                if coverage:
                    module_coverage[module_name] = coverage
                    all_issues.extend(issues)
                    
                    # Update totals
                    total_functions += coverage["total_functions"]
                    documented_functions += coverage["documented_functions"]
                    total_classes += coverage["total_classes"]
                    documented_classes += coverage["documented_classes"]
            
            overall_function_coverage = (documented_functions / max(total_functions, 1)) * 100
            overall_class_coverage = (documented_classes / max(total_classes, 1)) * 100
            
            return {
                "explanation": "This analysis shows how well your code is documented. Good documentation makes code easier to understand and maintain, especially for team projects.",
                "coverage_summary": {
                    "total_functions": total_functions,
                    "documented_functions": documented_functions,
                    "function_coverage_percentage": round(overall_function_coverage, 1),
                    "total_classes": total_classes,
                    "documented_classes": documented_classes,
                    "class_coverage_percentage": round(overall_class_coverage, 1),
                    "overall_quality": self._assess_overall_quality(overall_function_coverage, overall_class_coverage)
                },
                "module_coverage": module_coverage,
                "documentation_issues": self._prioritize_issues(all_issues),
                "recommendations": self._generate_recommendations(overall_function_coverage, all_issues)
            }
            
        except Exception as e:
            return {
                "error": f"Documentation analysis failed: {str(e)}",
                "explanation": "Unable to complete documentation analysis, but this won't affect other analysis modes."
            }
    
    def _analyze_module_documentation(self, module_name: str) -> tuple:
        """Analyze documentation for a single module"""
        try:
            file_path = self._module_to_filepath(module_name)
            if not file_path or not os.path.exists(file_path):
                return {}, []
                
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
                
            tree = ast.parse(source)
            visitor = DocumentationVisitor(module_name)
            visitor.visit(tree)
            
            # Calculate coverage statistics
            total_functions = len(visitor.functions)
            documented_functions = len([f for f in visitor.functions.values() if f["has_docstring"]])
            
            total_classes = len(visitor.classes)
            documented_classes = len([c for c in visitor.classes.values() if c["has_docstring"]])
            
            function_coverage = (documented_functions / max(total_functions, 1)) * 100
            class_coverage = (documented_classes / max(total_classes, 1)) * 100
            
            # Identify issues
            issues = self._identify_documentation_issues(module_name, visitor)
            
            coverage = {
                "total_functions": total_functions,
                "documented_functions": documented_functions,
                "function_coverage_percentage": round(function_coverage, 1),
                "total_classes": total_classes,
                "documented_classes": documented_classes,
                "class_coverage_percentage": round(class_coverage, 1),
                "has_module_docstring": visitor.module_docstring is not None,
                "type_hint_usage": self._assess_type_hint_usage(visitor),
                "comment_density": self._calculate_comment_density(source),
                "quality_score": self._calculate_quality_score(function_coverage, class_coverage, visitor)
            }
            
            return coverage, issues
            
        except Exception as e:
            print(f"Warning: Could not analyze documentation for {module_name}: {e}")
            return {}, []
    
    def _module_to_filepath(self, module_name: str) -> str:
        """Convert module name back to file path"""
        rel_path = module_name.replace('.', os.sep) + '.py'
        return os.path.join(self.root_path, rel_path)
    
    def _identify_documentation_issues(self, module_name: str, visitor) -> List[DocumentationIssue]:
        """Identify specific documentation issues"""
        issues = []
        
        # Check for missing module docstring
        if visitor.module_docstring is None and len(visitor.functions) > 3:
            issues.append(DocumentationIssue(
                location=module_name,
                issue_type="missing_module_docstring",
                severity="medium",
                description="Module lacks a docstring explaining its purpose",
                suggestion="Add a module-level docstring at the top of the file describing what this module does"
            ))
        
        # Check undocumented functions
        for func_name, func_data in visitor.functions.items():
            if not func_data["has_docstring"] and func_data["line_count"] > 5:
                issues.append(DocumentationIssue(
                    location=f"{module_name}.{func_name}",
                    issue_type="missing_function_docstring",
                    severity="medium" if func_data["line_count"] > 15 else "low",
                    description=f"Function {func_name} lacks documentation",
                    suggestion="Add a docstring explaining what this function does, its parameters, and return value"
                ))
            
            # Check for missing type hints on longer functions
            if not func_data["has_type_hints"] and func_data["line_count"] > 10:
                issues.append(DocumentationIssue(
                    location=f"{module_name}.{func_name}",
                    issue_type="missing_type_hints",
                    severity="low",
                    description=f"Function {func_name} lacks type hints",
                    suggestion="Add type hints to parameters and return value for better code clarity"
                ))
        
        # Check undocumented classes
        for class_name, class_data in visitor.classes.items():
            if not class_data["has_docstring"]:
                issues.append(DocumentationIssue(
                    location=f"{module_name}.{class_name}",
                    issue_type="missing_class_docstring",
                    severity="medium",
                    description=f"Class {class_name} lacks documentation",
                    suggestion="Add a class docstring explaining the purpose and usage of this class"
                ))
        
        return issues
    
    def _assess_type_hint_usage(self, visitor) -> str:
        """Assess type hint usage quality"""
        total_functions = len(visitor.functions)
        if total_functions == 0:
            return "No functions to analyze"
        
        type_hinted_functions = len([f for f in visitor.functions.values() if f["has_type_hints"]])
        coverage = (type_hinted_functions / total_functions) * 100
        
        if coverage >= 80:
            return "Excellent - most functions have type hints"
        elif coverage >= 60:
            return "Good - many functions have type hints"
        elif coverage >= 30:
            return "Fair - some functions have type hints"
        else:
            return "Poor - few functions have type hints"
    
    def _calculate_comment_density(self, source: str) -> Dict[str, Any]:
        """Calculate comment density in the source code"""
        lines = source.split('\n')
        total_lines = len(lines)
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        
        density = (comment_lines / max(total_lines, 1)) * 100
        
        return {
            "comment_lines": comment_lines,
            "total_lines": total_lines,
            "density_percentage": round(density, 1),
            "quality": "Good" if density > 15 else "Fair" if density > 5 else "Low"
        }
    
    def _calculate_quality_score(self, function_coverage: float, class_coverage: float, visitor) -> Dict[str, Any]:
        """Calculate overall documentation quality score"""
        score = 0
        max_score = 100
        
        # Function documentation (40 points)
        score += (function_coverage / 100) * 40
        
        # Class documentation (30 points)
        if visitor.classes:
            score += (class_coverage / 100) * 30
        else:
            # If no classes, redistribute points to functions
            score += (function_coverage / 100) * 30
        
        # Module docstring (15 points)
        if visitor.module_docstring:
            score += 15
        
        # Type hints (15 points)
        total_functions = len(visitor.functions)
        if total_functions > 0:
            type_hinted = len([f for f in visitor.functions.values() if f["has_type_hints"]])
            score += (type_hinted / total_functions) * 15
        
        return {
            "score": round(score, 1),
            "grade": self._score_to_grade(score),
            "description": self._describe_quality(score)
        }
    
    def _score_to_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _describe_quality(self, score: float) -> str:
        """Describe documentation quality"""
        if score >= 90:
            return "Excellent documentation - very maintainable codebase"
        elif score >= 80:
            return "Good documentation - well-maintained code"
        elif score >= 70:
            return "Fair documentation - some areas need improvement"
        elif score >= 60:
            return "Poor documentation - significant improvements needed"
        else:
            return "Very poor documentation - major maintainability concerns"
    
    def _assess_overall_quality(self, func_coverage: float, class_coverage: float) -> str:
        """Assess overall documentation quality"""
        avg_coverage = (func_coverage + class_coverage) / 2
        
        if avg_coverage >= 80:
            return "Excellent - well documented codebase"
        elif avg_coverage >= 60:
            return "Good - mostly documented with some gaps"
        elif avg_coverage >= 40:
            return "Fair - moderate documentation coverage"
        elif avg_coverage >= 20:
            return "Poor - significant documentation gaps"
        else:
            return "Very poor - minimal documentation"
    
    def _prioritize_issues(self, issues: List[DocumentationIssue]) -> Dict[str, List[Dict]]:
        """Prioritize and format issues for output"""
        high_priority = [issue for issue in issues if issue.severity == "high"]
        medium_priority = [issue for issue in issues if issue.severity == "medium"]
        low_priority = [issue for issue in issues if issue.severity == "low"]
        
        return {
            "high_priority": [self._format_issue(issue) for issue in high_priority[:5]],
            "medium_priority": [self._format_issue(issue) for issue in medium_priority[:10]],
            "low_priority": [self._format_issue(issue) for issue in low_priority[:10]]
        }
    
    def _format_issue(self, issue: DocumentationIssue) -> Dict:
        """Format issue for JSON output"""
        return {
            "location": issue.location,
            "issue": issue.description,
            "suggestion": issue.suggestion,
            "severity": issue.severity
        }
    
    def _generate_recommendations(self, overall_coverage: float, issues: List[DocumentationIssue]) -> List[str]:
        """Generate documentation improvement recommendations"""
        recommendations = []
        
        if overall_coverage < 50:
            recommendations.append("Priority: Start by adding docstrings to your most complex or important functions")
        
        missing_docstrings = len([i for i in issues if i.issue_type == "missing_function_docstring"])
        if missing_docstrings > 5:
            recommendations.append("Consider setting a team rule: all new functions must include docstrings")
        
        missing_type_hints = len([i for i in issues if i.issue_type == "missing_type_hints"])
        if missing_type_hints > 3:
            recommendations.append("Gradually add type hints to improve code clarity and catch errors early")
        
        missing_module_docs = len([i for i in issues if i.issue_type == "missing_module_docstring"])
        if missing_module_docs > 0:
            recommendations.append("Add module-level docstrings to explain the purpose of each file")
        
        if overall_coverage > 80:
            recommendations.append("Excellent documentation! Maintain this standard for new code")
        
        if not recommendations:
            recommendations.append("Focus on documenting the most complex parts of your codebase first")
        
        return recommendations


class DocumentationVisitor(ast.NodeVisitor):
    """AST visitor to analyze documentation coverage"""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.module_docstring = None
        self.functions = {}
        self.classes = {}
        self.current_class = None
        
    def visit_Module(self, node):
        # Check for module docstring
        if (node.body and isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and 
            isinstance(node.body[0].value.value, str)):
            self.module_docstring = node.body[0].value.value
        
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        func_info = self._analyze_function(node)
        
        if self.current_class:
            # This is a method
            method_name = f"{self.current_class}.{node.name}"
            self.functions[method_name] = func_info
        else:
            # This is a module-level function
            self.functions[node.name] = func_info
        
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)
    
    def visit_ClassDef(self, node):
        old_class = self.current_class
        self.current_class = node.name
        
        # Analyze class documentation
        class_info = self._analyze_class(node)
        self.classes[node.name] = class_info
        
        self.generic_visit(node)
        self.current_class = old_class
    
    def _analyze_function(self, node) -> Dict[str, Any]:
        """Analyze a function for documentation"""
        # Check for docstring
        has_docstring = (
            node.body and isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)
        )
        
        # Check for type hints
        has_return_annotation = node.returns is not None
        has_param_annotations = any(arg.annotation is not None for arg in node.args.args)
        has_type_hints = has_return_annotation or has_param_annotations
        
        # Calculate line count
        line_count = (node.end_lineno or node.lineno) - node.lineno + 1
        
        return {
            "has_docstring": has_docstring,
            "has_type_hints": has_type_hints,
            "has_return_annotation": has_return_annotation,
            "has_param_annotations": has_param_annotations,
            "parameter_count": len(node.args.args),
            "line_count": line_count
        }
    
    def _analyze_class(self, node) -> Dict[str, Any]:
        """Analyze a class for documentation"""
        # Check for class docstring
        has_docstring = (
            node.body and isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)
        )
        
        # Count methods
        method_count = len([n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))])
        
        return {
            "has_docstring": has_docstring,
            "method_count": method_count,
            "line_count": (node.end_lineno or node.lineno) - node.lineno + 1
        }