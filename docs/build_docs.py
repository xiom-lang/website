#!/usr/bin/env python3
# Copyright (c) 2026 Eleftherios Notas and XIOM Foundation
# SPDX-License-Identifier: MIT OR Apache-2.0
"""
xiom Documentation Builder
Converts docs/language/*.md -> docs/html/ and xiom-website/docs/
Run: python docs/build_docs.py

Outputs:
  docs/html/         -- static HTML, ships with releases, works from file://
  xiom-website/docs/ -- integrated into xiom-lang.org

Set XIOM_DOCS_VERSION to stamp pages with a release tag (default: latest).
"""

import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "docs" / "language"
AI_CONTEXT = ROOT / "docs" / "AI_CONTEXT.md"
OUT_HTML = ROOT / "docs" / "html"
OUT_WEBSITE = ROOT / "xiom-website" / "docs"
STYLE_CSS = ROOT / "xiom-website" / "style.css"
IMAGE_DIR = ROOT / "resource" / "img"

# Stamped onto pages that carry no version line of their own. CI sets this to
# the release tag being built; local runs default to "latest".
DOCS_VERSION = os.environ.get("XIOM_DOCS_VERSION", "latest")

# -- Markdown -> HTML Converter ------------------------------------------

def md_to_html(text: str) -> str:
    """Convert markdown text to HTML body content."""
    lines = text.split('\n')
    out = []
    i = 0
    in_code_block = False
    code_lang = ""
    code_lines = []
    in_table = False
    table_rows = []

    def link_repl(m):
        text, url = m.group(1), m.group(2)
        url = re.sub(r'\.md(?=#|$)', '.html', url)
        # Links written as ../<page> refer to the docs root; built root pages
        # are published flat, so drop the prefix for those.
        if url.startswith('../') and url.rsplit('/', 1)[-1] in ROOT_PAGES:
            url = url.rsplit('/', 1)[-1]
        return f'<a href="{url}">{text}</a>'

    def convert_links(s):
        return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link_repl, s)

    def flush_paragraph(buf):
        if not buf:
            return
        p = ' '.join(buf).strip()
        if p:
            # Inline code (backticks)
            p = re.sub(r'`([^`]+)`', r'<code>\1</code>', p)
            # Bold
            p = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', p)
            # Italic
            p = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', p)
            # Links -- convert .md to .html
            p = convert_links(p)
            out.append(f'<p>{p}</p>')

    def flush_table():
        nonlocal in_table, table_rows
        if not table_rows:
            return
        out.append('<table>')
        for ri, row in enumerate(table_rows):
            tag = 'th' if ri == 0 else 'td'
            out.append('<tr>')
            for cell in row:
                cell = cell.strip()
                # Inline code
                cell = re.sub(r'`([^`]+)`', r'<code>\1</code>', cell)
                # Bold
                cell = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', cell)
                # Links -- convert .md to .html
                cell = convert_links(cell)
                out.append(f'<{tag}>{cell}</{tag}>')
            out.append('</tr>')
        out.append('</table>')
        in_table = False
        table_rows = []

    para_buf = []

    while i < len(lines):
        line = lines[i]

        # Code block toggle
        if line.strip().startswith('```'):
            if not in_code_block:
                flush_paragraph(para_buf); para_buf = []
                flush_table()
                code_lang = line.strip()[3:].strip()
                code_lines = []
                in_code_block = True
            else:
                in_code_block = False
                lang_class = f' class="language-{code_lang}"' if code_lang else ''
                out.append(f'<pre{lang_class}><code>')
                for cl in code_lines:
                    # Basic syntax highlighting for xiom code
                    hl = cl
                    hl = re.sub(r'(//.*$)', r"<span class='cm'>\1</span>", hl)
                    hl = re.sub(r'"([^"]*)"', r"<span class='str'>\1</span>", hl)
                    hl = re.sub(r'(\b\d+\.?\d*\b)', r"<span class='num'>\1</span>", hl)
                    hl = re.sub(r'\b(Int|Int8|Int16|Int32|Int64|UInt|UInt8|UInt16|UInt32|UInt64|Float32|Float64|Bool|Str|Char|Vec|Map|Set|Option|Result|Slice|Self|Unit|Stack|Point|Health|Score|Vec3|TcpStream|TcpListener|HttpResponse|UdpSocket|NetError|IOError|ParseError|AppError|Channel|Mutex|RwLock|Arc|Barrier|Duration|Instant|SystemTime|DateTime|Regex|Rng|Cell|RefCell|Comparable|Ord|Eq|Clone|Display|Hash|Add|Sub|Mul|Div)\b', r"<span class='ty'>\1</span>", hl)
                    hl = re.sub(r'\b([a-z_][a-zA-Z0-9_]*)\s*\(', r"<span class='func'>\1</span>(", hl)
                    hl = re.sub(r'\b(fn|let|var|const|return|if|elif|else|match|while|for|in|spawn|async|await|comptime|module|use|pub|as|type|enum|interface|derive|requires|ensures|invariant|true|false|self|result|Some|None|Ok|Err|unsafe|extern|is)\b', r"<span class='kw'>\1</span>", hl)
                    out.append(hl)
                out.append('</code></pre>')
                code_lines = []
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Table row
        if '|' in line and line.strip().startswith('|'):
            flush_paragraph(para_buf); para_buf = []
            if not in_table:
                in_table = True
            # Skip separator rows like |---|----|
            if re.match(r'^\|[\s\-:|]+\|$', line.strip()):
                i += 1
                continue
            cells = [c.strip() for c in line.split('|')[1:-1]]
            table_rows.append(cells)
            i += 1
            continue
        elif in_table and not line.strip().startswith('|'):
            flush_table()

        # Headers
        if line.startswith('# '):
            flush_paragraph(para_buf); para_buf = []
            flush_table()
            h = re.sub(r'`([^`]+)`', r'<code>\1</code>', line[2:].strip())
            out.append(f'<h1>{h}</h1>')
        elif line.startswith('## '):
            flush_paragraph(para_buf); para_buf = []
            flush_table()
            h = re.sub(r'`([^`]+)`', r'<code>\1</code>', line[3:].strip())
            out.append(f'<h2>{h}</h2>')
        elif line.startswith('### '):
            flush_paragraph(para_buf); para_buf = []
            flush_table()
            h = re.sub(r'`([^`]+)`', r'<code>\1</code>', line[4:].strip())
            out.append(f'<h3>{h}</h3>')
        elif line.startswith('#### '):
            flush_paragraph(para_buf); para_buf = []
            flush_table()
            h = re.sub(r'`([^`]+)`', r'<code>\1</code>', line[5:].strip())
            out.append(f'<h4>{h}</h4>')

        # Horizontal rule
        elif line.strip() == '---':
            flush_paragraph(para_buf); para_buf = []
            flush_table()
            out.append('<hr>')

        # List items
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            flush_paragraph(para_buf); para_buf = []
            flush_table()
            item = line.strip()[2:]
            item = re.sub(r'`([^`]+)`', r'<code>\1</code>', item)
            item = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', item)
            item = convert_links(item)
            # Check if previous was list to avoid wrapping
            out.append(f'<li>{item}</li>')

        elif line.strip().startswith('1. ') or re.match(r'^\d+\. ', line.strip()):
            flush_paragraph(para_buf); para_buf = []
            flush_table()
            item = re.sub(r'^\d+\.\s*', '', line.strip())
            item = re.sub(r'`([^`]+)`', r'<code>\1</code>', item)
            item = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', item)
            item = convert_links(item)
            out.append(f'<li>{item}</li>')

        # Blockquote
        elif line.startswith('> '):
            flush_paragraph(para_buf); para_buf = []
            flush_table()
            q = line[2:].strip()
            q = re.sub(r'`([^`]+)`', r'<code>\1</code>', q)
            q = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', q)
            out.append(f'<blockquote><p>{q}</p></blockquote>')

        # Empty line -> end paragraph
        elif line.strip() == '':
            flush_paragraph(para_buf); para_buf = []
            flush_table()
            # Wrap consecutive <li> items in <ul> or <ol>
            if out and out[-1].startswith('<li>') and (len(out) == 1 or not out[-2].startswith('<li>')):
                # Need to wrap list items -- do it at flush time
                pass

        else:
            para_buf.append(line)

        i += 1

    flush_paragraph(para_buf)
    flush_table()

    # Wrap list items
    result = []
    buf = []
    in_list = False
    for item in out:
        if item.startswith('<li>'):
            if not in_list:
                in_list = True
            buf.append(item)
        else:
            if in_list:
                result.append('<ul>')
                result.extend(buf)
                result.append('</ul>')
                buf = []
                in_list = False
            result.append(item)
    if in_list:
        result.append('<ul>')
        result.extend(buf)
        result.append('</ul>')

    return '\n'.join(result)


