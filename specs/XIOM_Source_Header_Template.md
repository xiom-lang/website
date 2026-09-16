# XIOM -- Source File Header Template

> Standard comment block to add above source files in the XIOM codebase.
> Two versions below: full (for primary/original files) and short (for
> most files, to avoid clutter). Use `//` since XIOM follows C-family
> comment syntax per the existing spec examples.

---

## Short version (default -- use this on most files)

```
// XIOM -- [component name, e.g. Lexer / Parser / Type Checker]
// Copyright (c) 2026 Eleftherios Notas
// Licensed under the MIT or Apache-2.0 license, at your option.
// See LICENSE-MIT and LICENSE-APACHE in the project root.
```

---

## Full version (use once, at the top of `main.rs`/entry point, or in a
## small number of canonical files -- not needed on every file)

```
// XIOM Programming Language
// -----------------------------------------------------------------------
// Copyright (c) 2026 Eleftherios Notas
//
// XIOM is an independent project by Lefteris Notas, founder of Ngonart OU.
//
// Licensed under the MIT license <LICENSE-MIT or https://opensource.org/licenses/MIT>
// or the Apache License, Version 2.0 <LICENSE-APACHE or
// https://www.apache.org/licenses/LICENSE-2.0>, at your option.
//
// This file may not be copied, modified, or distributed except according
// to those terms.
// -----------------------------------------------------------------------
```

---

## Variant for files derived from Godot reference (once that work begins)

Use this **in addition to** the short version, only on files where Godot's
source was used as architectural reference per the earlier discussion --
not on unrelated XIOM files.

```
// XIOM -- [component name]
// Copyright (c) 2026 Eleftherios Notas
// Licensed under the MIT or Apache-2.0 license, at your option.
//
// Portions of this file reference the Godot Engine (https://godotengine.org),
// Copyright (c) 2014-present Godot Engine contributors, MIT License.
// See THIRD-PARTY-NOTICES.md for full attribution.
// "Godot" and "Godot Engine" are trademarks of the Godot Foundation;
// no affiliation or endorsement is implied.
```

---

## Where each goes

| File type | Header to use |
|---|---|
| Most source files (lexer, parser, codegen, stdlib, etc.) | Short version |
| Entry point / one or two canonical project files | Full version |
| Any file built with Godot source as reference | Short version + Godot variant |
| Generated files (build output, codegen artifacts) | None -- generated files shouldn't carry hand-written headers |

---

## One practical note

Don't over-apply this. A header on every single file in a large codebase
becomes noise, and is also extra surface area to keep in sync if the
license or copyright year ever changes. The short version is intentionally
terse for that reason -- it's enough to assert copyright and point to the
real LICENSE files, without repeating the full legal text everywhere.

---

*Companion to XIOM_Website_Content_Spec.md (Part 1 & 2 -- naming and
copyright holder decisions).*
