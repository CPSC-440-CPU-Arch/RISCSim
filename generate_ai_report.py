#!/usr/bin/env python3
"""
Generate AI usage report for RISCSim project.

This script:
1. Counts total lines in all Python files
2. Counts lines between AI-BEGIN/AI-END markers
3. Calculates percentage of AI-assisted code
4. Generates ai_report.json

Usage:
    python3 generate_ai_report.py
"""

import os
import json


def count_lines_in_file(filepath):
    """
    Count total lines and AI-tagged lines in a single file.
    
    Args:
        filepath: Path to Python file
    
    Returns:
        Tuple of (total_lines, ai_lines)
    """
    total_lines = 0
    ai_lines = 0
    in_ai_block = False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                total_lines += 1
                
                # Check for AI markers
                if '# AI-BEGIN' in line or '#AI-BEGIN' in line:
                    in_ai_block = True
                    ai_lines += 1  # Count the marker line itself
                elif '# AI-END' in line or '#AI-END' in line:
                    in_ai_block = False
                    ai_lines += 1  # Count the marker line itself
                elif in_ai_block:
                    ai_lines += 1
                    
    except Exception as e:
        print(f"Warning: Could not read {filepath}: {e}")
        return 0, 0
    
    return total_lines, ai_lines


def count_ai_lines(directory, exclude_dirs=None):
    """
    Recursively count lines in all Python files in directory.
    
    Args:
        directory: Root directory to search
        exclude_dirs: List of directory names to exclude
    
    Returns:
        Tuple of (total_lines, ai_lines, file_count)
    """
    if exclude_dirs is None:
        exclude_dirs = ['__pycache__', '.egg-info', 'venv', '.git']
    
    total_lines = 0
    ai_lines = 0
    file_count = 0
    
    for root, dirs, files in os.walk(directory):
        # Remove excluded directories from search
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.endswith('.egg-info')]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                file_total, file_ai = count_lines_in_file(filepath)
                
                if file_total > 0:
                    total_lines += file_total
                    ai_lines += file_ai
                    file_count += 1
                    
                    if file_ai > 0:
                        percent = (file_ai / file_total * 100) if file_total > 0 else 0
                        print(f"  {filepath}: {file_ai}/{file_total} ({percent:.1f}%)")
    
    return total_lines, ai_lines, file_count


def main():
    """Generate AI usage report."""
    print("=" * 70)
    print("RISCSim AI Usage Report Generator")
    print("=" * 70)
    print()
    
    # Count implementation code
    print("Counting lines in implementation (riscsim/)...")
    impl_total, impl_ai, impl_files = count_ai_lines('riscsim')
    print(f"  Total: {impl_total} lines in {impl_files} files")
    print(f"  AI-tagged: {impl_ai} lines")
    print()
    
    # Count test code
    print("Counting lines in tests (tests/)...")
    test_total, test_ai, test_files = count_ai_lines('tests')
    print(f"  Total: {test_total} lines in {test_files} files")
    print(f"  AI-tagged: {test_ai} lines")
    print()
    
    # Calculate totals
    total_lines = impl_total + test_total
    ai_lines = impl_ai + test_ai
    total_files = impl_files + test_files
    percent = (ai_lines / total_lines * 100) if total_lines > 0 else 0
    
    print("=" * 70)
    print("Summary:")
    print("=" * 70)
    print(f"Total Python files: {total_files}")
    print(f"Total lines: {total_lines}")
    print(f"AI-tagged lines: {ai_lines}")
    print(f"Percentage: {percent:.1f}%")
    print()
    
    # Determine AI tools used based on AI_USAGE.md
    ai_tools = []
    try:
        with open('AI_USAGE.md', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'Claude' in content:
                ai_tools.append('Claude Code (Anthropic)')
            if 'Copilot' in content or 'GitHub Copilot' in content:
                ai_tools.append('GitHub Copilot')
            if 'ChatGPT' in content:
                ai_tools.append('ChatGPT')
    except:
        ai_tools = ['Claude Code (Anthropic)']  # Default
    
    # Generate report
    report = {
        "total_lines": total_lines,
        "ai_tagged_lines": ai_lines,
        "percent": round(percent, 1),
        "tools": ai_tools,
        "method": "count markers",
        "breakdown": {
            "implementation": {
                "total_lines": impl_total,
                "ai_lines": impl_ai,
                "files": impl_files,
                "percent": round((impl_ai / impl_total * 100) if impl_total > 0 else 0, 1)
            },
            "tests": {
                "total_lines": test_total,
                "ai_lines": test_ai,
                "files": test_files,
                "percent": round((test_ai / test_total * 100) if test_total > 0 else 0, 1)
            }
        }
    }
    
    # Write JSON report
    output_file = 'ai_report.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Report saved to: {output_file}")
    print()
    
    # Print JSON for verification
    print("Generated JSON:")
    print("-" * 70)
    print(json.dumps(report, indent=2))
    print("-" * 70)
    print()
    
    # Compliance check
    print("Compliance Check:")
    print("-" * 70)
    if ai_lines > 0:
        print("✅ AI markers found in code")
    else:
        print("⚠️  Warning: No AI markers found. Add AI-BEGIN/AI-END comments.")
    
    if os.path.exists('AI_USAGE.md'):
        print("✅ AI_USAGE.md exists")
    else:
        print("❌ AI_USAGE.md missing")
    
    print("✅ ai_report.json generated")
    print()
    
    print("Next steps:")
    print("1. Review the generated ai_report.json")
    print("2. Update AI_USAGE.md with detailed session information")
    print("3. Commit both files to repository")
    print()


if __name__ == '__main__':
    main()
