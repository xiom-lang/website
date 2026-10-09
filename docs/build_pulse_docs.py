"""Build the PULSE product docs into static pages.

Phase A: the markdown lives in the PULSE repository under `docs/public/`
and is vendored here as `xiom-website/projects/pulse/docs-src/` so the
build is self-contained. This script renders each page with the same
markdown converter the rest of the docs site uses (`docs/build_docs.py`)
and writes flat HTML pages plus a shared stylesheet into
`xiom-website/projects/pulse/docs/`, which nginx serves at
pulse.xiom-lang.org/docs/.

Usage (from the repository root):

    python docs/build_pulse_docs.py

Options: --src <dir> --out <dir> to override the defaults.
"""

import argparse
import html
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

DEFAULT_SRC = os.path.join(ROOT, "xiom-website", "projects", "pulse", "docs-src")
DEFAULT_OUT = os.path.join(ROOT, "xiom-website", "projects", "pulse", "docs")


def load_renderer():
    """Load md_to_html from docs/build_docs.py without running its main."""
    path = os.path.join(HERE, "build_docs.py")
    spec = importlib.util.spec_from_file_location("pulse_build_docs_base", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["pulse_build_docs_base"] = module
    spec.loader.exec_module(module)
    return module.md_to_html


FRONT_MATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.S)
SUMMARY_ENTRY = re.compile(r"(?:\d+\.|-)\s+\[([^\]]+)\]\((?:\./)?([0-9a-z-]+)\.md\)")


def parse_front_matter(text):
    meta = {}
    m = FRONT_MATTER.match(text)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip().lower()] = value.strip().strip('"')
        text = text[m.end():]
    return meta, text


def parse_summary(src):
    path = os.path.join(src, "summary.md")
    entries = []
    seen = set()
    with open(path, "r", encoding="utf-8") as fh:
        for match in SUMMARY_ENTRY.finditer(fh.read()):
            title, slug = match.group(1).strip(), match.group(2).strip()
            if slug not in seen:
                seen.add(slug)
                entries.append((title, slug))
    if not entries:
        raise SystemExit("summary.md produced no entries")
    return entries


def slug_title(entries, slug):
    for title, entry_slug in entries:
        if entry_slug == slug:
            return title
    return slug


def nav_links(entries, current_slug):
    links = []
    for title, slug in entries:
        if slug == current_slug:
            style = "color:var(--signal);font-weight:600;"
        else:
            style = "color:var(--muted);"
        links.append(
            '<a href="{0}.html" style="display:block;padding:4px 0;font-size:14px;{1}">{2}</a>'.format(
                slug, style, html.escape(title)
            )
        )
    return "\n        ".join(links)


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} -- Pulse docs</title>
<meta name="description" content="{description}">
<link rel="canonical" href="https://pulse.xiom-lang.org/docs/{canonical}">
<link rel="icon" type="image/x-icon" href="../img/xiom-icon.ico">
<link rel="stylesheet" href="style.css">
</head>
<body>

<nav>
  <div class="wrap">
    <a href="../" class="logo">
      <img src="../img/xiom-logo_bg.png" alt="">
      PULSE docs
    </a>
    <div class="navlinks">
      <a href="../">Overview</a>
      <a href="index.html">Docs</a>
      <a href="../#install">Install</a>
      <a href="../#downloads">Downloads</a>
      <a href="https://opencollective.com/xiom">Support</a>
    </div>
    <a class="nav-cta" href="https://github.com/xiom-projects/xiom-pulse">GitHub</a>
  </div>
</nav>

<main class="wrap" style="padding-top:40px;">
  <div style="display:flex;gap:32px;flex-wrap:wrap;align-items:flex-start;">
    <nav aria-label="Documentation" style="flex:0 0 220px;min-width:200px;">
      <p style="font-family:var(--font-mono);font-size:11px;letter-spacing:0.08em;text-transform:uppercase;color:var(--signal);margin-bottom:8px;">Documentation</p>
      {nav}
    </nav>
    <article class="content-section" style="flex:1 1 420px;min-width:280px;margin-top:0;">
{body}
    </article>
  </div>
</main>

<footer>
  <div class="wrap">
    <div style="border-top:1px solid var(--line);padding-top:24px;margin-top:48px;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;color:var(--muted);font-size:13px;">
      <p>Pulse is a separate open-source project built with XIOM. Copyright (c) 2026 Eleftherios Notas and The XIOM Authors. Dual-licensed MIT or Apache-2.0.</p>
      <p><a href="../" style="color:var(--signal);">Pulse</a> -- <a href="https://xiom-lang.org/" style="color:var(--signal);">An XIOM project</a> -- <a href="https://opencollective.com/xiom" style="color:var(--signal);">Support XIOM</a></p>
    </div>
  </div>
</footer>

</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default=DEFAULT_SRC)
    parser.add_argument("--out", default=DEFAULT_OUT)
    args = parser.parse_args()

    md_to_html = load_renderer()
    entries = parse_summary(args.src)

    if not os.path.isdir(args.out):
        os.makedirs(args.out)

    written = 0
    for title, slug in entries:
        src_path = os.path.join(args.src, slug + ".md")
        if not os.path.isfile(src_path):
            raise SystemExit("missing source page: " + src_path)
        with open(src_path, "r", encoding="utf-8") as fh:
            meta, body_md = parse_front_matter(fh.read())

        page_title = meta.get("title", title)
        description = meta.get(
            "description", page_title + " -- PULSE documentation."
        )
        canonical = "" if slug == "index" else slug + ".html"

        body = md_to_html(body_md)
        page = PAGE.format(
            title=html.escape(page_title),
            description=html.escape(description, quote=True),
            canonical=canonical,
            nav=nav_links(entries, slug),
            body=body,
        )
        non_ascii = [ch for ch in page if ord(ch) > 127]
        if non_ascii:
            raise SystemExit(
                "non-ASCII content in {0}: {1!r}".format(slug, non_ascii[:5])
            )
        out_path = os.path.join(args.out, slug + ".html")
        with open(out_path, "w", encoding="ascii", newline="\n") as fh:
            fh.write(page)
        written += 1

    css_src = os.path.join(ROOT, "xiom-website", "style.css")
    css_dst = os.path.join(args.out, "style.css")
    with open(css_src, "r", encoding="utf-8") as fh:
        css = fh.read()
    with open(css_dst, "w", encoding="ascii", newline="\n") as fh:
        fh.write(css)

    print("wrote {0} pages + style.css to {1}".format(written, args.out))


if __name__ == "__main__":
    main()
