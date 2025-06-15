# cli.py

import argparse
import sys
import toml
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from .scanner import ModuleScanner
from .linker import DependencyLinker
from .exporter import export_json, export_csv, export_dot, export_function_map_json, export_function_dot
from .config import Walk3rConfig

# Import new analysis modules (with graceful fallback)
try:
    from .metrics import MetricsAnalyzer
    from .complexity import ComplexityAnalyzer
    from .db_detector import DatabaseCallDetector
    from .doc_coverage import DocCoverageAnalyzer
    from .summary import ProjectSummarizer
    LONG_WALK_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Long walk modules not available: {e}")
    print("   Only basic analysis mode will work.")
    LONG_WALK_AVAILABLE = False

def main():
    parser = argparse.ArgumentParser(description="Walk3r - Python Dependency Mapper")
    parser.add_argument("--path", required=True, help="Path to source directory")
    parser.add_argument("--format", choices=["json", "csv", "dot"], default="json", help="Export format")
    parser.add_argument("--output", default=f"dependency_graph-{datetime.now().strftime('%Y%m%d')}", help="Output file name without extension")
    parser.add_argument("--mode", choices=["basic", "long"], default="basic", help="Analysis mode: basic (original) or long (comprehensive)")
    parser.add_argument("--config", default="walk3r.toml", help="Configuration file path")
    args = parser.parse_args()

    try:
        if args.mode == "basic":
            return run_basic_analysis(args)
        elif args.mode == "long":
            if not LONG_WALK_AVAILABLE:
                print("❌ Long walk mode requires additional analysis modules that are not available.")
                print("   Please ensure all analysis modules are properly installed.")
                return 1
            return run_long_walk_analysis(args)
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return 1

def run_basic_analysis(args):
    """Run the original basic analysis (preserves exact original functionality)"""
    print("🚶 Running basic dependency analysis...")
    
    scanner = ModuleScanner(args.path)
    raw_data = scanner.scan()

    linker = DependencyLinker(raw_data)
    mapped = linker.resolve_links()

    output_path = f"{args.output}.{args.format}"
    if args.format == "json":
        export_json(mapped, output_path)
    elif args.format == "csv":
        export_csv(mapped, output_path)
    elif args.format == "dot":
        export_dot(mapped, output_path)

    print(f"✅ Dependency graph written to {output_path}")
    return 0

