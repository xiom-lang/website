#!/usr/bin/env python3
# Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
# SPDX-License-Identifier: MIT OR Apache-2.0
"""
Assemble the MkDocs source tree for docs.xiom-lang.org.

- copies the language guide from docs/language/ (top level only; the
  hand-written stdlib listings are replaced by generated API pages)
- adds docs/AI_CONTEXT.md at the root
- runs docs/build_api_docs.py over a stdlib checkout (or copies prebuilt
  API pages) into api/
- writes meta-refresh stubs for the legacy docs/html/ URLs so existing
  links keep working during and after the mike migration

Usage:
  python docs/build_mkdocs.py --stdlib <path> --xiom-doc <bin> --tag vX.Y.Z
  python docs/build_mkdocs.py --api-dir <dir> --tag latest

Then:
  mkdocs build --strict
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "docs" / "language"
AI_CONTEXT = ROOT / "docs" / "AI_CONTEXT.md"
DEFAULT_STAGE = ROOT / "build" / "mkdocs-src"
DEFAULT_LEGACY = ROOT / "docs" / "html"
SITE_URL = "https://docs.xiom-lang.org/"

# Hand-written pages superseded by the generated API tree.
EXCLUDED_SOURCES = {"api.md", "stdlib.md"}

# Guide order for the generated SUMMARY.md (read by mkdocs-literate-nav).
NAV = [
    ("index.md", "Overview"),
    ("getting-started.md", "Getting Started"),
    ("reference.md", "Language Reference"),
    ("concepts.md", "Concepts"),
    ("examples.md", "By Example"),
    ("syntax.md", "Syntax"),
    ("types.md", "Type System"),
    ("memory-model.md", "Memory Model"),
    ("unsafe.md", "Unsafe"),
    ("contracts.md", "Contracts"),
    ("error-handling.md", "Error Handling"),
    ("modules.md", "Modules"),
    ("generics.md", "Generics"),
    ("pattern-matching.md", "Pattern Matching"),
    ("derive.md", "Derive"),
    ("ffi.md", "C FFI"),
    ("compiler.md", "Compiler"),
    ("debugger.md", "Debugging"),
    ("registry.md", "Package Registry"),
    ("contributing.md", "Contributing"),
]

STUB = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Moved -- XIOM Documentation</title>
<link rel="canonical" href="{url}">
<meta http-equiv="refresh" content="0; url={url}">
</head>
<body>
<p>This page moved to <a href="{url}">{url}</a>.</p>
</body>
</html>
"""


def rewrite_links(text):
    """Point staged sources at their new MkDocs locations."""
    text = re.sub(r'\]\((?:\.\./)+AI_CONTEXT\.md', '](AI_CONTEXT.md', text)
    text = re.sub(r'\]\((?:\.\./)+stdlib\.md(#[^)]*)?\)', r'](api/index.md\1)', text)
    text = re.sub(r'\]\((?:\.\./)+api\.md(#[^)]*)?\)', r'](api/index.md\1)', text)
    text = re.sub(r'\]\(stdlib\.md(#[^)]*)?\)', r'](api/index.md\1)', text)
    text = re.sub(r'\]\(api\.md(#[^)]*)?\)', r'](api/index.md\1)', text)
    return text


def legacy_target(rel_path):
    """Map a legacy docs/html path to its MkDocs URL path, or None to skip."""
    rel = rel_path.replace("\\", "/")
    if rel == "index.html":
        return None
    if "/" in rel:
        head, name = rel.rsplit("/", 1)
        stem = name[:-5]
        if head == "stdlib":
            return "api/" if stem == "index" else "api/{0}/".format(stem)
        return "{0}/{1}/".format(head, stem)
    stem = rel[:-5]
    if stem in ("stdlib", "api"):
        return "api/"
    if stem == "AI_CONTEXT":
        return "AI_CONTEXT/"
    return stem + "/"


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def copy_api(args, stage):
    api_dir = stage / "api"
    if args.api_dir:
        source = Path(args.api_dir)
        if not source.is_dir():
            print("error: --api-dir not found: {0}".format(source), file=sys.stderr)
            return False
        shutil.copytree(str(source), str(api_dir))
        return True
    if not args.stdlib:
        existing = ROOT / "docs" / "api"
        if existing.is_dir():
            shutil.copytree(str(existing), str(api_dir))
            return True
        print("error: pass --stdlib or --api-dir so api/ can be built", file=sys.stderr)
        return False

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import build_api_docs

    binary = build_api_docs.find_xiom_doc(args.xiom_doc)
    result = build_api_docs.build(Path(args.stdlib), binary, api_dir, args.tag, False)
    return result == 0


