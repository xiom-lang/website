# Website Session -- Handoff & Work Guide

**Read this first** when working in `xiom-lang/website`. This repo owns the
public site (`xiom-lang.org`), the documentation front-end
(`docs.xiom-lang.org`), and the installers users run.

Deployment mechanics live in `DEPLOY.md`; this file covers the work queue.
Lane boundary: do not edit `crates/**`, `stdlib/**` or the registry service;
those live in their own repositories. Operational/deploy scripts live in the
private `xiom-lang/ops` repo.

## Live state (2026-09-17)

| URL | Served from | Notes |
|---|---|---|
| https://xiom-lang.org | `xiom-website/` | mirror-first download page, installers |
| https://docs.xiom-lang.org | `docs/html/` | generated documentation front-end |
| https://xiom-lang.org/docs/ | `xiom-website/docs/` | same docs inside the site (docs.html redirects here) |
| https://dl.xiom-lang.org | release mirror | `latest.json`, `releases/index.json`, artifacts |

Deploys are pull-based: `/opt/xiom/bin/web-deploy.sh` on the VPS (from
`xiom-lang/ops`) fetches this repo and publishes both docroots; it runs
hourly from `/etc/cron.d/xiom-deploy` (minute 23). Push to `main` and the
site is live within the hour, or run the script for an immediate publish.

## Repository layout

| Path | Purpose |
|---|---|
| `xiom-website/` | the site: pages, `style.css`, `img/`, `docs/` (generated) |
| `docs/language/` | hand-written documentation sources (Markdown) |
| `docs/ecosystem/`, `docs/error_codes/` | further doc sources |
| `docs/html/` | generated HTML (ships with releases, serves docs subdomain) |
| `docs/build_docs.py` | the generator (see known issue below) |
| `specs/` | language specification and strategy documents |
| `resource/img/` | shared image assets |

## Workstream 1: download experience

Current behaviour to preserve: `xiom-website/download.html` fetches
`https://dl.xiom-lang.org/latest.json` first and falls back to the GitHub
API; asset rows and the version line update automatically; macOS rows stay
hidden until those assets exist. `install.ps1` and `install.sh` are served
from the site root, download from the mirror, verify SHA256 against
`SHA256SUMS`, install into the user directory, and check for LLVM/Clang.

Queue:

1. **~~Version pinning~~ (done 2026-09-17)**: `-Version <tag>` and
   `--version <tag>` on both installers; pinned installs use
   `dl.xiom-lang.org/releases/<tag>/` directly and fail with a pointer to
   `releases/index.json` when the tag is not on the mirror. Tested end to
   end on Windows (v0.60.1) and via `sh` logic with a stubbed platform.
2. **~~Verification surfaced on the page~~ (done 2026-09-17)**: the
   download table shows the expected SHA256 per archive, filled from
   `SHA256SUMS` next to `latest.json`, with the attestation command in the
   verify section.
3. **macOS**: when the compiler release enables macOS builds (`xiom` repo
   variable `RELEASE_BUILD_MACOS=true`), the page rows appear
   automatically; add `install.sh` macOS support (Homebrew clang check,
   `xcode-select`) at the same time.
4. **~~One-line install honesty~~ (done 2026-09-17)**: the page describes
   what the installer does and warns about piping scripts from the
   internet; both installers stay short and auditable.
5. **Version manager (`xiomup`)**: keep the planned section until an actual
   implementation exists; do not promise it early.
6. **Point to docs in other repos**: the language guide lives here, but
   stdlib API docs are generated from `xiom-lang/stdlib`, and registry docs
   from `xiom-lang/registry`. Add an "Ecosystem docs" block linking those
   repositories' docs and the future generated API pages instead of
   duplicating content.

## Workstream 2: documentation platform

Current pipeline: `docs/build_docs.py` converts `docs/language/*.md` to
`docs/html/` and `xiom-website/docs/` (both generated; `docs/html/` is
canonical for the docs subdomain, the site copy is published under
`xiom-lang.org/docs/`). Fixed 2026-09-17: paths corrected for the
`xiom-website/` split, every `docs/language/` source is in the nav, output
is rebuilt from scratch (no orphan pages), generation is idempotent, and
`.github/workflows/docs.yml` fails when committed output differs. Set
`XIOM_DOCS_VERSION` to stamp pages (default `latest`); the mike migration
replaces that stamping with per-version builds.