# -- Page Template ------------------------------------------------------

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>xiom -- {title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" type="image/x-icon" href="{icon_path}">
<link rel="stylesheet" href="{css_path}">
</head>
<body>

<a class="skip-link" href="#main">Skip to content</a>

<nav>
  <div class="wrap">
    <a href="{home_path}" class="logo">
      <img src="{icon_path}" alt="xiom">
      xiom
    </a>
    <div class="navlinks">
      <a href="{site_base}spec.html">Spec</a>
      <a href="{site_base}docs/">Docs</a>
      <a href="{site_base}ecosystem.html">Ecosystem</a>
      <a href="{site_base}versions.html">Versions</a>
      <a href="https://playground.xiom-lang.org">Playground</a>
    </div>
    <a class="nav-cta" href="{site_base}download.html">download</a>
  </div>
</nav>

<div class="wrap" style="padding-top:48px;padding-bottom:48px;">
  <div style="display:grid;grid-template-columns:240px 1fr;gap:48px;align-items:start;">

    <nav style="position:sticky;top:80px;">
      <div style="font-family:var(--font-mono);font-size:11px;color:var(--muted);letter-spacing:0.08em;margin-bottom:16px;">DOCUMENTATION</div>
      <div style="display:flex;flex-direction:column;gap:4px;font-size:13px;">
        {nav_links}
      </div>
    </nav>

    <main class="content-section" id="main" style="border:none;padding-top:0;">
      <div class="eyebrow" style="margin-bottom:12px;">{version}</div>
      <h1 style="font-size:36px;margin-bottom:24px;">{title}</h1>
      {body}
    </main>

  </div>
</div>

<footer>
  <div class="wrap">
    <p>xiom {version_short} - <a href="{site_base}" style="color:var(--signal);">xiom-lang.org</a></p>
    <p>Dual-licensed <a href="{site_base}LICENSE-MIT" style="color:var(--signal);">MIT</a> or <a href="{site_base}LICENSE-APACHE" style="color:var(--signal);">Apache-2.0</a>. Copyright (c) 2026 XIOM Foundation.</p>
    <div class="foot-links">
      <a href="{site_base}spec.html">Spec</a>
      <a href="{site_base}docs/">Docs</a>
      <a href="{site_base}ecosystem.html">Ecosystem</a>
      <a href="{site_base}download.html">Download</a>
    </div>
  </div>
</footer>

</body>
</html>"""


# -- Navigation Sidebar -------------------------------------------------

NAV_ORDER = [
    ("index.md", "Overview"),
    ("getting-started.md", "Getting Started"),
    ("reference.md", "Language Reference"),
    ("concepts.md", "Concepts"),
    ("examples.md", "By Example"),
    ("syntax.md", "Syntax"),
    ("types.md", "Type System"),
    ("memory-model.md", "Memory Model"),
    ("contracts.md", "Contracts"),
    ("error-handling.md", "Error Handling"),
    ("modules.md", "Modules"),
    ("generics.md", "Generics"),
    ("pattern-matching.md", "Pattern Matching"),
    ("derive.md", "Derive"),
    ("ffi.md", "C FFI"),
    ("compiler.md", "Compiler"),
    ("stdlib.md", "Stdlib Reference"),
    ("api.md", "_api"),           # built but shown as sidebar section header
    ("../AI_CONTEXT.md", "AI Coding Ref"),
]

# Output filenames of root pages, used to rewrite ../ links from nested sources.
ROOT_PAGES = {fname.replace('../', '').replace('.md', '.html') for fname, _ in NAV_ORDER}

# Stdlib modules -- individual pages
STDLIB_NAV = [
    ("stdlib/index.md", "Overview"),
    ("stdlib/core.md", "core"),
    ("stdlib/io.md", "io"),
    ("stdlib/collections.md", "collections"),
    ("stdlib/string.md", "string"),
    ("stdlib/math.md", "math"),
    ("stdlib/sync.md", "sync"),
    ("stdlib/async.md", "async"),
    ("stdlib/net.md", "net"),
    ("stdlib/crypto.md", "crypto"),
    ("stdlib/serialize.md", "serialize"),
    ("stdlib/test.md", "test"),
    ("stdlib/iter.md", "iter"),
    ("stdlib/error.md", "error"),
    ("stdlib/char.md", "char"),
    ("stdlib/path.md", "path"),
    ("stdlib/array.md", "array"),
    ("stdlib/encoding.md", "encoding"),
    ("stdlib/num.md", "num"),
    ("stdlib/cmp.md", "cmp"),
    ("stdlib/thread.md", "thread"),
    ("stdlib/mem.md", "mem"),
    ("stdlib/ptr.md", "ptr"),
    ("stdlib/alloc.md", "alloc"),
    ("stdlib/rc.md", "rc"),
    ("stdlib/os.md", "os"),
    ("stdlib/env.md", "env"),
    ("stdlib/time.md", "time"),
    ("stdlib/convert.md", "convert"),
    ("stdlib/cell.md", "cell"),
    ("stdlib/fmt.md", "fmt"),
    ("stdlib/hash.md", "hash"),
    ("stdlib/compress.md", "compress"),
    ("stdlib/rand.md", "rand"),
    ("stdlib/regex.md", "regex"),
    ("stdlib/simd.md", "simd"),
    ("stdlib/bench.md", "bench"),
    ("stdlib/log.md", "log"),
    ("stdlib/contracts.md", "contracts"),
    ("stdlib/reflect.md", "reflect"),
    ("stdlib/ffi.md", "ffi"),
]

def build_nav(current_file: str, out_name: str, ext: str = ".html") -> str:
    """Build the navigation sidebar HTML with correct relative paths.

    Depth comes from the output path (out_name), not the source path: the
    shared ../AI_CONTEXT.md source is written to the output root.
    """
    current_depth = out_name.count('/')
    up = '../' * current_depth if current_depth > 0 else ''

    links = []
    # Main nav items (skip _api -- it's rendered as the section header below)
    for fname, title in NAV_ORDER:
        if title == '_api':
            continue
        href = fname.replace('../', '').replace(".md", ext)
        if current_depth > 0 and '/' not in href:
            href = up + href
        active = (fname == current_file)
        color = 'color:var(--signal);font-weight:500;' if active else 'color:var(--muted);'
        links.append(f'<a href="{href}" style="{color}">{title}</a>')

    # Standard Library -- clickable section header
    api_href = 'api.html'
    if current_depth > 0:
        api_href = up + api_href
    api_active = (current_file == 'api.md')
    api_color = 'color:var(--signal);font-weight:600;' if api_active else 'color:var(--paper);font-weight:500;'
    links.append(f'<div style="margin-top:20px;"></div>')
    links.append(f'<a href="{api_href}" style="{api_color};font-family:var(--font-mono);font-size:10px;letter-spacing:0.08em;text-transform:uppercase;">Standard Library</a>')

    # Stdlib module links
    for fname, title in STDLIB_NAV:
        href = fname.replace(".md", ext)
        if current_depth > 0 and fname.startswith('stdlib/'):
            href = fname.replace('stdlib/', '').replace(".md", ext)
        elif current_depth == 0 and fname.startswith('stdlib/'):
            href = fname.replace(".md", ext)
        active = (fname == current_file)
        color = 'color:var(--signal);font-weight:500;' if active else 'color:var(--muted);'
        links.append(f'<a href="{href}" style="{color}">{title}</a>')

    return '\n        '.join(links)


# -- Build --------------------------------------------------------------

def build(output_dir: Path, home_path: str, css_path: str, icon_path: str,
          ext: str = ".html", site_base: str = ""):
    """Build all markdown files to HTML.

    site_base prefixes links to the marketing site (e.g. "https://xiom-lang.org/"
    for the standalone tree, "../" for the copy under xiom-website/).
    """
    # Rebuild from scratch so removed sources do not leave orphan pages behind.
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    files = []
    for fname, _ in NAV_ORDER + STDLIB_NAV:
        # Handle files outside the language directory
        if fname.startswith("../"):
            src = ROOT / "docs" / fname.replace("../", "")
        else:
            src = SRC_DIR / fname
        if src.exists():
            files.append((fname, src))
        else:
            print(f"  [skip] {fname} -- not found")

    for fname, src in files:
        text = src.read_text(encoding='utf-8')
        # Drop a leading license comment block so it cannot become the title.
        text = re.sub(r'\A\s*<!--.*?-->\s*', '', text, count=1, flags=re.S)

        title = ""
        for line in text.split('\n'):
            stripped = line.strip()
            if not stripped:
                continue
            title = stripped[2:].strip() if stripped.startswith('# ') else stripped.lstrip('#').strip()
            break

        # Strip leading # Title from body -- template already renders <h1>{title}</h1>
        body_text = text
        if body_text.startswith('# '):
            body_text = body_text.split('\n', 1)[1].lstrip('\n')
        elif body_text.startswith('## '):
            body_text = body_text  # keep it -- it's a subsection header

        body = md_to_html(body_text)

        # Beta banner on the hand-written stdlib module pages.
        if fname.startswith('stdlib/') and fname != 'stdlib/index.md':
            body = (
                '<p style="border:1px solid var(--line);border-radius:var(--radius);'
                'padding:10px 14px;color:var(--muted);font-size:13px;">Beta: the standard '
                'library is still being completed -- see the '
                '<a href="https://github.com/xiom-lang/stdlib/blob/main/docs/STDLIB_BETA_LIMITATIONS.md" '
                'style="color:var(--signal);">known limitations</a>.</p>\n' + body
            )

        # Detect version from first line
        version_line = ""
        for line in text.split('\n')[:5]:
            if 'v0.' in line and ('Compiler' in line or 'Version' in line):
                version_line = line.strip('>').strip()
                break

        # Adjust paths for files in subdirectories. ../AI_CONTEXT.md lands at
        # the output root, so the output path drives the relative links.
        out_rel = fname.replace('.md', ext).replace('../', '')
        depth = out_rel.count('/')
        file_css = '../' * depth + css_path
        file_icon = '../' * depth + icon_path
        file_home = '../' * depth + home_path
        # Absolute site roots (standalone tree) need no depth adjustment.
        file_site = site_base if site_base.startswith('http') else '../' * depth + site_base

        short = re.search(r'v\d+\.\d+(?:\.\d+)?', version_line)
        html = PAGE_TEMPLATE.format(
            title=title,
            version=version_line or DOCS_VERSION,
            version_short=short.group(0) if short else DOCS_VERSION,
            body=body,
            nav_links=build_nav(fname, out_rel, ext),
            home_path=file_home,
            css_path=file_css,
            icon_path=file_icon,
            site_base=file_site,
        )

        out = output_dir / out_rel
        out.parent.mkdir(parents=True, exist_ok=True)  # M8: ensure subdirectories exist
        with out.open('w', encoding='utf-8', newline='\n') as fh:
            fh.write(html)
        print(f"  {fname} -> {out.relative_to(ROOT)}")

    print(f"\n  {len(files)} pages built to {output_dir.relative_to(ROOT)}/")


# -- Main ---------------------------------------------------------------

if __name__ == '__main__':
    print("xiom Documentation Builder\n")

    # 1. Build standalone HTML (ships with releases, works from file://)
    print("[1/2] Building standalone HTML (docs/html/)...")
    build(
        output_dir=OUT_HTML,
        home_path="index.html",
        css_path="style.css",
        icon_path="",
        site_base="https://xiom-lang.org/",
    )

    # 2. Build website docs (integrated into xiom-lang.org)
    print("\n[2/2] Building website docs (xiom-website/docs/)...")
    build(
        output_dir=OUT_WEBSITE,
        home_path="../",
        css_path="../style.css",
        icon_path="../img/xiom-icon.ico",
        site_base="../",
    )

    # 3. Copy style.css to docs/html/ so standalone works
    style_dest = OUT_HTML / "style.css"
    if not STYLE_CSS.exists():
        raise SystemExit(f"missing stylesheet: {STYLE_CSS}")
    shutil.copy2(STYLE_CSS, style_dest)
    print(f"\n  Copied style.css -> {style_dest.relative_to(ROOT)}")

    print("\nDone. Outputs:")
    print(f"  Standalone:  {OUT_HTML.relative_to(ROOT)}/  (ships with releases)")
    print(f"  Website:     {OUT_WEBSITE.relative_to(ROOT)}/  (xiom-lang.org/docs/)")
    print(f"\nOpen: { (OUT_HTML / 'index.html').relative_to(ROOT) }")
