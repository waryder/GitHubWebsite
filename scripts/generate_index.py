#!/usr/bin/env python3
"""
Generate index.html — nested tree of every .html/.htm page in the repo.
Run by .github/workflows/generate-index.yml on every push to main.
"""

from __future__ import annotations
import os
from pathlib import Path
from html import escape

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT = REPO_ROOT / "index.html"

# Folders to skip entirely
SKIP_DIRS = {".git", ".github", "node_modules", "scripts"}
# File extensions to include
INCLUDE_EXT = {".html", ".htm"}
# Files to skip by name (the generated index itself)
SKIP_FILES = {"index.html"}


def build_tree(root: Path) -> dict:
    """Return a nested dict: {folder_name: {...children..., '__files__': [filenames]}}"""
    tree: dict = {"__files__": []}
    for entry in sorted(root.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
        if entry.name.startswith("."):
            continue
        if entry.is_dir():
            if entry.name in SKIP_DIRS:
                continue
            sub = build_tree(entry)
            # Only include the folder if it has any html descendants
            if has_pages(sub):
                tree[entry.name] = sub
        else:
            if entry.name in SKIP_FILES:
                continue
            if entry.suffix.lower() in INCLUDE_EXT:
                tree["__files__"].append(entry.name)
    return tree


def has_pages(node: dict) -> bool:
    if node.get("__files__"):
        return True
    return any(has_pages(v) for k, v in node.items() if k != "__files__")


def render(node: dict, path_prefix: str = "") -> str:
    """Recursively render the tree to nested <ul>/<li> HTML."""
    parts: list[str] = []
    # Files at this level
    for fname in node.get("__files__", []):
        href = f"{path_prefix}{fname}" if path_prefix else fname
        parts.append(f'    <li class="file"><a href="{escape(href)}">{escape(fname)}</a></li>')
    # Subfolders
    for key, sub in node.items():
        if key == "__files__":
            continue
        sub_prefix = f"{path_prefix}{key}/"
        parts.append(f'    <li class="folder"><details open><summary>{escape(key)}/</summary>')
        parts.append("      <ul>")
        parts.append(render(sub, sub_prefix))
        parts.append("      </ul>")
        parts.append("    </details></li>")
    return "\n".join(parts)


def main() -> None:
    tree = build_tree(REPO_ROOT)
    body = render(tree)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Big Buffalo Bill Web Resources - Site Index</title>
  <style>
    :root {{ color-scheme: light dark; font-family: system-ui, sans-serif; }}
    body {{ max-width: 900px; margin: 2rem auto; padding: 0 1.25rem; line-height: 1.5; }}
    h1 {{ margin-bottom: 0.25rem; }}
    .meta {{ color: #888; font-size: 0.9rem; margin-bottom: 1.5rem; }}
    ul {{ list-style: none; padding-left: 1.25rem; }}
    li.folder > details > summary {{ cursor: pointer; font-weight: 600; }}
    li.file a {{ text-decoration: none; }}
    li.file a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <h1>Big Buffalo Bill Web Resources - Site Index</h1>
  <p class="meta">Auto-generated. Updated on every push to <code>main</code>.</p>
  <ul>
{body}
  </ul>
</body>
</html>
"""
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)} ({OUTPUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
