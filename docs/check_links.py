#!/usr/bin/env python3
# Copyright (c) 2026 Eleftherios Notas and XIOM Foundation
# SPDX-License-Identifier: MIT OR Apache-2.0
"""
Check relative links in built HTML trees.

Walks every *.html file under the given roots, resolves relative href/src
targets against the file location, and fails when a target is missing.
External URLs, anchors, and non-HTTP schemes are skipped.

Usage:
  python docs/check_links.py docs/html xiom-website
"""

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

SKIP_SCHEMES = ("http", "https", "mailto", "tel", "javascript", "data", "ftp")


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ("href", "src"):
            if key in attrs and attrs[key] is not None:
                self.links.append(attrs[key])


def check(root):
    broken = []
    pages = sorted(root.rglob("*.html"))
    for page in pages:
        parser = LinkParser()
        parser.feed(page.read_text(encoding="utf-8", errors="replace"))
        for raw in parser.links:
            if not raw or raw.startswith("#"):
                continue
            split = urlsplit(raw)
            if split.scheme.lower() in SKIP_SCHEMES:
                continue
            target = unquote(split.path)
            if not target:
                continue
            resolved = (page.parent / target).resolve()
            if not resolved.exists():
                broken.append((page.relative_to(root), raw))
    return broken, len(pages)


def main():
    roots = sys.argv[1:]
    if not roots:
        print("usage: check_links.py <html-root> [<html-root> ...]", file=sys.stderr)
        return 2
    total_pages = 0
    total_broken = 0
    for arg in roots:
        root = Path(arg)
        if not root.is_dir():
            print("error: not a directory: {0}".format(root), file=sys.stderr)
            return 2
        broken, pages = check(root)
        total_pages += pages
        total_broken += len(broken)
        print("{0}: {1} pages, {2} broken relative links".format(arg, pages, len(broken)))
        for page, link in broken[:50]:
            print("  {0} -> {1}".format(page, link))
    print("total: {0} pages, {1} broken".format(total_pages, total_broken))
    return 1 if total_broken else 0


if __name__ == "__main__":
    sys.exit(main())
