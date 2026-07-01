#!/usr/bin/env python3
"""
AXIOM Documentation Builder
Converts docs/language/*.md → docs/html/ and website/docs/
Run: python docs/build_docs.py

Outputs:
  docs/html/         — static HTML, ships with releases, works from file://
  website/docs/      — integrated into axiom-lang.org
"""

import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "docs" / "language"
AI_CONTEXT = ROOT / "docs" / "AI_CONTEXT.md"
OUT_HTML = ROOT / "docs" / "html"
OUT_WEBSITE = ROOT / "website" / "docs"
STYLE_CSS = ROOT / "website" / "style.css"
IMAGE_DIR = ROOT / "resource" / "img"

# ── Markdown → HTML Converter ──────────────────────────────────────────

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

    def flush_paragraph(buf):
        if not buf:
            return
        p = ' '.join(buf).strip()
        if p:
            # Inline code
            p = re.sub(r'`([^`]+)`', r'<code>\1</code>', p)
            # Bold
            p = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', p)
            # Italic
            p = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', p)
            # Links
            p = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', p)
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
                cell = re.sub(r'`([^`]+)`', r'<code>\1</code>', cell.strip())
                cell = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', cell)
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
                    # Basic syntax highlighting for axiom code
                    hl = cl
                    hl = re.sub(r'(//.*$)', r'<span class="cm">\1</span>', hl)
                    hl = re.sub(r'\b(fn|let|var|const|return|if|elif|else|match|while|for|in|spawn|async|await|comptime|module|use|pub|as|type|enum|interface|derive|requires|ensures|invariant|true|false|self|result|Some|None|Ok|Err|unsafe|extern|is)\b', r'<span class="kw">\1</span>', hl)
                    hl = re.sub(r'\b(Int|Int8|Int16|Int32|Int64|UInt|UInt8|UInt16|UInt32|UInt64|Float32|Float64|Bool|Str|Char|Vec|Map|Set|Option|Result|Slice|Self|Unit|Stack|Point|Health|Score|Vec3|TcpStream|TcpListener|HttpResponse|UdpSocket|NetError|IOError|ParseError|AppError|Channel|Mutex|RwLock|Arc|Barrier|Duration|Instant|SystemTime|DateTime|Regex|Rng|Cell|RefCell|Comparable|Ord|Eq|Clone|Display|Hash|Add|Sub|Mul|Div)\b', r'<span class="ty">\1</span>', hl)
                    hl = re.sub(r'("[^"]*")', r'<span class="str">\1</span>', hl)
                    hl = re.sub(r'(\b\d+\.?\d*\b)', r'<span class="num">\1</span>', hl)
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
            item = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', item)
            # Check if previous was list to avoid wrapping
            out.append(f'<li>{item}</li>')

        elif line.strip().startswith('1. ') or re.match(r'^\d+\. ', line.strip()):
            flush_paragraph(para_buf); para_buf = []
            flush_table()
            item = re.sub(r'^\d+\.\s*', '', line.strip())
            item = re.sub(r'`([^`]+)`', r'<code>\1</code>', item)
            item = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', item)
            out.append(f'<li>{item}</li>')

        # Blockquote
        elif line.startswith('> '):
            flush_paragraph(para_buf); para_buf = []
            flush_table()
            q = line[2:].strip()
            q = re.sub(r'`([^`]+)`', r'<code>\1</code>', q)
            q = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', q)
            out.append(f'<blockquote><p>{q}</p></blockquote>')

        # Empty line → end paragraph
        elif line.strip() == '':
            flush_paragraph(para_buf); para_buf = []
            flush_table()
            # Wrap consecutive <li> items in <ul> or <ol>
            if out and out[-1].startswith('<li>') and (len(out) == 1 or not out[-2].startswith('<li>')):
                # Need to wrap list items — do it at flush time
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


