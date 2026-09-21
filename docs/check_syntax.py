#!/usr/bin/env python3
# Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
# SPDX-License-Identifier: MIT OR Apache-2.0
"""
Check XIOM code snippets for canonical-syntax drift.

Rules, applied to ```xiom fenced blocks in Markdown and to the code blocks in
the hand-written site pages:

  1. Contract clauses use a colon -- `requires:`, `ensures:`, `invariant:`.
  2. `use` declarations end with a semicolon.
  3. Generics use square brackets -- `Vec[Int]`, `fn max[T: Ord]` -- never
     angle brackets such as `Vec<Int>` or `fn max<T>`. Turbofish compiles
     but is not canonical, so it is reported too.
  4. Syntax the compiler does not implement: `if let` (use `match` or
     `if value is Variant`) and the `Byte` type name (use `UInt8`).

Usage:
  python docs/check_syntax.py docs/language docs/AI_CONTEXT.md xiom-website

Arguments may be files or directories; directories are searched recursively
for *.md and *.html. Exit status is 1 when any rule is violated.
"""

import html
import re
import sys
from pathlib import Path

# Rule 1 -- a contract keyword must be followed by a colon (optionally with
# spaces before it). Comments that merely use the word in prose should be
# reworded or annotated with `lint:allow`.
CONTRACT_RE = re.compile(r"\b(requires|ensures|invariant)\b(?!\s*:)")

# Rule 2 -- a `use` declaration line must end with a semicolon.
USE_RE = re.compile(r"^(?:pub\s+)?use\s+\S")

# Rule 3 -- angle-bracket generic forms: <T>, <T, U>, <Int>. Turbofish
# (`parse::<Int>`) is the same drift and gets a clearer message.
ANGLE_RE = re.compile(r"<[A-Z][A-Za-z0-9_]*(?:\s*,\s*[A-Z][A-Za-z0-9_]*)*>")
TURBOFISH_RE = re.compile(r"::\s*<")

# Rule 4 -- syntax the compiler does not implement. `if let` is documented
# nowhere, but older material used it; Byte is not accepted as a type name.
IF_LET_RE = re.compile(r"\bif\s+let\b")
BYTE_TYPE_RE = re.compile(r"(?::\s*Byte\b|\bas\s+Byte\b)")

# A block may opt out with a `syntax-lint: allow` marker in its first lines
# (for deliberate counter-examples in documentation).
ALLOW_MARKER = "syntax-lint: allow"

FENCE_RE = re.compile(r"^```\s*([A-Za-z0-9_+-]*)\s*$")
PRE_BLOCK_RE = re.compile(
    r"<pre[^>]*>\s*<code[^>]*>(.*?)</code>\s*</pre>", re.DOTALL | re.IGNORECASE
)
PANEL_BLOCK_RE = re.compile(
    r'<div\s+class="code-panel-body">(.*?)</div>', re.DOTALL | re.IGNORECASE
)
TAG_RE = re.compile(r"<[^>]+>")
BR_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)


def markdown_blocks(path):
    """Yield (line_number, text) for each ```xiom fenced block."""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    in_block = False
    lang = ""
    start = 0
    buf = []
    for idx, line in enumerate(lines, 1):
        if not in_block:
            match = FENCE_RE.match(line)
            if match:
                in_block = True
                lang = match.group(1).lower()
                start = idx + 1
                buf = []
        else:
            if line.strip().startswith("```"):
                if lang == "xiom":
                    yield start, "\n".join(buf)
                in_block = False
            else:
                buf.append(line)


def html_blocks(path):
    """Yield (line_number, text) for code blocks in a hand-written page."""
    text = path.read_text(encoding="utf-8", errors="replace")
    for pattern in (PRE_BLOCK_RE, PANEL_BLOCK_RE):
        for match in pattern.finditer(text):
            line_number = text.count("\n", 0, match.start(1)) + 1
            body = BR_RE.sub("\n", match.group(1))
            body = TAG_RE.sub("", body)
            yield line_number, html.unescape(body)


def check_block(text):
    """Return a list of (offset, message) findings for one snippet."""
    findings = []
    for offset, line in enumerate(text.splitlines(), 1):
        # Rule 1 and rule 2 apply to code, not to trailing prose comments;
        # `//` inside a string literal is rare in documentation snippets.
        code = line.split("//", 1)[0]
        for match in CONTRACT_RE.finditer(code):
            findings.append(
                (
                    offset,
                    "contract keyword needs a colon: {0}:".format(match.group(1)),
                )
            )
        stripped = code.strip()
        if USE_RE.match(stripped) and not stripped.endswith(";"):
            findings.append((offset, "use declaration needs a terminating semicolon"))
        if TURBOFISH_RE.search(code):
            findings.append(
                (
                    offset,
                    "turbofish is accepted but not canonical (write name[Type], "
                    "for example parse[Int])",
                )
            )
        else:
            for match in ANGLE_RE.finditer(code):
                findings.append(
                    (
                        offset,
                        "angle-bracket generics are not XIOM syntax: {0} "
                        "(use square brackets)".format(match.group(0)),
                    )
                )
        if IF_LET_RE.search(code):
            findings.append(
                (
                    offset,
                    "if let is not implemented (use match or `if value is Variant`)",
                )
            )
        if BYTE_TYPE_RE.search(code):
            findings.append(
                (offset, "the Byte alias is not accepted by the compiler (use UInt8)")
            )
    return findings


def check_file(path):
    """Return a list of (line, message) findings for one file."""
    if path.suffix.lower() == ".md":
        blocks = list(markdown_blocks(path))
    elif path.suffix.lower() == ".html":
        blocks = list(html_blocks(path))
    else:
        return []
    findings = []
    for start, text in blocks:
        if ALLOW_MARKER in text:
            continue
        for offset, message in check_block(text):
            findings.append((start + offset - 1, message))
    return findings


def collect_files(args):
    files = []
    for arg in args:
        path = Path(arg)
        if path.is_dir():
            for suffix in ("*.md", "*.html"):
                files.extend(sorted(path.rglob(suffix)))
        elif path.is_file():
            files.append(path)
        else:
            print("error: no such file or directory: {0}".format(arg), file=sys.stderr)
            raise SystemExit(2)
    return files


def main():
    if len(sys.argv) < 2:
        print("usage: check_syntax.py <path> [<path> ...]", file=sys.stderr)
        return 2
    files = collect_files(sys.argv[1:])
    total = 0
    scanned = 0
    for path in files:
        findings = check_file(path)
        if findings:
            for line, message in findings:
                print("{0}:{1}: {2}".format(path, line, message))
            total += len(findings)
        scanned += 1
    print("{0} files scanned, {1} syntax findings".format(scanned, total))
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
