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
  - 2026-09-21: superseded -- the XIOM Foundation is not yet a legal entity;
    the copyright holder is Eleftherios Notas and The XIOM Authors until it
    is formed (policy: `xiom-lang/.github` `docs/LICENSING.md` section 8).
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
`og-card.png` (1200x630) as the social preview everywhere (replaced by `og-card.webp` 2026-09-25, item 29); the footer legal
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
2. ~~Header sweep~~ (done 2026-09-21): every notice now reads
   `Copyright (c) 2026 Eleftherios Notas and The XIOM Authors`; the
   Foundation is no longer named anywhere as holder (policy:
   `xiom-lang/.github` `docs/LICENSING.md` section 8).
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
   separate and the comparison table removed). Verification wording is
   settled (compiler lane, 2026-09-19): checked/exported/proved documented
   in `compiler.md`, `--verify` exports, `xiom-verify --check` runs the
   bundled z3, unsat is the only proof verdict.
9. **Prior art and trade-offs (done 2026-09-21)**: `prior-art.html` covers
   the Design by Contract lineage (Eiffel, Ada 2012/SPARK, Dafny, Frama-C),
   Rust's lifetime system vs XIOM second-class references, and the runtime
   contract cost model without invented numbers. It is explicitly
   non-normative; spec section 8, the Why page and the homepage why-section
   point at it, and the sitemap lists it. Concepts and memory-model wording
   was aligned in the same pass (no "same safety as Rust", contracts are not
   unique to XIOM) and C# rows were added to the Concepts page (intro, null,
   async `Task`, `IDisposable` mapping). Still open: a "XIOM for game
   developers" page (waiting on owner engine facts); publish benchmark
   results with the harness -- the benchmark and its research paper live in
   a private repository and the owner will say when to link and showcase
   them; publish a current specification revision (compiler lane);
   playground copy fixes ("Never Crash", stats bar) belong to the playground
   lane; the legal-entity wording is an owner decision.
10. **XIOM snippet syntax lint (done 2026-09-21)**: `docs/check_syntax.py`
    lints ```xiom fenced blocks in the guides and `AI_CONTEXT.md` plus the
    code blocks in the site pages for contract colons, `use` semicolons and
    square-bracket generics (turbofish flagged separately); wired into
    `docs.yml` and into the publish gate in `docs-versioned.yml`. The first
    run found and fixed drift in `modules.md`,
    `stdlib/crypto.md`, `stdlib/serialize.md` and `AI_CONTEXT.md`
    (`Result<KeyPair, Str>`, `Vec<JsonValue>`, turbofish intrinsics).
11. **UI/UX and docs-content pass (done 2026-09-21)**: footer rebuilt as a
    brand block plus Language/Explore/Project link columns over a legal bar
    on every site page and in the generated docs template; Prior art was
    added to the top nav (with a mid-width gap rule) and History to the
    footer everywhere. `history.html` narrates the project evolution
    (v0.1.0/v0.2.0 pipeline and full surface, v0.22-v0.33 hardening,
    v0.50.0 first release, v0.52+ cadence, v0.56-v0.61, self-hosting
    status) from the compiler repo records and links to Roadmap/Versions.
    Code blocks got framed panels, a language badge, scroll styling and
    the missing `.func` token color; `build_docs.py` now HTML-escapes code
    blocks and inline code (raw `<` used to swallow comparison operators
    and `<T>` generics in generated pages) and protects code spans from
    the bold/italic rules. Version teaching was removed from user docs:
    AI_CONTEXT "New in vX" banners and inline version tags, the
    `compiler.md` "Since" column, and the `index.md` milestones table now
    point at History/Versions. MkDocs code chrome restyled; mobile pass on
    nav, footer and code sizing.
12. **Syntax audit against the compiler (done 2026-09-21)**: every documented
    construct was type-checked with the local compiler build (v0.61.0,
    `--check`, 80+ probes). Verified and now documented: labeled loops
    (`@label:`, `break @label;`), `loop`, compound assignment, `defer`,
    `const` declarations and blocks, `unsafe`/`asm` rules, `while let`,
    `is` tests, `@pre`, never type, `as` casts, `Float128`
    conversion-only, and 128-bit integer literals. Corrections landed:
    `if let` is NOT implemented (guides and AI_CONTEXT now say so and show
    `match` / `if value is Variant`), there is no range expression, the
    `Byte` alias is not accepted by the compiler (use `UInt8`), `\u{...}`
    is a string-only escape (`'\u{1F600}'` is a lexer error), statements
    require semicolons (AI_CONTEXT 2.1 examples fixed), match arms
    canonically end with `,` (block arms need no separator), and turbofish
    compiles but is not canonical. `check_syntax.py` gained rules for
    `if let` and the `Byte` type name, and its turbofish message now says
    "accepted but not canonical". Compiler-lane discrepancies to report:
    the spec's `Byte` alias is not implemented, and `if let` appears in the
    spec/older material only.
13. **Unsafe guide and Contributing hub (done 2026-09-21)**: a dedicated
    `docs/language/unsafe.md` now documents the confinement model end to end
    (block rule, extern and signature gates, pre-entry contracts, guard heap,
    stack guard, fault trap with codes, once-only retry, zero-escape rules,
    FFI ownership, `#[unsafe_no_retry]` / `#[unsafe_direct]`, the safe C
    wrapper pattern, and `--sandbox` auditing); it is wired into both docs
    navs and linked from the memory model. The site also gained
    `contributing.html` plus a docs mirror (`docs/language/contributing.md`):
    pre-beta status, links to the .github policy sources (CONTRIBUTING,
    LICENSING, DCO, GOVERNANCE, CODE_OF_CONDUCT, SUPPORT, SECURITY), the
    fork-to-PR path, signed-off commit examples and the repository map.
    Contributing is in the top nav and the footer Project column on every
    page, the landing "Start contributing" card points at it, and the
    sitemap lists it. Commit `-s` sign-off is now used.
14. **Social links (done 2026-09-21)**: eight inline SVG icons (Simple Icons,
    CC0) in the footer brand column of every page and in the generated docs
    template: Discord (community, open invite), X, Mastodon (rel=me so the
    profile can verify), Bluesky, Reddit, Hacker News, LinkedIn, Facebook.
    The order is community, then updates, then discussion, then professional
    and broad reach. Every link has an aria-label and title, opens in a new
    tab with rel=noopener, and `.footer-social` wraps on mobile. The icons
    are inline (no webfont, no external request); each anchor stays on one
    line so the markup compresses well.
15. **Publishing assets (done 2026-09-21, revised after review)**:
    `docs/wikipedia-draft.md` is now an internal planning and fact sheet, NOT
    article text: it states that Wikipedia prohibits LLM-generated content
    (WP:LLM plus the speedy-deletion criterion), records the reviewer's
    round-1 blockers (notability, COI, AI text) and fixes (infobox `released`
    not `first appeared`, one consistent date story, the corrected Z3 nuance
    -- runtime guards shipped, `--verify` export plus `xiom-verify --check`
    with bundled z3, automatic static proof still planned), and carries a
    verified fact/source table where every URL returned 200 on 2026-09-21.
    The earlier paste-ready wikitext was removed so it cannot be submitted.
    `docs/marketplace-publisher.md` holds the marketplace copy: vendor name,
    tagline, 193-character short description, ~70-word About, keywords, links
    and the legal line. Neither file is part of the site.
