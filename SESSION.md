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
| https://docs.xiom-lang.org | `docs/html/` + `gh-pages` (mike) | generated documentation front-end |
| https://xiom-lang.org/docs/ | `docs.html` (redirect) | forwards to the canonical docs subdomain |
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
3. **~~macOS installer~~ (done 2026-09-19)**: `install.sh` handles Darwin
   x64/arm64 (asset naming, `shasum` checksum fallback, `xcode-select`
   check) and reports a clear message until macOS assets ship with
   `RELEASE_BUILD_MACOS`; the download-page rows still appear
   automatically. Installer follow-ups also landed: every `bin/xiom*`
   tool is symlinked into `~/.local/bin` (z3 stays in the install bin
   dir), one copy-paste activation line is printed, `XIOM_ADD_PATH=1`
   appends the PATH export to `~/.profile` idempotently, and the Windows
   installer lists every installed tool.
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
`docs/html/` (standalone bundle for releases; the site copy under
`xiom-website/docs/` was retired 2026-09-19 and `docs.html` redirects to
the docs subdomain). Fixed 2026-09-17: paths corrected for the
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

Ops round trip (2026-09-17): the org enforces
`sha_pinning_required=true`, so every `uses:` ref in `.github/workflows/`
must be a full commit SHA (pinned in 6ff5554; tag refs fail at job setup).
The first `docs-versioned` dispatch succeeded (run 35286233792) and
published `gh-pages`: `v0.60.1/` (full site plus legacy redirect stubs),
`latest` symlink, `versions.json`. The ops switch script
(`xiom-lang/ops`, `docs/DOCS_MIKE_SWITCH.md`) copies the default version's
stubs to the docroot root and symlinks its top-level dirs, so old `*.html`
URLs keep working with no website-side changes. `SUMMARY.md` is excluded
from the rendered site.

Docs staleness fix (2026-09-19, ops request): `docs-versioned` also
publishes on pushes touching `docs/**`, `mkdocs.yml`,
`requirements-docs.txt`, or the workflow itself, resolving the release tag
from `dl.xiom-lang.org/latest.json` when no dispatch version is present.
Guide edits republish the current version plus the `latest` alias; that
snapshot is refreshed from main sources until a release dispatch publishes
the next tag. Ops confirmed this semantics (2026-09-19): a version directory
is main-as-of-publish, not byte-frozen to its tag; push runs default
`stdlib_ref`/`compiler_ref` to main, so API pages may describe unreleased
compiler/stdlib state between releases ("latest docs track main"). If
byte-stable snapshots are ever required (e.g. at 1.0), the pattern is a
dedicated dev channel: push -> `dev`, release -> `vX.Y.Z` + `latest`.

Queue:

1. **~~Fix and pin the generator~~ (done 2026-09-17)**: paths, full nav
   coverage, clean rebuild, and CI drift check in place. Remaining: decide
   whether the site copy stays once mike versioning lands.
2. **~~MkDocs Material + mike migration~~ (done 2026-09-17)**: config,
   pinned toolchain, assembly script, strict build, legacy redirects,
   publish workflow, and the first successful publish to `gh-pages` are in
   place. Remaining: the ops session executes the docroot switch on the
   VPS (script ready at `xiom-lang/ops` `docs/DOCS_MIKE_SWITCH.md`); the
   generated site copy under `xiom-website/docs/` was retired 2026-09-19.
3. **Stdlib/compiler API pages (done 2026-09-17)**: `docs/build_api_docs.py`
   walks a stdlib checkout, runs `xiom-doc` over every source and writes
   per-module MkDocs pages plus an index. Spike over the local stdlib at
   v0.60.0: 44 modules, 517 files, 6,879 symbols, 0 parse failures, ~8s.
   Wired into `docs/build_mkdocs.py`; `docs-versioned.yml` builds
   `xiom-doc` from the xiom ref (`--locked`) before assembling. The first
   CI dispatch published 45 API pages and validated the cross-repo build.
4. **Trigger**: `docs-versioned.yml` accepts
   `repository_dispatch: compiler-release` (payload `tag`, optional
   `stdlib_ref`/`compiler_ref`) and manual dispatch. Remaining: the
   compiler release workflow (compiler lane) must fire the event.
   Related cross-lane blocker reported by ops: the `xiom-lang/stdlib`
   workflows still use tag refs and will fail under
   `sha_pinning_required=true`; that is the stdlib lane's to fix (pinned
   SHAs for checkout, upload-artifact, rust-toolchain, and cache were
   handed over in the ops report).
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
7. **Docs dev channel (rejected 2026-09-18, pattern reserved for later)**:
   ops asked to keep publishing on the release dispatch at beta, so a draft
   `docs-dev.yml` was removed before commit. If byte-stable version
   snapshots become a requirement (e.g. at 1.0), the reserved pattern is a
   `dev` channel: push -> `dev`, release -> `vX.Y.Z` + `latest`.
