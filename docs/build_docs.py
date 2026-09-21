#!/usr/bin/env python3
# Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
# SPDX-License-Identifier: MIT OR Apache-2.0
"""
xiom Documentation Builder
Converts docs/language/*.md -> docs/html/
Run: python docs/build_docs.py

Outputs:
  docs/html/ -- static HTML, ships with releases, works from file://;
                published to docs.xiom-lang.org via the mike pipeline

Set XIOM_DOCS_VERSION to stamp pages with a release tag (default: latest).
"""

import html
import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "docs" / "language"
AI_CONTEXT = ROOT / "docs" / "AI_CONTEXT.md"
OUT_HTML = ROOT / "docs" / "html"
STYLE_CSS = ROOT / "xiom-website" / "style.css"
IMAGE_DIR = ROOT / "resource" / "img"

# Stamped onto pages that carry no version line of their own. CI sets this to
# the release tag being built; local runs default to "latest".
DOCS_VERSION = os.environ.get("XIOM_DOCS_VERSION", "latest")

# -- Markdown -> HTML Converter ------------------------------------------

def inline_code(text: str) -> str:
    """Render `code` spans with HTML escaping.

    Raw <, > and & in code must not be parsed as tags or entities by the
    browser; escaping keeps `a < b` and `Option<T>` visible.
    """
    return re.sub(
        r'`([^`]+)`',
        lambda m: '<code>{0}</code>'.format(html.escape(m.group(1), quote=False)),
        text,
    )


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

    def render_inline(s):
        """Render one line/paragraph of inline Markdown.

        Code spans are stashed first so the bold, italic and link rules can
        never reach inside them (a '*' inside `xiom_*` must stay literal).
        """
        spans = []

        def stash(match):
            spans.append(
                '<code>{0}</code>'.format(html.escape(match.group(1), quote=False))
            )
            return '\x00{0}\x00'.format(len(spans) - 1)

        s = re.sub(r'`([^`]+)`', stash, s)
        s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
        s = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', s)
        s = convert_links(s)
        return re.sub(r'\x00(\d+)\x00', lambda m: spans[int(m.group(1))], s)

    def flush_paragraph(buf):
        if not buf:
            return
        p = ' '.join(buf).strip()
        if p:
            p = render_inline(p)
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
                cell = render_inline(cell)
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
                    # Basic syntax highlighting for xiom code. Escape first so
                    # comparison operators and generics stay visible.
                    hl = html.escape(cl, quote=False)
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
            h = inline_code(line[2:].strip())
            out.append(f'<h1>{h}</h1>')
        elif line.startswith('## '):
            flush_paragraph(para_buf); para_buf = []
            flush_table()
            h = inline_code(line[3:].strip())
            out.append(f'<h2>{h}</h2>')
        elif line.startswith('### '):
            flush_paragraph(para_buf); para_buf = []
            flush_table()
            h = inline_code(line[4:].strip())
            out.append(f'<h3>{h}</h3>')
        elif line.startswith('#### '):
            flush_paragraph(para_buf); para_buf = []
            flush_table()
            h = inline_code(line[5:].strip())
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
            item = render_inline(item)
            # Check if previous was list to avoid wrapping
            out.append(f'<li>{item}</li>')

        elif line.strip().startswith('1. ') or re.match(r'^\d+\. ', line.strip()):
            flush_paragraph(para_buf); para_buf = []
            flush_table()
            item = re.sub(r'^\d+\.\s*', '', line.strip())
            item = render_inline(item)
            out.append(f'<li>{item}</li>')

        # Blockquote
        elif line.startswith('> '):
            flush_paragraph(para_buf); para_buf = []
            flush_table()
            q = line[2:].strip()
            q = render_inline(q)
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

