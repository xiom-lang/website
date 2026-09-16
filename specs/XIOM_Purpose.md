<!--
Copyright (c) 2026 Eleftherios Notas and XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
**XIOM**

Why We Are Building This Language

Purpose  -  Motivation  -  Idea

# The Problem

Programming languages have not kept up with how software is actually written today.

Most code is no longer written by a single engineer who holds the entire system in their head. It is written by teams, maintained by people who did not write it, generated in part by AI tools, and deployed to environments that did not exist when the language was designed. Yet the dominant systems languages -- C, C++, and even Rust -- were designed for a world where a human expert reads every line before it runs.

|  | *The contract between the programmer and the compiler has not changed since 1972. We think it should.* |
| :---- | :---- |

The consequences are visible everywhere:

- Memory bugs that have existed for decades because the language cannot express the intent clearly enough for the compiler to catch them
- AI-generated code that compiles and passes tests but violates assumptions the author never wrote down
- Interfaces documented in comments that no toolchain enforces
- Languages so complex that even expert programmers cannot reason about all the corner cases

We are not building XIOM because we think all existing languages are bad. We are building it because we believe one specific gap has never been properly closed: **the gap between what a programmer intends and what the compiler can verify.**

# The Idea

XIOM is built on one core conviction:

|  | *Specification and implementation must be the same artifact.* |
| :---- | :---- |

In every language today, the specification for a function lives in documentation, in comments, in test files, in the programmer's head -- everywhere except the one place the compiler can read it. XIOM puts the specification inside the function signature, where it belongs, in a form the compiler can reason about.

A function that requires its input to be non-zero says so. A function that guarantees its output is sorted says so. A type that must never hold a negative value says so. These are not assertions that crash at runtime. They are contracts that the compiler enforces.

| Specification | Verification | Trust |
| :---- | :---- | :---- |
| Pre-conditions, post-conditions, and invariants written directly in the language. | The compiler enforces contracts at minimum via runtime guards with precise error messages. Static proof is a planned later phase. | When a contract passes, you trust the output -- human written or AI generated. |

This matters most when code is not written by a human expert. When AI generates a function, or a junior engineer modifies one, or a library is updated by someone who did not write the original -- the contract layer catches what code review misses. Not because the reviewer is negligent, but because the compiler never gets tired, never assumes, and never skips a case.

# Why AI Changes The Game

AI is writing significant amounts of production code. This is not a prediction. It is happening. The tooling to verify AI-generated code at the language level does not yet exist. Every AI coding tool today produces output that must be manually reviewed by a human who understands what the code was supposed to do. That does not scale.

Code review cannot be the only safety layer when the volume of generated code exceeds what humans can read. The safety must move into the language itself. Contracts are the mechanism:

- AI writes a function with stated intent (`requires` and `ensures`)
- The compiler checks the implementation against that intent
- Violations are caught at compile time or the first test run -- not in production
- The contract is machine-readable, so the AI itself can reason about it when composing functions

This is not about making AI better at writing code. It is about making the output **verifiable by construction** rather than by human review. The compiler becomes the reviewer. The contract is the review specification.

# Why Now

Two things are true simultaneously that were not both true before:

First -- AI is writing significant amounts of production code. The tooling to verify AI-generated code at the language level does not yet exist.

Second -- the infrastructure to build a new language properly now exists in a way it did not twenty years ago. LLVM means we do not need to write a backend for every CPU architecture. SMT solvers like Z3 are mature enough to power a practical contract verification system when the language is ready for static proof. WebAssembly means a new language can target virtually every compute environment from day one without platform-specific work.

|  | *The right time to build this language was ten years ago. The second best time is now.* |
| :---- | :---- |

# What XIOM Is Not

Being clear about scope is part of the idea.

- **XIOM is not a research language.** It is designed to be used in production by working programmers.
- **XIOM is not a domain-specific language.** It has no built-in primitives for graphics, networking, AI, or any other application area. Those are libraries.
- **XIOM is not a replacement for Python or JavaScript for rapid prototyping.** It is a systems language. It competes with Rust, Zig, and C++ -- not with scripting languages.
- **XIOM is not trying to be the only language.** Good languages coexist. C FFI means XIOM works alongside everything that already exists.
- **XIOM is not finished.** This document describes the intention. The language is being built.

# The Three Pillars

In plain terms: *build a language where correct code is easier to write than incorrect code.*

Not through restrictions that make the language painful to use. Through a design where expressing intent is natural, and the compiler uses that expressed intent to find problems before they ship.

The three properties we will not compromise on:

| SAFE | VERIFIED | PRECISE |
| :---- | :---- | :---- |
| No garbage collector. No null. No hidden allocations. Memory behaviour is explicit and deterministic. Ownership with lexical scope borrowing -- simpler than Rust, same safety guarantee. | Contracts are part of the language, not the documentation. The compiler is the verifier. Runtime guards from Phase 1. Static proof from Phase 3. | One way to write each thing. No implicit behaviour. No surprising control flow. What you read is what runs. `derive` handles the boilerplate that AI and humans both get wrong. |

Everything else -- syntax choices, standard library scope, toolchain features -- can be debated and revised. These three cannot.

# Summary

Existing languages were designed for a world where a human expert reads every line. That world is changing. Code is increasingly written by teams, maintained by people who did not write it, and generated by AI tools that produce syntactically correct output with no understanding of intent.

XIOM is our answer to that shift. A systems programming language where intent is expressed in the language itself -- not in comments, not in tests, not in documentation -- and where the compiler verifies that intent before the code ever runs.

We are building it because the gap between what a programmer means and what the compiler checks is where most serious bugs live. Closing that gap, for human and AI written code alike, is the purpose of XIOM.

---

**XIOM -- Purpose Document**

This document describes intent. The language specification is a separate document.
