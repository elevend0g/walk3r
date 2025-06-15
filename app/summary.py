# summary.py

from typing import Dict, List, Any, Optional
from datetime import datetime

class ProjectSummarizer:
    """Creates LLM-friendly project summaries combining all analysis data"""
    
    def __init__(self, all_analysis_data: Dict[str, Any]):
        self.data = all_analysis_data
        
    def generate_summary(self) -> Dict[str, Any]:
        """Generate main project summary for LLM consumption"""
        try:
            # Extract key data from various analyses
            deps = self.data.get('dependencies', {})
            functions = self.data.get('functions', {})
            metrics = self.data.get('metrics', {})
            complexity = self.data.get('complexity', {})
            db_calls = self.data.get('db_calls', {})
            docs = self.data.get('documentation', {})
            
            return {
                "project_description": self._generate_project_description(metrics, deps),
                "architecture_overview": self._generate_architecture_overview(deps, functions, db_calls),
                "code_health_summary": self._generate_health_summary(metrics, complexity, docs),
                "dependency_insights": self._generate_dependency_insights(deps),
                "complexity_highlights": self._generate_complexity_highlights(complexity),
                "database_usage_summary": self._generate_database_summary(db_calls),
                "documentation_status": self._generate_documentation_status(docs),
                "key_recommendations": self._generate_key_recommendations(),
                "suggested_questions": self._generate_suggested_questions()
            }
            
        except Exception as e:
            return {
                "error": f"Summary generation failed: {str(e)}",
                "explanation": "Unable to generate project summary, but individual analysis files are still available."
            }
    
    def create_llm_context(self) -> Dict[str, Any]:
        """Create detailed technical context for LLM ingestion"""
        try:
            deps = self.data.get('dependencies', {})
            functions = self.data.get('functions', {})
            metrics = self.data.get('metrics', {})
            complexity = self.data.get('complexity', {})
            
            return {
                "codebase_summary": self._create_codebase_summary(metrics, deps),
                "module_explanations": self._create_module_explanations(deps, functions, complexity),
                "architectural_insights": self._create_architectural_insights(deps, functions),
                "change_impact_guide": self._create_change_impact_guide(deps),
                "technical_context": self._create_technical_context(functions, complexity)
            }
            
        except Exception as e:
            return {
                "error": f"LLM context generation failed: {str(e)}",
                "explanation": "Unable to generate LLM context, but other analysis files are available."
            }
    
    def _generate_project_description(self, metrics: Dict, deps: Dict) -> str:
        """Generate human-readable project description"""
        try:
            project_summary = metrics.get('project_summary', {})
            total_files = project_summary.get('total_files', 0)
            total_functions = project_summary.get('total_functions', 0)
            total_lines = project_summary.get('total_lines_of_code', 0)
            size_category = project_summary.get('project_size_category', 'Unknown size')
            
            # Try to identify the project type
            module_names = list(deps.keys()) if deps else []
            project_type = self._guess_project_type(module_names)
            
            return (f"This is a {project_type} with {total_files} modules, "
                   f"{total_functions} functions, and {total_lines} lines of code. "
                   f"{size_category}.")
        except:
            return "Project analysis data is incomplete."
    
    def _guess_project_type(self, module_names: List[str]) -> str:
        """Guess project type from module names"""
        modules_str = ' '.join(module_names).lower()
        
        if any(keyword in modules_str for keyword in ['api', 'server', 'http', 'flask', 'django', 'fastapi']):
            return "web application or API"
        elif any(keyword in modules_str for keyword in ['cli', 'command', 'argparse']):
            return "command-line application"
        elif any(keyword in modules_str for keyword in ['test', 'unittest', 'pytest']):
            return "test suite or testing framework"
        elif any(keyword in modules_str for keyword in ['data', 'analysis', 'pandas', 'numpy']):
            return "data analysis or processing application"
        elif any(keyword in modules_str for keyword in ['game', 'pygame', 'graphics']):
            return "game or graphics application"
        elif any(keyword in modules_str for keyword in ['scraper', 'crawler', 'requests']):
            return "web scraping or data collection application"
        else:
            return "Python application"
    
    def _generate_architecture_overview(self, deps: Dict, functions: Dict, db_calls: Dict) -> Dict[str, Any]:
        """Generate architecture overview"""
        try:
            # Identify entry points (modules with few/no dependencies)
            entry_points = {}
            core_components = {}
            utility_modules = {}
            
            for module, links in deps.items():
                imports = list(links.get('imports', []))  # Convert set to list
                calls = list(links.get('calls', []))      # Convert set to list
                total_deps = len(imports) + len(calls)
                
                # Guess module role based on dependencies and name
                if total_deps <= 1 and any(keyword in module.lower() for keyword in ['main', 'cli', 'app', 'server']):
                    entry_points[module] = self._describe_module_purpose(module, functions.get(module, {}))
                elif 'util' in module.lower() or 'helper' in module.lower() or 'config' in module.lower():
                    utility_modules[module] = self._describe_module_purpose(module, functions.get(module, {}))
                else:
                    core_components[module] = self._describe_module_purpose(module, functions.get(module, {}))
            
            # Generate dependency flow description
            dependency_flow = self._analyze_dependency_flow(deps)
            
            return {
                "entry_points": entry_points,
                "core_components": core_components,
                "utility_modules": utility_modules,
                "dependency_flow": dependency_flow
            }
        except:
            return {"error": "Could not analyze architecture"}
    
    def _describe_module_purpose(self, module_name: str, functions: Dict) -> str:
        """Describe what a module likely does based on its name and functions"""
        name_lower = module_name.lower()
        func_names = list(functions.keys()) if functions else []
        func_str = ' '.join(func_names).lower()
        
        # Check module name patterns
        if 'auth' in name_lower:
            return "Authentication and user management"
        elif 'database' in name_lower or 'db' in name_lower:
            return "Database operations and data models"
        elif 'api' in name_lower:
            return "API endpoints and request handling"
        elif 'config' in name_lower:
            return "Configuration management"
        elif 'util' in name_lower or 'helper' in name_lower:
            return "Utility functions and helpers"
        elif 'test' in name_lower:
            return "Testing and test utilities"
        elif 'main' in name_lower or 'app' in name_lower:
            return "Application entry point and initialization"
        elif 'cli' in name_lower:
            return "Command-line interface"
        
        # Check function patterns
        if any(keyword in func_str for keyword in ['login', 'authenticate', 'verify']):
            return "User authentication and security"
        elif any(keyword in func_str for keyword in ['get', 'fetch', 'load', 'save', 'store']):
            return "Data retrieval and storage operations"
        elif any(keyword in func_str for keyword in ['process', 'handle', 'execute']):
            return "Business logic and data processing"
        elif any(keyword in func_str for keyword in ['render', 'display', 'show']):
            return "User interface and presentation"
        
        # Count functions to estimate complexity
        func_count = len(func_names)
        if func_count == 0:
            return "Module purpose unclear (no functions detected)"
        elif func_count <= 3:
            return f"Simple module with {func_count} functions"
        else:
            return f"Complex module with {func_count} functions - likely core business logic"
    
    def _analyze_dependency_flow(self, deps: Dict) -> Dict[str, Any]:
        """Analyze how modules depend on each other"""
        try:
            # Find main flow patterns
            flows = []
            
            # Look for chains of dependencies
            for module, links in deps.items():
                calls = list(links.get('calls', []))  # Convert set to list
                if calls:
                    for target in calls:
                        if target in deps:
                            target_calls = list(deps[target].get('calls', []))  # Convert set to list
                            if target_calls:
                                flow = f"{module} → {target} → {target_calls[0]}"
                                flows.append(flow)
            
            return {
                "explanation": "The application follows these main dependency patterns:",
                "main_flows": flows[:5] if flows else ["No clear dependency chains detected"],
                "architecture_style": self._identify_architecture_style(deps)
            }
        except:
            return {"explanation": "Could not analyze dependency flow"}
    
    def _identify_architecture_style(self, deps: Dict) -> str:
        """Identify the overall architecture style"""
        total_modules = len(deps)
        
        # Count modules with many dependencies vs few
        high_dep_modules = 0
        low_dep_modules = 0
        
        for module, links in deps.items():
            imports = list(links.get('imports', []))  # Convert set to list
            calls = list(links.get('calls', []))      # Convert set to list
            total_deps = len(imports) + len(calls)
            if total_deps > 3:
                high_dep_modules += 1
            elif total_deps <= 1:
                low_dep_modules += 1
        
        if low_dep_modules > total_modules * 0.6:
            return "Modular architecture - modules are relatively independent"
        elif high_dep_modules > total_modules * 0.4:
            return "Interconnected architecture - modules have many dependencies"
        else:
            return "Balanced architecture - mix of independent and connected modules"
    
    def _generate_health_summary(self, metrics: Dict, complexity: Dict, docs: Dict) -> Dict[str, Any]:
        """Generate overall code health summary"""
        health_score = 0
        max_score = 100
        health_factors = []
        
        try:
            # Metrics contribution (30 points)
            if metrics and 'project_summary' in metrics:
                size_category = metrics['project_summary'].get('project_size_category', '')
                if 'easy to understand' in size_category or 'well-structured' in size_category:
                    health_score += 30
                    health_factors.append("Good project size and structure")
                elif 'moderate complexity' in size_category:
                    health_score += 20
                    health_factors.append("Moderate project complexity")
                else:
                    health_score += 10
                    health_factors.append("Large/complex project structure")
            
            # Complexity contribution (40 points)
            if complexity and 'complexity_summary' in complexity:
                summary = complexity['complexity_summary']
                total_funcs = summary.get('total_functions', 1)
                high_complex = summary.get('high_complexity', 0)
                
                complexity_ratio = high_complex / total_funcs
                if complexity_ratio < 0.1:
                    health_score += 40
                    health_factors.append("Low complexity - most functions are manageable")
                elif complexity_ratio < 0.2:
                    health_score += 25
                    health_factors.append("Moderate complexity - some functions need attention")
                else:
                    health_score += 10
                    health_factors.append("High complexity - many functions need refactoring")
            
            # Documentation contribution (30 points)
            if docs and 'coverage_summary' in docs:
                coverage = docs['coverage_summary']
                func_coverage = coverage.get('function_coverage_percentage', 0)
                
                if func_coverage >= 80:
                    health_score += 30
                    health_factors.append("Excellent documentation coverage")
                elif func_coverage >= 60:
                    health_score += 20
                    health_factors.append("Good documentation coverage")
                elif func_coverage >= 30:
                    health_score += 10
                    health_factors.append("Fair documentation coverage")
                else:
                    health_factors.append("Poor documentation coverage")
            
            return {
                "overall_score": round(health_score, 1),
                "grade": self._score_to_grade(health_score),
                "health_factors": health_factors,
                "assessment": self._assess_health(health_score)
            }
        except:
            return {"assessment": "Unable to assess code health"}
    
    def _score_to_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90: return "A"
        elif score >= 80: return "B"
        elif score >= 70: return "C"
        elif score >= 60: return "D"
        else: return "F"
    
    def _assess_health(self, score: float) -> str:
        """Assess overall health"""
        if score >= 80:
            return "Healthy codebase - well-structured and maintainable"
        elif score >= 60:
            return "Good codebase - minor improvements recommended"
        elif score >= 40:
            return "Fair codebase - some areas need attention"
        else:
            return "Needs improvement - significant refactoring recommended"
    
    def _generate_dependency_insights(self, deps: Dict) -> Dict[str, Any]:
        """Generate insights about dependencies"""
        if not deps:
            return {"insight": "No dependency data available"}
        
        # Find most connected modules
        connection_counts = {}
        for module, links in deps.items():
            imports = list(links.get('imports', []))  # Convert set to list
            calls = list(links.get('calls', []))      # Convert set to list
            total_connections = len(imports) + len(calls)
            connection_counts[module] = total_connections
        
        most_connected = sorted(connection_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        least_connected = sorted(connection_counts.items(), key=lambda x: x[1])[:3]
        
        return {
            "most_connected_modules": [{"module": mod, "connections": count} for mod, count in most_connected],
            "least_connected_modules": [{"module": mod, "connections": count} for mod, count in least_connected],
            "insight": "Most connected modules are likely core components; least connected are utilities or entry points"
        }
    
    def _generate_complexity_highlights(self, complexity: Dict) -> Dict[str, Any]:
        """Generate complexity highlights"""
        if not complexity:
            return {"insight": "No complexity data available"}
        
        hotspots = complexity.get('hotspots', [])[:3]
        well_structured = complexity.get('well_structured_examples', [])[:2]
        
        return {
            "areas_of_concern": [
                f"{item['location']}: {item['issue']} - {item['suggestion']}"
                for item in hotspots
            ],
            "well_structured_examples": [
                f"{item['location']}: {item['reason']}"
                for item in well_structured
            ]
        }
    
    def _generate_database_summary(self, db_calls: Dict) -> Dict[str, Any]:
        """Generate database usage summary"""
        if not db_calls:
            return {"insight": "No database operations detected"}
        
        summary = db_calls.get('database_summary', {})
        modules_with_db = summary.get('modules_list', [])
        
        if not modules_with_db:
            return {"insight": "No database operations detected"}
        
        return {
            "modules_with_db_access": modules_with_db,
            "total_operations": summary.get('total_db_operations', 0),
            "insight": f"Database operations found in {len(modules_with_db)} modules"
        }
    
    def _generate_documentation_status(self, docs: Dict) -> Dict[str, Any]:
        """Generate documentation status"""
        if not docs:
            return {"status": "No documentation analysis available"}
        
        coverage = docs.get('coverage_summary', {})
        func_coverage = coverage.get('function_coverage_percentage', 0)
        quality = coverage.get('overall_quality', 'Unknown')
        
        return {
            "function_coverage_percentage": func_coverage,
            "overall_quality": quality,
            "status": f"{func_coverage}% of functions documented - {quality.lower()}"
        }
    
    def _generate_key_recommendations(self) -> List[str]:
        """Generate top recommendations across all analyses"""
        recommendations = []
        
        # Extract recommendations from each analysis
        for analysis_name, analysis_data in self.data.items():
            if isinstance(analysis_data, dict) and 'recommendations' in analysis_data:
                recs = analysis_data['recommendations']
                if isinstance(recs, list):
                    recommendations.extend(recs[:2])  # Top 2 from each
        
        # Also check for improvement suggestions
        complexity = self.data.get('complexity', {})
        if complexity and 'improvement_suggestions' in complexity:
            recommendations.extend(complexity['improvement_suggestions'][:2])
        
        return recommendations[:5]  # Return top 5 overall
    
    def _generate_suggested_questions(self) -> List[str]:
        """Generate questions users might ask about their codebase"""
        questions = [
            "What are the main components of this application and how do they work together?",
            "Which parts of the code are most complex and might need refactoring?",
            "How is data handled throughout the application?",
            "What would be the impact of changing [specific module]?",
            "Where should I start if I want to understand this codebase?",
            "What are the biggest technical debt areas that need attention?"
        ]
        
        # Customize based on available data
        if self.data.get('db_calls'):
            questions.append("How does the application interact with the database?")
        
        if self.data.get('complexity', {}).get('hotspots'):
            questions.append("Which functions are too complex and how should I break them down?")
        
        return questions[:6]
    
    def _create_codebase_summary(self, metrics: Dict, deps: Dict) -> Dict[str, Any]:
        """Create detailed codebase summary for LLM context"""
        try:
            project_summary = metrics.get('project_summary', {}) if metrics else {}
            module_names = list(deps.keys()) if deps else []
            
            return {
                "purpose": self._guess_project_type(module_names),
                "language": "Python",
                "framework_clues": self._identify_frameworks(module_names),
                "total_modules": len(module_names),
                "total_lines": project_summary.get('total_lines_of_code', 0),
                "total_functions": project_summary.get('total_functions', 0),
                "complexity_assessment": project_summary.get('project_size_category', 'Unknown')
            }
        except:
            return {"purpose": "Unknown Python application"}
    
    def _identify_frameworks(self, module_names: List[str]) -> List[str]:
        """Identify likely frameworks from module names"""
        modules_str = ' '.join(module_names).lower()
        frameworks = []
        
        framework_patterns = {
            'flask': ['flask', 'app'],
            'django': ['django', 'models', 'views'],
            'fastapi': ['fastapi', 'api'],
            'requests': ['requests', 'http'],
            'sqlalchemy': ['sqlalchemy', 'database'],
            'pandas': ['pandas', 'data'],
            'numpy': ['numpy', 'array']
        }
        
        for framework, patterns in framework_patterns.items():
            if any(pattern in modules_str for pattern in patterns):
                frameworks.append(framework)
        
        return frameworks
    
    def _create_module_explanations(self, deps: Dict, functions: Dict, complexity: Dict) -> Dict[str, Any]:
        """Create detailed module explanations"""
        explanations = {}
        
        for module in list(deps.keys())[:5]:  # Top 5 modules
            try:
                links = deps.get(module, {})
                module_functions = functions.get(module, {})
                
                explanations[module] = {
                    "purpose": self._describe_module_purpose(module, module_functions),
                    "key_functions": list(module_functions.keys())[:5],
                    "dependencies": list(links.get('calls', [])),  # Convert set to list
                    "used_by": [m for m, l in deps.items() if module in list(l.get('calls', []))],  # Convert set to list
                    "complexity_notes": self._get_module_complexity_notes(module, complexity)
                }
            except Exception as e:
                explanations[module] = {"purpose": f"Analysis incomplete: {str(e)}"}
        
        return explanations
    
    def _get_module_complexity_notes(self, module: str, complexity: Dict) -> str:
        """Get complexity notes for a module"""
        if not complexity or 'hotspots' not in complexity:
            return "No complexity analysis available"
        
        hotspots = complexity['hotspots']
        module_issues = [h for h in hotspots if module in h.get('location', '')]
        
        if not module_issues:
            return "Well-structured module with good complexity"
        elif len(module_issues) == 1:
            return f"One complexity issue: {module_issues[0].get('issue', '')}"
        else:
            return f"Multiple complexity issues - review recommended"
    
    def _create_architectural_insights(self, deps: Dict, functions: Dict) -> Dict[str, Any]:
        """Create architectural insights"""
        return {
            "strengths": self._identify_architectural_strengths(deps),
            "potential_improvements": self._identify_architectural_improvements(deps, functions),
            "patterns": self._identify_architectural_patterns(deps)
        }
    
    def _identify_architectural_strengths(self, deps: Dict) -> List[str]:
        """Identify architectural strengths"""
        strengths = []
        
        # Check for good separation
        utility_modules = [m for m in deps.keys() if any(keyword in m.lower() for keyword in ['util', 'helper', 'config'])]
        if utility_modules:
            strengths.append("Good separation of utility functions into dedicated modules")
        
        # Check for reasonable module count
        if 3 <= len(deps) <= 20:
            strengths.append("Reasonable number of modules - not too fragmented or monolithic")
        
        return strengths
    
    def _identify_architectural_improvements(self, deps: Dict, functions: Dict) -> List[str]:
        """Identify potential architectural improvements"""
        improvements = []
        
        # Check for very large modules
        large_modules = []
        for module, funcs in functions.items():
            if len(funcs) > 15:
                large_modules.append(module)
        
        if large_modules:
            improvements.append(f"Consider breaking down large modules: {', '.join(large_modules[:2])}")
        
        return improvements
    
    def _identify_architectural_patterns(self, deps: Dict) -> List[str]:
        """Identify architectural patterns"""
        patterns = []
        
        # Look for layered patterns
        entry_modules = []
        for module, links in deps.items():
            imports = list(links.get('imports', []))  # Convert set to list
            calls = list(links.get('calls', []))      # Convert set to list
            if len(imports) + len(calls) <= 1:
                entry_modules.append(module)
        
        if entry_modules:
            patterns.append("Entry point pattern - clear application entry points")
        
        return patterns
    
    def _create_change_impact_guide(self, deps: Dict) -> Dict[str, Any]:
        """Create guide for understanding change impacts"""
        high_risk = []
        safe_to_modify = []
        
        # Calculate how many modules depend on each module
        dependency_counts = {}
        for module, links in deps.items():
            calls = list(links.get('calls', []))  # Convert set to list
            for target in calls:
                dependency_counts[target] = dependency_counts.get(target, 0) + 1
        
        for module in deps.keys():
            dependent_count = dependency_counts.get(module, 0)
            if dependent_count >= 3:
                high_risk.append(module)
            elif dependent_count <= 1:
                safe_to_modify.append(module)
        
        return {
            "high_risk_modules": {
                "modules": high_risk[:3],
                "reason": "Many other modules depend on these"
            },
            "safe_to_modify": {
                "modules": safe_to_modify[:3],
                "reason": "Few or no dependencies on these modules"
            }
        }
    
    def _create_technical_context(self, functions: Dict, complexity: Dict) -> Dict[str, Any]:
        """Create technical context for LLM"""
        return {
            "total_functions_analyzed": sum(len(funcs) for funcs in functions.values()),
            "complexity_distribution": complexity.get('complexity_summary', {}) if complexity else {},
            "analysis_timestamp": datetime.now().isoformat(),
            "context_note": "This analysis was generated by Walk3r static analysis tool"
        }