<nav>
  <div class="wrap">
    <a href="{home_path}" class="logo">
      <img src="{icon_path}" alt="xiom">
      xiom
    </a>
    <div class="navlinks">
      <a href="{site_base}spec.html">Spec</a>
      <a href="https://docs.xiom-lang.org/">Docs</a>
      <a href="{site_base}why.html">Why</a>
      <a href="{site_base}prior-art.html">Prior art</a>
      <a href="{site_base}ecosystem.html">Ecosystem</a>
      <a href="https://registry.xiom-lang.org">Registry</a>
      <a href="{site_base}roadmap.html">Roadmap</a>
      <a href="{site_base}contributing.html">Contributing</a>
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
    <div class="footer-grid">
      <div class="footer-brand">
        <a href="{home_path}" class="logo">
          <img src="{icon_path}" alt="xiom">
          xiom
        </a>
        <p>Dual-licensed <a href="{site_base}LICENSE-MIT" style="color:var(--signal);">MIT</a> or <a href="{site_base}LICENSE-APACHE" style="color:var(--signal);">Apache-2.0</a>, at your option.</p>
        <p>An independent project by <a href="https://github.com/Lefteris-Notas" style="color:var(--signal);">Lefteris Notas</a>.</p>
        <!-- Icons: Simple Icons (CC0) -->
        <div class="footer-social">
          <a href="https://discord.gg/fsxQfDUg9" aria-label="XIOM community Discord (open invite)" title="Discord" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M20.317 4.3698a19.7913 19.7913 0 00-4.8851-1.5152.0741.0741 0 00-.0785.0371c-.211.3753-.4447.8648-.6083 1.2495-1.8447-.2762-3.68-.2762-5.4868 0-.1636-.3933-.4058-.8742-.6177-1.2495a.077.077 0 00-.0785-.037 19.7363 19.7363 0 00-4.8852 1.515.0699.0699 0 00-.0321.0277C.5334 9.0458-.319 13.5799.0992 18.0578a.0824.0824 0 00.0312.0561c2.0528 1.5076 4.0413 2.4228 5.9929 3.0294a.0777.0777 0 00.0842-.0276c.4616-.6304.8731-1.2952 1.226-1.9942a.076.076 0 00-.0416-.1057c-.6528-.2476-1.2743-.5495-1.8722-.8923a.077.077 0 01-.0076-.1277c.1258-.0943.2517-.1923.3718-.2914a.0743.0743 0 01.0776-.0105c3.9278 1.7933 8.18 1.7933 12.0614 0a.0739.0739 0 01.0785.0095c.1202.099.246.1981.3728.2924a.077.077 0 01-.0066.1276 12.2986 12.2986 0 01-1.873.8914.0766.0766 0 00-.0407.1067c.3604.698.7719 1.3628 1.225 1.9932a.076.076 0 00.0842.0286c1.961-.6067 3.9495-1.5219 6.0023-3.0294a.077.077 0 00.0313-.0552c.5004-5.177-.8382-9.6739-3.5485-13.6604a.061.061 0 00-.0312-.0286zM8.02 15.3312c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9555-2.4189 2.157-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.9555 2.4189-2.1569 2.4189zm7.9748 0c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9554-2.4189 2.1569-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.946 2.4189-2.1568 2.4189Z"/></svg></a>
          <a href="https://x.com/XiomLang" aria-label="XIOM on X" title="X" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z"/></svg></a>
          <a href="https://mastodon.social/@xiom_lang" aria-label="XIOM on Mastodon" title="Mastodon" target="_blank" rel="me noopener"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M23.268 5.313c-.35-2.578-2.617-4.61-5.304-5.004C17.51.242 15.792 0 11.813 0h-.03c-3.98 0-4.835.242-5.288.309C3.882.692 1.496 2.518.917 5.127.64 6.412.61 7.837.661 9.143c.074 1.874.088 3.745.26 5.611.118 1.24.325 2.47.62 3.68.55 2.237 2.777 4.098 4.96 4.857 2.336.792 4.849.923 7.256.38.265-.061.527-.132.786-.213.585-.184 1.27-.39 1.774-.753a.057.057 0 0 0 .023-.043v-1.809a.052.052 0 0 0-.02-.041.053.053 0 0 0-.046-.01 20.282 20.282 0 0 1-4.709.545c-2.73 0-3.463-1.284-3.674-1.818a5.593 5.593 0 0 1-.319-1.433.053.053 0 0 1 .066-.054c1.517.363 3.072.546 4.632.546.376 0 .75 0 1.125-.01 1.57-.044 3.224-.124 4.768-.422.038-.008.077-.015.11-.024 2.435-.464 4.753-1.92 4.989-5.604.008-.145.03-1.52.03-1.67.002-.512.167-3.63-.024-5.545zm-3.748 9.195h-2.561V8.29c0-1.309-.55-1.976-1.67-1.976-1.23 0-1.846.79-1.846 2.35v3.403h-2.546V8.663c0-1.56-.617-2.35-1.848-2.35-1.112 0-1.668.668-1.67 1.977v6.218H4.822V8.102c0-1.31.337-2.35 1.011-3.12.696-.77 1.608-1.164 2.74-1.164 1.311 0 2.302.5 2.962 1.498l.638 1.06.638-1.06c.66-.999 1.65-1.498 2.96-1.498 1.13 0 2.043.395 2.74 1.164.675.77 1.012 1.81 1.012 3.12z"/></svg></a>
          <a href="https://bsky.app/profile/xiom-lang.bsky.social" aria-label="XIOM on Bluesky" title="Bluesky" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 10.8c-1.087-2.114-4.046-6.053-6.798-7.995C2.566.944 1.561 1.266.902 1.565.139 1.908 0 3.08 0 3.768c0 .69.378 5.65.624 6.479.815 2.736 3.713 3.66 6.383 3.364.136-.02.275-.039.415-.056-.138.022-.276.04-.415.056-3.912.58-7.387 2.005-2.83 7.078 5.013 5.19 6.87-1.113 7.823-4.308.953 3.195 2.05 9.271 7.733 4.308 4.267-4.308 1.172-6.498-2.74-7.078a8.741 8.741 0 0 1-.415-.056c.14.017.279.036.415.056 2.67.297 5.568-.628 6.383-3.364.246-.828.624-5.79.624-6.478 0-.69-.139-1.861-.902-2.206-.659-.298-1.664-.62-4.3 1.24C16.046 4.748 13.087 8.687 12 10.8Z"/></svg></a>
          <a href="https://www.reddit.com/r/xiom_lang/" aria-label="XIOM on Reddit" title="Reddit" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 0C5.373 0 0 5.373 0 12c0 3.314 1.343 6.314 3.515 8.485l-2.286 2.286C.775 23.225 1.097 24 1.738 24H12c6.627 0 12-5.373 12-12S18.627 0 12 0Zm4.388 3.199c1.104 0 1.999.895 1.999 1.999 0 1.105-.895 2-1.999 2-.946 0-1.739-.657-1.947-1.539v.002c-1.147.162-2.032 1.15-2.032 2.341v.007c1.776.067 3.4.567 4.686 1.363.473-.363 1.064-.58 1.707-.58 1.547 0 2.802 1.254 2.802 2.802 0 1.117-.655 2.081-1.601 2.531-.088 3.256-3.637 5.876-7.997 5.876-4.361 0-7.905-2.617-7.998-5.87-.954-.447-1.614-1.415-1.614-2.538 0-1.548 1.255-2.802 2.803-2.802.645 0 1.239.218 1.712.585 1.275-.79 2.881-1.291 4.64-1.365v-.01c0-1.663 1.263-3.034 2.88-3.207.188-.911.993-1.595 1.959-1.595Zm-8.085 8.376c-.784 0-1.459.78-1.506 1.797-.047 1.016.64 1.429 1.426 1.429.786 0 1.371-.369 1.418-1.385.047-1.017-.553-1.841-1.338-1.841Zm7.406 0c-.786 0-1.385.824-1.338 1.841.047 1.017.634 1.385 1.418 1.385.785 0 1.473-.413 1.426-1.429-.046-1.017-.721-1.797-1.506-1.797Zm-3.703 4.013c-.974 0-1.907.048-2.77.135-.147.015-.241.168-.183.305.483 1.154 1.622 1.964 2.953 1.964 1.33 0 2.47-.81 2.953-1.964.057-.137-.037-.29-.184-.305-.863-.087-1.795-.135-2.769-.135Z"/></svg></a>
          <a href="https://news.ycombinator.com/user?id=xiom-lang" aria-label="XIOM on Hacker News" title="Hacker News" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M0 24V0h24v24H0zM6.951 5.896l4.112 7.708v5.064h1.583v-4.972l4.148-7.799h-1.749l-2.457 4.875c-.372.745-.688 1.434-.688 1.434s-.297-.708-.651-1.434L8.831 5.896h-1.88z"/></svg></a>
          <a href="https://www.linkedin.com/company/145216062/" aria-label="XIOM on LinkedIn" title="LinkedIn" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg></a>
          <a href="https://www.facebook.com/profile.php?id=61594524426045" aria-label="XIOM on Facebook" title="Facebook" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036 26.805 26.805 0 0 0-.733-.009c-.707 0-1.259.096-1.675.309a1.686 1.686 0 0 0-.679.622c-.258.42-.374.995-.374 1.752v1.297h3.919l-.386 2.103-.287 1.564h-3.246v8.245C19.396 23.238 24 18.179 24 12.044c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.628 3.874 10.35 9.101 11.647Z"/></svg></a>
        </div>
      </div>
      <div class="footer-col">
        <h4>Language</h4>
        <a href="{site_base}spec.html">Specification</a>
        <a href="{site_base}why.html">Why XIOM</a>
        <a href="{site_base}prior-art.html">Prior art</a>
        <a href="{site_base}roadmap.html">Roadmap</a>
        <a href="{site_base}history.html">History</a>
      </div>
      <div class="footer-col">
        <h4>Explore</h4>
        <a href="https://docs.xiom-lang.org/">Documentation</a>
        <a href="https://playground.xiom-lang.org">Playground</a>
        <a href="https://registry.xiom-lang.org">Registry</a>
        <a href="{site_base}versions.html">Versions</a>
        <a href="{site_base}download.html">Download</a>
      </div>
      <div class="footer-col">
        <h4>Project</h4>
        <a href="https://github.com/xiom-lang">GitHub</a>
        <a href="mailto:support@xiom-lang.org">support@xiom-lang.org</a>
        <a href="{site_base}contributing.html">Contributing</a>
        <a href="{site_base}terms.html">Terms of Use</a>
        <a href="{site_base}privacy.html">Privacy Policy</a>
      </div>
    </div>
    <div class="footer-bottom">
      <p>Copyright (c) 2026 Eleftherios Notas and The XIOM Authors.</p>
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

    # Build standalone HTML (ships with releases, works from file://)
    print("[1/1] Building standalone HTML (docs/html/)...")
    build(
        output_dir=OUT_HTML,
        home_path="index.html",
        css_path="style.css",
        icon_path="",
        site_base="https://xiom-lang.org/",
    )

    # Copy style.css to docs/html/ so standalone works
    style_dest = OUT_HTML / "style.css"
    if not STYLE_CSS.exists():
        raise SystemExit(f"missing stylesheet: {STYLE_CSS}")
    shutil.copy2(STYLE_CSS, style_dest)
    print(f"\n  Copied style.css -> {style_dest.relative_to(ROOT)}")

    print("\nDone. Output:")
    print(f"  Standalone:  {OUT_HTML.relative_to(ROOT)}/  (ships with releases; docs.xiom-lang.org)")
    print(f"\nOpen: { (OUT_HTML / 'index.html').relative_to(ROOT) }")
