#!/usr/bin/env python3
"""Add per-page banners to a PR preview built by gha's preview workflow.

Two banners, which gha's preview does not provide (Morrison-Lab/gha#1025):

* a list of the pages this PR changes, on every page except the home page
  (gha's `changed-chapters-banner` already writes that list on the home page);
* a list of the page's other formats: its tracked-changes Word file
  (`<stem>-tracked-changes.docx`, gha's naming) and its slide deck
  (`<stem>-slides.html`), on every page including the home page.

Environment variables:

HTML_DIR           Rendered site directory (required; the script fails if it is
                   missing or holds no HTML).
INDEX_PAGE         Home page relative to HTML_DIR (default `index.html`).
CHANGED_CHAPTERS   JSON array of changed page ids from gha's `changed-chapters`
                   output (a page's path relative to HTML_DIR, no extension).
DETECTION_STATUS   gha's `detection-status`. `skipped` means there was nothing
                   published to compare with, so every page counts as changed.
"""

import json
import os
import re
import sys
from pathlib import Path


# Written before the banners, so a re-run over its own output adds nothing.
BANNER_MARKER = "<!-- qwt-page-banners -->"


def fail(message):
    print(f"::error::{message}", file=sys.stderr)
    sys.exit(1)


def is_slides(html_path):
    return html_path.stem.endswith("-slides")


def get_page_title(html_path):
    """Extract the page title from an HTML file."""
    content = html_path.read_text(encoding="utf-8")
    h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", content, re.DOTALL)
    if h1_match:
        title_html = re.sub(r'<span class="chapter-number">(\d+)</span>\s*', "", h1_match.group(1))
        title = re.sub(r"<[^>]+>", "", title_html).strip()
        if title:
            return title
    title_match = re.search(r"<title>(.*?)</title>", content)
    if title_match:
        return title_match.group(1).strip()
    return html_path.stem


def changed_pages(html_dir, pages):
    """Return the rendered HTML pages this PR changes."""
    if os.getenv("DETECTION_STATUS", "") == "skipped":
        return list(pages)
    ids = json.loads(os.getenv("CHANGED_CHAPTERS", "") or "[]")
    found = []
    for page_id in ids:
        html_path = html_dir / f"{page_id}.html"
        if html_path.is_file() and not is_slides(html_path):
            found.append(html_path)
    return found


def changes_banner(html_path, changed):
    links = []
    for page in changed:
        link = os.path.relpath(page, html_path.parent)
        links.append(f'<a href="{link}">{get_page_title(page)}</a>')
    if not links:
        return ""
    return f"""
<div class="preview-changes-banner" style="background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 4px; padding: 12px; margin: 16px 0;">
    <p style="margin: 0;">
        <strong>📋 Changes in this PR:</strong> {", ".join(links)}
        <br>
        <strong>💡 Tip:</strong> If change highlighting is glitchy, add the <code>no-preview-highlights</code> label to this PR to disable it.
    </p>
</div>
"""


def formats_banner(html_path):
    stem = html_path.stem
    links = []
    if (html_path.parent / f"{stem}-tracked-changes.docx").exists():
        links.append(f'<a href="{stem}-tracked-changes.docx" download>📝 MS Word (tracked changes)</a>')
    if (html_path.parent / f"{stem}-slides.html").exists():
        links.append(f'<a href="{stem}-slides.html">🎞️ Slides</a>')
    if not links:
        return ""
    return f"""
<div class="preview-page-formats-banner" style="background-color: #e7f3ff; border: 1px solid #b3d9ff; border-radius: 4px; padding: 12px; margin: 16px 0;">
    <p style="margin: 0;">
        <strong>📋 Other Formats:</strong> {" | ".join(links)}
    </p>
</div>
"""


def add_page_banners(html_path, html_dir, index_path, changed):
    rel_path = html_path.relative_to(html_dir)
    banners = []
    if html_path != index_path:
        banners.append(changes_banner(html_path, changed))
    banners.append(formats_banner(html_path))
    combined = "\n".join(b for b in banners if b)
    if not combined:
        print(f"  No banners to add for {rel_path}")
        return
    html = html_path.read_text(encoding="utf-8")
    if BANNER_MARKER in html:
        print(f"  Banners already present in {rel_path}; skipped")
        return
    main_match = re.search(r"(<main[^>]*>)", html)
    if not main_match:
        print(f"  No <main> in {rel_path}; banners skipped")
        return
    html = html[: main_match.end()] + BANNER_MARKER + combined + html[main_match.end():]
    html_path.write_text(html, encoding="utf-8")
    print(f"  Added banner(s) to {rel_path}")


def main():
    html_dir = Path(os.getenv("HTML_DIR", ""))
    if not os.getenv("HTML_DIR") or not html_dir.is_dir():
        fail(f"HTML_DIR {os.getenv('HTML_DIR')!r} is not a directory; the preview artifact is not laid out as expected")
    pages = sorted(p for p in html_dir.rglob("*.html") if not is_slides(p))
    if not pages:
        fail(f"no HTML pages under {html_dir}")
    index_path = html_dir / (os.getenv("INDEX_PAGE") or "index.html")
    changed = changed_pages(html_dir, pages)
    print(f"{len(pages)} page(s), {len(changed)} changed")
    for page in pages:
        add_page_banners(page, html_dir, index_path, changed)


if __name__ == "__main__":
    main()
