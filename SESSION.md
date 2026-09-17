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
4. **One-line install honesty**: the installers are proven on Windows and
   Linux (container test). Add a short "what it does" note (download,
   checksum, PATH, clang check) and keep the pipe-to-shell warning advice.
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

Queue:

1. **~~Fix and pin the generator~~ (done 2026-09-17)**: paths, full nav
   coverage, clean rebuild, and CI drift check in place. Remaining: decide
   whether the site copy stays once mike versioning lands.
2. **MkDocs Material + mike migration**: versioned documentation
   (`https://docs.xiom-lang.org/vX.Y.Z/` plus a `latest` alias, frozen
   versions per release). Sources: `docs/language/` plus generated API
   pages. Keep old versions browsable; add redirects for the current
   `docs/html/*.html` paths so existing links keep working.
3. **Stdlib/compiler API pages**: `docs/build_api_docs.py` (done
   2026-09-17) walks a stdlib checkout, runs `xiom-doc` over every source
   and writes per-module MkDocs pages plus an index. Spike over the local
   stdlib at v0.60.0: 44 modules, 517 files, 6,879 symbols, 0 parse
   failures, ~8s. Remaining: run it in CI from the stdlib release tag and
   wire the output into the MkDocs nav; the release archive ships only
   `bin/xiom`, so CI must build `xiom-doc` from the xiom tag (a debug build
   of the dep graph takes seconds; `--locked`).
4. **Trigger**: the compiler release workflow fires a `repository_dispatch`
   at this repo; the docs job builds the versioned site and deploys through
   the VPS hook. Until that exists, the hourly pull keeps the current docs
   fresh.
5. **~~`versions.html` from the mirror~~ (done 2026-09-17)**: the current
   card and release table are read from
   `https://dl.xiom-lang.org/releases/index.json` (mirror retains 20 tags);
   pre-0.13 history has no artifacts and is no longer listed. Frozen docs
   links land with the mike migration.
6. **Link checking**: add a CI step that checks internal links and the
   documented external URLs (installers, mirror, releases). Current
   generator output has 8 known broken links per tree from stale sources
   (`../M10_SCRIPTING_MODE.md`, `../ecosystem/*.md` which the generator
   does not build, `../../checklists/stdlib-implementation.*`).

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

Priority: (1) scaffold the MkDocs Material + mike migration and wire in the
generated API pages (the API driver is done: `docs/build_api_docs.py`, 0
parse failures over 517 stdlib files); note the local machine only has
Python 3.7, so mkdocs/mike need a 3.8+ interpreter or a CI-verified setup.
The ops web-deploy.sh must stop publishing docs/html/ to the docs docroot
before versioned docs can go live. (2) Wire the API driver + docs build into
CI: repository_dispatch from the compiler release, `xiom-doc` built from the
xiom tag, mike deploy per version. (3) Ecosystem doc pointers stay deferred
until stdlib is 100%. Keep the site static, ASCII-only, and driven by the
mirror JSON files - never hardcode versions.
```