8. **Guide content refresh**: version-specific claims were removed from
   `index.md` and `compiler.md` (2026-09-18). A full refresh of compiler
   details (flags, gates, test counts) needs canonical numbers from the
   compiler lane; do not invent numbers.
9. **Site polish (done 2026-09-18)**: canonical, Open Graph and Twitter
   metadata on the five main pages, plus `robots.txt` and `sitemap.xml`.
   `xiom-landing.html` was archived to `specs/xiom-landing-mockup.html`;
   `docs/ecosystem/*.md` stay as drafts; `docs/error_codes/*.md` stay
   unpublished (see the audit follow-ups below).

## Website audit follow-ups (2026-09-18)

Owner decisions:
- Copyright holder is XIOM Foundation (overrides the personal-holder
  recommendation in `specs/XIOM_Website_Content_Spec.md` Part 1/2); code is
  MIT OR Apache-2.0. The Godot third-party notice in that spec does not
  apply.
- No self-hosting claims: gates are cleared, but no self-hosted release has
  shipped. Likewise no test counts or codebase stats on the site.
- The standard library is beta; the site and docs link
  `STDLIB_BETA_LIMITATIONS.md` in the stdlib repository.
- The release tag (mirror `latest.json`) is the version source; the binary
  `--version` string is known to lag and is not used on the site.
- Author/byline link: https://github.com/Lefteris-Notas.

