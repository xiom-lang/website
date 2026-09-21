#!/usr/bin/env python3
# Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
# SPDX-License-Identifier: MIT OR Apache-2.0
"""
xiom API documentation builder.

Walks a stdlib checkout, runs the `xiom-doc` binary over every source file and
assembles MkDocs-ready pages: one page per module plus an index.

Usage:
  python docs/build_api_docs.py --stdlib <path-to-stdlib-repo> \
      [--xiom-doc <path-to-xiom-doc>] [--out docs/api] [--tag vX.Y.Z] [--strict]

The stdlib source tree is expected at <stdlib>/xiom/<module>/**.xi. The driver
reads the stdlib release tag (or COMPILER_VERSION when present) for the page
header unless --tag is given. Output is deterministic; --strict exits non-zero
when any file fails to parse.
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

HEADING_RE = re.compile(r'^(#{1,6})\s')
MODULE_HEADING_RE = re.compile(r'^#+\s+Module\s+`?([A-Za-z0-9_.]+)`?\s*$')

LIMITATIONS_URL = "https://github.com/xiom-lang/stdlib/blob/main/docs/STDLIB_BETA_LIMITATIONS.md"


def find_xiom_doc(explicit):
    if explicit:
        return explicit
    env = os.environ.get("XIOM_DOC_BIN")
    if env:
        return env
    name = "xiom-doc.exe" if os.name == "nt" else "xiom-doc"
    home = os.environ.get("XIOM_HOME")
    if home:
        candidate = Path(home) / "bin" / name
        if candidate.exists():
            return str(candidate)
    return name


def run_xiom_doc(binary, source_file):
    """Return (markdown, error_message)."""
    try:
        proc = subprocess.run(
            [binary, str(source_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError as exc:
        return None, f"cannot run {binary}: {exc}"
    if proc.returncode != 0:
        detail = proc.stderr.decode("utf-8", errors="replace").strip()
        return None, detail or f"exit code {proc.returncode}"
    return proc.stdout.decode("utf-8", errors="replace"), None


DECL_RE = re.compile(r'^\s*pub\s+(fn|type|enum|const|interface|struct|trait)\s+([A-Za-z0-9_.]+)')
HEADING_SYMBOL_RE = re.compile(r'^(fn|type|enum|const|interface|struct|trait)\s+([A-Za-z0-9_.]+)')


LIST_ITEM_RE = re.compile(r'^([-*]|\d+\.)\s')


def format_doc_block(lines):
    """Render `///` lines as a Markdown blockquote, keeping paragraphs and lists."""
    paragraphs = []
    current = []
    for part in lines:
        if part == "":
            if current:
                paragraphs.append(current)
                current = []
            continue
        current.append(part)
    if current:
        paragraphs.append(current)

    blocks = []
    for paragraph in paragraphs:
        if LIST_ITEM_RE.match(paragraph[0]):
            blocks.append("\n".join("> " + line for line in paragraph))
        else:
            blocks.append("> " + " ".join(paragraph))
    return "\n>\n".join(blocks)


def parse_doc_comments(source_path):
    """Collect `///` documentation blocks keyed to the declaration they precede."""
    entries = []
    buffer = []
    for line in source_path.read_text(encoding="utf-8", errors="replace").split("\n"):
        stripped = line.strip()
        if stripped.startswith("///"):
            buffer.append(stripped[3:].strip())
            continue
        match = DECL_RE.match(stripped)
        if match and buffer:
            name = match.group(2)
            entries.append({
                "kind": match.group(1),
                "full": name,
                "base": name.split(".")[-1],
                "doc": format_doc_block(buffer),
            })
            buffer = []
        elif stripped.startswith("#["):
            continue  # attributes sit between the doc block and its declaration
        elif stripped:
            buffer = []
        else:
            buffer = []
    return entries


def heading_symbol(line):
    """Return (kind, name, base, text) for a declaration heading, or None."""
    text = line.strip().lstrip("#").strip().strip("`")
    match = HEADING_SYMBOL_RE.match(text)
    if not match:
        return None
    name = match.group(2)
    return match.group(1), name, name.split(".")[-1], text


SIGNATURE_RE = re.compile(r'^fn\s+[A-Za-z0-9_.]+(?:\[[^\]]*\])?\((.*)\)\s*(?:->\s*(.+))?$')

TITLE_RE = re.compile(r'^//\s*XIOM\s*\W+\s*(.+?)\s*$')
PURPOSE_RE = re.compile(r'^//\s*Purpose:\s*(.+?)\s*$')


def module_purpose(module_dir, module_name):
    """One-line module purpose.

    Prefers an explicit `// Purpose:` line (the convention to adopt in the
    stdlib), falling back to the `// XIOM -- Title` line at the top of the
    module's primary file.
    """
    primary = module_dir / (module_name + ".xi")
    candidates = [primary] if primary.is_file() else sorted(module_dir.glob("*.xi"))
    if not candidates:
        return None
    try:
        lines = candidates[0].read_text(encoding="utf-8", errors="replace").split("\n")
    except OSError:
        return None
    title = None
    for index, line in enumerate(lines):
        match = PURPOSE_RE.match(line)
        if match:
            return match.group(1).strip()
        if title is None and index < 40:
            match = TITLE_RE.match(line)
            if match:
                title = match.group(1).strip()
    return title


def split_top_level(text):
    parts, depth, current = [], 0, ""
    for ch in text:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            parts.append(current.strip())
            current = ""
        else:
            current += ch
    if current.strip():
        parts.append(current.strip())
    return parts


def generated_summary(heading_text):
    """Fallback synopsis for functions without a source comment."""
    match = SIGNATURE_RE.match(heading_text)
    if not match:
        return "*Generated summary:* No source comment yet."
    params = split_top_level(match.group(1))
    returns = (match.group(2) or "").strip()
    is_method = any(part.startswith("self") for part in params)
    others = [part for part in params if not part.startswith("self")]
    bits = []
    if is_method:
        bits.append("Method")
    if others:
        shown = ", ".join("`{0}`".format(part) for part in others[:4])
        if len(others) > 4:
            shown += ", ..."
        bits.append("takes " + shown)
    else:
        bits.append("Takes no arguments")
    bits.append("returns `{0}`".format(returns) if returns else "returns nothing")
    return "*Generated summary:* " + "; ".join(bits) + ". No source comment yet."


def clean_file_output(text, source=None):
    """Normalize one file's xiom-doc output for embedding under an H2.

    Removes the per-file preamble and module wrapper headings and keeps the
    declaration headings at H4, so the right-hand table of contents stays at
    file level while the declarations keep their anchors. When the source
    path is given, `///` doc comments are merged under their declarations.
    Returns (body_lines, symbol_count).
    """
    docs = parse_doc_comments(source) if source is not None else []
    doc_index = 0

    cleaned = []
    for line in text.replace("\r\n", "\n").split("\n"):
        if line.startswith("# XIOM API Documentation"):
            continue
        if line.startswith("> Generated by `xiom doc`"):
            continue
        if MODULE_HEADING_RE.match(line):
            continue
        cleaned.append(line)

    body = []
    for line in cleaned:
        doc_line = None
        if line.startswith("####"):
            symbol = heading_symbol(line)
            if symbol:
                kind, name, base, heading_text = symbol
                for index in range(doc_index, len(docs)):
                    entry = docs[index]
                    if entry["full"] == name or entry["base"] == name or entry["base"] == base:
                        if entry["doc"]:
                            doc_line = entry["doc"]
                        doc_index = index + 1
                        break
                if not doc_line and kind == "fn":
                    doc_line = generated_summary(heading_text)
        if not line.strip() and body and not body[-1].strip():
            continue
        body.append(line)
        if doc_line:
            body.append("")
            body.append(doc_line)
    while body and not body[0].strip():
        body.pop(0)
    symbols = sum(1 for line in body if line.startswith("####"))
    return body, symbols


def module_sort_key(name):
    return (0, "core") if name == "core" else (1, name)


def build(stdlib_root, binary, out_dir, tag, strict):
    src_root = stdlib_root / "xiom"
    if not src_root.is_dir():
        print(f"error: no xiom/ source tree under {stdlib_root}", file=sys.stderr)
        return 2

    files = sorted(p for p in src_root.rglob("*.xi"))
    modules = {}
    failures = []
    empties = 0
    symbols = 0

    for source in files:
        module = source.relative_to(src_root).parts[0]
        text, error = run_xiom_doc(binary, source)
        if error is not None:
            failures.append((source.relative_to(stdlib_root).as_posix(), error.splitlines()[0]))
            continue
        body, count = clean_file_output(text, source)
        if count == 0 and not any(line.strip() for line in body):
            empties += 1
            continue
        symbols += count
        modules.setdefault(module, []).append((source.name, body, count))

    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = tag or "latest"
    purposes = {module: module_purpose(src_root / module, module) for module in modules}
    index_lines = [
        "# Standard Library API",
        "",
        f"> Generated from the stdlib sources at `{stamp}` by `docs/build_api_docs.py`.",
        f"> {len(files)} source files, {len(modules)} modules, {symbols} documented symbols.",
        "",
        "> **Beta:** the standard library is still being completed; see the",
        f"> [known limitations]({LIMITATIONS_URL}) for current gaps.",
        "",
        "> Each entry shows its source `///` comment when present (otherwise a",
        "> generated summary), followed by its contracts: the contract is the",
        "> specification.",
        "",
        "| Module | Purpose | Files | Symbols |",
        "|---|---|---|---|",
    ]
    written = 0
    for module in sorted(modules, key=module_sort_key):
        entries = sorted(modules[module])
        page = out_dir / f"{module}.md"
        lines = [f"# `stdlib.{module}`", ""]
        if purposes.get(module):
            lines.append(f"> **{purposes[module]}**")
            lines.append(">")
        lines.append(
            f"> Generated from `{stamp}`. {len(entries)} source files, "
            f"{sum(c for _, _, c in entries)} documented symbols."
        )
        lines.append("")
        for name, body, _ in entries:
            if not body:
                continue
            lines.append(f"## `{name}`")
            lines.append("")
            lines.extend(body)
            lines.append("")
        write_text(page, "\n".join(lines).rstrip() + "\n")
        written += 1
        index_lines.append(
            "| [`{0}`]({0}.md) | {1} | {2} | {3} |".format(
                module,
                purposes.get(module) or "-",
                len(entries),
                sum(c for _, _, c in entries),
            )
        )
    index_lines.append("")
    write_text(out_dir / "index.md", "\n".join(index_lines))

    print(f"modules: {written}")
    print(f"files:   {len(files)} ({empties} without public symbols)")
    print(f"symbols: {symbols}")
    print(f"failed:  {len(failures)}")
    for path, error in failures[:20]:
        print(f"  {path}: {error}")
    if failures and strict:
        return 1
    return 0


def write_text(path, text):
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def main():
    parser = argparse.ArgumentParser(description="Build stdlib API pages via xiom-doc")
    parser.add_argument("--stdlib", required=True, help="path to the stdlib repository")
    parser.add_argument("--xiom-doc", default=None, help="path to the xiom-doc binary")
    parser.add_argument("--out", default="docs/api", help="output directory (default: docs/api)")
    parser.add_argument("--tag", default=None, help="release tag stamped into page headers")
    parser.add_argument("--strict", action="store_true", help="exit non-zero on parse failures")
    args = parser.parse_args()

    binary = find_xiom_doc(args.xiom_doc)
    return build(Path(args.stdlib), binary, Path(args.out), args.tag, args.strict)


if __name__ == "__main__":
    sys.exit(main())