def run_long_walk_analysis(args):
    """Run comprehensive long walk analysis"""
    print("🚶‍♀️ Running comprehensive long walk analysis...")
    
    # Load configuration
    try:
        with open(args.config, 'r') as f:
            config_data = toml.load(f)['walk3r']
        config = Walk3rConfig(**config_data)
    except Exception as e:
        print(f"⚠️  Warning: Could not load config from {args.config}, using defaults: {e}")
        config = Walk3rConfig(
            root_path=args.path,
            output_dir="./reports/",
            formats=["json"]
        )
    
    # Use config values, with command line overrides
    root_path = getattr(config, 'root_path', args.path)
    output_dir = Path(config.output_dir)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get timestamp for all files
    date_tag = datetime.now().strftime("%Y%m%d")
    
    print(f"📁 Output directory: {output_dir}")
    print(f"🎯 Analyzing: {root_path}")
    
    # Step 1: Basic dependency analysis (same as original)
    print("\n📊 Step 1: Scanning modules and dependencies...")
    try:
        scanner = ModuleScanner(root_path)
        raw_data = scanner.scan()
        
        linker = DependencyLinker(raw_data)
        dependency_map = linker.resolve_links()
        function_map = linker.get_function_map()
        
        print(f"   Found {len(raw_data)} modules with {sum(len(data.get('functions', {})) for data in raw_data.values())} functions")
    except Exception as e:
        print(f"   ❌ Module scanning failed: {e}")
        return 1
    
    # Export basic dependency files
    for fmt in config.formats:
        try:
            output_path = output_dir / f"deps-{date_tag}.{fmt}"
            if fmt == "json":
                export_json(dependency_map, output_path)
            elif fmt == "csv":
                export_csv(dependency_map, output_path)
            elif fmt == "dot":
                export_dot(dependency_map, output_path)
            print(f"   ✅ Basic {fmt.upper()} exported: {output_path.name}")
        except Exception as e:
            print(f"   ⚠️  Warning: Could not export {fmt}: {e}")
    
    # Export function maps
    try:
        func_json_path = output_dir / f"functions-{date_tag}.json"
        export_function_map_json(function_map, func_json_path)
        print(f"   ✅ Function map exported: {func_json_path.name}")
        
        func_dot_path = output_dir / f"functions-{date_tag}.dot"
        export_function_dot(function_map, func_dot_path)
        print(f"   ✅ Function graph exported: {func_dot_path.name}")
    except Exception as e:
        print(f"   ⚠️  Warning: Could not export function maps: {e}")
    
    # Collect all analysis data
    all_analysis_data = {
        'dependencies': dependency_map,
        'functions': function_map
    }
    
    # Step 2: Metrics Analysis
    if config.enable_metrics:
        print("\n📏 Step 2: Analyzing code metrics...")
        try:
            metrics_analyzer = MetricsAnalyzer(root_path, raw_data)
            metrics_data = metrics_analyzer.analyze_metrics()
            all_analysis_data['metrics'] = metrics_data
            
            metrics_path = output_dir / f"metrics-{date_tag}.json"
            with open(metrics_path, 'w', encoding='utf-8') as f:
                json.dump({"metrics": metrics_data}, f, indent=2)
            print(f"   ✅ Metrics analysis exported: {metrics_path.name}")
            
            # Print brief summary
            summary = metrics_data.get('project_summary', {})
            print(f"   📈 Project: {summary.get('total_files', 0)} files, {summary.get('total_lines_of_code', 0)} lines, {summary.get('total_functions', 0)} functions")
        except Exception as e:
            print(f"   ⚠️  Warning: Metrics analysis failed: {e}")
    
    # Step 3: Complexity Analysis
    if config.enable_complexity:
        print("\n🧠 Step 3: Analyzing function complexity...")
        try:
            complexity_analyzer = ComplexityAnalyzer(root_path, raw_data, config)
            complexity_data = complexity_analyzer.analyze_complexity()
            all_analysis_data['complexity'] = complexity_data
            
            complexity_path = output_dir / f"complexity-{date_tag}.json"
            with open(complexity_path, 'w', encoding='utf-8') as f:
                json.dump({"complexity": complexity_data}, f, indent=2)
            print(f"   ✅ Complexity analysis exported: {complexity_path.name}")
            
            # Print brief summary
            summary = complexity_data.get('complexity_summary', {})
            high_complexity = summary.get('high_complexity', 0)
            total_functions = summary.get('total_functions', 0)
            if total_functions > 0:
                print(f"   🎯 Complexity: {high_complexity}/{total_functions} functions need attention ({round(high_complexity/total_functions*100, 1)}%)")
        except Exception as e:
            print(f"   ⚠️  Warning: Complexity analysis failed: {e}")
    
    # Step 4: Database Detection
    if config.enable_db_detection:
        print("\n🗄️  Step 4: Detecting database operations...")
        try:
            db_detector = DatabaseCallDetector(root_path, raw_data, config)
            db_data = db_detector.detect_db_calls()
            all_analysis_data['db_calls'] = db_data
            
            db_path = output_dir / f"db-calls-{date_tag}.json"
            with open(db_path, 'w', encoding='utf-8') as f:
                json.dump({"database_analysis": db_data}, f, indent=2)
            print(f"   ✅ Database analysis exported: {db_path.name}")
            
            # Print brief summary
            summary = db_data.get('database_summary', {})
            db_modules = summary.get('modules_with_db_access', 0)
            total_ops = summary.get('total_db_operations', 0)
            if total_ops > 0:
                print(f"   💾 Database: {total_ops} operations across {db_modules} modules")
            else:
                print(f"   💾 Database: No database operations detected")
        except Exception as e:
            print(f"   ⚠️  Warning: Database detection failed: {e}")
    
    # Step 5: Documentation Coverage
    if config.enable_doc_coverage:
        print("\n📚 Step 5: Analyzing documentation coverage...")
        try:
            doc_analyzer = DocCoverageAnalyzer(root_path, raw_data)
            doc_data = doc_analyzer.analyze_documentation()
            all_analysis_data['documentation'] = doc_data
            
            doc_path = output_dir / f"doc-coverage-{date_tag}.json"
            with open(doc_path, 'w', encoding='utf-8') as f:
                json.dump({"documentation": doc_data}, f, indent=2)
            print(f"   ✅ Documentation analysis exported: {doc_path.name}")
            
            # Print brief summary
            summary = doc_data.get('coverage_summary', {})
            func_coverage = summary.get('function_coverage_percentage', 0)
            quality = summary.get('overall_quality', 'Unknown')
            print(f"   📖 Documentation: {func_coverage}% function coverage - {quality.lower()}")
        except Exception as e:
            print(f"   ⚠️  Warning: Documentation analysis failed: {e}")
    
    # Step 6: Generate Summaries
    if config.enable_summary:
        print("\n📋 Step 6: Generating project summaries...")
        try:
            summarizer = ProjectSummarizer(all_analysis_data)
            
            # Generate main summary
            summary_data = summarizer.generate_summary()
            summary_path = output_dir / f"summary-{date_tag}.json"
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump({"project_summary": summary_data}, f, indent=2)
            print(f"   ✅ Project summary exported: {summary_path.name}")
            
            # Generate LLM context
            llm_context = summarizer.create_llm_context()
            llm_path = output_dir / f"llm-context-{date_tag}.json"
            with open(llm_path, 'w', encoding='utf-8') as f:
                json.dump({"llm_context": llm_context}, f, indent=2)
            print(f"   ✅ LLM context exported: {llm_path.name}")
            
        except Exception as e:
            print(f"   ⚠️  Warning: Summary generation failed: {e}")
    
    # Final summary
    print(f"\n🎉 Long walk analysis complete!")
    print(f"📁 All files saved to: {output_dir}")
    print(f"💡 Pro tip: Upload the summary-{date_tag}.json to ChatGPT/Claude to ask questions about your codebase!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())