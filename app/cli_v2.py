#!/usr/bin/env python3
"""
Walk3r 2.0 - Enhanced CLI Interface
Easy-to-use static analysis tool for non-programmers and AI assistant integration
"""

import argparse
import sys
import os
import toml
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import webbrowser

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("📦 Installing rich for better experience...")
    os.system("pip install rich")
    try:
        from rich.console import Console
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
        from rich.panel import Panel
        from rich.table import Table
        from rich.prompt import Prompt, Confirm
        from rich.text import Text
        RICH_AVAILABLE = True
    except ImportError:
        RICH_AVAILABLE = False

from .scanner import ModuleScanner
from .linker import DependencyLinker
from .exporter import export_json, export_csv, export_dot, export_function_map_json, export_function_dot
from .config import Walk3rConfig

# Import analysis modules
try:
    from .metrics import MetricsAnalyzer
    from .complexity import ComplexityAnalyzer
    from .db_detector import DatabaseCallDetector
    from .db_compliance import DatabaseComplianceAnalyzer
    from .doc_coverage import DocCoverageAnalyzer
    from .summary import ProjectSummarizer
    LONG_WALK_AVAILABLE = True
except ImportError as e:
    LONG_WALK_AVAILABLE = False

console = Console() if RICH_AVAILABLE else None

def print_fancy(message: str, style: str = ""):
    """Print with rich formatting if available, otherwise plain text"""
    if RICH_AVAILABLE and console:
        console.print(message, style=style)
    else:
        print(message)

def print_panel(message: str, title: str = "", style: str = ""):
    """Print a panel with rich formatting if available"""
    if RICH_AVAILABLE and console:
        console.print(Panel(message, title=title, style=style))
    else:
        print(f"\n=== {title} ===")
        print(message)
        print("=" * (len(title) + 8))

