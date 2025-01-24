#!/usr/bin/env python3
"""
Minimal project flattener with gitignore-style patterns
"""

import argparse
import fnmatch
from pathlib import Path

# --- Core Logic ---
def load_ignore_patterns(root, ignore_file):
    patterns = ['.git*', '__pycache__', 'venv', 'node_modules', '*.pyc']
    if ignore_file and (path := Path(ignore_file)).exists():
        patterns += [ln.strip() for ln in path.read_text().splitlines() 
                    if ln.strip() and not ln.startswith('#')]
    return [p.replace('\\', '/') for p in patterns]

def is_binary(path):
    try:
        with path.open('rb') as f:
            return b'\x00' in (f.read(512) or b'')
    except OSError:
        return True

def read_with_fallback(path):
    for enc in ('utf-8', 'latin-1'):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return None

def main():
    parser = argparse.ArgumentParser(description='Flatten codebase to markdown')
    parser.add_argument('--root', default='.', help='Project root (default: .)')
    parser.add_argument('--output', default='codebase.md', help='Output file')
    parser.add_argument('--ignore-file', help='Custom ignore file')
    parser.add_argument('--include-binary', action='store_true')
    parser.add_argument('--include-hidden', action='store_true')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    patterns = load_ignore_patterns(root, args.ignore_file)
    
    with Path(args.output).open('w', encoding='utf-8') as md:
        md.write(f"# {root.name} Codebase\n\n")
        
        for path in root.rglob('*'):
            rel_path = path.relative_to(root)
            str_path = str(rel_path).replace('\\', '/')
            
            if (not args.include_hidden and rel_path.name.startswith('.')) or \
               any(fnmatch.fnmatch(str_path, p) for p in patterns):
                continue
                
            if path.is_file() and (args.include_binary or not is_binary(path)):
                if content := read_with_fallback(path):
                    lang = {'md': 'markdown'}.get(path.suffix[1:], '')
                    md.write(f"## `{rel_path}`\n```{lang}\n{content}\n```\n\n")

if __name__ == '__main__':
    main()
