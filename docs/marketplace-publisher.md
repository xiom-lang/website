<!--
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Marketplace publisher description

Copy blocks for IDE marketplace listings (Visual Studio Marketplace,
Open VSX, JetBrains Marketplace). Keep every claim to what the released
toolchain does; the project is pre-beta and the standard library is beta.

## Publisher / vendor display name

```
XIOM
```

If a longer vendor name is required, use `The XIOM Authors`.

## Tagline (one line, about 55 characters)

```
Compiled, contract-first, memory-safe systems language
```

## Short description (193 characters, extension listing)

```
XIOM language support: syntax highlighting, diagnostics, formatting and a
language server for the contract-first XIOM systems language. Installs
alongside the XIOM toolchain from xiom-lang.org.
```

Character count: 193 with the line break collapsed to a space. Trim the last
sentence if the field is tighter.

## Publisher About (about 70 words)

```
XIOM is an open-source systems programming language with ownership-based
memory safety, Design by Contract clauses in the core language, and native
plus WebAssembly output. The project is pre-beta: the compiler and tooling
are usable, and the standard library is beta. The editor extensions connect
to the toolchain you install from xiom-lang.org (compiler, language server,
debugger, formatter), and never bundle a second copy of it. Licensed
MIT OR Apache-2.0.
```

## Keywords / tags

```
xiom, systems programming, language server, lsp, contracts, design by
contract, memory safety, compiler, llvm, wasm
```

## Links to include on the listing

```
Homepage:    https://xiom-lang.org
Docs:        https://docs.xiom-lang.org
Repository:  https://github.com/xiom-lang/xiom
Registry:    https://registry.xiom-lang.org
Issues:      https://github.com/xiom-lang/xiom/issues
```

## Legal line for the listing footer

```
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors. Dual-licensed
MIT or Apache-2.0, at your option.
```

## Notes

- Do not name the XIOM Foundation as the holder; the copyright line above is
  the current policy.
- Do not state a version number in the listing text; the marketplace shows
  the version that is actually published.
- The editor extension requires the official toolchain first; make that the
  first prerequisite line in every install section.