class Walk3rCLI:
    def __init__(self):
        self.console = console
        
    def auto_detect_project(self, path: str = ".") -> Dict[str, Any]:
        """Auto-detect project type and suggest configuration"""
        path = Path(path).resolve()
        
        project_info = {
            "root_path": str(path),
            "project_type": "unknown",
            "suggested_config": {},
            "detected_files": []
        }
        
        # Check for common project files
        common_files = ["setup.py", "pyproject.toml", "requirements.txt", "__init__.py"]
        found_files = [f for f in common_files if (path / f).exists()]
        project_info["detected_files"] = found_files
        
        # Count Python files
        py_files = list(path.rglob("*.py"))
        project_info["python_files_count"] = len(py_files)
        
        # Determine project type
        if (path / "setup.py").exists() or (path / "pyproject.toml").exists():
            project_info["project_type"] = "python_package"
        elif (path / "__init__.py").exists():
            project_info["project_type"] = "python_module"
        elif len(py_files) > 0:
            project_info["project_type"] = "python_scripts"
        
        # Suggest configuration
        if len(py_files) < 10:
            size = "small"
        elif len(py_files) < 100:
            size = "medium"
        else:
            size = "large"
            
        project_info["suggested_config"] = {
            "root_path": str(path),
            "output_dir": "./walk3r_reports",
            "formats": ["json", "csv"] if size == "small" else ["json"],
            "enable_complexity": True,
            "enable_db_detection": True,
            "enable_doc_coverage": True,
            "enable_metrics": True,
            "enable_summary": True,
            "enable_db_compliance": size != "small"
        }
        
        return project_info
    
    def interactive_setup(self) -> Walk3rConfig:
        """Interactive configuration wizard"""
        print_panel("🚀 Welcome to Walk3r 2.0! Let's set up your analysis.", 
                   "Walk3r Setup Wizard", "bold blue")
        
        # Auto-detect current directory
        current_dir = os.getcwd()
        print_fancy(f"📁 Current directory: {current_dir}")
        
        # Ask for project path
        if RICH_AVAILABLE:
            project_path = Prompt.ask("🎯 Enter the path to your Python project", 
                                    default=current_dir)
        else:
            project_path = input(f"🎯 Enter the path to your Python project [{current_dir}]: ").strip()
            if not project_path:
                project_path = current_dir
        
        # Auto-detect project
        project_info = self.auto_detect_project(project_path)
        
        print_fancy(f"🔍 Detected: {project_info['project_type']}")
        print_fancy(f"📊 Found {project_info['python_files_count']} Python files")
        
        if project_info["detected_files"]:
            print_fancy(f"📋 Project files: {', '.join(project_info['detected_files'])}")
        
        # Ask if user wants recommended settings
        use_recommended = True
        if RICH_AVAILABLE:
            use_recommended = Confirm.ask("✨ Use recommended settings?", default=True)
        else:
            response = input("✨ Use recommended settings? [Y/n]: ").strip().lower()
            use_recommended = response in ['', 'y', 'yes']
        
        if use_recommended:
            config_dict = project_info["suggested_config"]
        else:
            # Manual configuration
            config_dict = self.manual_configuration(project_info)
        
        # Create config object
        config = Walk3rConfig(**config_dict)
        
        # Ask if user wants to save config
        save_config = True
        if RICH_AVAILABLE:
            save_config = Confirm.ask("💾 Save configuration to walk3r.toml?", default=True)
        else:
            response = input("💾 Save configuration to walk3r.toml? [Y/n]: ").strip().lower()
            save_config = response in ['', 'y', 'yes']
        
        if save_config:
            self.save_config(config_dict)
            print_fancy("✅ Configuration saved to walk3r.toml", "green")
        
        return config
    
    def manual_configuration(self, project_info: Dict) -> Dict[str, Any]:
        """Manual configuration for advanced users"""
        config = project_info["suggested_config"].copy()
        
        print_panel("🛠️ Manual Configuration", style="yellow")
        
        # Output directory
        if RICH_AVAILABLE:
            output_dir = Prompt.ask("📂 Output directory", default=config["output_dir"])
        else:
            output_dir = input(f"📂 Output directory [{config['output_dir']}]: ").strip()
            if not output_dir:
                output_dir = config["output_dir"]
        config["output_dir"] = output_dir
        
        # Analysis options
        analysis_options = [
            ("enable_complexity", "🧠 Complexity analysis"),
            ("enable_db_detection", "🗄️ Database detection"),
            ("enable_doc_coverage", "📚 Documentation coverage"),
            ("enable_metrics", "📊 Code metrics"),
            ("enable_summary", "📋 Summary generation"),
            ("enable_db_compliance", "🏗️ Database compliance")
        ]
        
        for key, description in analysis_options:
            if RICH_AVAILABLE:
                config[key] = Confirm.ask(description, default=config.get(key, True))
            else:
                response = input(f"{description} [Y/n]: ").strip().lower()
                config[key] = response in ['', 'y', 'yes']
        
        return config
    
    def save_config(self, config_dict: Dict[str, Any]):
        """Save configuration to walk3r.toml"""
        config_content = {
            "walk3r": config_dict
        }
        
        with open("walk3r.toml", "w") as f:
            toml.dump(config_content, f)
    
    def run_analysis_with_progress(self, config: Walk3rConfig) -> int:
        """Run analysis with progress indicators"""
        if not RICH_AVAILABLE:
            return self.run_analysis_simple(config)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            
            # Step 1: Module scanning
            task1 = progress.add_task("🔍 Scanning modules...", total=100)
            
            try:
                scanner = ModuleScanner(config.root_path)
                raw_data = scanner.scan()
                progress.update(task1, completed=50)
                
                linker = DependencyLinker(raw_data)
                dependency_map = linker.resolve_links()
                function_map = linker.get_function_map()
                progress.update(task1, completed=100)
                
                console.print(f"✅ Found {len(raw_data)} modules with {sum(len(data.get('functions', {})) for data in raw_data.values())} functions")
                
            except Exception as e:
                console.print(f"❌ Module scanning failed: {e}", style="red")
                return 1
            
            # Export basic files
            output_dir = Path(config.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            date_tag = datetime.now().strftime("%Y%m%d")
            
            task2 = progress.add_task("💾 Exporting basic files...", total=len(config.formats) + 2)
            
            for fmt in config.formats:
                output_path = output_dir / f"deps-{date_tag}.{fmt}"
                if fmt == "json":
                    export_json(dependency_map, output_path)
                elif fmt == "csv":
                    export_csv(dependency_map, output_path)
                elif fmt == "dot":
                    export_dot(dependency_map, output_path)
                progress.advance(task2)
            
            # Export function maps
            func_json_path = output_dir / f"functions-{date_tag}.json"
            export_function_map_json(function_map, func_json_path)
            progress.advance(task2)
            
            func_dot_path = output_dir / f"functions-{date_tag}.dot"
            export_function_dot(function_map, func_dot_path)
            progress.advance(task2)
            
            # Collect analysis data
            all_analysis_data = {
                'dependencies': dependency_map,
                'functions': function_map
            }
            
            # Run extended analysis
            analysis_steps = []
            if config.enable_metrics:
                analysis_steps.append(("📊 Analyzing metrics", self.run_metrics_analysis))
            if config.enable_complexity:
                analysis_steps.append(("🧠 Analyzing complexity", self.run_complexity_analysis))
            if config.enable_db_detection:
                analysis_steps.append(("🗄️ Detecting database calls", self.run_db_detection))
            if config.enable_doc_coverage:
                analysis_steps.append(("📚 Analyzing documentation", self.run_doc_analysis))
            if config.enable_db_compliance:
                analysis_steps.append(("🏗️ Checking compliance", self.run_compliance_analysis))
            if config.enable_summary:
                analysis_steps.append(("📋 Generating summaries", self.run_summary_generation))
            
            for description, analysis_func in analysis_steps:
                task = progress.add_task(description, total=100)
                try:
                    result = analysis_func(config, raw_data, output_dir, date_tag)
                    if result:
                        all_analysis_data.update(result)
                    progress.update(task, completed=100)
                except Exception as e:
                    console.print(f"⚠️ {description} failed: {e}", style="yellow")
                    progress.update(task, completed=100)
        
        # Final summary
        self.show_completion_summary(output_dir, date_tag)
        return 0
    
    def run_analysis_simple(self, config: Walk3rConfig) -> int:
        """Simple analysis without progress bars"""
        print_fancy("🚀 Starting Walk3r analysis...", "bold blue")
        
        # Basic scanning
        print_fancy("🔍 Scanning modules...")
        try:
            scanner = ModuleScanner(config.root_path)
            raw_data = scanner.scan()
            
            linker = DependencyLinker(raw_data)
            dependency_map = linker.resolve_links()
            function_map = linker.get_function_map()
            
            print_fancy(f"✅ Found {len(raw_data)} modules")
        except Exception as e:
            print_fancy(f"❌ Scanning failed: {e}", "red")
            return 1
        
        # Export files
        output_dir = Path(config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        date_tag = datetime.now().strftime("%Y%m%d")
        
        print_fancy("💾 Exporting files...")
        for fmt in config.formats:
            output_path = output_dir / f"deps-{date_tag}.{fmt}"
            if fmt == "json":
                export_json(dependency_map, output_path)
            elif fmt == "csv":
                export_csv(dependency_map, output_path)
            elif fmt == "dot":
                export_dot(dependency_map, output_path)
        
        print_fancy("✅ Analysis complete!")
        print_fancy(f"📁 Results saved to: {output_dir}")
        return 0
    
    def run_metrics_analysis(self, config, raw_data, output_dir, date_tag):
        """Run metrics analysis"""
        if not LONG_WALK_AVAILABLE:
            return None
        
        metrics_analyzer = MetricsAnalyzer(config.root_path, raw_data)
        metrics_data = metrics_analyzer.analyze_metrics()
        
        metrics_path = output_dir / f"metrics-{date_tag}.json"
        with open(metrics_path, 'w') as f:
            json.dump({"metrics": metrics_data}, f, indent=2)
        
        return {"metrics": metrics_data}
    
    def run_complexity_analysis(self, config, raw_data, output_dir, date_tag):
        """Run complexity analysis"""
        if not LONG_WALK_AVAILABLE:
            return None
        
        complexity_analyzer = ComplexityAnalyzer(config.root_path, raw_data, config)
        complexity_data = complexity_analyzer.analyze_complexity()
        
        complexity_path = output_dir / f"complexity-{date_tag}.json"
        with open(complexity_path, 'w') as f:
            json.dump({"complexity": complexity_data}, f, indent=2)
        
        return {"complexity": complexity_data}
    
    def run_db_detection(self, config, raw_data, output_dir, date_tag):
        """Run database detection"""
        if not LONG_WALK_AVAILABLE:
            return None
        
        db_detector = DatabaseCallDetector(config.root_path, raw_data, config)
        db_data = db_detector.detect_db_calls()
        
        db_path = output_dir / f"db-calls-{date_tag}.json"
        with open(db_path, 'w') as f:
            json.dump({"database_analysis": db_data}, f, indent=2)
        
        return {"db_calls": db_data}
    
    def run_doc_analysis(self, config, raw_data, output_dir, date_tag):
        """Run documentation analysis"""
        if not LONG_WALK_AVAILABLE:
            return None
        
        doc_analyzer = DocCoverageAnalyzer(config.root_path, raw_data)
        doc_data = doc_analyzer.analyze_documentation()
        
        doc_path = output_dir / f"doc-coverage-{date_tag}.json"
        with open(doc_path, 'w') as f:
            json.dump({"documentation": doc_data}, f, indent=2)
        
        return {"documentation": doc_data}
    
    def run_compliance_analysis(self, config, raw_data, output_dir, date_tag):
        """Run compliance analysis"""
        if not LONG_WALK_AVAILABLE:
            return None
        
        compliance_analyzer = DatabaseComplianceAnalyzer(config.root_path, raw_data, config)
        compliance_data = compliance_analyzer.analyze_compliance()
        
        compliance_path = output_dir / f"db-compliance-{date_tag}.json"
        with open(compliance_path, 'w') as f:
            json.dump({"database_compliance": compliance_data}, f, indent=2)
        
        return {"db_compliance": compliance_data}
    
    def run_summary_generation(self, config, raw_data, output_dir, date_tag):
        """Run summary generation"""
        if not LONG_WALK_AVAILABLE:
            return None
        
        # This would need the full analysis data
        return None
    
    def show_completion_summary(self, output_dir: Path, date_tag: str):
        """Show completion summary with helpful tips"""
        if RICH_AVAILABLE:
            table = Table(title="📊 Analysis Complete!")
            table.add_column("📁 File", style="cyan")
            table.add_column("📝 Description", style="green")
            
            files = [
                (f"deps-{date_tag}.json", "Module dependencies"),
                (f"functions-{date_tag}.json", "Function call graph"),
                (f"complexity-{date_tag}.json", "Code complexity analysis"),
                (f"summary-{date_tag}.json", "Human-readable summary")
            ]
            
            for filename, description in files:
                if (output_dir / filename).exists():
                    table.add_row(filename, description)
            
            console.print(table)
        
        print_panel(
            f"""🎉 Walk3r analysis complete!

📁 Results location: {output_dir}

💡 Next steps:
• Review summary-{date_tag}.json for project overview
• Upload files to AI assistants for code help
• Check complexity-{date_tag}.json for improvement areas
• Use deps-{date_tag}.json to understand dependencies

🤖 AI Assistant Tips:
• "Analyze this codebase" → Upload summary-{date_tag}.json
• "Help me refactor" → Upload complexity-{date_tag}.json  
• "Explain dependencies" → Upload deps-{date_tag}.json""",
            "🚀 Success!", "green"
        )
        
        # Ask if user wants to open results
        if RICH_AVAILABLE:
            open_results = Confirm.ask("🌐 Open results folder?", default=False)
            if open_results:
                try:
                    if sys.platform == "win32":
                        os.startfile(output_dir)
                    elif sys.platform == "darwin":
                        os.system(f"open {output_dir}")
                    else:
                        os.system(f"xdg-open {output_dir}")
                except:
                    print_fancy(f"📁 Results are in: {output_dir}")

def create_parser():
    """Create argument parser with user-friendly commands"""
    parser = argparse.ArgumentParser(
        description="Walk3r 2.0 - Easy code analysis for everyone",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  walk3r scan                    # Interactive setup and scan current directory
  walk3r scan /path/to/project   # Scan specific project
  walk3r setup                   # Configuration wizard only
  walk3r quick                   # Quick analysis with defaults
  
For AI assistants:
  walk3r scan --ai-ready        # Generate files optimized for AI upload
  
Visit: https://github.com/elevend0g/walk3r for more info
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scan command (main command)
    scan_parser = subparsers.add_parser('scan', help='Analyze your project')
    scan_parser.add_argument('path', nargs='?', default='.', 
                           help='Project path to analyze (default: current directory)')
    scan_parser.add_argument('--config', '-c', default='walk3r.toml',
                           help='Configuration file (default: walk3r.toml)')
    scan_parser.add_argument('--quick', '-q', action='store_true',
                           help='Quick analysis with minimal output')
    scan_parser.add_argument('--ai-ready', action='store_true',
                           help='Generate files optimized for AI assistants')
    scan_parser.add_argument('--no-setup', action='store_true',
                           help='Skip interactive setup')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Configuration wizard')
    setup_parser.add_argument('path', nargs='?', default='.',
                            help='Project path to configure')
    
    # Quick command
    quick_parser = subparsers.add_parser('quick', help='Quick analysis with defaults')
    quick_parser.add_argument('path', nargs='?', default='.',
                            help='Project path to analyze')
    
    return parser

def main():
    """Main CLI entry point"""
    parser = create_parser()
    
    # If no arguments, show help and run interactive mode
    if len(sys.argv) == 1:
        print_panel("🚀 Welcome to Walk3r 2.0!", "Easy Code Analysis", "bold blue")
        print_fancy("No command specified. Running interactive mode...", "yellow")
        sys.argv.append('scan')  # Default to scan command
    
    args = parser.parse_args()
    cli = Walk3rCLI()
    
    try:
        if args.command == 'setup':
            config = cli.interactive_setup()
            print_fancy("✅ Setup complete! Run 'walk3r scan' to analyze your project.", "green")
            return 0
            
        elif args.command == 'scan':
            # Check if config exists or if user wants interactive setup
            config_path = Path(args.config)
            config = None
            
            if not args.no_setup and not config_path.exists():
                print_fancy("📋 No configuration found. Let's set one up!", "yellow")
                config = cli.interactive_setup()
            else:
                # Load existing config or create default
                if config_path.exists():
                    try:
                        with open(config_path, 'r') as f:
                            config_data = toml.load(f)['walk3r']
                        config = Walk3rConfig(**config_data)
                        print_fancy(f"✅ Loaded configuration from {config_path}", "green")
                    except Exception as e:
                        print_fancy(f"⚠️ Config error: {e}. Using defaults.", "yellow")
                        config = None
                
                if config is None:
                    # Auto-detect and create basic config
                    project_info = cli.auto_detect_project(args.path)
                    config_dict = project_info["suggested_config"]
                    config_dict["root_path"] = args.path
                    config = Walk3rConfig(**config_dict)
            
            # Run analysis
            return cli.run_analysis_with_progress(config)
            
        elif args.command == 'quick':
            # Quick analysis with minimal configuration
            project_info = cli.auto_detect_project(args.path)
            config_dict = project_info["suggested_config"]
            config_dict["root_path"] = args.path
            config_dict["formats"] = ["json"]  # Minimal output
            config = Walk3rConfig(**config_dict)
            
            print_fancy("⚡ Running quick analysis...", "bold yellow")
            return cli.run_analysis_simple(config)
            
        else:
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        print_fancy("\n⚠️ Analysis cancelled by user", "yellow")
        return 1
    except Exception as e:
        print_fancy(f"❌ Error: {e}", "red")
        if "--debug" in sys.argv:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())