Done (2026-09-18): site honesty pass; license files served and legal
footer block on every page; docs footer and MkDocs copyright; UI rebrand to
the playground palette (indigo `#5C6BFF` on `#08090B`, radii 8/10/16, glow
accents, refreshed syntax palette, system fonts with Google Fonts removed);
accessibility (skip link, `:focus-visible`, reduced motion); Material
themed through `docs/mkdocs-brand.css` with `font: false`; Why and Roadmap
pages built from the specs and added to every nav plus the sitemap; beta
banner injected on the hand-written stdlib pages; landing mockup archived
to `specs/xiom-landing-mockup.html` (unpublished); docs search enabled
(the explicit plugins block had overridden the default search plugin);
stdlib `///` doc comments merged into the generated API pages; mobile
pass on the site (scrollable nav links row, stacked split sections,
scrollable tables) and Material verified at 390px; docs header carries the
site logo, favicon and a xiom-lang.org back-link; API pages render stdlib
`///` prose where present (coverage 83.2% after the stdlib prose pass,
paragraphs and lists preserved) and generated signature summaries
otherwise; the compiler guide gained Architecture and Modes sections; the
homepage was restructured for every audience -- a hero strip (getting
started / playground / spec / contracts / GitHub), five plain-language
feature stories (scripting, AI, proof, safety, targets) with runnable
examples, an "Also in the box" toolchain inventory, and a "Built in the
open" community section with source, issues and roadmap links. The live
package registry (registry.xiom-lang.org, read-only UI plus public JSON) is
now on the ecosystem page, and the docs gained a Package Registry guide
covering install, locking, trust, yank and troubleshooting. The ecosystem
page was reframed as a plan (status table, porting plan, direction
categories) with no unfinished packages or product names, and Registry
joined the top navigation on every page. Brand illustrations are wired in:
five story chips on the homepage, three pillar icons on the Why page, and
`og-card.png` (1200x630) as the social preview everywhere; the footer legal
block is split into three short lines, docs code is 13px, and the card grids
use proper gaps and bordered panels. The docs table of contents was tamed:
API declarations are H4 (anchors kept) with `toc_depth: 3`, so the TOC lists
file sections only while guides keep their subsections, and the sidebar got
compact styling. The social card is now also visible in the homepage CTA,
the footer carries a social row (GitHub plus support@xiom-lang.org until the
X/Facebook/Instagram/Discord/Reddit links land), and API module pages got
their own styling (file-section dividers, readable declaration rows, flat
doc prose, anchor scroll margins). Terms of Use and Privacy Policy pages
were added (terms.html, privacy.html) and linked from every footer,
including the generated docs chrome. Docs reading comfort pass: lifted dark
surfaces (#0E1014 background, #DDE1E8 text) and softened light mode
(#F7F8FA / #2A2E37), all AA; API declarations separated by hairline rows
with calmer signature sizing; on large screens the grid widens to 64rem
and the rails slim to 11rem so the content column gains ~15%.

Remaining:
1. **~~AI_CONTEXT metadata~~ (done 2026-09-18)**: refreshed to the compiler
   lane's verified block (v0.61.0, 517 source files, 6,532 pub fns, gate
   counts, and the new v0.59-v0.61 line). Note: the file is stamped
   v0.61.0, so it reads ahead of the released v0.60.1 docs until the next
   release publish.
2. Header sweep (optional): source headers still read "Eleftherios Notas
   and XIOM Foundation" while LICENSE and footers say "XIOM Foundation";
   both name the Foundation, so this is cosmetic.
3. Optional: self-host Inter (current stack is system-native by design).
4. `docs/error_codes/*` stays unpublished for now -- the index is
   incomplete (one README plus X0010/X0011/X0100). Revisit when the
   compiler lane owns error-code docs.
5. ~~`xiom-website/docs/` site copy~~ (retired 2026-09-19): `docs.html`
   redirects to the canonical `https://docs.xiom-lang.org/`, the generator
   no longer produces the site copy, and a single redirect stub at
   `xiom-website/docs/index.html` keeps `/docs/` working.
6. **~~Compiler review~~ (done 2026-09-18)**: the compiler lane verified the
   new Modes/Architecture content against source (main v0.61.0) -- all
   three flags are real, the 20-crate list is confirmed, and the
   v0.57/v0.58 feature rows are accurate. The compiler now prints
   `--keep-debug-checks` in `xiom --help` (003e1fde).
7. **Playground backup disclosure (pending ops, 2026-09-19)**: the
   playground-data volume is not yet in the restic set, so `privacy.html`
   currently says the progress document "is not currently part of the
   off-site backup set". When ops adds it
   (`/var/lib/docker/volumes/playground_playground-data/_data` in
   `scripts/restic-backup.sh`) and the playground session confirms,
   replace that clause with: "nightly backups age out after 30 days, with
   12 monthly snapshots kept." The playground session keeps a facts list in
   its `DEPLOY.md` and will flag changes to sandbox flags, retention,
   cookie lifetime or backups.
8. **External review follow-ups (2026-09-19)**: applied the honesty and UX
   fixes from review round one (hero example, badge wording, prior art, Rust
   trade-off, ordering, alt text, CTAs, module counts) and round two
   (removed "specification and implementation are the same artifact", the
   1972 claim, "no runtime", "compiler is the verifier", "same safety
   guarantee as Rust", "not a scripting replacement", absolute
   "one way to write each thing" and "no hidden allocations"; repositioned
   the Why page around intent -> enforcement -> AI; the spec page is now
   labelled Revision 0.3 for the core language with implementation docs
   separate and the comparison table removed). Still open: publish a
   current specification revision (compiler lane); publish benchmark
   results with the harness -- the benchmark lives in its own repository and
   includes a research paper, both private for now; the owner will say when
   to link and showcase them; verify-tooling semantics (bundled z3 vs
   export-only) is with the compiler lane; a prior-art and trade-offs
   page; a "XIOM for game developers" page; C# on the concepts page;
   playground copy fixes ("Never Crash", stats bar); the legal-entity
   wording is an owner decision.

## Rules

- Pure ASCII files only; the org encoding gate rejects mojibake.
- Never hardcode versions in pages; read `latest.json` / `index.json`.
- No secrets, no environment-specific URLs beyond `xiom-lang.org` and
  `dl.xiom-lang.org`.
- Test installer changes end to end (Windows locally, Linux in a container)
  before pushing; they are the first thing users run.
- Nav consistency: use `https://playground.xiom-lang.org` (absolute) or a
  deliberate relative path in every page, not a mix.
- All GitHub Actions refs must be pinned to full commit SHAs; the
  xiom-lang org enforces `sha_pinning_required=true` and tag refs fail at
  job setup.
- Commit identity: set the repo-local `user.name` / `user.email` to
  `Lefteris Notas <lefterisnotas@gmail.com>` before the first commit and
  verify with `git log -1 --format='%an <%ae>'` before every push; never
  use the global work identity or `--author`. Rewriting pushed history
  happens only on the owner's explicit request. The owner-authorized
  rewrite completed on 2026-09-18 (main and tags rewritten; the gh-pages
  bot commits were preserved) - existing clones must be re-cloned, not
  pulled.
- `docs/html/` is generated; do not hand-edit.

## Paste-ready prompt for the next session

```
Work in E:\xiom-lang\website (website lane) for the XIOM project. Read
SESSION.md (this file) and DEPLOY.md before acting. Deploys are pull-based
from this repo to the VPS via /opt/xiom/bin/web-deploy.sh (cron minute 23);
push to main and it publishes within the hour, or run the script on the VPS
with the owner in PuTTY (outputs pasted back; never request credentials).

Priority: (1) ops session executes the docs docroot switch on the VPS
(script ready, `xiom-lang/ops` `docs/DOCS_MIKE_SWITCH.md`) and verifies
`/`, `/latest/`, `/v0.60.1/`, `versions.json`, a legacy stub such as
`/syntax.html`, and `/api/core/`; (2) compiler release workflow fires
`repository_dispatch: compiler-release` with the tag so publishes are
automatic; (3) stdlib lane pins its workflow action refs (blocker reported
by ops); (4) macOS installer support once `RELEASE_BUILD_MACOS=true`;
(5) ecosystem doc pointers stay deferred until stdlib is 100%. Keep the
site static, ASCII-only, and driven by the mirror JSON files - never
hardcode versions.
```
