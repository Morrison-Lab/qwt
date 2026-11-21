#!/usr/bin/env python3
"""Write anchor-index.json: which page of the rendered site holds each id.

anchor-landing.html reads it when a reader arrives at a page whose `#id` the page
no longer holds, because the content moved to another page, and sends them to the
page that holds the id now.  So a link from another site, a bookmark or a search
result keeps working after a definition moves, without the link being rewritten.

Runs as a `post-render` step: it scans every website page in the output directory
(`QUARTO_PROJECT_OUTPUT_DIR`, else `_site`) and writes

    {"version": 1, "ids": {"def-intercept": "algebra-polynomials.html", ...}}

with each page given relative to the site root.  It leaves out

- reveal.js decks, which repeat their page's ids (the reader wants the page);
- ids held by more than one page, such as Quarto's own page chrome,
  since a redirect to one of them would be a guess.

Shared site scaffolding: the canonical copy is in Morrison-Lab/qwt, and the sites
vendor it through their sync-site-scaffolding workflow.  Do not edit a site's copy.

    python3 anchor-index.py [--site DIR] [--out FILE]
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

# An id attribute, double- or single-quoted.  A regex is enough: Quarto writes its
# own HTML, and a false hit (an id-like string inside a <script>) is dropped below
# unless it is unique, where it costs one unused entry.
ID_ATTR = re.compile(r"""\sid\s*=\s*(?:"([^"]+)"|'([^']+)')""")
REVEAL = re.compile(r"""<div\s+class="reveal[\s"]""")
OUT_NAME = "anchor-index.json"


def site_pages(site):
    """The website pages in `site`, as (path relative to the site root, text)."""
    for path in sorted(site.rglob("*.html")):
        rel = path.relative_to(site).as_posix()
        if rel.startswith("site_libs/") or "/site_libs/" in rel:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if REVEAL.search(text):
            continue
        yield rel, text


def build(site):
    holders = {}
    for rel, text in site_pages(site):
        for m in ID_ATTR.finditer(text):
            holders.setdefault(m.group(1) or m.group(2), set()).add(rel)
    ids = {i: next(iter(p)) for i, p in sorted(holders.items()) if len(p) == 1}
    return {"version": 1, "ids": ids}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--site", default=os.environ.get("QUARTO_PROJECT_OUTPUT_DIR", "_site"),
                    help="the rendered site (default: $QUARTO_PROJECT_OUTPUT_DIR or _site)")
    ap.add_argument("--out", help=f"where to write the index (default: SITE/{OUT_NAME})")
    args = ap.parse_args(argv)
    site = Path(args.site)
    if not site.is_dir():
        sys.exit(f"anchor-index.py: no rendered site at {site}")
    index = build(site)
    out = Path(args.out) if args.out else site / OUT_NAME
    out.write_text(json.dumps(index, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8")
    print(f"anchor-index.py: {len(index['ids'])} ids -> {out}")


if __name__ == "__main__":
    main()
