# XIOM Website -- Content Spec (Pages, Copy, Naming & Licensing)

> Companion to the xiom-landing.html mockup. That file covers visual design;
> this document covers site structure, page-by-page copy direction, and the
> naming/copyright questions raised separately.

---

## Part 1 -- Naming & Copyright Holder

### Lefteris Notas vs. Eleftherios Notas

**Recommendation: use both, in the right place for each.**

- **Public-facing brand name (website, social, talks, README "created by" line):**
  `Lefteris Notas` -- this is consistent with how you already operate
  Lakeside Games and Ngonart publicly, and it's the name people will
  search for and recognize.
- **Legal/copyright line (license file, copyright notice):**
  `Eleftherios Notas - XIOM Foundation` -- copyright notices carry more
  legal weight when they match the actual rights holder, and keeping the
  legal name alongside the foundation preserves the authorship
  attribution. Many public figures do exactly this split (public byline
  vs. legal copyright holder) without any conflict -- it's not unusual or
  risky to use both.

The LICENSE file carries the full legal copyright line
(`Eleftherios Notas - XIOM Foundation`), with `Lefteris Notas` used
everywhere else.

### Copyright holder vs. Ngonart OU

**Recommendation: copyright holder is `Eleftherios Notas - XIOM Foundation`, not Ngonart OU.**

XIOM is not currently a Ngonart business work product -- Ngonart is the
publishing/B2B outsourcing entity for game dev contracting, and XIOM
doesn't sit inside that business activity as a matter of fact. Putting the
company down as copyright holder when it didn't commission, fund, or own
the work creates a mismatch between the legal claim and reality -- this
matters if ownership is ever questioned (contributor dispute, wanting to
later relicense or spin the project out differently than Ngonart's other
dealings).

Bringing XIOM formally into Ngonart as a company asset is a real option
later, but it's a deliberate business decision with real implications
(Estonian corporate tax treatment, the company owning what's currently
your personal project, needing internal docs if you ever want to spin it
out) -- not something to back into casually via a copyright line.

**Split recommendation:**
- **Copyright holder:** `Eleftherios Notas - XIOM Foundation`
- **Public "built by" / attribution line:** Ngonart can still show up here
  without being the legal IP owner -- e.g. *"XIOM is an independent
  project by Lefteris Notas, founder of Ngonart OU."* This gets the brand
  association without the legal commitment.

**Why this matters for open source specifically:** contributors and the
wider ecosystem generally trust non-corporate maintainer copyright over
corporate copyright for community language projects -- it signals the
project won't get acquired, relicensed, or shut down by a corporate
decision (a real, well-known concern after several high-profile
"company relicensed the open-source project" controversies). Foundation
copyright with Ngonart as a visible-but-separate brand association is the
stronger trust signal here, not a weaker one.

Copyright now rests with `Eleftherios Notas - XIOM Foundation` -- the
dedicated-foundation pattern (Rust Foundation, Python Software Foundation
model) rather than a company holding the IP.

---

## Part 2 -- Copyright Notice & License Block

XIOM is licensed under the Apache License, Version 2.0. Here's the standard
block structure to include in the repo and reference on the website footer.

**LICENSE file (repo root):**
- `LICENSE` -- Apache License, Version 2.0

**Copyright line -- `Eleftherios Notas - XIOM Foundation`, not Ngonart OU, per Part 1:**

Source file headers:

```
Copyright (c) 2026 Eleftherios Notas - XIOM Foundation
```

LICENSE appendix boilerplate (canonical Apache form, no `(c)`):

```
Copyright 2026 Eleftherios Notas - XIOM Foundation
```

**README / website footer short form -- attribution can name Ngonart:**

```
XIOM is licensed under Apache-2.0.
Copyright (c) 2026 Eleftherios Notas - XIOM Foundation.

XIOM is an independent project by Lefteris Notas, founder of Ngonart OU.
```

**If/when the Godot-derived showcase work ships**, add a separate notice
file acknowledging that, since it's a different obligation than your own
copyright line:

```
THIRD-PARTY-NOTICES.md

This project references the Godot Engine (https://godotengine.org),
Copyright (c) 2014-present Godot Engine contributors, MIT License,
as architectural reference for select subsystems re-implemented in XIOM.
"Godot" and "Godot Engine" are trademarks of the Godot Foundation;
no affiliation or endorsement is implied.
```

Not legal advice -- worth a lawyer pass before public launch given the
dual-entity structure (Lakeside Games / Ngonart) already in play.

---

## Part 3 -- Site Structure (Information Architecture)

```
/                    Home
/why                 Purpose / philosophy (from XIOM_Purpose.md)
/spec                Language Reference (from XIOM_Language_Spec.md)
/install              Get XIOM -- binaries + build from source
/docs                Documentation hub (stub until Phase 1.5/2 docs exist)
/roadmap             Build strategy, phase status (public-safe excerpt)
/showcase            XiomVDB / XiomDB project pages (stub until built)
/blog                Optional -- dev log / progress updates
/github              External link, not a page
```

Keep this shallow for now. A pre-1.0 language site with ten thin pages
looks worse than one with five substantial ones -- expand as Phase 2/3
content actually exists, don't pad early.

---

## Part 4 -- Page-by-Page Spec

### `/` -- Home

**Job:** convey the one-sentence thesis fast, prove it with the live
contract demo (already built), get the right two audiences to their next
step (curious-but-skeptical engineers -> `/why`; ready-to-try -> `/install`).