16. **MkDocs syntax highlighting (done 2026-09-21)**: `docs/xiom_lexer.py` is
    a Pygments regex lexer for XIOM (keywords, contract clauses, built-in
    types, function names, strings, comments, numbers, labels, attributes).
    `docs/mkdocs_hooks.py` registers it in `pygments.lexers._mapping.LEXERS`
    during `on_config`, and `mkdocs.yml` loads `hooks: [docs/mkdocs_hooks.py]`,
    so ```xiom fences on docs.xiom-lang.org are highlighted instead of
    rendering as plain text. Token colours are aligned with the standalone
    docs palette through `--md-code-hl-*` overrides in `docs/mkdocs-brand.css`
    (light and slate). Tests: `python docs/xiom_lexer.py` self-test; the hook
    registration was verified against Pygments 2.14 locally and the lookup
    code is unchanged in Pygments 2.19.2 (checked from the wheel source).
17. **Install path and AI setup docs (done 2026-09-21)**: `getting-started.md`
    was stale (monorepo tree, `XIOM-lang/XIOM` clone URL, "1041 tests", VS Code
    extension planned, playground on the wrong host). It now documents the
    multi-repo layout, the release installer for Windows/Linux/macOS with
    beginner notes (where it installs, PATH behaviour, pinning, uninstall),
    LLVM/Clang required plus NASM recommended and Z3 bundled with the verifier,
    build-from-source with `scripts/fetch-stdlib`, the editor story
    (xiom-lsp/xiom-dbg in recent archives, editors/README.md matrix, VS Code
    listing pending), and a full `--ai` setup section: config file search order
    (project, `$XIOM_HOME`, home), JSON fields, env vars, how to change the key,
    and security notes. `compiler.md` gained the same config details and the
    MCP registry tools. The website `download.html` Requirements section now
    lists NASM (recommended) and the Z3 bundling, the One-Line Install block
    covers macOS and explains what the installer changes, and a new
    "AI-assisted errors (--ai)" section shows the key file; the index AI
    paragraph links to the setup guide.
18. **Debugger guide (done 2026-09-21)**: the guides only mentioned `xiom-dbg`
    in passing, so `docs/language/debugger.md` now covers it: `-g` compile,
    the debug intrinsics and their release stripping, DAP client wiring
    (VS Code launch config, Neovim `nvim-dap`, Emacs `dape`, editors/README.md
    matrix), the `xiom-dbg --json` command set, raw GDB usage,
    breakpoints/stepping/inspection, contract traps, and the honest limits
    (no conditional or hit-count breakpoints, no logpoints, the JSON API has
    no pause, the CDB backend is basic). Verified locally: the guide snippet
    type-checks and `xiom dbg --version` dispatches to `xiom-dbg v0.61.0`.
    Wired into both docs navs and the guide index, linked from `compiler.md`
    and `getting-started.md`.
19. **Error-code reference published and corrected (done 2026-09-21)**: the
    compiler emits `L001` (lexer), `P001` (parser), `T001` (type checker),
    `E001` (borrow checker), `C001` (codegen), `W000` (checker warnings) and
    `W001` (catalog collisions); `--diagnostics=json` carries the code, and
    `xiom --explain <code>` prints `docs/error_codes/{code}.md` from the
    current directory. The old index listed an X family that the compiler does
    not emit, so the reference was rewritten: new pages for all seven emitted
    codes with verified examples (probed against v0.61.0), the X pages kept
    with a "reserved, not emitted" banner, and README/index and `--explain`
    examples updated. Both builders render `docs/error_codes/*.md`
    (standalone `docs/html/error_codes/` with a sidebar section, MkDocs
    `error-codes/` with a nav section); the syntax lint scans them too.
20. **Docs honesty softens from the probes (done 2026-09-21)**: the probes
    showed that non-exhaustive `match` is not rejected (T001 passes) and that
    returning a borrow is `warning[E001]` during compilation, not a hard
    error. `syntax.md`, `pattern-matching.md`, `memory-model.md` and
    `AI_CONTEXT.md` now state the rule, the current behaviour and the E001/W000
    codes instead of claiming the compiler enforces them.
21. **Trusted-base boundary documented (done 2026-09-22)**: the contracts page
    now carries the reviewer's requested "Verification Scope and the Trusted
    Base" section -- the verifier reasons about contracts, not implementations;
    stdlib `ensures` clauses are assumptions; the assembly-accelerated hot
    paths (crypto, bulk memory, context switching) sit inside the trusted base;
    accelerated/portable equivalence is a testing property, not a proof. The
    Verification Modes table was rewritten to the settled wording (runtime
    guards by default, `--verify` export, `xiom-verify --check` with the bundled
    z3, only `unsat` proves) and the AI section no longer claims compile-time
    enforcement. `unsafe.md` gained "Runtime Assembly Is Not User Unsafe"; the
    NASM prerequisite no longer claims an equivalent C fallback. Follow-up
    (2026-09-22): `compiler.md` gained a "Native Toolchain" table (clang
    required; opt and nasm optional; `XIOM_NO_ASM` when NASM is absent), and
    the stdlib API intros (`api.md`, `stdlib.md`) now state the verification
    scope and link the contracts guide, so "nasm"/"assembly" searches land on
    the boundary instead of only the prerequisite list.
22. **Broken external links fixed (done 2026-09-22)**: the standalone docs
    builder rewrote `.md` to `.html` inside absolute URLs, so every GitHub blob
    link in the generated pages 404ed (CONTRIBUTING, LICENSING, GOVERNANCE,
    SECURITY, SUPPORT, CODE_OF_CONDUCT, editors/README, stdlib limitations);
    `link_repl` now skips URLs with a scheme. The download page's pre-JS
    fallbacks point at the GitHub release instead of the mirror directory
    (403). A 65-URL external scan is clean except reserved/blocked hosts
    (example.com placeholder, api.deepseek.com 401, LinkedIn bot 999, a
    `https://...` in a code comment).
23. **Compiler-lane docs rendered (done 2026-09-22)**: the docs site now
    publishes the compiler repo's canonical `AI_CONTEXT.md` as "Toolchain
    Context" and `docs/POST_RELEASE_PLAN.md` as "Post-release Plan" under a
    Project nav section, staged at build time from the compiler checkout
    (`--toolchain-context`, `--post-release-plan`; docs-versioned passes
    `.deps/xiom/...`), so the site describes the same toolchain the archives
    carry. `compiler.md` gained a 16-tool MCP table (names and one-liners from
    `crates/xiom-mcp`) plus pointers to both pages and the updater note. The
    contracts "Contradictory = compile error" row was removed after probing:
    contradictory `requires` and impossible invariants compile today.
24. **Docs design pass (done 2026-09-22)**: MkDocs type scale unified so
    guides and generated API pages share heading, table, code and list sizes
    (removed three different heading-code sizes and the unscoped H4 rules;
    API refinements now scope to `:has(h4)`, which guides never match).
    Contrast measured with WCAG ratios and fixed in both schemes: dark code
    background lifted to #1A1E26 (chips/blocks now distinguishable from the
    page), dark comments #7A7F8C -> #A6ADBC (4.2:1 -> 7.4:1); light tokens
    were actually below AA on the code background (constant 3.7:1, keyword
    4.2:1, comment 4.2:1) and now use #3F4BD1/#00695C/#9A5B00/#256B2A/#6A4FBF/
    #555C6B (4.7-5.8:1). The standalone docs palette mirrors the dark comment
    change (#A6ADBC on #111217, 8:1).
25. **Module count and archive contents verified (done 2026-09-22)**: the
    canonical count is **44 top-level stdlib modules** -- confirmed by the
    GitHub API for `xiom-lang/stdlib` `xiom/` on main and by the local
    checkout; the generated API builds 44 module pages plus an index, and the
    517 `.xi` files are the submodule sources. The number "60" that circulates
    in stdlib docs (`VERIFICATION_BASELINE.md`, `stdlib_session.md`) is a
    probe-scan namespace count, not the module list. Fixed the one stale
    claim (`index.md` said 40). The v0.61.1 Windows archive was downloaded and
    inspected: `bin/` contains xiom, xiom-dbg, xiom-doc, xiom-ffigen, xiom-fmt,
    xiom-lsp, xiom-mcp, xiom-pkg, xiom-verify, z3 plus the VC runtime DLLs --
    so the homepage "Companion tools" box now lists the MCP server and the
    pinned z3 too.
26. **Release notes ("What's new") system shipped (done 2026-09-24)**: the
    contract is `docs/release-notes-schema.md` (schema v1): one immutable
    `release.json` per tag, authored from a strict markdown template,
    converted and validated at release time, published to
    `dl.xiom-lang.org/releases/<tag>/release.json` and committed as
    `release-notes/<tag>.json` before the tag (raw GitHub fallback). The site
    side is complete: `js/release-notes.js` (validates, fetches mirror then
    tag-pinned raw, renders with textContent only, 10-minute cache for hits
    and 60-second cache for misses), a "What's new" panel on `download.html`
    for the current release, a three-highlight summary on the current-release
    card in `versions.html`, and a lazy per-row disclosure on older rows with
    `aria-expanded`; when no valid document exists the pages show only the
    changelog link. Tested with 20 module tests plus DOM-level integration
    tests for both pages (mirror hit, raw fallback, invalid documents, cached
    misses, row expansion, graceful missing-notes state). Relays for the
    compiler, stdlib and registry lanes are in the paste-ready section
    below.
27. **Installer resilience and current-release accuracy (done 2026-09-24)**:
    the mirror still reported v0.60.1 while GitHub was at v0.61.3, so
    `install.ps1` installed the old release. Both installers and both release
    pages now consult the mirror and the GitHub releases API and use the
    newer release (pages cache the API lookup ten minutes); the PowerShell
    installer also stopped aborting after a successful install when
    `xiom-pkg --version` wrote to stderr. Verified end to end: the installer
    downloads v0.61.3, checksum verifies, all nine tools report, and the
    installed compiler runs. macOS copy updated everywhere (archives ship for
    Intel and Apple Silicon; the "not published yet" caveats and the
    roadmap's "macOS in progress" line are gone).
28. **Live deploy verified, checksum copy corrected (done 2026-09-24)**: after
    the 16:23 UTC cron pull, every live file fetched was byte-identical to
    HEAD (index/download/versions pages, `install.ps1`, `install.sh`,
    `style.css`, `js/release-notes.js`). `irm
    https://xiom-lang.org/install.ps1 | iex` printed "Mirror reports v0.60.1;
    GitHub has v0.61.3 -- using GitHub.", checksum-verified the 21.32 MB
    Windows archive and installed the nine tools at v0.61.3. Headless Chrome
    rendered download.html with all four platform rows and versions.html with
    the three GitHub releases (v0.61.3, v0.61.1, v0.60.1), v0.61.3 current,
    and the "what's new" toggle showing "No release notes published for this
    version" (right: the tag predates the notes system). Finding: the SHA256
    column cannot fill in browsers because neither GitHub release assets nor
    the mirror send `Access-Control-Allow-Origin`, so it shows "see
    SHA256SUMS"; the two download.html sentences that claimed the column is
    always filled now describe the fallback (`d25d652`). The column fills for
    real if the mirror serves `SHA256SUMS` with ACAO or the compiler lane
    commits a tag-pinned checksums file (raw.githubusercontent sends ACAO
    `*`); neither exists today.
29. **Owner webp art refresh, og-card switched to webp (done 2026-09-25)**:
    the three pillar icons, the five story chips and the social card were
    replaced with the owner's higher-quality webp files (the generated ones
    were too soft). All nine webps are valid VP8 and match their PNG sources'
    dimensions (icons 355-380 x 343-345, story chips 356-395 x 310-357,
    og-card 1200x630), so the HTML width/height hints stay correct. All twelve
    `og:image` meta tags and the homepage CTA banner now use `og-card.webp`;
    `og-card.jpg` was removed (`1f61a88`, `b762899`).
30. **Ecosystem status pass and benchmark move (done 2026-09-25)**: the
    roadmap gained an Ecosystem section with verified statuses -- Registry
    1.0 live (publish, install, search, sha256 checks, ed25519 signatures
    and provenance), editor tooling live (the VS Code extension is on the VS
    Code Marketplace and Open VSX; `release.yml` publishes new extension
    versions to both and skips toolchain-only releases), playground live,
    and Registry 2.0 recorded as a direction at the time (superseded
    2026-09-26: 2.0 is live -- item 32). The live package count is
    read at page load from `registry.xiom-lang.org/index.json` through
    `js/registry-count.js` (ACAO `*`; installable = entries with a non-empty
    `latest`; 37 of 38 today, the yanked probe excluded) on both the roadmap
    and ecosystem pages, with authored fallback text in the markup. The
    stale "mirror is v0.60.1; v0.61.0 on main" rows are gone from both
    pages. The "AI benchmark" card was removed from the homepage and became
    the "Reproducible evidence (in preparation)" section on the roadmap
    (`roadmap.html#benchmark`); no results are claimed.
31. **Docs refresh automation (done 2026-09-25)**: `docs-versioned.yml` now
    resolves the current tag from the GitHub releases API with a mirror
    fallback for runs without a dispatch version, and carries a weekly
    schedule (Monday 04:00 UTC) that republishes the current release from
    main -- so stdlib/compiler drift shows up at least weekly without the
    release dispatch. The first run is the push that lands this change
    (workflow-file changes trigger the push path); it publishes v0.61.3 +
    latest from main instead of the stale mirror's v0.60.1. Release dispatch
    stays the release-accurate path once `XIOM_RELEASE_TOKEN` covers this
    repo (owner action, relay above). DEPLOY.md documents the trigger set.
32. **Registry 2.0 launched and reflected on the site (done 2026-09-26)**:
    production serves registry 2.0.0 (protocol 1.0.0) with 113 entries / 112
    installable. Verified live: `/login` 200 with GitHub sign-in ("request a
    publish token"), `/auth/github/start` 302, `/account`, `/review` and
    `/admin/requests` auth-gated, `/whats-new` renders the changelog,
    package pages render the README and a Reviews section, `/index.json`
    shape unchanged. The roadmap Ecosystem table now shows Registry 1.0
    (shipped protocol foundation) and Registry 2.0 (live: sign-in
    identity-only, self-service token/trusted-publisher requests with
    operator approval, reviews, READMEs, what's-new); the ecosystem page
    drops the "read-only UI" and "not scheduled" wording; the registry guide
    gains "Publishing and accounts" and README/reviews in Browse. Count
    labels became "Installable packages in the registry" (live count, 112
    today). `docs/html` regenerated; checks clean.
33. **MCP client setup in Getting Started (done 2026-09-26)**: the guide now
    documents the shipped `xiom-mcp` stdio server client-by-client -- Claude
    Code (`claude mcp add`, `.mcp.json`), Cursor (`.cursor/mcp.json`), VS
    Code (`.vscode/mcp.json` `servers`), Codex CLI (`config.toml`
    `[mcp_servers.xiom]`), Kilo (`kilo.json` `mcp` with `type: local`), plus
    the portable `mcpServers` block and the Windows absolute-path fallback.
    Formats verified against the clients' current documentation on
    2026-09-26; the compiler page links to the section (`ebf9c33`; the docs
    run published it to gh-pages). The client named as "gravity" in the
    request could not be matched against current docs; unlisted clients use
    the portable block.
34. **Owner webp banner refresh, higher resolution (done 2026-09-26)**: the
    referenced banners prior-art, roadmap, spec, why (2172x724) and ecosystem
    (2171x724) were replaced, plus the unreferenced playground and registry
    (2172x724); all were 1539x510 before, and every referenced banner got a
    matching size hint (`9a78059`, `f22e5af`). Dimensions verified; checks
    clean; `contributing.webp` is the only banner still at 1539x510. Note:
    `playground.webp` and `registry.webp` have no references anywhere in the
    repo (checked with `git grep`); they are kept for future use.
35. **Privacy page synced to the playground P2 cutover (done 2026-09-26)**:
    relay from the playground lane; the accounts paragraph now mirrors
    playground DEPLOY.md's "User data and privacy facts": one JSON progress
    document per account stored by the host-side playground service on the
    host (access-controlled, mode 0600, atomic writes) with no copy in the
    web container, and the backup sentence points at the host state directory
    plus the pre-cutover Docker volume retained only for the rollback window
    (`7ac30eb`). The DEPLOY list is authoritative; its future-tense
    nightly-backup wording stays pending until ops confirms the first restic
    snapshot and a restore drill.
36. **Ecosystem category statuses corrected (done 2026-09-26)**: the registry
    index now serves 250 entries / 249 installable, so the eight category
    cards no longer read "planned": seven are "shipping" with texts stating
    what is live (serialization/data formats, protocol codecs, model/tensor
    formats, domain formats, image/audio/video, system formats and dev tools,
    property/fuzz/SMT-LIB) and what is next; Interoperability and bridges
    stays "planned" because no FFI or binding package exists yet. The
    first-party table row reads "shipping", the plan list is present tense,
    and `eco-tag.shipping` reuses the verified accent (`7174924`; generated
    docs/html/style.css refreshed).
37. **Ecosystem growth-cycle section and packages-lane relay (done
    2026-09-27)**: `ecosystem.html` gained "How the ecosystem grows" (a
    receive/give-back table for compiler, stdlib, packages and registry; the
    publish-gate guarantee; two live loop examples -- reproducible compiler
    findings filed by package suites, CRC and bit-reading helpers tracked as
    stdlib work) and "What comes next" replaced "The plan". One
    owner-approved line states AI-assisted porting under review. A
    paste-ready relay for the packages lane (public README landing) is in
    the lane-prompts section (`c87a484`); the section image is planned from
    the owner.
38. **Growth-cycle diagram integrated; packages README landed (done
    2026-09-27)**: `img/eco_growth_cycle.webp` (1145x1374, owner-supplied)
    now sits in "How the ecosystem grows" as a two-column layout -- figure
    left (480px) beside the receive/give-back table, stacking at 860px, with
    descriptive alt text, a caption and a click-to-open-full-size link; the
    `.growth-*` styles are in style.css and the docs/html copy is refreshed
    (`f4e1743`; verified with desktop and mobile screenshots). The packages
    lane landed the public README (`776e369`) with the approved framing,
    closing the relay; their SESSION.md says framing changes go back through
    this lane.
39. **Growth-diagram lightbox and mobile audit (done 2026-09-27)**: the
    diagram opens in an in-page modal now (`js/lightbox.js`; `data-lightbox`
    links) instead of a new tab -- Escape, the Close button and a
    click-outside all close it, focus returns to the link, background scroll
    locks; without JavaScript the link still opens the file in the same tab.
    Verified with CDP device emulation at a true 414x900 viewport (image
    397x477, Close fully inside the frame) and at desktop size. Audit of all
    seven hero/banner pages (index, contributing, ecosystem, prior-art,
    roadmap, spec, why) at 414px: `scrollWidth == innerWidth` everywhere (no
    horizontal overflow); banners render 414x138 with the title block inside
    the artwork's open area; the index hero is 414x511 with full-width CTAs
    (`d7bb744`). Test wrappers removed after the audit; no page code beyond
    the lightbox changed.
40. **Scripting guide, verified examples, and the example audit (done
    2026-09-27)**: `docs/language/scripting.md` published with examples
    type-checked 9/9 and run end to end on Linux: hello, itos values,
    while-sum, files, environment/exit and spawn verified green; `run
    --watch` re-runs on change; the shebang form is `#!/usr/bin/env -S xiom
    run` (plain `env xiom` parses in program mode and fails). Findings
    relayed to the compiler lane (below): for-in over array literals fails
    LLVM codegen; `xiom run` passes no script arguments; piped stdin crashes
    on Linux; `io.println(<Int>)` is T001 (reference loop examples fixed
    with `itos`); `xiom build` without a manifest errors oddly; the help's
    launcher note is stale. The guide marks the first three as known
    limitations. Correction recorded: the earlier `run` "hang" was machine
    load (compiler diagnosis), not a bug (`212290d`, `6957446`). The full
    corpus `--check` audit (400 blocks; `verify-code.js` writes
    `audit-results.json`) was stopped under the shared machine's load and
    is deferred to a quiet window, then a run-level audit of `examples.md`
    (output claims, not just types) follows. Load hygiene note: the stale
    stdlib checkout under `%TEMP%\kilo\stdlib_ws\compiler_main3\stdlib`
    costs every compile a second tree walk plus ~90 `W001` warnings; the
    stdlib lane should remove or relocate it once its battery is idle.
41. **Lightbox zoom and pan (done 2026-09-27)**: the growth-diagram modal
    gained cursor-anchored wheel/trackpad zoom (1x-8x), drag-to-pan with
    clamping and grab/grabbing cursors, pinch zoom on touch, a bottom
    toolbar (-, percentage, +, Reset), a double-click toggle and +/-/0
    shortcuts; Escape, Close and click-outside still dismiss and focus
    returns to the link. Verified with CDP-driven interactions (toolbar to
    140 percent, wheel to 237 percent, drag changes the transform, Reset
    back to 100 percent, Escape closes) plus a zoomed screenshot; the test
    wrapper was removed and the figure caption now says to zoom and drag
    (`2e3bd46`).
42. **Extension install link fixed (done 2026-09-28)**: `/install`, linked
    from the VS Code extension's missing-toolchain notification, returned
    404; the site now carries a directory stub (same pattern as `/docs`)
    redirecting `/install` to `/download.html#install`, and the One-Line
    Install section has the anchor (`90efe11`). The extension needs no
    change to keep the URL; the compiler lane can repoint it at
    `/download.html` if preferred. Reminder from the same thread: the iOS
    stale-stylesheet report was traced to the vhost's far-future caching on
    non-hashed assets (DEPLOY.md "Static asset caching", ops relay).

43. **Ops routing and cache fixes verified (done 2026-09-28)**: `/download`
    and `/install` serve 200 directly; `style.css` sends `Cache-Control:
    no-cache` plus a past `Expires` and answers 304 on conditional requests
    (verified with curl etag-compare and If-Modified-Since); docs hashed
    assets revalidate; `dl.xiom-lang.org/` 302s to the download page. The
    `/download/` stub lands with the next pull. DEPLOY.md's "Static asset
    caching" and "URL routing" now describe the applied state; the
    immutable-long-cache option for hashed MkDocs assets is recorded for
    ops (recommended, narrow rule, nothing depends on it). Ops then asked
    for the one-time asset bump so pre-fix Safari clients stop serving the
    poisoned 10-year `style.css` entry: `?v=20260928` was applied to
    `style.css` (14 pages), the five JS includes, and the images that
    changed since (story/pillar icons, `og-card.webp`, the refreshed
    banners); HTML always revalidates, so every client picks the new URLs up
    on the next visit.
44. **Installer resilience implemented and tested (done 2026-09-28)**:
    `install.ps1` now sets `$ProgressPreference = 'SilentlyContinue'`, lists
    running `xiom*` processes before touching the install directory, retries
    removal three times and otherwise installs side by side to
    `<dir>.new` with its bin prepended to PATH; the next successful run
    consolidates and prunes the stale tree and PATH entry (`733656b`).
    Tested in three phases (clean install; `vcruntime140.dll` held open
    with FileShare.None; consolidated rerun with the side-by-side tree
    gone) and against a real locked run: the owner's machine had the VS Code
    LSP plus eight xiom-mcp processes live, so the installer went side by
    side and v0.62.1 is now first on PATH from `%LOCALAPPDATA%\xiom.new`.
    The canonical tree lost its exes to the partial wipe and consolidates on
    the     next installer run after VS Code closes. The download page documents
    the fallback.
45. **Self-hosting progress made accurate and live (done 2026-09-29)**: the
    roadmap, history and spec pages claimed "self-hosting gates cleared"
    while the compiler lane's tracker (`docs/SELFHOST_PROGRESS.md`,
    `532bfa75`) reports 9% (1 of 11 gates) with selfhost shipping only at
    100%. The copy now says in progress, and the roadmap carries a live
    meter (`js/selfhost-meter.js`) that reads the tracker from `main` via
    raw.githubusercontent.com (ACAO `*`) and shows "N% (x of y gates)",
    with the authored fallback until the fetch succeeds; verified by unit
    tests (success and fallback paths) and a local render (`d41295d`).
    The tracker sits in five unpushed compiler commits, so the live page
    shows the fallback today and activates the moment the compiler lane
    pushes; no further website change is needed.
46. **Instagram added to the footer social row (done 2026-09-29)**: the
    `.footer-social` row gained a ninth icon, `XIOM on Instagram`
    (`https://www.instagram.com/xiom.language/`), appended after Facebook on
    all twelve pages that carry a footer, with the same aria-label, title,
    `target="_blank"` and `rel="noopener"` rules. Verified at a true 414px
    viewport: nine icons in one row, no horizontal overflow, Instagram last;
    link checker clean. The playground/registry lane prompt now lists the
    new order and URL.
47. **Self-hosting progress bar (done 2026-09-29)**: the tracker went public,
    so the roadmap's self-hosting section now renders a rounded progress bar
    filled with the brand accent gradient (#66fff1 -> #4cc8ff) and glow,
    with the percentage inside the bar, the "x of y gates" detail beside it
    and the same live percentage in the state table. `js/selfhost-meter.js`
    drives fill width, labels and `aria-valuenow`, and only unhides the bar
    when the tracker fetch succeeds; the authored fallback stands otherwise
    (`63701eb`).     Unit tests cover both paths; desktop and mobile renders
    verified at a true 414px viewport.
48. **Roadmap refreshed to the live platform state (done 2026-09-30)**: the
    roadmap was re-checked against the registry change log (2.7.0) and
    `/health`. Added a Platforms row (Windows and Linux x64, macOS Intel and
    Apple Silicon shipping; ARM and RISC-V cross-compilation in progress);
    the registry row now reads 2.x with the shipped features (self-service
    grant requests and rotations, download stats, feeds and following,
    contributor profiles and sponsors, signed index digest, publish
    preflight); Next dropped the stale "reviewer roles and the moderation
    console" (shipped in 2.4-2.5) and the macOS item (archives ship),
    leaving packages plus post-beta object storage and index sharding, and
    ARM/RISC-V. The ecosystem page and the registry guide were updated to
    match (the guide now mentions the `POST /validate` preflight); the live
    package count reads 362 installable (`7c9644b`).
49. **Live meters generalized; verification gates fetched (done 2026-10-02)**:
    `js/progress-meter.js` replaces the selfhost-only script and drives both
    roadmap bars (selfhost, stdlib) from their trackers, plus the
    Verification gates table cells from an optional
    `**Gates: label x/y, ...**` line (authored values remain the snapshot
    fallback). The roadmap gains a Standard library section with a
    readiness bar (hidden until the stdlib tracker publishes its meter
    line) and routes the smoke gates to the Verification table; a `[hidden]`
    reset fixes `display: flex` overriding the attribute. Verified with 15
    unit tests (success, partial and failure paths) and local renders --
    selfhost 18% live, stdlib fallback hidden, no overflow (`6e71c18`).
    Relay requests for the two tracker lines are in the lane notes above.
    The compiler lane published its gates line the same day; after a parser
    tweak for its `(+4 ignored)` annotation, the live table reads e2e
    2395/2395, checker 195/195, feature 517/517, robustness 63/63, fuzz
    24/24, perf 3/3, formatter 86/86, lsp 45/45 from the tracker, with the
    stdlib corpus on the snapshot until its tracker publishes a gates line
    (`7bdebb5`).
50. **Dijkstra quote on the Why page; stdlib tracker lines pending push
    (done 2026-10-02)**: a styled pull quote ("Testing can only prove the
    presence of bugs, not their absence." -- Edsger W. Dijkstra) closes the
    Four layers of protection section on why.html, rendered and checked
    (`378e479`). The compiler's gates line was verified live on the page
    (feature 517/517, perf 3/3 immediately; e2e 2395/2395 once `7bdebb5`
    deploys). The stdlib lane reported adding the meter (70%, 7 of 10) and
    gates lines (`415e20d`), and both match the parser regexes locally, but
    their `main` is seven commits ahead of origin, so the raw tracker does
    not carry them yet and the bar correctly stays hidden; the site will
    show 70% and corpus 951/951 as soon as they push `main`. Pushed later
    the same day and verified live: the stdlib bar reads 70% (7 of 10
    gates), the corpus row 951/951, and the compiler e2e row 2395/2395 with
    the parser fix deployed; `probes 208/208` is carried and ignored until a
    matching row exists.
51. **Benchmark cover (done 2026-10-02)**: the Reproducible evidence section
    carries `img/benchmark-chaos.webp` (1254x1254, owner-supplied) as a 2:1
    centered cover crop (`object-fit: cover`, `aspect-ratio: 2/1`,
    `max-height: 460px`) that keeps the XIOM mark and the BENCHMARK OF CHAOS
    title in frame; alt text and lazy loading included, and the status line
    now says the harness is still being battle-tested before the repository
    and results go public (`d110ef9`). Verified with desktop and mobile
    renders (image complete, 1100x460 and 382x191, no overflow); the
    deploy lands with the 15:23 pull. The owner supplies the public
    repository link when it launches.
52. **Stdlib gate rows (done 2026-10-02)**: the Verification gates table
    gained live rows for the standard library's modules (type-check clean),
    probes and bare-name scan alongside the corpus row; all twelve rows
    fill from the two trackers (verified in a local render: e2e 2395/2395,
    corpus 951/951, modules 509/509, probes 208/208, barename 0/509), and
    the snapshot note scopes the 4,212 figure to the compiler snapshot plus
    the original corpus (`ff1b827`).
53. **Self-hosting gate wording (done 2026-10-02)**: the Self-hosting
    section now states the gates are differential -- the self-hosted
    compiler must match the bootstrap compiler's output at token, AST and
    byte-identical IR level on the corpus, and the final chain requires
    byte-identical self-compiled binaries -- matching the tracker's 100%
    definition and T1/T2/T3 harness (`6f77857`).
54. **Verification-gates intro clarified (done 2026-10-02)**: the intro now
    states that rows fill automatically on page view from each repository's
    tracker, and that only a row without a published tracker value keeps the
    last verified snapshot (v0.61.0, checked 2026-09-22). No new fetch is
    involved: the values were already live; the old sentence implied the
    displayed table was the snapshot. The tracker files themselves carry
    their measurement provenance (commit/date/box) for audit.
55. **Registry trust explained in plain terms (done 2026-10-02)**: the
    registry guide now explains why tampering fails -- immutable versions
    (republishing returns `409`), sha256-verified artifacts, the signed
    index digest (`/index-digest.json`; a pinned key detects an altered or
    rolled-back index), CI provenance naming repository/workflow/commit with
    a run link, the staging canary before official packages reach
    production, and yank-instead-of-rewrite -- with the trust-model table
    gaining digest and provenance rows; the ecosystem page carries the same
    summary (`de1a850`). Claims verified against the live signed digest,
    the live per-version provenance block in `/index.json` and the registry
    docs.

## Cross-lane notes

Release-notes mirror publish cannot be a website job (found 2026-09-24): the
compiler lane's publisher is done (`crates/xiom-release-notes`, convert +
verify, hard schema validation) and it hands requirement 5 (mirror publish +
`"notes": true`) to this lane. The website repository has no credentials for
`dl.xiom-lang.org`: no workflow uses any secret (checked all of
`.github/workflows/`), there is no mirror script, and the release-dispatch
PAT is still 403. So the mirror copy must be written by whoever already
publishes archives to the mirror -- the compiler release pipeline or the
owner's VPS sync -- as one more file in that same step. Note the reader is
not blocked meanwhile: `js/release-notes.js` falls back to the tag-pinned
`raw.githubusercontent.com/xiom-lang/xiom/<tag>/release-notes/<tag>.json`,
which the compiler lane commits before tagging (its `verify` guarantees
byte-identity), so the next release renders notes even while the mirror lags.
Acceptance on the next tag: notes visible on the download and versions pages
via the raw fallback, and, once the mirror writer adds the file,
`releases/index.json` carrying `"notes": true` so the pages stop trying for
older tags.

Registry correlation (confirmed 2026-09-24): the registry stores the
toolchain pin per package version and serves it as `compiler` on the package
page; it needs no changes. The stdlib publish pass must pass the pin as
metadata -- `xiom-std@0.61.3` currently has no `compiler` value, so there is
nothing to correlate yet. The registry's `index.json` lists package names
only (38 packages), so the field lives in the per-package detail. Deferred
website idea: when values exist, surface "pinned toolchain" beside
`xiom-std` where the docs or versions page mention it -- not actionable until
the stdlib publish pass emits the field. Registry release notes (release.json
per schema v1 at `registry.xiom-lang.org/releases/<tag>/release.json`) were
acknowledged and are not applicable today.

Per-release test counts (compiler lane, asked 2026-09-22): the versions page
can only show verification numbers per tag if the release metadata carries
them -- today neither the mirror (`releases/index.json` has tag + published
only) nor the GitHub release bodies include counts. Suggested shape, additive
so old clients ignore it:

    {"tag":"v0.61.1","published":"...","verification":{
      "e2e":2345,"checker":195,"feature":510,"robustness":63,"fuzz":24,
      "perf":2,"formatter":86,"lsp":45,"stdlib_corpus":949}}

Once that exists, the versions page renders a checks column per release and
the roadmap table can become a live summary. Current static numbers live on
the roadmap page: 3,263 compiler gate cases + 949 stdlib corpus programs =
4,212 checks, labelled with what each unit counts.

Compiler context file corrections (compiler lane, found 2026-09-22): the
root `AI_CONTEXT.md` (shipped as `lib/AI_CONTEXT.md`, served by
`xiom_workflow_guide {topic:"context"}`) maps diagnostics as "X contract",
but the compiler emits no X codes. Re-probed v0.61.1: a runtime `requires`
violation prints `contract violated: requires at 2:13` with no code;
contract-related compile cases return `T001`; `--diagnostics=json` carries
L/P/T/E/C codes only. The MCP `explain_error_code` description still uses
`X0100` as its example, and the website's `docs/error_codes/` reference
documents the real L/P/T/E/C/W families with X marked reserved. Ask the
compiler lane to update the canonical file and the MCP example. Also probed
and confirmed: contradictory `requires` clauses and impossible type
invariants are not rejected today, so the contracts guide no longer claims
"Contradictory = compile error"; either implement contradiction detection or
keep the docs as they now read.

Specification wording (compiler lane, 2026-09-22): the authoritative
`specs/XIOM_Language_Spec.md` still contains statements the reviewer wants
gone -- "no runtime" (line 43), "Static (Phase 3)" (line 538) and
"No runtime crash -- compile error" (line 497). The website spec page now
labels Revision 0.3 as the core-language reference, states that self-hosting
gates are cleared with no self-hosted release, and describes contracts as
runtime guards plus an export path rather than a proof. When the compiler
lane publishes the next revision, update `specs/` and the page together.
Also probed and confirmed: a direct field assignment that violates a type
invariant compiles and does not trap at runtime today, so the specification
row and `contracts.md` now say invariant enforcement coverage is partial
instead of claiming the compiler rejects such paths.

Mirror lag blocks the four-platform docs (owner/compiler lane, found
2026-09-22): the GitHub release v0.61.1 (published 07:22 UTC) carries
linux-x64, windows-x64, macos-x64 and macos-arm64 archives plus the
`xiom-vscode-0.12.0.vsix`, but `dl.xiom-lang.org/latest.json` and
`releases/index.json` still serve v0.60.1 with two platforms only. The
download and versions pages read the mirror, so they show v0.60.1 while the
extension requires v0.61.0+ -- new users cannot install a compatible
toolchain until the mirror syncs. The macOS rows and the "macOS archives not
published yet" notes are held back until then.

Mirror lag (owner/VPS action, still broken 2026-09-23): the mirror's
`latest.json` and `releases/index.json` still report v0.60.1 even though the
v0.61.1 asset directory exists on the mirror, and GitHub is already at
v0.61.3. Because installers trusted the mirror, `install.ps1` installed
v0.60.1. The website lane hardened everything that reads release metadata:
`install.ps1`, `install.sh`, `download.html` and `versions.html` now consult
the mirror and the GitHub releases API and use whichever release is newer
(the pages cache the API lookup for ten minutes to stay inside the anonymous
rate limit). The mirror sync pipeline itself still needs fixing so the
canonical source stops lagging.

Docs refresh automation (done 2026-09-25, owner-approved): the compiler
release workflow already dispatches `compiler-release` with tag, `stdlib_ref`
(from STDLIB_VERSION) and `compiler_ref` (release.yml CRB-4b); the 403 is
only the token, which must cover `xiom-lang/website` with Contents:
read/write (fine-grained) or classic `repo` scope. Token mapping (owner,
2026-09-25): `XIOM_RELEASE_TOKEN` is the org fine-grained token
`xiom-release-write` (it must gain Contents: read/write on website);
`XIOM_CROSS_REPO_TOKEN` is `xiom-cross-repo-read` (read-only checkouts, no
website access needed). The owner added website to `xiom-release-write`;
confirmation is the dispatch line in the next tagged release. Until the
token lands, docs no longer wait on it: `docs-versioned.yml` gained
a weekly schedule (Monday 04:00 UTC) and GitHub-first tag resolution
(`/releases/latest`, mirror fallback), so the current release is republished
from main every week. The dispatch remains the release-accurate path (pinned
refs) once the token covers the repo.

No-NASM crypto stubs (compiler/stdlib lane, found 2026-09-22):
`stdlib/runtime/xiom_runtime.c` defines, under `-DXIOM_NO_ASM`,
`xiom_asm_aes128_encrypt_block`, `xiom_asm_aes128_decrypt_block` and
`xiom_asm_aes128_key_expand` as empty functions, and
`xiom_asm_constant_time_compare` / `xiom_asm_memcmp_ct` as `return 0`. The mem
stubs delegate to libc, so those are semantically correct. If the dispatch
layer can reach the crypto stubs in a no-NASM build, AES silently produces no
output and the constant-time compares always report equal -- a security hole,
not just a performance fallback. Please confirm reachability and either
implement real portable crypto, fail loudly, or document NASM as required for
the crypto modules. `docs/RUNTIME_SYMBOL_AUDIT.md` shows the dead-symbol trim
already removed the sha256 stub; these AES/CT entries may be in the same
family. Related reviewer asks, still open for the stdlib lane: per-symbol
"NASM-backed" flags in the generated API and published differential-test
evidence between accelerated and portable paths.

Error-code follow-ups (compiler lane, 2026-09-21): the website reference now
documents the codes the compiler actually emits (L001, P001, T001, E001, C001,
W000, W001) and reserves the X family as never-emitted. What remains on the
compiler side: (a) non-exhaustive `match` is not rejected and W000 did not
reproduce for it under `--check`, while the specification requires
exhaustiveness -- enforcement or a reliable warning is missing; (b)
`warning[E001]` for returning a borrow lets the build succeed -- decide
whether default builds should fail; (c) `--explain` resolves
`docs/error_codes/{code}.md` from the current directory and archives do not
ship it, so installed users cannot use it -- ship the directory or embed the
text; (d) the stale archive README below.

Debugger symbol surface (compiler lane, question 2026-09-22): XIOM has no
symbol-control attributes today (`#[no_mangle]`, `#[export_name]`,
`#[inline(never)]`). Debugging works through `-g` DWARF plus the `debugger;`,
`assert` and `dbg!` intrinsics, so nothing is missing for the normal workflow.
If C-calling-XIOM embedding or stepping through optimized builds becomes a
supported workflow, those attributes are the gap to fill.

Release archives (v0.60.1) ship a stale `README.md` inside the package: it
names the XIOM Foundation as copyright holder, points at
`NgonArt_STUDIO/XIOM`, claims version 0.20.0 and self-hosting. The compiler
lane should refresh the README that goes into the archives before the next
tag; the website must not reflect any of it.

The v0.60.1 archives contain only `bin/xiom(.exe)`; the release workflow now
builds the nine tool crates and a pinned z3, so the next tag is the first
archive with the full `bin/` set. Docs say "recent releases ship" and point at
the release notes rather than promising the tool list for every tag.

## Paste-ready prompts for other lanes

Send these to the playground and registry sessions; they match the website
implementation committed on 2026-09-21 (`xiom-website/index.html` and the
`.footer-social` rules in `xiom-website/style.css`).

### Playground lane

Add the website's social row to the playground footer (or About panel):
copy the `.footer-social` block from `xiom-website/index.html` and the
matching `.footer-social*` CSS from `xiom-website/style.css`. Keep the order
Discord, X, Mastodon, Bluesky, Reddit, Hacker News, LinkedIn, Facebook,
Instagram; one `aria-label` and `title` per link; `target="_blank"
rel="noopener"` (Mastodon also `rel="me"` immediately after `title`).
Wording for Discord must stay "XIOM community Discord (open invite)" -- the
server is invite only and must not be described as discoverable.
URLs:
- https://discord.gg/fsxQfDUg9
- https://x.com/XiomLang
- https://mastodon.social/@xiom_lang
- https://bsky.app/profile/xiom-lang.bsky.social
- https://www.reddit.com/r/xiom_lang/
- https://news.ycombinator.com/user?id=xiom-lang
- https://www.linkedin.com/company/145216062/
- https://www.facebook.com/profile.php?id=61594524426045
- https://www.instagram.com/xiom.language/

### Registry lane

Same block and CSS in the registry UI footer, same order, labels and
rel/target rules. Keep the Discord invite wording identical; keep
registry@xiom-lang.org next to the row for registry-specific contact.

### Playground lane: banner header

The owner supplied a banner image for the playground site:
`E:\xiom-lang\website\xiom-website\img\playground.webp` (1539x510, textless,
subject on the right, negative space on the left). Copy it into the
playground's own assets and use the same header treatment the website now
uses on six pages (CSS in `xiom-website/style.css`, "Page banners" section):

```html
<header class="page-banner">
  <img src="img/playground.webp" alt="" width="1539" height="510">
  <div class="xiom-banner-text">
    <h1 class="xiom-heading"><span class="xiom-brand" aria-hidden="true">XIOM</span><span class="xiom-section">PLAYGROUND</span></h1>
    <span class="xiom-accent" aria-hidden="true"></span>
  </div>
</header>
```

Key values: brand #F3F7FF, weight 300, tracking 0.28em; section #69B8FF,
tracking 0.36em; accent gradient #66FFF1 -> #4CC8FF with a restrained glow.
The block is centred inside the artwork's open left area: `left: 22%;
top: 50%; transform: translate(-50%, -50%)`, with centred text, so it never
reaches into the subject on the right. Keep the h1 semantic (brand span
aria-hidden) and the image alt empty.

Important for sites with buttons in the hero (playground, registry): do not
stack CTAs into the left area under the banner text. Either move the CTA row
below the banner as a normal section, or centre it directly under the banner
image; the banner itself stays wordmark + section + accent (+ at most one
short tagline).

### Registry lane: banner header

Same treatment with `E:\xiom-lang\website\xiom-website\img\registry.webp`
(1539x510) and the section title `REGISTRY`. Copy the CSS block above from
`xiom-website/style.css`; keep the registry site's existing palette and only
adopt the banner typography and placement.

### Compiler lane: publish release notes on the next tag

The website's "What's new" system is live; the contract is
`docs/release-notes-schema.md` in `xiom-lang/website` (schema v1). Please
implement the publisher for the next release:

1. Author `release-notes/<tag>.md` from `release-notes/TEMPLATE.md`: one
   summary sentence; 1-6 highlights with a `kind:` line
   (`language`, `compiler`, `stdlib`, `tooling`, `fix`, `security`); a
   breaking-changes section (write `None.` when there is nothing); optional
   known issues and docs links. Plain ASCII text, no internal IDs or hashes.
2. Merge the stdlib fragment `release-notes/<tag>.md` from the checkout
   pinned by `STDLIB_VERSION`; its highlights become `kind: "stdlib"` unless
   the fragment sets its own kind.
3. Convert to `release-notes/<tag>.json` and validate it hard: required
   fields, length limits, kind enum, and a present `breaking` array. Fail the
   release on any violation.
4. Commit the JSON **before** creating the tag -- the site reads
   `raw.githubusercontent.com/xiom-lang/xiom/<tag>/release-notes/<tag>.json`
   as the fallback source.
5. Publish the same file to
   `dl.xiom-lang.org/releases/<tag>/release.json` and add `"notes": true` to
   that tag's entry in `releases/index.json`.

No website deploy is needed: the pages fetch notes by tag at runtime. If
nothing is published, the pages simply link the changelog.

### Stdlib lane: release-notes fragment

The site now renders per-release "What's new" notes (contract:
`docs/release-notes-schema.md` in `xiom-lang/website`). For the next tag, add
`release-notes/<tag>.md` to the stdlib repository using the compiler
template's `###` highlight blocks; the compiler release step merges it from
the pinned checkout and tags its bullets as `stdlib`. Keep entries
user-facing (what a user gains -- no wave names, no task IDs), one to two
sentences each, at most 320 characters. If nothing user-visible ships in the
release window, say so to the compiler lane so the fragment can be omitted.

Also for the next publish: pass the toolchain pin as package metadata on
`xiom-std` (the field the registry serves as `compiler`, per version). The
registry already supports it; `xiom-std@0.61.3` has no value yet, so there is
nothing to correlate until the publish pass emits it.

### Registry lane: release notes when tagged releases exist

Same contract applies if the registry starts tagged user-facing releases:
publish `release.json` (schema v1) at a stable URL -- suggest
`registry.xiom-lang.org/releases/<tag>/release.json` -- and we can render it
where the website links to registry releases. No action needed for the
current toolchain notes. Optional but useful: keep the `xiom-std` package
metadata listing the toolchain tag it is pinned to, so package versions can
be correlated with toolchain releases.

### Packages lane: public README landing (owner-approved framing)

The website now has a "How the ecosystem grows" section that presents the
loop -- compiler, standard library, packages, registry -- and the publish
gates, and it states in one line that the corpus is ported with AI assistance
under review. That is deliberate: we do not hide the method, and no one would
believe the pace without assistance. The public pitch is the system loop and
its guarantees, not the coordination mechanics; `xiom-packages/packages` has
no README, so its first impression is `SESSION.md` and `docs/` in internal
vocabulary (waves, sessions, dispatches). Please add a public `README.md`
that owns the method and frames those files as internal working notes kept
public on purpose. Keep the tone matter-of-fact, not apologetic; if anyone
disagrees with the framing, raise it rather than adopting it half-way.

Suggested README content:

## How this corpus is built

This is the staging and release home of the XIOM package ecosystem. The
corpus is ported and maintained with AI assistance; that is not hidden, and
it is why the ecosystem has grown to hundreds of packages this fast. What
makes the result trustworthy is not the absence of assistance but the process
around it: every package must pass its conformance suite on a pinned
toolchain, findings are filed upstream with reproductions, and nothing
publishes without the release gate. If that method is not for you, the
ecosystem is not for you -- we would rather say this plainly than have you
discover it later.

`SESSION.md` and the notes under `docs/` are the internal record of that
process. They are kept public for transparency and describe how the work is
coordinated, not the product story; the product story is what ships:
verified, signed and immutable releases.

### Compiler lane: scripting findings (2026-09-27)

Found while writing the scripting guide; verified against the installed
v0.61.3 (Linux runs in WSL, checks on Windows). The guide marks 1-3 as
known limitations until fixed.

1. `for x in [ ... ]` over an array literal fails at LLVM codegen:
   `xiominput.ll:695:31: error: invalid getelementptr indices ... error:
   compilation failed` (clang exit 1). Reproduced with an accumulating body
   and with a print-only body; `--check` passes, so it is codegen. The
   reference docs now carry the caveat.
2. `xiom run` does not pass script arguments: `args.args_raw()` (and
   `io.args()`) return exactly one element -- the temporary binary path --
   with or without a `--` separator. Repro: a script printing each raw
   entry, run as `xiom run args.xi --shout --name Ada one two`.
3. Piped stdin crashes on Linux in both `io.read_all_stdin()` and
   `io.read_line_trim()`: `Fatal error: glibc detected an invalid stdio
   handle`, exit -1 (`printf 'a\nb\n' | xiom run script.xi`).
4. `io.println(<Int>)` is `T001` (expected Str); several reference loop
   examples printed an Int. Fixed with `itos` and an explicit
   `use xiom.convert.itos;`.
5. `xiom build` in a directory without `xiom.toml` errors
   `cannot read 'build'` (treated as a source path) while the help lists
   `build`; a clearer standing error when no manifest is present would help.
6. The help says tool dispatchers need the `xiom.bat`/wrapper launcher, but
   `xiom.exe` dispatches `fmt`, `pkg` and `doctor` directly (verified);
   `xiom doc --help` prints the main compiler help instead of the doc
   tool's.
7. Confirmed working and documented: `run -e` and `run -` complete (the
   earlier 25-60 s timeouts were machine load, per the compiler diagnosis),
   `run --watch` re-runs on change, shebang via
   `#!/usr/bin/env -S xiom run`, and the example set (hello, values,
   while-sum, files, env/exit, spawn) is green end to end.

### Ops lane: URL routing and cache headers (2026-09-28, actioned)

Ops applied both fixes on 2026-09-28. The `xiom-static` Hestia template
pair (assigned to `xiom-lang.org` and `docs.xiom-lang.org`) now serves
`Cache-Control: no-cache` with a past `Expires`; conditional requests answer
`304` via `ETag`/`Last-Modified` (verified here with curl etag-compare and
If-Modified-Since for `style.css`, and the docs hashed assets revalidate
too). `/download` and `/install` resolve directly, and `dl.xiom-lang.org/`
302s to the download page. HTML headers are unchanged.

Open question back to ops: MkDocs assets are content-hashed, so they could
be immutable long-cache. The website recommends a narrow immutable rule for
those hashed asset directories only, leaving HTML and the fixed-name site
assets revalidating; nothing depends on it. The directory stubs stay for
the trailing-slash forms (`/download/` answers once the stub deploys) and as
belt-and-braces.

### Compiler lane: extension install link (2026-09-28, delivered)

The owner relayed this to the compiler lane on 2026-09-28; kept here for
reference. The missing-toolchain notification in the VS Code extension
points at
`https://xiom-lang.org/install`, which was a 404. The website now serves
that URL: a directory stub redirects it to the One-Line Install section of
`https://xiom-lang.org/download.html#install`. No extension change is needed;
if you prefer a direct target, point the notification and README at
`https://xiom-lang.org/download.html` (note: the extensionless `/download`
does not resolve on this vhost). The marketplace text still says "Minimum
toolchain: v0.61.0" while v0.62.0 is out; it is correct as a floor, update
it whenever the extension docs are next touched.

### Compiler lane: installer resilience (2026-09-28, actioned)

The requested changes are live: `$ProgressPreference = 'SilentlyContinue'`,
running-`xiom*` detection before the wipe, removal retries, and a
side-by-side fallback to `<InstallDir>.new` with PATH preemption when
`vcruntime140.dll` is locked; the next run consolidates back. Verified with
a held `FileShare.None` handle and a real locked run (VS Code LSP plus
xiom-mcp processes); the owner's machine now runs v0.62.1 from
`%LOCALAPPDATA%\xiom.new`, PATH-first, and consolidates after VS Code
closes. Extension-link audit acknowledged: no extension change needed.

### Compiler lane: tracker lines (updated 2026-10-02)

The website renders the bootstrap meter live from
`main:docs/SELFHOST_PROGRESS.md` (origin/main, fetched per page view); it
now shows 18% (2 of 11), so the earlier worktree note is closed -- just keep
landing tracker commits on `main`. Optional second line for the Verification
gates table (rows update when present, snapshot values otherwise):

**Gates: e2e X/Y, checker X/Y, feature X/Y, robustness X/Y, fuzz X/Y, perf
X/Y, formatter X/Y, lsp X/Y.**

Add or refresh it whenever the release gate run completes; if a better file
than the selfhost tracker should carry it, say so and we re-point.

### Stdlib lane: readiness tracker lines (2026-10-02)

The roadmap now has a Standard library readiness bar and routes the smoke
gates into the Verification gates table. Both are fetched live from
`main:docs/PRODUCTION_READINESS_QUEUE.md`, so please add two lines near the
top and update them as work lands:

**<N>% -- <x> of <y> readiness gates complete.**

**Gates: corpus <x>/<y>, modules <x>/<y>, probes <x>/<y>, barename
<x>/<y>.**

The `corpus` label fills the Standard library corpus row; other labels are
recorded until matching rows exist. The bar stays hidden until the meter
line appears; no website change is needed after that.

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
SESSION.md and DEPLOY.md before acting. Deploys are pull-based: push to main
publishes the site within the hour (web-deploy.sh, cron minute 23) and the
docs-versioned push trigger republishes docs.xiom-lang.org; the docs docroot
switch is DONE and live. The owner account has a ruleset bypass, so direct
pushes to main are expected.

State (2026-09-25): HEAD 98b1daa. Copyright notices across the repo read
"Copyright (c) 2026 Eleftherios Notas and The XIOM Authors" per
xiom-lang/.github docs/LICENSING.md section 8; the XIOM Foundation must not
be named as holder. Review rounds 1-2 are applied (honest claims, Why page
rewritten around intent -> enforcement -> AI, spec page labelled Revision
0.3 for the core language, 128-bit primitives documented, syntax examples
aligned to canonical colons and semicolons). The snippet syntax lint runs in
`docs.yml` and `docs-versioned.yml` and the corpus is clean. Landed since the
last refresh: prior-art and History pages, unsafe guide, Contributing hub,
error-code reference (L/P/T/E/C/W families, X reserved), debugger guide,
MkDocs XIOM highlighting, version-teaching removal, footer rebuild with the
eight social icons (mobile-sized), two-column index hero plus banners on six
pages, the editor-support block (XIOM Toolchain 0.12.0 on both
marketplaces), the verification trust-boundary section, the external-link
fix, the toolchain-context and post-release-plan pages rendered from the
compiler checkout, the release-notes system (schema v1 in
`docs/release-notes-schema.md`, `js/release-notes.js`, panels on the
download and versions pages, fully tested), installer resilience
(mirror + GitHub, newer release wins; macOS shipping copy), the
checksum-column copy correction from the live deploy verification, the
owner's webp art refresh including the og-card webp switch, the
ecosystem status pass with the live registry package count and the benchmark
move to the roadmap, the weekly docs refresh with GitHub-first tag
resolution, the compiler-relay semicolon rule, and the Registry 2.0 launch
update. All guide syntax
was audited against a local compiler build: `if let`, range expressions
and the `Byte` alias are not implemented and the docs do not claim them.
Commits carry `-s` sign-off. `docs/wikipedia-draft.md` is a planning sheet
only and `docs/marketplace-publisher.md` holds the marketplace copy; neither
is built into the site.

The live deploy was verified on 2026-09-24 (item 28): the installer picks
GitHub and installs v0.61.3, download.html lists four platforms, versions.html
reads GitHub, and the notes toggle is honest until the next tag.

Next, in order:
1. Next tagged release: verify the release-notes render end to end (mirror
   first, tag-pinned raw fallback) and that a tag without notes shows only
   the changelog link. The mirror publish of `release.json` and
   `"notes": true` belongs to whoever writes archives to the mirror; the
   website has no credentials for it (recorded in cross-lane notes).
2. Draft "XIOM for game developers" once the owner provides engine facts
   (C# coverage on the Concepts page landed 2026-09-21).
3. Benchmark showcase: when the owner says the benchmark repo and paper are
   public, add a "Reproducible evidence" page (task definition, generated
   source, compiler output, runtime results, contract configuration, tool
   interactions, tokens, environment, sessions) and link it from the Why
   page; the "in preparation" section now lives on the roadmap
   (`roadmap.html#benchmark`) with no results claimed, and the homepage card
   was removed 2026-09-25.
4. If the compiler lane publishes a current specification revision, update
   specs/ and the spec page and bump the revision label (0.3 carries a
   2026-09-20 maintenance note for 128-bit primitives).

Cross-lane: playground owns its copy fixes (Never Crash, stats bar,
audience framing) per the brief already delivered; macOS ships on all
releases now (Intel and Apple Silicon archives in v0.61.3), so the earlier
"wait for RELEASE_BUILD_MACOS" note is closed; ecosystem/registry doc
pointers stay deferred until stdlib is 100%; registry correlation
(`compiler` pin metadata) waits on the stdlib publish pass.

Mirror state (owner/VPS and compiler lane, checked 2026-09-24): the mirror
still serves v0.60.1 in `latest.json`/`releases/index.json` and sends no
`Access-Control-Allow-Origin`; its archive writer must also publish
`releases/<tag>/release.json` and set `"notes": true` per the release-notes
schema. The website cannot write to the mirror (no credentials in any
workflow). It no longer depends on the mirror being current: the installers
and both release pages compare mirror and GitHub and use the newer release,
and release notes fall back to the tag-pinned raw file. Proper fixes:
regenerate `latest.json`/`index.json` on every tag, add
`add_header Access-Control-Allow-Origin "https://xiom-lang.org";` for the
JSON paths, and publish the notes file. The checksum column would also need
ACAO on the `SHA256SUMS` files (or a tag-pinned checksums file in the
compiler repository, read from raw.githubusercontent.com) to fill in
browsers.

Rules: ASCII-only; never hardcode versions (read mirror JSON); pin GitHub
Actions refs to full SHAs; commit identity is repo-local (Lefteris Notas
<lefterisnotas@gmail.com>); DCO is now a required check on main -- sign
commits with `git commit -s`; keep the site static and honest - no claim the
implementation does not support.
```

## Relay from the compiler lane (2026-09-25)

**Statement semicolons -- owner decision: option (a), the Rust-like tail
form, STAYS.** The rule to document where beginners meet it: `;` separates
statements; ONLY a block's final expression (its value) may omit it; a
statement before another statement always needs the separator (`P001`
otherwise). `if`/`match`/blocks are expressions and their final expression is
the block's value, which is why `fn min(a: Int, b: Int) -> Int { if a <= b { a
} else { b } }` is valid -- and why a single-statement body
(`fn main() { io.println("hi") }`) is accepted. Guidance for docs and starter
snippets: end every statement with `;` in multi-statement examples, and only
use a tail expression deliberately where a value is produced. The compiler now
states this in the canonical `AI_CONTEXT.md` (shipped as `lib/AI_CONTEXT.md`
and served by `xiom_workflow_guide {topic:"context"}`) and in the MCP
`xiom_language_guide`; a `P001` note pointing at the missing separator is
queued in the compiler's Stage 6 (`docs/STAGE6_LINT_WAVE.md`, companion
diagnostics polish).

**Your 2026-09-22 diagnostic-code request is ACTIONED** (compiler commit
`b5b816b0`): the root `AI_CONTEXT.md` no longer claims an emitted `X` contract
family -- it now reads L lexer / P parse / T type (umbrella; compile-time
contract issues land here) / E ownership-borrow / C codegen / W warnings,
notes that runtime contract violations print `contract violated: ...` with NO
code, and marks `X` reserved. The MCP `explain_error_code` description example
is now `T001`, its fallback maps `W` and labels `X` reserved, and the
`--explain` unknown-code hint no longer suggests `X0010`. `docs/AI_PIPELINE.md`
carries a historical note. Please re-verify against your copies.

**Compile-side gap found while fixing that (your call with ops):**
`xiom --explain` and the MCP `explain_error_code` read
`docs/error_codes/<code>.md` relative to the CURRENT DIRECTORY. The compiler
repo has no such directory, so the reference only resolves inside a checkout
that contains the pages (this repo), not from a user project or an install --
there the MCP fallback now points at
`docs.xiom-lang.org/latest/error-codes/`. Options recorded as a compiler Stage
6 item: stage `docs/error_codes/` into `lib/docs/error_codes/` in the release
archives (release.yml fetch at the docs ref) or embed a minimal index in the
compiler. Note your section 4 says `docs/error_codes/*` stays unpublished for
now; if that changes, the staging path becomes the clean fix.

**P001 page (unpublished draft):** when the error-code pages are revisited,
the "statement terminators matter" bullet can state the tail-expression rule
explicitly (it currently only says `let x = 1;` needs its semicolon).

**Website response (2026-09-25):** the rule is now stated in
`docs/language/syntax.md` (new "Statements and Expressions" section, the quick
look and the Functions bullets) and in the website's `docs/AI_CONTEXT.md`
snapshot (three spots); `docs/error_codes/P001.md` states the tail rule and
carries a verified missing-separator example (probed on v0.61.3:
`error[P001]: 3:3: expected ';', found io`). Re-verified our copies: neither
`docs/AI_CONTEXT.md` nor the language guides claim an emitted X family, and
`docs/error_codes/` keeps the X pages reserved with banners. The `--explain`
gap is acknowledged as a compiler Stage 6 item; the pages the MCP fallback
points at are live at `docs.xiom-lang.org/latest/error-codes/`.
