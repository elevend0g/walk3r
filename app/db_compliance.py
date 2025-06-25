# db_compliance.py

import ast
import os
import re
from typing import Dict, List, Set, Any
from dataclasses import dataclass
from .config import should_ignore

@dataclass
class ComplianceMetrics:
    """Metrics for database architecture compliance"""
    module_name: str
    total_db_operations: int
    correct_service_calls: int
    direct_violations: int
    architectural_score: float
    violation_details: List[Dict]
    service_usage: List[Dict]

class DatabaseComplianceAnalyzer:
    """Analyzes database architecture compliance within Walk3r framework"""
    
    def __init__(self, root_path: str, module_data: Dict[str, Dict], config):
        self.root_path = root_path
        self.module_data = module_data
        self.config = config
        
        # Get patterns from config or use defaults
        self.violation_patterns = getattr(config, 'violation_patterns', self._default_violation_patterns())
        self.service_patterns = getattr(config, 'service_patterns', self._default_service_patterns())
        
    def _default_violation_patterns(self) -> Dict[str, List[str]]:
        """Default violation patterns - can be overridden in config"""
        return {
            'direct_redis': [
                r'\.redis\.',
                r'redis\..*\(',
                r'\.lpush\(',
                r'\.xread\(',
                r'\.hget\(',
                r'\.zrangebyscore\(',
                r'\.pipeline\(\)',
            ],
            'direct_sql': [
                r'cursor\.execute\(',
                r'\.execute\s*\(',
                r'SELECT\s+.*FROM',
                r'INSERT\s+INTO',
                r'UPDATE\s+.*SET',
                r'DELETE\s+FROM',
            ],
            'direct_orm': [
                r'session\.query\(',
                r'\.session\.',
                r'Model\.objects\.',
                r'\.filter\(',
                r'\.create\(',
            ],
            'direct_adapters': [
                r'from.*adapters.*import',
                r'RedisAdapter\(',
                r'DatabaseAdapter\(',
                r'\.adapter\.',
            ]
        }
    
    def _default_service_patterns(self) -> Dict[str, List[str]]:
        """Default correct service patterns - can be overridden in config"""
        return {
            'service_layer': [
                r'_service\.',
                r'Service\(',
                r'\.service\.',
                r'service_layer\.',
            ],
            'repository_pattern': [
                r'Repository\(',
                r'\.repository\.',
                r'_repo\.',
                r'repo\.',
            ],
            'facade_pattern': [
                r'DatabaseFacade\.',
                r'DataAccess\.',
                r'\.facade\.',
            ],
            'proper_abstractions': [
                r'DataManager\.',
                r'StorageManager\.',
                r'PersistenceLayer\.',
            ]
        }

    def analyze_compliance(self) -> Dict[str, Any]:
        """Analyze database architecture compliance across all modules"""
        try:
            module_metrics = {}
            total_violations = 0
            total_correct = 0
            total_modules_with_db = 0
            
            for module_name in self.module_data.keys():
                metrics = self._analyze_module_compliance(module_name)
                if metrics and metrics.total_db_operations > 0:
                    module_metrics[module_name] = metrics
                    total_violations += metrics.direct_violations
                    total_correct += metrics.correct_service_calls
                    total_modules_with_db += 1
            
            # Calculate overall scores
            overall_score = self._calculate_overall_score(module_metrics)
            compliance_summary = self._generate_compliance_summary(module_metrics)
            
            return {
                "explanation": "This analysis evaluates how well your codebase follows proper database architecture patterns, distinguishing between direct database access (violations) and correct service layer usage.",
                "compliance_summary": compliance_summary,
                "overall_architectural_score": overall_score,
                "module_compliance": {name: self._format_module_metrics(metrics) 
                                   for name, metrics in module_metrics.items()},
                "violation_hotspots": self._identify_violation_hotspots(module_metrics),
                "compliance_recommendations": self._generate_recommendations(module_metrics),
                "architectural_patterns": self._analyze_architectural_patterns(module_metrics)
            }
            
        except Exception as e:
            return {
                "error": f"Database compliance analysis failed: {str(e)}",
                "explanation": "Unable to complete compliance analysis, but this won't affect other analysis modes."
            }
    
    def _analyze_module_compliance(self, module_name: str) -> ComplianceMetrics:
        """Analyze compliance for a single module"""
        try:
            file_path = self._module_to_filepath(module_name)
            if not file_path or not os.path.exists(file_path):
                return None
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find violations and correct usage
            violations = self._find_violations(content)
            service_usage = self._find_service_usage(content)
            
            # Calculate metrics
            total_ops = len(violations) + len(service_usage)
            correct_ops = len(service_usage)
            violation_count = len(violations)
            
            # Calculate architectural score (0-100)
            if total_ops == 0:
                score = 100.0  # No database operations = perfect
            else:
                score = (correct_ops / total_ops) * 100
            
            return ComplianceMetrics(
                module_name=module_name,
                total_db_operations=total_ops,
                correct_service_calls=correct_ops,
                direct_violations=violation_count,
                architectural_score=score,
                violation_details=violations,
                service_usage=service_usage
            )
            
        except Exception as e:
            print(f"Warning: Could not analyze compliance for {module_name}: {e}")
            return None
    
    def _module_to_filepath(self, module_name: str) -> str:
        """Convert module name back to file path"""
        rel_path = module_name.replace('.', os.sep) + '.py'
        return os.path.join(self.root_path, rel_path)
    
    def _find_violations(self, content: str) -> List[Dict]:
        """Find direct database access violations"""
        violations = []
        lines = content.split('\n')
        
        for violation_type, patterns in self.violation_patterns.items():
            for pattern in patterns:
                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        violations.append({
                            'type': violation_type,
                            'line': line_num,
                            'code': line.strip(),
                            'pattern': pattern,
                            'severity': self._get_severity(violation_type),
                            'suggestion': self._get_fix_suggestion(violation_type)
                        })
        
        return violations
    
    def _find_service_usage(self, content: str) -> List[Dict]:
        """Find correct service layer usage"""
        service_calls = []
        lines = content.split('\n')
        
        for service_type, patterns in self.service_patterns.items():
            for pattern in patterns:
                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        service_calls.append({
                            'type': service_type,
                            'line': line_num,
                            'code': line.strip(),
                            'pattern': pattern
                        })
        
        return service_calls
    
    def _get_severity(self, violation_type: str) -> str:
        """Get severity level for violation type"""
        severity_map = {
            'direct_redis': 'HIGH',
            'direct_sql': 'CRITICAL',
            'direct_orm': 'HIGH',
            'direct_adapters': 'CRITICAL'
        }
        return severity_map.get(violation_type, 'MEDIUM')
    
    def _get_fix_suggestion(self, violation_type: str) -> str:
        """Get fix suggestion for violation type"""
        suggestions = {
            'direct_redis': 'Use a Redis service layer or repository pattern instead of direct Redis calls',
            'direct_sql': 'Move SQL queries to a data access layer or repository class',
            'direct_orm': 'Wrap ORM calls in service methods or repository pattern',
            'direct_adapters': 'Avoid direct adapter usage; use service layer interfaces'
        }
        return suggestions.get(violation_type, 'Consider using proper abstraction layers')
    
    def _calculate_overall_score(self, module_metrics: Dict[str, ComplianceMetrics]) -> float:
        """Calculate overall architectural compliance score"""
        if not module_metrics:
            return 100.0
        
        total_ops = sum(m.total_db_operations for m in module_metrics.values())
        total_correct = sum(m.correct_service_calls for m in module_metrics.values())
        
        return (total_correct / max(total_ops, 1)) * 100
    
    def _generate_compliance_summary(self, module_metrics: Dict[str, ComplianceMetrics]) -> Dict[str, Any]:
        """Generate compliance summary statistics"""
        if not module_metrics:
            return {"message": "No modules with database operations found"}
        
        scores = [m.architectural_score for m in module_metrics.values()]
        
        critical = len([m for m in module_metrics.values() if m.architectural_score < 50])
        warning = len([m for m in module_metrics.values() if 50 <= m.architectural_score < 80])
        good = len([m for m in module_metrics.values() if 80 <= m.architectural_score < 100])
        perfect = len([m for m in module_metrics.values() if m.architectural_score == 100])
        
        return {
            "total_modules_with_db": len(module_metrics),
            "average_compliance_score": round(sum(scores) / len(scores), 1),
            "compliance_distribution": {
                "critical": critical,
                "warning": warning, 
                "good": good,
                "perfect": perfect
            },
            "total_violations": sum(m.direct_violations for m in module_metrics.values()),
            "total_correct_patterns": sum(m.correct_service_calls for m in module_metrics.values())
        }
    
    def _format_module_metrics(self, metrics: ComplianceMetrics) -> Dict[str, Any]:
        """Format module metrics for JSON output"""
        return {
            "architectural_score": round(metrics.architectural_score, 1),
            "total_operations": metrics.total_db_operations,
            "violations": metrics.direct_violations,
            "correct_patterns": metrics.correct_service_calls,
            "violation_details": metrics.violation_details[:5],  # Limit to first 5
            "service_patterns": metrics.service_usage[:3]  # Limit to first 3
        }
    
    def _identify_violation_hotspots(self, module_metrics: Dict[str, ComplianceMetrics]) -> List[Dict]:
        """Identify modules that need immediate attention"""
        hotspots = []
        
        # Sort by worst compliance score
        sorted_modules = sorted(
            module_metrics.items(),
            key=lambda x: x[1].architectural_score
        )
        
        for module_name, metrics in sorted_modules[:5]:  # Top 5 worst
            if metrics.architectural_score < 80:
                hotspots.append({
                    "module": module_name,
                    "score": round(metrics.architectural_score, 1),
                    "violations": metrics.direct_violations,
                    "priority": "CRITICAL" if metrics.architectural_score < 50 else "HIGH",
                    "top_violations": [v['type'] for v in metrics.violation_details[:3]]
                })
        
        return hotspots
    
    def _generate_recommendations(self, module_metrics: Dict[str, ComplianceMetrics]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        critical_modules = [m for m in module_metrics.values() if m.architectural_score < 50]
        if critical_modules:
            recommendations.append(f"URGENT: {len(critical_modules)} modules have critical compliance issues - refactor to use service layers")
        
        violation_types = {}
        for metrics in module_metrics.values():
            for violation in metrics.violation_details:
                violation_types[violation['type']] = violation_types.get(violation['type'], 0) + 1
        
        # Top violation type
        if violation_types:
            top_violation = max(violation_types.items(), key=lambda x: x[1])
            recommendations.append(f"Most common violation: {top_violation[0]} ({top_violation[1]} instances) - consider creating abstraction layer")
        
        perfect_modules = [m for m in module_metrics.values() if m.architectural_score == 100]
        if perfect_modules:
            recommendations.append(f"{len(perfect_modules)} modules show perfect compliance - use as examples for refactoring")
        
        return recommendations
    
    def _analyze_architectural_patterns(self, module_metrics: Dict[str, ComplianceMetrics]) -> Dict[str, Any]:
        """Analyze what architectural patterns are being used"""
        pattern_usage = {}
        
        for metrics in module_metrics.values():
            for service in metrics.service_usage:
                pattern_type = service['type']
                pattern_usage[pattern_type] = pattern_usage.get(pattern_type, 0) + 1
        
        return {
            "detected_patterns": pattern_usage,
            "most_used_pattern": max(pattern_usage.items(), key=lambda x: x[1])[0] if pattern_usage else None,
            "pattern_diversity": len(pattern_usage),
            "recommendation": self._recommend_architectural_pattern(pattern_usage)
        }
    
    def _recommend_architectural_pattern(self, patterns: Dict[str, int]) -> str:
        """Recommend architectural improvements based on current patterns"""
        if not patterns:
            return "Consider implementing service layer or repository patterns for database access"
        
        if 'service_layer' in patterns:
            return "Good use of service layer pattern - consider standardizing across all modules"
        elif 'repository_pattern' in patterns:
            return "Repository pattern detected - consider expanding to cover all data access"
        else:
            return "Consider implementing consistent service layer pattern across all database operations"