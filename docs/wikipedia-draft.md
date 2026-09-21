<!--
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Wikipedia planning notes: XIOM (programming language)

This file is an internal planning and fact sheet, NOT article text. It is not
published by the website or the docs pipeline.

Hard rules for the Wikipedia submission:

1. Do not submit AI-generated prose. Wikipedia's LLM guideline prohibits
   using large language models to generate or rewrite article content (narrow
   exceptions such as copyediting and translation aside), and unreviewed LLM
   output is a speedy-deletion criterion. The earlier prose draft in this file
   was AI-assisted and must not be pasted into Wikipedia. Write the article
   yourself, in your own words, from the facts below; if you want the facts
   checked, ask someone to review the sources, not to write sentences.
2. Notability gate. Wikipedia needs significant coverage in independent,
   reliable, secondary sources. A conference talk, an article in the
   technology press (LWN, InfoQ and similar), or a paper by authors not
   affiliated with the project would count. Project posts, forum threads and
   grant pages do not. Until at least two or three such sources exist, do not
   submit; repeated submissions by the founder can be seen as promotional.
3. Conflict of interest. Disclose the connection on your user page (WP:COI,
   WP:PAID), create the page through the Articles for Creation wizard, and
   never create it directly or move it to mainspace yourself. An independent
   editor writing the page is the ideal outcome.
4. Let AfC add its own banners. Do not add {{Draft article}} or similar
   yourself; the wizard and reviewers handle the templates.

## Reviewer feedback from round 1 and how it is resolved here

| Feedback | Resolution |
|---|---|
| Infobox `first appeared` does not render; template documents `released` / `year` | Use `released` for the initial public release and `latest release version` / `latest release date` only when written. |
| Date story inconsistent (June 30 appearance vs July public release; 0.50.0 called "stable") | One story: the first public release was 0.50.0 in July 2026. Internal milestones such as the 2026-06-30 v0.1.0 build are pre-public history and, if mentioned at all, must be described that way. Do not call a 0.x release "stable". |
| Z3 claim overstated | Correct nuance: runtime contract guards are shipped; `--verify` exports proof obligations as SMT-LIB and `xiom-verify --check` checks them with the bundled z3 (only `unsat` counts as proved). Automatic in-compiler static proof is still planned. See the contracts guide, which says static proof is planned. |
| Verify release-stripping, Send/Sync, second-class references, signed registry | All four are documented shipped behavior: contracts strip in release unless `--runtime-contracts`; `Send`/`Sync` are compile-time checked; references cannot be returned or stored (no lifetime annotations); the registry verifies ed25519 signatures and aborts on mismatch. Cite the specific guide pages. |
| Citations need publisher, date and archive links | Use `{{cite web}}` with `publisher`, `date` where known, `access-date`, and an `archive-url` once a snapshot exists. All URLs below resolved on 2026-09-21. |
| `{{Draft article}}` | Removed; use the AfC wizard. |

## Verified facts and sources (all checked 2026-09-21)

Every source below is primary (project-controlled). That is why the page cannot
be submitted yet.

| Fact | Source | URL | Status |
|---|---|---|---|
| Language site; project identity, goals | XIOM project | https://xiom-lang.org/ | 200 |
| Released versions and dates | XIOM versions page (reads the download mirror) | https://xiom-lang.org/versions.html | 200 |
| Development history and milestones | XIOM history page | https://xiom-lang.org/history.html | 200 |
| Current status and next work | XIOM roadmap page | https://xiom-lang.org/roadmap.html | 200 |
| Ownership, lexical-scope borrowing, second-class references, Send/Sync | Documentation: memory model | https://docs.xiom-lang.org/latest/memory-model/ | 200 |
| Contracts: runtime guards by default; static proof planned; export/check tooling | Documentation: contracts | https://docs.xiom-lang.org/latest/contracts/ | 200 |
| Confined unsafe blocks, guard heap, fault trapping, retry | Documentation: unsafe | https://docs.xiom-lang.org/latest/unsafe/ | 200 |
| Compiler flags: release stripping, verification export, targets | Documentation: compiler | https://docs.xiom-lang.org/latest/compiler/ | 200 |
| Signed packages, pinned keys, fail-closed installs | Documentation: package registry | https://docs.xiom-lang.org/latest/registry/ | 200 |
| Dual licensing, no CLA, DCO sign-off | Licensing policy (public) | https://github.com/xiom-lang/.github/blob/main/docs/LICENSING.md | 200 |
| Contribution process, governance | Organization docs (public) | https://github.com/xiom-lang/.github/blob/main/CONTRIBUTING.md | 200 |
| Compiler repository | Source repository | https://github.com/xiom-lang/xiom | 200 |
| Package registry (early; few packages) | Registry service | https://registry.xiom-lang.org | 200 |
| Browser playground | Playground | https://playground.xiom-lang.org | 200 |

## Section skeleton for a human-written article

Use these headings; write the sentences yourself from the table above and from
whatever independent sources you eventually have.

- Lead (what XIOM is, who designs it, what makes it distinct, first public release)
- History (pre-public milestones, first public release, later releases)
- Design
  - Memory model
  - Contracts
  - Unsafe code
  - Other language features
- Tooling
- Licensing
- Reception (only with independent sources; leave out otherwise)
- See also
- References
- External links

Candidate title: XIOM (programming language)

Candidate categories (enable only after a mainspace move):
Programming languages created in 2026; Systems programming languages;
Statically typed programming languages; Free software programmed in Rust.
