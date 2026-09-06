#!/usr/bin/env python3
"""Internal link/asset check for this portfolio + resume site.

Walks every .html file in the repo and verifies every internal href/src
resolves to a file that actually exists -- checked case-sensitively, since
GitHub Pages serves from Linux even though this may be run on a
case-insensitive filesystem. Handles this site's root-relative paths
(e.g. href="/resume/full/") by resolving them against the repo root, since
this repo publishes as a user site (ylnhari.github.io) where "/" *is* the
repo root -- and directory-style links (trailing slash, or a bare directory)
by looking for an index.html inside. External links (http/https, mailto,
tel, javascript, data URIs) and same-page fragments are skipped; this script
does not check external URLs.

It also lists tracked files that no page links to (checked with `git
ls-files`, skipping config/tooling files). This is reported as a WARNING and
never fails the run -- an unlinked tracked file (e.g. a resume PDF kept for
direct download) may be entirely intentional; only the owner should decide
whether to link it, remove it, or leave it.

Exit 0: every internal href/src resolves (regardless of orphan warnings).
Exit 1: at least one href/src does not resolve -- the message names the page
  and the target.

Usage:
    python scripts/check_links.py
"""
from __future__ import annotations

import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

REPO_ROOT = Path(__file__).resolve().parent.parent
SKIP_DIR_NAMES = {".git"}
LINK_ATTRS = {"href", "src"}
EXTERNAL_SCHEMES = {"http", "https", "mailto", "tel", "javascript", "data"}

# Tracked files that are config/tooling, not content -- never candidates for
# the "orphaned asset" warning. index.html is the site's own entry point: by
# definition nothing inside the site links to it, that's not an orphan.
ORPHAN_EXEMPT = {
    "index.html",
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    ".nojekyll",
    ".gitignore",
}
ORPHAN_EXEMPT_DIRS = {".github", "scripts"}


class RefCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.refs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in LINK_ATTRS and value:
                self.refs.append(value)


def is_external_or_fragment(value: str) -> bool:
    if value.startswith("#"):
        return True
    if value.startswith("//"):
        return True
    scheme = urlsplit(value).scheme
    return scheme.lower() in EXTERNAL_SCHEMES


def resolve(start_dir: Path, target: str) -> Path | None:
    """Resolve `target` (relative to start_dir, or repo-root-relative if it
    starts with '/') to an existing file, matching case exactly. Returns the
    resolved Path (relative-to-root form obtainable via .relative_to), or
    None if it doesn't resolve."""
    if target.startswith("/"):
        current = REPO_ROOT
        target = target[1:]
    else:
        current = start_dir

    parts = [p for p in target.split("/") if p != ""]

    for part in parts:
        if part == ".":
            continue
        if part == "..":
            current = current.parent
            continue
        try:
            entries = {entry.name: entry for entry in current.iterdir()}
        except (FileNotFoundError, NotADirectoryError):
            return None
        if part not in entries:
            return None
        current = entries[part]

    if current.is_dir():
        current = current / "index.html"
    return current if current.is_file() else None


def tracked_files() -> list[str] | None:
    try:
        out = subprocess.run(
            ["git", "ls-files"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return [line for line in out.stdout.splitlines() if line]


def main() -> int:
    html_files = sorted(
        p
        for p in REPO_ROOT.rglob("*.html")
        if not any(part in SKIP_DIR_NAMES for part in p.parts)
    )

    broken: list[tuple[str, str]] = []
    resolved_targets: set[str] = set()
    page_texts: list[str] = []

    for page in html_files:
        html = page.read_text(encoding="utf-8", errors="replace")
        page_texts.append(html)
        parser = RefCollector()
        parser.feed(html)
        for raw in parser.refs:
            if is_external_or_fragment(raw):
                continue
            target = raw.split("#", 1)[0].split("?", 1)[0]
            if not target:
                continue
            hit = resolve(page.parent, target)
            if hit is None:
                broken.append((page.relative_to(REPO_ROOT).as_posix(), raw))
            else:
                resolved_targets.add(hit.relative_to(REPO_ROOT).as_posix())

    print(f"Checked {len(html_files)} HTML file(s) under {REPO_ROOT}.")

    if broken:
        print("\nBroken internal links/assets:")
        for page, target in broken:
            print(f"  - {page}: {target}")
    else:
        print("All internal hrefs and asset paths resolve.")

    tracked = tracked_files()
    if tracked is None:
        print("\n(Skipped orphaned-asset check: `git ls-files` unavailable.)")
    else:
        orphans = []
        for path in tracked:
            top = path.split("/", 1)[0]
            if path in ORPHAN_EXEMPT or top in ORPHAN_EXEMPT_DIRS:
                continue
            if path in resolved_targets:
                continue
            if path.endswith(".html"):
                # Pages are reached via navigation, not necessarily as a raw
                # href string match (e.g. "/resume/" resolves to this file).
                # Being resolved as *any* link's target is enough.
                orphans.append(path)
            elif any(path in text for text in page_texts):
                # Referenced as a literal string outside a static href/src
                # attribute -- e.g. built up in a <script> block. Not a
                # markup link, so it's not in resolved_targets, but it's not
                # unused either.
                continue
            else:
                orphans.append(path)
        if orphans:
            print(
                "\nWARNING: tracked file(s) no page links to (not a failure -- "
                "for the owner to decide):"
            )
            for path in sorted(orphans):
                print(f"  - {path}")

    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
