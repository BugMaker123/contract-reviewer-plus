#!/usr/bin/env python3
"""
File limits checker enforcing guidelines from 07-可维护性与文件门禁.md:
- Vue SFC: <= 300 lines, <= 24 KiB
- TS/JS: <= 300 lines, <= 24 KiB
- Python: <= 400 lines, <= 32 KiB
- CSS: <= 300 lines, <= 24 KiB
- Prompt: <= 120 lines, <= 16 KiB
- Markdown docs: <= 250 lines (ADR <= 100 lines)
"""
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

LIMITS = {
    ".vue": {"lines": 300, "bytes": 24 * 1024, "desc": "Vue SFC"},
    ".ts": {"lines": 300, "bytes": 24 * 1024, "desc": "TypeScript"},
    ".js": {"lines": 300, "bytes": 24 * 1024, "desc": "JavaScript"},
    ".py": {"lines": 400, "bytes": 32 * 1024, "desc": "Python business code"},
    ".css": {"lines": 300, "bytes": 24 * 1024, "desc": "Handwritten CSS"},
    ".md": {"lines": 250, "bytes": 32 * 1024, "desc": "Design/Docs Markdown"},
}

EXCLUDED_DIRS = {
    "node_modules", ".venv", "venv", "dist", "build",
    "__pycache__", ".git", ".idea", ".vscode", "coverage",
    ".system_generated", "generated"
}

EXCLUDED_FILES = {
    "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "poetry.lock"
}

def count_file(path: Path):
    try:
        content = path.read_bytes()
        size_bytes = len(content)
        lines = len(content.split(b"\n"))
        return lines, size_bytes
    except Exception as e:
        print(f"Warning: could not read {path}: {e}")
        return 0, 0

def check_files():
    violations = []
    checked = 0

    for root, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for f in files:
            if f in EXCLUDED_FILES:
                continue
            path = Path(root) / f
            ext = path.suffix.lower()
            if ext not in LIMITS:
                continue

            # Special case for ADR markdown or prompts
            limit = LIMITS[ext].copy()
            if ext == ".md":
                if "prompts" in path.parts:
                    limit = {"lines": 120, "bytes": 16 * 1024, "desc": "Prompt file"}
                elif "adr" in path.parts:
                    limit = {"lines": 100, "bytes": 16 * 1024, "desc": "ADR document"}
                elif "业务设计" in path.parts or "需求文档" in path.name:
                    # Existing pre-refactor PRD is excluded from hand-written limits
                    continue

            lines, size_bytes = count_file(path)
            checked += 1

            if lines > limit["lines"] or size_bytes > limit["bytes"]:
                violations.append({
                    "path": str(path.relative_to(ROOT_DIR)),
                    "lines": lines,
                    "max_lines": limit["lines"],
                    "bytes": size_bytes,
                    "max_bytes": limit["bytes"],
                    "desc": limit["desc"],
                })

    print(f"=== Quality Gate: Checked {checked} files ===")
    if violations:
        print(f"FAILED: Found {len(violations)} file limit violations:")
        for v in violations:
            print(f"  - {v['path']}: {v['lines']} lines (max {v['max_lines']}), {v['bytes']} bytes (max {v['max_bytes']}) [{v['desc']}]")
        return 1
    else:
        print("PASSED: All checked files conform to maintainability standards.")
        return 0

if __name__ == "__main__":
    sys.exit(check_files())