def build_legacy_stubs(legacy_dir, stage, skip):
    if skip or not legacy_dir.is_dir():
        return 0
    count = 0
    for source in sorted(legacy_dir.rglob("*.html")):
        rel = source.relative_to(legacy_dir).as_posix()
        target = legacy_target(rel)
        if target is None:
            continue
        url = SITE_URL + target
        write_text(stage / rel, STUB.format(url=url))
        count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description="Assemble the MkDocs docs tree")
    parser.add_argument("--stdlib", default=None, help="path to a stdlib checkout")
    parser.add_argument("--xiom-doc", default=None, help="path to the xiom-doc binary")
    parser.add_argument("--api-dir", default=None, help="prebuilt API pages to copy")
    parser.add_argument("--tag", default="latest", help="release tag stamped into pages")
    parser.add_argument("--stage", default=str(DEFAULT_STAGE), help="staging directory")
    parser.add_argument("--legacy-from", default=str(DEFAULT_LEGACY),
                        help="published layout to derive redirect stubs from")
    parser.add_argument("--no-legacy", action="store_true", help="skip redirect stubs")
    args = parser.parse_args()

    stage = Path(args.stage)
    if stage.exists():
        shutil.rmtree(str(stage))
    stage.mkdir(parents=True)

    guides = 0
    for source in sorted(SRC_DIR.glob("*.md")):
        if source.name in EXCLUDED_SOURCES:
            continue
        write_text(stage / source.name, rewrite_links(source.read_text(encoding="utf-8")))
        guides += 1

    if AI_CONTEXT.is_file():
        write_text(stage / "AI_CONTEXT.md", rewrite_links(AI_CONTEXT.read_text(encoding="utf-8")))

    # Error-code reference (docs/error_codes/): published under error-codes/,
    # with README.md becoming the section index.
    error_codes_dir = ROOT / "docs" / "error_codes"
    error_pages = []
    if error_codes_dir.is_dir():
        dest = stage / "error-codes"
        dest.mkdir(parents=True, exist_ok=True)
        for source in sorted(error_codes_dir.glob("*.md")):
            name = "index.md" if source.name.upper() == "README.MD" else source.name
            write_text(dest / name, rewrite_links(source.read_text(encoding="utf-8")))
            error_pages.append(name)

    brand = ROOT / "docs" / "mkdocs-brand.css"
    if brand.is_file():
        assets = stage / "assets"
        assets.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(brand), str(assets / "brand.css"))

    img_src = ROOT / "xiom-website" / "img"
    if img_src.is_dir():
        img_dst = stage / "img"
        img_dst.mkdir(parents=True, exist_ok=True)
        for name in ("xiom-logo.png", "xiom-icon.png"):
            source = img_src / name
            if source.is_file():
                shutil.copy2(str(source), str(img_dst / name))

    if not copy_api(args, stage):
        return 1

    # The generated API index is the page users see as "Standard Library API".
    # Surface the verification scope there too: the hand-written guide pages
    # that carry it (api.md, stdlib.md) are excluded from the MkDocs staging.
    api_index = stage / "api" / "index.md"
    if api_index.is_file():
        text = api_index.read_text(encoding="utf-8")
        if "**Verification scope:**" not in text:
            note = (
                "> **Verification scope:** contracts are what the verifier "
                "reasons about; the implementations, including the "
                "NASM-accelerated runtime paths, are assumed to honor them. "
                "See the [contracts guide](../contracts.md).\n\n"
            )
            write_text(api_index, note + text)

    # SUMMARY.md drives the navigation via mkdocs-literate-nav.
    nav_lines = ["* [xiom-lang.org](https://xiom-lang.org/)"]
    for name, title in NAV:
        if (stage / name).is_file():
            nav_lines.append("* [{0}]({1})".format(title, name))
    nav_lines.append("* Standard Library API")

    def api_key(page):
        if page.stem == "index":
            return (0, "")
        if page.stem == "core":
            return (1, "")
        return (2, page.stem)

    api_pages = sorted((stage / "api").glob("*.md"), key=api_key)
    for page in api_pages:
        title = "Overview" if page.stem == "index" else page.stem
        nav_lines.append("    * [{0}](api/{1})".format(title, page.name))
    if error_pages:
        nav_lines.append("* Error Codes")
        for name in error_pages:
            stem = name[:-3]
            title = "Overview" if stem == "index" else stem
            nav_lines.append("    * [{0}](error-codes/{1})".format(title, name))
    nav_lines.append("* [AI Coding Reference](AI_CONTEXT.md)")
    write_text(stage / "SUMMARY.md", "\n".join(nav_lines) + "\n")

    stubs = build_legacy_stubs(Path(args.legacy_from), stage, args.no_legacy)

    try:
        shown = stage.relative_to(ROOT)
    except ValueError:
        shown = stage
    print("staged: {0} guides, {1} api pages, {2} legacy stubs -> {3}".format(
        guides,
        len(api_pages),
        stubs,
        shown,
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