**Sections (maps to the existing HTML mockup):**
1. Hero -- headline, lede, two CTAs (`Read the purpose`, `See build status`)
2. Proof panel -- the animated contract demo (already built)
3. Three Pillars (SAFE / VERIFIED / PRECISE)
4. Idea excerpt -- 2-3 short paragraphs pulled from Purpose.md, with a
   "Read the full purpose ->" link to `/why`
5. Ownership demo -- the lexical scope borrowing example (already built)
6. Roadmap strip -- phase status, links to `/roadmap` for detail
7. Footer -- license line, copyright, links

**Do not put full spec text on the homepage.** It's a landing page, not
documentation -- link out to `/spec` and `/why` for depth.

---

### `/why` -- Purpose & Philosophy

**Source:** XIOM_Purpose.md, lightly adapted for web reading (shorter
paragraphs, the existing table-based comparisons translate well to styled
cards using the same visual system as the homepage).

**Structure:**
- The Problem
- The Idea ("Specification and implementation must be the same artifact")
- Why AI Changes the Game
- Why Now
- What XIOM Is Not (good to keep -- scope clarity builds credibility)
- The Three Pillars (can also live partially on Home, full detail here)

This page can be close to a direct, reformatted port of your existing
Purpose document -- it's already well-written and doesn't need much
rewriting, just web typography.

---

### `/spec` -- Language Reference

**Source:** XIOM_Language_Spec.md.

**Recommendation:** don't hand-port this as one long page. Once the spec
stabilizes post-Phase 1.5, structure it as a sidebar-navigated reference
(similar to Rust's or Go's language reference sites) -- sections like
Types, Ownership & Borrowing, Contracts, Generics, Error Handling, FFI.

**For now (pre-Phase 2), a single page with a table of contents anchor
sidebar is enough** -- don't over-invest in reference-site tooling before
the spec itself is done changing.

---

### `/install` -- Get XIOM

Maps directly to the distribution model recommendation already written up.

**Structure:**
1. Primary CTA -- one-line installer command, big and obvious (the
   `curl | sh` style command), with OS auto-detection if feasible
2. Platform package alternatives (`.msi`, `.pkg`, `.deb`/`.rpm`) below the
   fold, secondary weight
3. "Build from source" section, clearly secondary -- repo link + build
   command, framed as "if you need to build from source (CI, packaging,
   policy reasons), here's how"
4. Verify installation -- `xiom --version`, "Hello World" quick-start

**Honest caveat to include on this page until it's true:** if binaries
aren't ready yet (pre-Phase 2/3), this page should say so plainly --
"XIOM is pre-release. Build from source today; pre-built binaries are
planned for Phase 3" -- rather than implying a download exists. Credibility
with a developer audience depends on this kind of plain status honesty.

---

### `/roadmap` -- Build Strategy (Public Excerpt)

**Source:** XIOM_Build_Strategy.md, but **not the whole document
published verbatim** -- that file includes internal decision-log detail
(rationale tables, rejected alternatives, toolchain choices) that's useful
for you and contributors but noisy for a general visitor.

**Recommendation:** public version = the Build Order section (Phase 0
through 3, condensed) + current status, styled like the timeline already
in the HTML mockup, expanded to a full page. Link to the full internal
doc on GitHub for anyone who wants the detailed decision log -- that
audience exists (other language designers, serious contributors) but
isn't the homepage audience.

---

### `/showcase` -- XiomVDB / XiomDB

**Status: stub until something real exists to show.**

**Recommendation:** don't build this page with placeholder content now --
an empty "coming soon" page undersells a pre-1.0 language more than no
page at all. Add it when XiomVDB has something demonstrable (even a
basic insert/query benchmark), per the sequencing already agreed --
XiomVDB first, this page follows that milestone, not the website
timeline.

---

### `/blog` (optional)

**Recommendation: yes, but only if you'll actually keep it updated.**
A language at this stage benefits more from visible momentum (dev log
style posts: "Phase 1.5 gardening, week 3" / "what self-hosting broke and
how we fixed it") than from a polished-but-static site. This is also
exactly the kind of "watching it survive contact with real use" signal
that builds the credibility discussed earlier re: long-term adoption.
If you don't have bandwidth to post regularly, skip it rather than let
it visibly go stale -- a dead blog reads worse than no blog.

---

## Part 5 -- Tone & Copy Guidelines (for whoever writes/edits page copy)

- Match the existing Purpose doc's voice: direct, confident, no hype
  words ("revolutionary," "next-generation," "game-changing") -- the
  existing docs already avoid this well, keep that discipline on the
  website.
- Every claim should be either true today or clearly marked as
  planned/Phase N -- the "What XIOM Is Not" section's honesty about scope
  is a real asset; the website should carry that same restraint rather
  than overselling.
- Code examples throughout should come directly from the actual spec /
  build strategy docs, not invented for marketing -- keeps the site
  honest and saves rewrite work later when the spec evolves.

---

## Summary Table

| Page | Status now | Primary source |
|---|---|---|
| `/` | Build now | New copy + existing HTML mockup |
| `/why` | Build now | XIOM_Purpose.md (light edit) |
| `/spec` | Build now, simple version | XIOM_Language_Spec.md |
| `/install` | Build now, with honest pre-release notice | XIOM_CrossPlatform_Distribution.md |
| `/roadmap` | Build now, condensed | XIOM_Build_Strategy.md (public excerpt) |
| `/showcase` | Wait for XiomVDB | -- |
| `/blog` | Optional, only if maintained | -- |

---

*Companion to xiom-landing.html, XIOM_Build_Strategy.md,
XIOM_CrossPlatform_Distribution.md.*
