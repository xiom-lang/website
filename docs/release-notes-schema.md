<!--
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Release notes contract ("What's new")

This file is the contract between the release pipeline (compiler and stdlib
repositories, mirror) and the website. It is not built into the site; it is
the reference the lane relays quote. Schema version: **1**.

## Purpose

Give users a short, user-facing "what changed for me" document per toolchain
release, separate from the technical changelog. The changelog stays on GitHub;
this document is what the website renders on the download and versions pages.

## Artifact

One JSON document per release tag:

- Canonical URL (mirror): `https://dl.xiom-lang.org/releases/<tag>/release.json`
- Fallback URL (tag-pinned, CORS-enabled): `https://raw.githubusercontent.com/xiom-lang/xiom/<tag>/release-notes/<tag>.json`

Both copies are byte-identical and immutable once published. The generated
JSON is committed to the compiler repository **before** the tag is created so
the raw fallback exists at the tag; the mirror copy is published from that
same file.

## Schema

```json
{
  "schema": 1,
  "tag": "v0.61.4",
  "published": "2026-09-25T10:00:00Z",
  "summary": "One sentence for users, plain text, at most 240 characters.",
  "highlights": [
    {
      "kind": "language",
      "title": "At most 60 characters",
      "text": "One or two sentences of plain text, at most 320 characters."
    }
  ],
  "breaking": [],
  "known_issues": [],
  "docs": [
    { "title": "Contracts guide", "url": "https://docs.xiom-lang.org/latest/contracts/" }
  ],
  "full_changelog": "https://github.com/xiom-lang/xiom/releases/tag/v0.61.4"
}
```

### Field rules

| Field | Required | Rules |
|-------|----------|-------|
| `schema` | yes | Must be `1`. A shape change bumps this and the site ignores unknown versions. |
| `tag` | yes | Must equal the release tag, `vX.Y.Z` (suffix allowed). |
| `published` | no | ISO 8601; the site falls back to the mirror's date. |
| `summary` | yes | Plain text, 1-240 characters, one sentence, no version number inside. |
| `highlights` | yes | 1-6 items. `kind` in `language`, `compiler`, `stdlib`, `tooling`, `fix`, `security`. `title` 1-60, `text` 1-320. |
| `breaking` | yes | Array; `[]` means "no breaking changes" and is the only way to say it. Each item 1-240 characters. |
| `known_issues` | no | Array; each item 1-240 characters. |
| `docs` | no | 0-6 entries with `title` (1-60) and an `https://` URL. |
| `full_changelog` | yes | `https://` URL to the GitHub release. |

Content rules: plain text only -- no HTML, no markdown, no emoji, ASCII only.
No internal identifiers (task IDs, wave names, commit hashes). Write for a
user deciding whether to upgrade. The breaking-changes field is the most
trusted line on the page; fill it even when empty.

## Authoring template (compiler repository)

Authoring happens in `release-notes/<tag>.md`, converted and validated by the
release step:

```md
# v0.61.4

## Summary
One sentence for users.

## Highlights

### Explicit generic arguments
kind: language
You can now write parse[Int](s) and the type argument is checked.

### Faster incremental builds
kind: compiler
Unchanged files are skipped through the IR cache.

## Breaking changes
- None.

## Known issues
- None.

## Docs
- Contracts guide | https://docs.xiom-lang.org/latest/contracts/
```

Converter rules: `###` blocks are highlights; the `kind:` line sets the tag;
the body is the text. Under "Breaking changes", the single item `None.` means
`[]`. Under "Docs", each line is `Title | URL`.

## Stdlib fragment (stdlib repository)

The stdlib repository provides `release-notes/<tag>.md` with a **Summary**
section (optional) and a **Highlights** section using the same `###` block
format. The converter merges its highlights with `kind: "stdlib"` unless the
fragment names a different kind. The pinned stdlib ref is read from
`STDLIB_VERSION` at conversion time.

## Pipeline requirements

1. Convert and validate on every release; the release fails on any schema
   violation, missing summary, more than six highlights, over-long field, or
   missing `breaking` section.
2. Commit `release-notes/<tag>.json` before creating the tag.
3. Publish the same file to `dl.xiom-lang.org/releases/<tag>/release.json`.
4. Add `"notes": true` to that release's entry in `releases/index.json` so the
   website can avoid requests for tags without notes (the site also works when
   the field is absent -- it just tries once).
5. `latest.json` keeps its current shape; the site resolves notes by tag.

## Website behavior (already implemented)

- Download page: a "What's new" panel for the current release (summary, kind
  chips, highlights, upgrade notes or "no breaking changes", docs links, full
  changelog).
- Versions page: the current-release card shows up to three highlights; every
  release row with notes has a lazy "what's new" disclosure.
- Sources tried in order per tag: mirror, then the tag-pinned raw file. If
  neither exists or a document fails validation, the page shows only the
  changelog link -- never invented content.
- All rendered from `textContent`; documents are treated as untrusted data.
- Lookups are cached for ten minutes in `sessionStorage`.
