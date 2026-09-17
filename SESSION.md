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

1. **Version pinning**: add `-Version <tag>` / `--version <tag>` to both
   installers so users can install a specific release (default: latest).
2. **Verification surfaced on the page**: show the expected SHA256 per
   archive (fetch `SHA256SUMS` next to `latest.json`) and the
   `gh attestation verify` command beside it.
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
`docs/html/` and a site copy. **Known issue after the monorepo split**: the
script still writes `website/docs` and reads `website/style.css`; the site
tree is now `xiom-website/`. Fix the paths and decide the canonical copy
(suggestion: `docs/html/` is canonical for the docs subdomain, and
`xiom-website/docs/` is a generated copy; or drop the site copy and make
`docs.html` link to `https://docs.xiom-lang.org`).

Queue:

1. **Fix and pin the generator**: correct the paths, run it in CI, and fail
   the build when generated output differs from the committed copy.
2. **MkDocs Material + mike migration**: versioned documentation
   (`https://docs.xiom-lang.org/vX.Y.Z/` plus a `latest` alias, frozen
   versions per release). Sources: `docs/language/` plus generated API
   pages. Keep old versions browsable; add redirects for the current
   `docs/html/*.html` paths so existing links keep working.
3. **Stdlib/compiler API pages**: generate them in CI by checking out
   `xiom-lang/xiom` and `xiom-lang/stdlib` at the release tag and running
   `xiom doc`; never hand-maintain API listings.
4. **Trigger**: the compiler release workflow fires a `repository_dispatch`
   at this repo; the docs job builds the versioned site and deploys through
   the VPS hook. Until that exists, the hourly pull keeps the current docs
   fresh.
5. **`versions.html`**: make the version history read
   `https://dl.xiom-lang.org/releases/index.json` (like the download page
   reads `latest.json`) instead of hardcoded rows; link each version to its
   release notes and its frozen docs URL once versioning lands.
6. **Link checking**: add a CI step that checks internal links and the
   documented external URLs (installers, mirror, releases).

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

Priority: (1) fix docs/build_docs.py for the split layout (website/ ->
xiom-website/) and make generation reproducible in CI; (2) add -Version
pinning and the checksum display to the installers and the download page;
(3) plan and start the MkDocs Material + mike migration with versioned docs
and redirects; (4) make versions.html read dl.xiom-lang.org/releases/index.json;
(5) add ecosystem doc pointers to stdlib and registry repos. Keep the site
static, ASCII-only, and driven by the mirror JSON files - never hardcode
versions.
```
