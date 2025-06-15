# complexity.py

import ast
import os
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from .config import should_ignore

@dataclass
class ComplexityIssue:
    """Represents a complexity issue found in code"""
    location: str
    issue_type: str
    severity: str
    current_value: int
    threshold: int
    description: str
    suggestion: str

class ComplexityAnalyzer:
    """Analyzes function complexity and identifies improvement opportunities"""
    
    def __init__(self, root_path: str, module_data: Dict[str, Dict], config):
        self.root_path = root_path
        self.module_data = module_data
        self.max_function_length = getattr(config, 'max_function_length', 30)
        self.max_complexity_score = getattr(config, 'max_complexity_score', 10)
        self.max_parameter_count = getattr(config, 'max_parameter_count', 6)
        
    def analyze_complexity(self) -> Dict[str, Any]:
        """Analyze complexity across all modules"""
        try:
            all_issues = []
            function_analysis = {}
            complexity_summary = {
                "total_functions": 0,
                "high_complexity": 0,
                "medium_complexity": 0,
                "low_complexity": 0
            }
            
            for module_name in self.module_data.keys():
                module_issues, module_functions = self._analyze_module_complexity(module_name)
                all_issues.extend(module_issues)
                if module_functions:
                    function_analysis[module_name] = module_functions
                    
                # Update summary counts
                for func_data in module_functions.values():
                    complexity_summary["total_functions"] += 1
                    if func_data["overall_complexity"] == "high":
                        complexity_summary["high_complexity"] += 1
                    elif func_data["overall_complexity"] == "medium":
                        complexity_summary["medium_complexity"] += 1
                    else:
                        complexity_summary["low_complexity"] += 1
            
            # Sort issues by severity
            high_priority = [issue for issue in all_issues if issue.severity == "high"]
            medium_priority = [issue for issue in all_issues if issue.severity == "medium"]
            
            return {
                "explanation": "This analysis identifies functions that might be too complex, making them harder to understand, test, and maintain. Focus on the high-priority issues first.",
                "complexity_summary": complexity_summary,
                "hotspots": self._format_issues_for_output(high_priority[:10]),
                "medium_priority_issues": self._format_issues_for_output(medium_priority[:10]),
                "well_structured_examples": self._find_good_examples(function_analysis),
                "function_details": function_analysis,
                "improvement_suggestions": self._generate_improvement_suggestions(all_issues)
            }
            
        except Exception as e:
            return {
                "error": f"Complexity analysis failed: {str(e)}",
                "explanation": "Unable to complete complexity analysis, but this won't affect other analysis modes."
            }
    
    def _analyze_module_complexity(self, module_name: str) -> Tuple[List[ComplexityIssue], Dict]:
        """Analyze complexity for a single module"""
        try:
            file_path = self._module_to_filepath(module_name)
            if not file_path or not os.path.exists(file_path):
                return [], {}
                
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
                
            tree = ast.parse(source)
            visitor = ComplexityVisitor()
            visitor.visit(tree)
            
            issues = []
            function_details = {}
            
            for func_name, data in visitor.functions.items():
                full_name = f"{module_name}.{func_name}"
                
                # Calculate various complexity metrics
                line_count = data['end_line'] - data['start_line'] + 1
                param_count = len(data['parameters'])
                nesting_depth = data['max_nesting']
                branch_count = data['branches']
                
                # Determine overall complexity
                complexity_score = self._calculate_complexity_score(
                    line_count, param_count, nesting_depth, branch_count
                )
                
                function_details[func_name] = {
                    "line_count": line_count,
                    "parameter_count": param_count,
                    "max_nesting_depth": nesting_depth,
                    "branch_count": branch_count,
                    "complexity_score": complexity_score,
                    "overall_complexity": self._categorize_complexity(complexity_score)
                }
                
                # Check for specific issues
                if line_count > self.max_function_length:
                    issues.append(ComplexityIssue(
                        location=full_name,
                        issue_type="function_length",
                        severity="high" if line_count > self.max_function_length * 2 else "medium",
                        current_value=line_count,
                        threshold=self.max_function_length,
                        description=f"Function is {line_count} lines long",
                        suggestion=f"Break into smaller functions. Consider extracting logical blocks into separate functions."
                    ))
                
                if param_count > self.max_parameter_count:
                    issues.append(ComplexityIssue(
                        location=full_name,
                        issue_type="parameter_count", 
                        severity="medium",
                        current_value=param_count,
                        threshold=self.max_parameter_count,
                        description=f"Function has {param_count} parameters",
                        suggestion="Consider using a configuration object or class to group related parameters."
                    ))
                
                if nesting_depth > 4:
                    issues.append(ComplexityIssue(
                        location=full_name,
                        issue_type="deep_nesting",
                        severity="medium",
                        current_value=nesting_depth,
                        threshold=4,
                        description=f"Function has {nesting_depth} levels of nesting",
                        suggestion="Extract nested logic into separate functions or use early returns to reduce nesting."
                    ))
                
                if complexity_score > self.max_complexity_score:
                    issues.append(ComplexityIssue(
                        location=full_name,
                        issue_type="high_complexity",
                        severity="high",
                        current_value=complexity_score,
                        threshold=self.max_complexity_score,
                        description=f"Function has complexity score of {complexity_score}",
                        suggestion="This function does too many things. Break it down into smaller, focused functions."
                    ))
            
            return issues, function_details
            
        except Exception as e:
            print(f"Warning: Could not analyze complexity for {module_name}: {e}")
            return [], {}
    
    def _module_to_filepath(self, module_name: str) -> str:
        """Convert module name back to file path"""
        rel_path = module_name.replace('.', os.sep) + '.py'
        return os.path.join(self.root_path, rel_path)
    
    def _calculate_complexity_score(self, lines: int, params: int, nesting: int, branches: int) -> int:
        """Calculate overall complexity score"""
        score = 0
        score += max(0, lines - 20) // 5  # Penalty for long functions
        score += max(0, params - 3) * 2   # Penalty for many parameters
        score += max(0, nesting - 2) * 3  # Penalty for deep nesting
        score += max(0, branches - 5)     # Penalty for many branches
        return score
    
    def _categorize_complexity(self, score: int) -> str:
        """Categorize complexity level"""
        if score <= 3:
            return "low"
        elif score <= 7:
            return "medium"
        else:
            return "high"
    
    def _format_issues_for_output(self, issues: List[ComplexityIssue]) -> List[Dict]:
        """Format issues for JSON output"""
        return [
            {
                "location": issue.location,
                "issue": issue.description,
                "severity": issue.severity,
                "impact": self._get_impact_description(issue.issue_type),
                "suggestion": issue.suggestion
            }
            for issue in issues
        ]
    
    def _get_impact_description(self, issue_type: str) -> str:
        """Get human-readable impact description"""
        impacts = {
            "function_length": "Hard to understand, test, and debug",
            "parameter_count": "Difficult to call correctly, hard to remember parameter order",
            "deep_nesting": "Complex logic flow, hard to follow and test all paths",
            "high_complexity": "Very difficult to maintain, high risk of bugs"
        }
        return impacts.get(issue_type, "May impact code maintainability")
    
    def _find_good_examples(self, function_analysis: Dict) -> List[Dict]:
        """Find examples of well-structured functions"""
        good_examples = []
        
        for module, functions in function_analysis.items():
            for func_name, data in functions.items():
                if (data["overall_complexity"] == "low" and 
                    data["line_count"] >= 5 and data["line_count"] <= 20):
                    good_examples.append({
                        "location": f"{module}.{func_name}",
                        "reason": f"Well-sized function ({data['line_count']} lines) with good structure",
                        "note": "Good example of appropriate function complexity"
                    })
                    
                if len(good_examples) >= 3:
                    break
            if len(good_examples) >= 3:
                break
                
        return good_examples
    
    def _generate_improvement_suggestions(self, issues: List[ComplexityIssue]) -> List[str]:
        """Generate general improvement suggestions"""
        suggestions = []
        
        high_count = len([i for i in issues if i.severity == "high"])
        medium_count = len([i for i in issues if i.severity == "medium"])
        
        if high_count > 0:
            suggestions.append(f"Priority: Address {high_count} high-complexity functions first - these are the biggest maintenance risks.")
        
        if medium_count > 3:
            suggestions.append("Consider a gradual refactoring approach - tackle one complex function per development cycle.")
        
        long_functions = len([i for i in issues if i.issue_type == "function_length"])
        if long_functions > 2:
            suggestions.append("Look for opportunities to extract reusable helper functions from long functions.")
        
        if not suggestions:
            suggestions.append("Code complexity is well-managed - continue following current practices.")
            
        return suggestions


