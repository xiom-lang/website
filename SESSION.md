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

## Cross-lane notes

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

Mirror lag blocks the four-platform docs (owner/compiler lane, found
2026-09-22): the GitHub release v0.61.1 (published 07:22 UTC) carries
linux-x64, windows-x64, macos-x64 and macos-arm64 archives plus the
`xiom-vscode-0.12.0.vsix`, but `dl.xiom-lang.org/latest.json` and
`releases/index.json` still serve v0.60.1 with two platforms only. The
download and versions pages read the mirror, so they show v0.60.1 while the
extension requires v0.61.0+ -- new users cannot install a compatible
toolchain until the mirror syncs. The macOS rows and the "macOS archives not
published yet" notes are held back until then.

Release dispatch to the website is broken (owner action, reported 2026-09-22):
the compiler release workflow's dispatch to xiom-lang/website fails with 403
because the release token lacks `Contents: read/write` on this repository; the
workflow now warns instead of failing, so docs are not republished on new
tags. Options: extend the PAT, or add an alternative publisher (for example a
scheduled docs-versioned run that reads the mirror's latest tag and publishes
if the tag is not yet on gh-pages) -- the latter needs owner approval because
it changes CI permissions.

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
Discord, X, Mastodon, Bluesky, Reddit, Hacker News, LinkedIn, Facebook;
one `aria-label` and `title` per link; `target="_blank" rel="noopener"`
(Mastodon also `rel="me"` immediately after `title`). Wording for Discord
must stay "XIOM community Discord (open invite)" -- the server is invite
only and must not be described as discoverable.
URLs:
- https://discord.gg/fsxQfDUg9
- https://x.com/XiomLang
- https://mastodon.social/@xiom_lang
- https://bsky.app/profile/xiom-lang.bsky.social
- https://www.reddit.com/r/xiom_lang/
- https://news.ycombinator.com/user?id=xiom-lang
- https://www.linkedin.com/company/145216062/
- https://www.facebook.com/profile.php?id=61594524426045

### Registry lane

Same block and CSS in the registry UI footer, same order, labels and
rel/target rules. Keep the Discord invite wording identical; keep
registry@xiom-lang.org next to the row for registry-specific contact.

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

State (2026-09-22): HEAD 958cdaa. Copyright notices across the repo read
"Copyright (c) 2026 Eleftherios Notas and The XIOM Authors" per
xiom-lang/.github docs/LICENSING.md section 8; the XIOM Foundation must not
be named as holder. Review rounds 1-2 are applied (honest claims, Why page
rewritten around intent -> enforcement -> AI, spec page labelled Revision
0.3 for the core language, 128-bit primitives documented, module purpose
lines rendered, syntax examples aligned to requires:/ensures: colons and
use semicolons). The snippet syntax lint runs in `docs.yml` and
`docs-versioned.yml` and the corpus is clean. Since then: the Prior art
page, History page, unsafe guide, Contributing hub, error-code reference
(L001/P001/T001/E001/C001/W000/W001, X family reserved), debugger guide,
MkDocs XIOM highlighting, version-teaching removal, footer/social rebuild,
a full mobile pass, the editor-support block (XIOM Toolchain 0.12.0, both
listings live), the verification trust-boundary section, and an
external-link fix (absolute GitHub `.md` URLs are no longer rewritten to
`.html`). All guide syntax was audited against a local v0.61.0 compiler
build: `if let`, range expressions and the `Byte` alias are not implemented
and the docs no longer claim them; labeled loops, `loop`, `defer`, `const`
blocks, `while let` and the numeric widths/casts are documented and
probe-verified. Commits carry `-s` sign-off. The publishing files
(`docs/wikipedia-draft.md` planning sheet, `docs/marketplace-publisher.md`
copy) live in docs/ and are not built into the site.

Next, in order:
1. Draft "XIOM for game developers" once the owner provides engine facts
   (C# coverage on the Concepts page landed 2026-09-21).
2. Benchmark showcase: the benchmark is a separate private repo plus a
   research paper; when the owner says it is public, add a "Reproducible
   evidence" page (task definition, generated source, compiler output,
   runtime results, contract configuration, tool interactions, tokens,
   environment, sessions) and link it from the Why page.
3. If the compiler lane publishes a current specification revision, update
   specs/ and the spec page and bump the revision label (0.3 carries a
   2026-09-20 maintenance note for 128-bit primitives).
4. Editor support block (DONE 2026-09-22): both listings verified 200
   (Visual Studio Marketplace and Open VSX) after v0.61.1 shipped. Shipped an
   "Editor Support" section on download.html after "One-Line Install"
   (toolchain first; "XIOM Toolchain" extension 0.12.0 on both marketplaces,
   requires toolchain v0.61.0+; resolves xiom-lsp/xiom-dbg from the install;
   other editors via editors/README.md; agents via xiom-mcp), and updated the
   VS Code notes in getting-started.md and debugger.md. Remaining owner/DNS
   action: the Marketplace verified-publisher badge needs a
   domain-verification TXT record for xiom-lang.org.

Cross-lane: playground owns its copy fixes (Never Crash, stats bar,
audience framing) per the brief already delivered; macOS installer support
activates when RELEASE_BUILD_MACOS ships assets; ecosystem/registry doc
pointers stay deferred until stdlib is 100%.

Mirror CORS (owner/VPS action, found 2026-09-21): `dl.xiom-lang.org` serves
`latest.json` and `releases/index.json` without
`Access-Control-Allow-Origin`, so browser `fetch()` from xiom-lang.org is
blocked; the versions page used to show "could not load mirror data" while
the download page silently used its GitHub API fallback. Both pages now try
the mirror first and fall back to `api.github.com/repos/xiom-lang/xiom`
(which sends CORS), then to static links. Proper fix: add
`add_header Access-Control-Allow-Origin "https://xiom-lang.org";` (or `*`)
for the JSON paths in the mirror nginx config; the pages pick the mirror up
automatically once the header exists.

Rules: ASCII-only; never hardcode versions (read mirror JSON); pin GitHub
Actions refs to full SHAs; commit identity is repo-local (Lefteris Notas
<lefterisnotas@gmail.com>); DCO is now a required check on main -- sign
commits with `git commit -s`; keep the site static and honest - no claim the
implementation does not support.
```
