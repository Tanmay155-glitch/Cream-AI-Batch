#!/usr/bin/env python3
"""
check_no_secrets.py — Pre-commit secret scanner for LeniGuide.
Scans staged files (or all tracked files) for key-like strings and .env files.
Exit code 0 = clean, 1 = secrets found.
"""

import re
import subprocess
import sys

# Patterns that look like API keys or secrets
SECRET_PATTERNS = [
    re.compile(r'(?:GROQ_API_KEY|GEMINI_API_KEY|API_KEY|SECRET_KEY)\s*=\s*["\']?[A-Za-z0-9_\-]{20,}', re.IGNORECASE),
    re.compile(r'(?:sk-|gsk_|AIza)[A-Za-z0-9_\-]{20,}'),
    re.compile(r'Bearer\s+[A-Za-z0-9_\-]{20,}'),
]

# Files that must never be committed
FORBIDDEN_FILES = ['.env']

def get_staged_files():
    """Get list of staged files, or all tracked files if not in a git context."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True, text=True, timeout=10
        )
        files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
        if files:
            return files
    except Exception:
        pass

    # Fallback: check all tracked files
    try:
        result = subprocess.run(
            ['git', 'ls-files'],
            capture_output=True, text=True, timeout=10
        )
        return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
    except Exception:
        return []


def check_for_secrets():
    """Scan files for secrets and forbidden filenames."""
    files = get_staged_files()
    issues = []

    for filepath in files:
        # Check for forbidden files
        basename = filepath.split('/')[-1].split('\\')[-1]
        if basename in FORBIDDEN_FILES:
            issues.append(f"FORBIDDEN FILE: {filepath} (must not be committed)")
            continue

        # Skip binary and non-text files
        if any(filepath.endswith(ext) for ext in ['.pyc', '.png', '.jpg', '.svg', '.ico', '.woff', '.exe', '.dll']):
            continue

        # Read and scan file contents
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            for pattern in SECRET_PATTERNS:
                matches = pattern.findall(content)
                for match in matches:
                    # Exclude .env.example placeholders
                    if 'your_' in match.lower() or 'placeholder' in match.lower() or 'example' in match.lower():
                        continue
                    if 'YOUR_' in match or 'PASTE_' in match:
                        continue
                    issues.append(f"POSSIBLE SECRET in {filepath}: {match[:40]}...")

        except (FileNotFoundError, PermissionError):
            continue

    return issues


def main():
    print("=" * 60)
    print("LeniGuide Secret Scanner (check_no_secrets.py)")
    print("=" * 60)

    issues = check_for_secrets()

    if issues:
        print(f"\n❌ FAILED: Found {len(issues)} issue(s):\n")
        for issue in issues:
            print(f"  🚨 {issue}")
        print("\nFix these before committing!")
        sys.exit(1)
    else:
        print("\n✅ CLEAN: No secrets or forbidden files detected.")
        sys.exit(0)


if __name__ == "__main__":
    main()
