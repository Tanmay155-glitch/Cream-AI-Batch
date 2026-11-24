#!/usr/bin/env python3
"""
LeniGuide Code Compliance Checker
Systematically verifies each requirement against actual code files
"""

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple


@dataclass
class Finding:
    req_id: str
    requirement: str
    verdict: str  # MET, PARTIAL, MISSING, MD-ONLY, UNVERIFIABLE
    file_line: str
    evidence: str
    gap: str
    fix: str

def check_file_exists(path: str) -> Tuple[bool, str]:
    """Check if file exists and return path"""
    p = Path(path)
    if p.exists():
        return True, str(p)
    return False, ""

def search_in_file(filepath: str, pattern: str) -> List[Tuple[int, str]]:
    """Search for pattern in file, return (line_num, line_text) tuples"""
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    results.append((i, line.strip()))
    except:
        pass
    return results

def count_lines(filepath: str) -> int:
    """Count non-empty lines in file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return len([line for line in f if line.strip()])
    except Exception:
        return 0

def load_json(filepath: str) -> dict:
    """Load JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def main():
    findings = []
    
    # === A. Day 1 ===
    print("[A] Checking Day 1 requirements...")
    
    # R-01: day01_intro.py
    exists, path = check_file_exists("day01_intro.py")
    if exists:
        lines = count_lines(path)
        has_input = bool(search_in_file(path, r'input\('))
        has_fstring = bool(search_in_file(path, r'f["\']'))
        
        if has_input and has_fstring and lines > 10:
            findings.append(Finding(
                "R-01", "day01_intro.py with variables, f-strings, input()",
                "MET", f"{path}:all", 
                f"File exists ({lines} lines), uses input() and f-strings",
                "", ""
            ))
        else:
            findings.append(Finding(
                "R-01", "day01_intro.py",
                "PARTIAL", f"{path}:all",
                f"File exists but missing: input={has_input}, f-string={has_fstring}",
                "May be incomplete", "Add missing features"
            ))
    else:
        findings.append(Finding(
            "R-01", "day01_intro.py",
            "MISSING", "", "File not found", "Required Day 1 deliverable", "Create file"
        ))
    
    # R-02: day01_menu.py
    exists, path = check_file_exists("day01_menu.py")
    if exists:
        content = open(path, 'r').read()
        has_while = 'while' in content.lower()
        has_menu = any(x in content for x in ['1', '2', '3', '0'])
        
        if has_while and has_menu:
            findings.append(Finding(
                "R-02", "day01_menu.py with while loop menu",
                "MET", f"{path}:all",
                "Has while loop and menu options",
                "", ""
            ))
        else:
            findings.append(Finding(
                "R-02", "day01_menu.py",
                "PARTIAL", f"{path}:all",
                f"while={has_while}, menu={has_menu}",
                "Menu logic incomplete", "Add full menu"
            ))
    else:
        findings.append(Finding(
            "R-02", "day01_menu.py",
            "MISSING", "", "File not found", "", "Create file"
        ))
    
    # === B. Day 2 ===
    print("[B] Checking Day 2 requirements...")
    
    # R-03: Sample records (20 records with 6 fields)
    sample_paths = ["data/sample_records.json", "data/sample_records.py", "data/records.json"]
    found_sample = False
    for spath in sample_paths:
        if Path(spath).exists():
            if spath.endswith('.json'):
                data = load_json(spath)
                if isinstance(data, list) and len(data) == 20:
                    # Check fields
                    required_fields = {'site', 'cave_no', 'religion_period', 'highlights', 'visit_info', 'source_url'}
                    if data and all(required_fields.issubset(set(r.keys())) for r in data):
                        findings.append(Finding(
                            "R-03", "Sample records: 20 records with 6 fields",
                            "MET", f"{spath}:1",
                            f"Found {len(data)} records with correct fields",
                            "", ""
                        ))
                        found_sample = True
                    else:
                        findings.append(Finding(
                            "R-03", "Sample records",
                            "PARTIAL", f"{spath}:1",
                            f"Found {len(data)} records, field check needed",
                            "May be missing fields", "Verify all 6 fields present"
                        ))
                        found_sample = True
                else:
                    findings.append(Finding(
                        "R-03", "Sample records",
                        "PARTIAL", f"{spath}:1",
                        f"Found file but has {len(data) if isinstance(data, list) else '?'} records (need 20)",
                        "Need exactly 20 records", "Add/remove records"
                    ))
                    found_sample = True
            break
    
    if not found_sample:
        findings.append(Finding(
            "R-03", "Sample records",
            "MISSING", "", "No sample_records.json or records.json found",
            "Required data file", "Create data file"
        ))
    
    # R-04: Cave number verification - will be done in separate script
    findings.append(Finding(
        "R-04", "Verify exact cave numbers",
        "DEFERRED", "data/records.json",
        "Requires parsing - see separate check script",
        "", "Run cave number verification"
    ))
    
    # R-05: app/records.py functions
    exists, path = check_file_exists("app/records.py")
    if exists:
        content = open(path, 'r').read()
        funcs = {
            'load_records': 'def load_records' in content,
            'search': 'def search' in content,
            'count_by': 'def count_by' in content,
            'get_by_id': 'def get_by_id' in content
        }
        
        if all(funcs.values()):
            # Check for real logic (not just pass)
            has_logic = 'return' in content and len(content) > 500
            if has_logic:
                findings.append(Finding(
                    "R-05", "app/records.py with 4 functions",
                    "MET", f"{path}:1",
                    f"All 4 functions present with logic ({len(content)} chars)",
                    "", ""
                ))
            else:
                findings.append(Finding(
                    "R-05", "app/records.py",
                    "PARTIAL", f"{path}:1",
                    "Functions exist but may be stubs",
                    "Need real implementations", "Implement full logic"
                ))
        else:
            missing = [k for k, v in funcs.items() if not v]
            findings.append(Finding(
                "R-05", "app/records.py",
                "PARTIAL", f"{path}:1",
                f"Missing functions: {', '.join(missing)}",
                f"Need {len(missing)} more functions", "Implement missing functions"
            ))
    else:
        findings.append(Finding(
            "R-05", "app/records.py",
            "MISSING", "", "File not found", "Required module", "Create file"
        ))
    
    # Save findings
    print(f"\nGenerated {len(findings)} findings so far...")
    return findings

if __name__ == "__main__":
    findings = main()
    
    # Save to JSON for further processing
    output = []
    for f in findings:
        output.append({
            'req_id': f.req_id,
            'requirement': f.requirement,
            'verdict': f.verdict,
            'file_line': f.file_line,
            'evidence': f.evidence,
            'gap': f.gap,
            'fix': f.fix
        })
    
    with open('code_compare/logs/findings_partial.json', 'w') as out:
        json.dump(output, out, indent=2)
    
    print(f"Saved {len(output)} findings to findings_partial.json")
    print("\nVerdict summary:")
    verdicts = {}
    for f in findings:
        verdicts[f.verdict] = verdicts.get(f.verdict, 0) + 1
    for v, count in sorted(verdicts.items()):
        print(f"  {v}: {count}")