The versioned pipeline is in place as of 2026-09-17: `docs/build_mkdocs.py`
stages `build/mkdocs-src/` (guides + generated API pages + meta-refresh
stubs for every legacy `docs/html/*.html` URL), `mkdocs build --strict`
passes with mkdocs-material 9.7.7 / mike 2.2.0, and
`.github/workflows/docs-versioned.yml` publishes with mike to `gh-pages` on
dispatch. Note: MkDocs needs Python 3.8+; this machine only has 3.7, so
local verification used a portable `uv` Python 3.12.

Queue:

1. **~~Fix and pin the generator~~ (done 2026-09-17)**: paths, full nav
   coverage, clean rebuild, and CI drift check in place. Remaining: decide
   whether the site copy stays once mike versioning lands.
2. **~~MkDocs Material + mike migration~~ (scaffold done 2026-09-17)**:
   config, pinned toolchain, assembly script, strict build, legacy
   redirects, and the publish workflow are in place. Remaining: the ops
   session must switch the docs docroot from `docs/html/` to the mike
   output on `gh-pages`; until then the hourly pull keeps `docs/html/`
   live. Also decide the site copy once the switch happens.
3. **Stdlib/compiler API pages (done 2026-09-17)**: `docs/build_api_docs.py`
   walks a stdlib checkout, runs `xiom-doc` over every source and writes
   per-module MkDocs pages plus an index. Spike over the local stdlib at
   v0.60.0: 44 modules, 517 files, 6,879 symbols, 0 parse failures, ~8s.
   Wired into `docs/build_mkdocs.py`; `docs-versioned.yml` builds
   `xiom-doc` from the xiom ref (`--locked`) before assembling. Remaining:
   first real dispatch run to validate the cross-repo build.
4. **Trigger**: `docs-versioned.yml` accepts
   `repository_dispatch: compiler-release` (payload `tag`, optional
   `stdlib_ref`/`compiler_ref`) and manual dispatch. Remaining: the
   compiler release workflow (compiler lane) must fire the event.
5. **~~`versions.html` from the mirror~~ (done 2026-09-17)**: the current
   card and release table are read from
   `https://dl.xiom-lang.org/releases/index.json` (mirror retains 20 tags);
   pre-0.13 history has no artifacts and is no longer listed. Frozen docs
   links land with the mike migration.
6. **~~Link checking~~ (done 2026-09-17)**: `docs/check_links.py` runs in
   `docs.yml` over `docs/html` and `xiom-website` (0 broken); the dead
   `M10_SCRIPTING_MODE`, `ecosystem/*`, and `checklists/*` references were
   removed or repointed, and MkDocs strict mode validates the versioned
   tree.

## Rules

- Pure ASCII files only; the org encoding gate rejects mojibake.
- Never hardcode versions in pages; read `latest.json` / `index.json`.
- No secrets, no environment-specific URLs beyond `xiom-lang.org` and
  `dl.xiom-lang.org`.
- Test installer changes end to end (Windows locally, Linux in a container)
  before pushing; they are the first thing users run.
- Nav consistency: use `https://playground.xiom-lang.org` (absolute) or a
  deliberate relative path in every page, not a mix.
- `docs/html/` and `xiom-website/docs/` are generated; do not hand-edit.

## Paste-ready prompt for the next session

```
Work in E:\xiom-lang\website (website lane) for the XIOM project. Read
SESSION.md (this file) and DEPLOY.md before acting. Deploys are pull-based
from this repo to the VPS via /opt/xiom/bin/web-deploy.sh (cron minute 23);
push to main and it publishes within the hour, or run the script on the VPS
with the owner in PuTTY (outputs pasted back; never request credentials).

Priority: (1) ops session switches the docs docroot from `docs/html/` to
the mike output on `gh-pages`, then run the first `docs-versioned` publish
(manual dispatch) and verify `https://docs.xiom-lang.org/latest/` plus a
frozen `/vX.Y.Z/` and the legacy `.html` redirects; (2) compiler release
workflow fires `repository_dispatch: compiler-release` with the tag so
publishes are automatic; (3) macOS installer support once
`RELEASE_BUILD_MACOS=true`; (4) ecosystem doc pointers stay deferred until
stdlib is 100%. Keep the site static, ASCII-only, and driven by the mirror
JSON files - never hardcode versions.
```