# ── Page Template ──────────────────────────────────────────────────────

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AXIOM — {title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" type="image/png" href="{icon_path}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{css_path}">
</head>
<body>

<nav>
  <div class="wrap">
    <a href="{home_path}" class="logo">
      <img src="{icon_path}" alt="AXIOM" style="width:20px;height:20px;">
      AXIOM
    </a>
    <div class="navlinks">
      <a href="{home_path}spec.html">Spec</a>
      <a href="{home_path}docs/">Docs</a>
      <a href="{home_path}ecosystem.html">Ecosystem</a>
      <a href="{home_path}versions.html">Versions</a>
      <a href="{home_path}playground/">Playground</a>
    </div>
    <a class="nav-cta" href="{home_path}download.html">download</a>
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

    <main class="content-section" style="border:none;padding-top:0;">
      <div class="eyebrow" style="margin-bottom:12px;">{version}</div>
      <h1 style="font-size:36px;margin-bottom:24px;">{title}</h1>
      {body}
    </main>

  </div>
</div>

<footer>
  <div class="wrap">
    <p>AXIOM {version_short} · <a href="{home_path}" style="color:var(--signal);">axiom-lang.org</a></p>
    <div class="foot-links">
      <a href="{home_path}spec.html">Spec</a>
      <a href="{home_path}docs/">Docs</a>
      <a href="{home_path}ecosystem.html">Ecosystem</a>
      <a href="{home_path}download.html">Download</a>
    </div>
  </div>
</footer>

</body>
</html>"""


# ── Navigation Sidebar ─────────────────────────────────────────────────

NAV_ORDER = [
    ("index.md", "Overview"),
    ("getting-started.md", "Getting Started"),
    ("examples.md", "By Example"),
    ("syntax.md", "Syntax"),
    ("types.md", "Type System"),
    ("memory-model.md", "Memory Model"),
    ("contracts.md", "Contracts"),
    ("error-handling.md", "Error Handling"),
    ("modules.md", "Modules"),
    ("generics.md", "Generics"),
    ("derive.md", "Derive"),
    ("ffi.md", "C FFI"),
    ("stdlib.md", "Standard Library"),
    ("compiler.md", "Compiler"),
    ("../AI_CONTEXT.md", "AI Coding Ref"),
]

def build_nav(current_file: str, output_dir: str, ext: str = ".html") -> str:
    """Build the navigation sidebar HTML."""
    links = []
    for fname, title in NAV_ORDER:
        if fname == current_file:
            links.append(f'<a href="{fname.replace(".md", ext)}" style="color:var(--signal);font-weight:500;">{title}</a>')
        else:
            links.append(f'<a href="{fname.replace(".md", ext)}" style="color:var(--muted);">{title}</a>')
    return '\n        '.join(links)


# ── Build ──────────────────────────────────────────────────────────────

def build(output_dir: Path, home_path: str, css_path: str, icon_path: str, ext: str = ".html"):
    """Build all markdown files to HTML."""
    output_dir.mkdir(parents=True, exist_ok=True)

    files = []
    for fname, _ in NAV_ORDER:
        # Handle files outside the language directory
        if fname.startswith("../"):
            src = ROOT / "docs" / fname.replace("../", "")
        else:
            src = SRC_DIR / fname
        if src.exists():
            files.append((fname, src))
        else:
            print(f"  [skip] {fname} — not found")

    for fname, src in files:
        text = src.read_text(encoding='utf-8')
        title = text.split('\n')[0].lstrip('#').strip()
        body = md_to_html(text)

        # Detect version from first line
        version_line = ""
        for line in text.split('\n')[:5]:
            if 'v0.' in line and ('Compiler' in line or 'Version' in line):
                version_line = line.strip('>').strip()
                break

        html = PAGE_TEMPLATE.format(
            title=title,
            version=version_line or "v0.12.0 · 234 tests",
            version_short="v0.12.0",
            body=body,
            nav_links=build_nav(fname, str(output_dir), ext),
            home_path=home_path,
            css_path=css_path,
            icon_path=icon_path,
        )

        out = output_dir / fname.replace('.md', ext).replace('../', '')
        out.write_text(html, encoding='utf-8')
        print(f"  {fname} -> {out.relative_to(ROOT)}")

    print(f"\n  {len(files)} pages built to {output_dir.relative_to(ROOT)}/")


# ── Main ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("AXIOM Documentation Builder\n")

    # 1. Build standalone HTML (ships with releases, works from file://)
    print("[1/2] Building standalone HTML (docs/html/)...")
    build(
        output_dir=OUT_HTML,
        home_path="../website/",
        css_path="../website/style.css",
        icon_path="../resource/img/axiom-icon.png",
    )

    # 2. Build website docs (integrated into axiom-lang.org)
    print("\n[2/2] Building website docs (website/docs/)...")
    build(
        output_dir=OUT_WEBSITE,
        home_path="../",
        css_path="../style.css",
        icon_path="../../resource/img/axiom-icon.png",
    )

    # 3. Copy style.css to docs/html/ so standalone works
    style_dest = OUT_HTML / "style.css"
    if STYLE_CSS.exists():
        shutil.copy2(STYLE_CSS, style_dest)
        print(f"\n  Copied style.css -> {style_dest.relative_to(ROOT)}")

    print("\nDone. Outputs:")
    print(f"  Standalone:  {OUT_HTML.relative_to(ROOT)}/  (ships with releases)")
    print(f"  Website:     {OUT_WEBSITE.relative_to(ROOT)}/  (axiom-lang.org/docs/)")
    print(f"\nOpen: { (OUT_HTML / 'index.html').relative_to(ROOT) }")

    # 3. Copy style.css to docs/html/ so standalone works
    style_dest = OUT_HTML / "style.css"
    if STYLE_CSS.exists():
        shutil.copy2(STYLE_CSS, style_dest)
        print(f"\n  Copied style.css -> {style_dest.relative_to(ROOT)}")

    print("\nDone. Outputs:")
    print(f"  Standalone:  {OUT_HTML.relative_to(ROOT)}/  (ships with releases)")
    print(f"  Website:     {OUT_WEBSITE.relative_to(ROOT)}/  (axiom-lang.org/docs/)")
    print(f"\nOpen: { (OUT_HTML / 'index.html').relative_to(ROOT) }")
