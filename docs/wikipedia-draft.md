<!--
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Wikipedia draft: XIOM (programming language)

This file is a paste-ready wikitext draft. It is NOT published by the website
or the docs pipeline; it exists so the owner can submit it to Wikipedia.

Read this before pasting:

1. Notability. Wikipedia requires significant coverage in independent,
   reliable, secondary sources (WP:GNG, WP:NPRODUCT). As of 2026-09-21 no such
   coverage is known to exist; every source below is primary (the project's own
   repositories and site). A draft submitted in this state will be declined.
   Wait until at least two or three independent articles, papers or books
   discuss XIOM in depth, then cite them.
2. Conflict of interest. If you are connected to the project, disclose it on
   your user page (WP:COI, WP:PAID) and use the Articles for Creation wizard
   (Draft:XIOM (programming language)). Do not create the article directly and
   do not remove maintenance templates.
3. Neutrality. The wikitext below is deliberately flat and sourced. Keep it
   that way; do not add marketing adjectives, benchmarks, or unsourced claims.
4. Versions. Wikipedia wants a released version with a source. Pull the current
   tag and date from https://xiom-lang.org/versions.html (the mirror JSON is
   authoritative) and cite the mirror, not this repository.

--- paste below this line ---

{{Draft article}}
{{Primary sources|date=September 2026}}
{{Infobox programming language
| name                   = XIOM
| logo                   = <!-- File:XIOM logo.svg, only if a free-licensed file exists on Commons -->
| paradigm               = [[Multi-paradigm programming language|Multi-paradigm]]: [[Imperative programming|imperative]], [[Procedural programming|procedural]], [[Generic programming|generic]]
| designer               = Eleftherios Notas
| developer              = The XIOM Authors
| first appeared         = {{Start date and age|2026|06|30}}
| latest release version = <!-- fill from the release mirror -->
| latest release date    = <!-- fill from the release mirror -->
| typing                 = [[Static typing|Static]], [[Type inference|inferred]], [[Nominal typing|nominal]] with [[Structural type system|structural]] interfaces
| memory management      = [[Ownership (programming)|Ownership]] and lexical-scope borrowing; no garbage collector
| platform               = [[x86-64]], [[AArch64]], [[WebAssembly]]
| license                = [[MIT License|MIT]] or [[Apache License 2.0|Apache-2.0]] (dual)
| file ext               = .xi
| website                = {{URL|https://xiom-lang.org}}
| influenced by          = [[Rust (programming language)|Rust]], [[Eiffel (programming language)|Eiffel]], [[Ada (programming language)|Ada]]/[[SPARK (programming language)|SPARK]], [[Dafny (programming language)|Dafny]], [[Frama-C]]
}}

'''XIOM''' is a [[statically typed]], [[compiled language|compiled]] [[systems programming language]].<ref name="site">{{cite web |title=XIOM |url=https://xiom-lang.org/ |access-date=2026-09-21}}</ref> It combines ownership-based memory management, [[design by contract|contract]] clauses, and [[monomorphization|monomorphised]] generics, and compiles to native code through [[LLVM]] and to [[WebAssembly]].<ref name="docs">{{cite web |title=XIOM documentation: language guide |url=https://docs.xiom-lang.org/ |access-date=2026-09-21}}</ref> The first public release was published in July 2026.<ref name="roadmap">{{cite web |title=XIOM roadmap |url=https://xiom-lang.org/roadmap.html |access-date=2026-09-21}}</ref>

== History ==
Development began in 2026, and version 0.1.0 (2026-06-30) established an end-to-end pipeline from source text through a lexer, parser, type checker and [[LLVM IR]] to native and WebAssembly output.<ref name="history">{{cite web |title=XIOM history |url=https://xiom-lang.org/history.html |access-date=2026-09-21}}</ref> Version 0.2.0 added the ownership and borrow checker, contract clauses, generics with inline constraints, modules and a standard library.<ref name="history" /> The first stable public release, 0.50.0 (2026-07-25), added scripting and [[Just-in-time compilation|JIT]] execution, editor tooling and release automation.<ref name="roadmap" /> Later releases added a package registry, compiler-assisted diagnostics, a confined model for `unsafe` code, and a repository split between the compiler and the standard library.<ref name="history" />

The compiler itself is written in [[Rust (programming language)|Rust]].<ref name="repo">{{cite web |title=xiom-lang/xiom repository |url=https://github.com/xiom-lang/xiom |access-date=2026-09-21}}</ref> Self-hosting, compiling the compiler with itself, is a stated long-term goal; as of 2026 no self-hosted release has been published.<ref name="history" />

== Design ==

=== Memory model ===
XIOM uses ownership with lexical-scope borrowing and requires no [[Garbage collection (computer science)|garbage collector]].<ref name="memory">{{cite web |title=XIOM documentation: memory model |url=https://docs.xiom-lang.org/memory-model/ |access-date=2026-09-21}}</ref> References are second-class: they cannot be returned from a function or stored in a struct field, so the language has no lifetime annotations. Patterns that require escaping borrows are expressed with owned values. `Send` and `Sync` are checked at compile time.<ref name="memory" />

=== Contracts ===
Functions may declare `requires` and `ensures` clauses, and types may declare `invariant` clauses.<ref name="contracts">{{cite web |title=XIOM documentation: contracts |url=https://docs.xiom-lang.org/contracts/ |access-date=2026-09-21}}</ref> Contracts are enforced at runtime by default and can be compiled out of release builds; the toolchain can also export a subset of proof obligations as [[SMT-LIB]] and check them with an embedded [[Z3 (solver)|Z3]] solver, reporting only an `unsat` result as proved.<ref name="contracts" />

=== Unsafe code ===
`unsafe` applies only to block expressions. Each block is treated as a confined transaction: allocations are isolated, faults are trapped, and values that would escape the block are rejected by the compiler.<ref name="unsafe">{{cite web |title=XIOM documentation: unsafe |url=https://docs.xiom-lang.org/unsafe/ |access-date=2026-09-21}}</ref>

=== Other features ===
The language includes [[pattern matching]], structural interfaces without an `implements` keyword, `Result` and `Option` types in place of [[Exception handling|exceptions]] and null, modules with explicit imports, and compile-time evaluation.<ref name="docs" /> The compiler targets native code, WebAssembly, and other back ends through LLVM.<ref name="repo" />

== Tooling ==
The toolchain includes a compiler driver, a [[Language Server Protocol|language server]], a debugger, a formatter, a documentation generator, and a package manager that uses a signed package registry.<ref name="repo" /><ref name="registry">{{cite web |title=XIOM package registry |url=https://registry.xiom-lang.org |access-date=2026-09-21}}</ref> A browser playground and a versioned documentation site are also available.<ref name="playground">{{cite web |title=XIOM playground |url=https://playground.xiom-lang.org |access-date=2026-09-21}}</ref>

== Licensing ==
The compiler, standard library, registry, website and playground are dual-licensed under the [[MIT License]] or [[Apache License 2.0]], at the user's option, with inbound contributions under the same terms and a [[Developer Certificate of Origin]] sign-off instead of a contributor license agreement.<ref name="license">{{cite web |title=XIOM licensing policy |url=https://github.com/xiom-lang/.github/blob/main/docs/LICENSING.md |access-date=2026-09-21}}</ref>

== Reception ==
<!-- Do not write this section without independent, reliable sources.
     Acceptable examples: technology press coverage, peer-reviewed papers,
     books, or reviews that do not originate from the project. -->

== See also ==
* [[Design by contract]]
* [[Ownership (programming)]]
* [[Rust (programming language)]]
* [[Dafny (programming language)]]
* [[SPARK (programming language)]]

== References ==
{{reflist}}

== External links ==
* {{Official website|https://xiom-lang.org}}

<!-- Categories: only enable these when the draft is accepted and moved to
     mainspace. Wikipedia does not want draft categories live.
[[Category:Programming languages created in 2026]]
[[Category:Systems programming languages]]
[[Category:Statically typed programming languages]]
[[Category:Free software programmed in Rust]]
-->