class ComplexityVisitor(ast.NodeVisitor):
    """AST visitor to analyze function complexity"""
    
    def __init__(self):
        self.functions = {}
        self.current_function = None
        self.nesting_depth = 0
        self.current_branches = 0
        
    def visit_FunctionDef(self, node):
        # Store function info
        self.functions[node.name] = {
            'start_line': node.lineno,
            'end_line': node.end_lineno or node.lineno,
            'parameters': [arg.arg for arg in node.args.args],
            'max_nesting': 0,
            'branches': 0
        }
        
        # Visit function body to analyze complexity
        old_function = self.current_function
        old_nesting = self.nesting_depth
        old_branches = self.current_branches
        
        self.current_function = node.name
        self.nesting_depth = 0
        self.current_branches = 0
        
        self.generic_visit(node)
        
        # Store max values
        self.functions[node.name]['max_nesting'] = self.nesting_depth
        self.functions[node.name]['branches'] = self.current_branches
        
        # Restore previous state
        self.current_function = old_function
        self.nesting_depth = old_nesting
        self.current_branches = old_branches
    
    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)  # Same logic as regular function
    
    def visit_If(self, node):
        if self.current_function:
            self.current_branches += 1
            self.nesting_depth += 1
            self.generic_visit(node)
            self.nesting_depth -= 1
        else:
            self.generic_visit(node)
    
    def visit_For(self, node):
        if self.current_function:
            self.nesting_depth += 1
            self.generic_visit(node)
            self.nesting_depth -= 1
        else:
            self.generic_visit(node)
    
    def visit_While(self, node):
        if self.current_function:
            self.nesting_depth += 1
            self.generic_visit(node)
            self.nesting_depth -= 1
        else:
            self.generic_visit(node)
    
    def visit_Try(self, node):
        if self.current_function:
            self.nesting_depth += 1
            self.generic_visit(node)
            self.nesting_depth -= 1
        else:
            self.generic_visit(node)
    
    def visit_With(self, node):
        if self.current_function:
            self.nesting_depth += 1
            self.generic_visit(node)
            self.nesting_depth -= 1
        else:
            self.generic_visit(node)