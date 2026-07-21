# XIOM Language Documentation

> **Compiler:** v0.49.8 | **Spec:** v0.3 | **Tests:** 234 passing

## Contents

| Section | Description |
|---------|-------------|
| [Getting Started](getting-started.md) | Installation, first program, CLI reference |
| [Concepts](concepts.md) | XIOM for programmers from other languages — Java, C++, Python, Rust, Go |
| [By Example](examples.md) | Progressive examples from Hello World to generics + contracts |
| [Syntax](syntax.md) | Full language syntax: variables, functions, control flow, expressions |
| [Type System](types.md) | Primitive types, compound types, structs, enums, type inference |
| [Memory Model](memory-model.md) | Ownership, lexical scope borrowing, move semantics, unsafe |
| [Contracts](contracts.md) | requires/ensures/invariant, contract collections, verification modes |
| [Error Handling](error-handling.md) | Result, Option, ? operator, match exhaustion |
| [Modules](modules.md) | module/use/pub, visibility, packages, method declarations |
| [Generics](generics.md) | Comptime monomorphisation, inline type constraints, interface bounds |
| [Derive](derive.md) | Compiler-generated Eq, Clone, Display, Hash, Ord |
| [C FFI](ffi.md) | Zero-cost C interoperability, extern blocks, unsafe |
| [Compiler](compiler.md) | Pipeline overview, CLI flags, build targets, WASM |
| [Standard Library](stdlib.md) | Complete API reference for all 40 stdlib modules |
| [AI Coding Reference](../AI_CONTEXT.md) | Single-file AI prompt — inject into any LLM to enable XIOM code generation |

## Language Overview

XIOM is a compiled, statically typed, memory-safe systems programming language.

```
.xi source → Lexer → Parser → Type Checker → Borrow Checker
           → LLVM IR (+ Contracts + Derive + Generics)
           → clang → native .exe / .wasm
```

### Three Pillars

| SAFE | Ownership-based memory safety. No garbage collector. No null. Memory freed deterministically when the owner leaves scope. |
| VERIFIED | Contracts (requires, ensures, invariant) are first-class language constructs enforced by the compiler. |
| PRECISE | The grammar is unambiguous. One canonical form for every construct. No implicit coercions, hidden allocations, or surprising control flow. |

## Quick Example

```xiom
fn fib(n: Int) -> Int
  requires: n >= 0
{
  if n <= 1 { return n; }
  return fib(n - 1) + fib(n - 2);
}

fn main() -> Int {
  return fib(10);  // → 55
}
```

```xiom
// Types with invariants and derive
type Health = {
  current: Int;
  maximum: Int;
  invariant: current >= 0;
  invariant: current <= maximum;
} derive[Clone, Display]

// Functions with contracts
fn divide(a: Float64, b: Float64) -> Float64
  requires: b != 0.0
  ensures:  result * b == a
{
  return a / b;
}
```

## Getting Started

Ready to build with XIOM?

| Step | Resource |
|------|----------|
| Install the compiler | [Installation Guide](getting-started.md) |
| Write your first program | [Getting Started Tutorial](getting-started.md) |
| Learn the language | [Syntax](syntax.md), [Type System](types.md), [Memory Model](memory-model.md) |
| Browse the standard library | [Stdlib Reference](stdlib.md) |
| Find or publish packages | [Ecosystem & Packages](../ecosystem/packages.md) |

## Ecosystem

XIOM's ecosystem is organized across three tiers: first-party, first-party FFI bindings, and community.

| Resource | Description |
|----------|-------------|
| [Expansion Roadmap](../ecosystem/roadmap.md) | Full strategy for database, networking, GPU, GUI, ML, game dev, and serialization packages |
| [Package Guide](../ecosystem/packages.md) | How to create, structure, and publish XIOM packages |
| `xiom:net` | First-party FFI HTTP client (libcurl) |
| `xiom:sql` | First-party FFI SQLite bindings |
| `xiom:serialize` | First-party JSON / binary serialization |
| `xiom:crypto` | First-party FFI OpenSSL bindings |

For a complete list of planned and in-progress packages, see the [Expansion Roadmap](../ecosystem/roadmap.md).

## Current Status

| Phase | Version | Status |
|-------|---------|--------|
| Phase 0 | v0.1.0 "Pipeline" | Released — working pipeline, 36 tests |
| Phase 1 | v0.2.0 "Guardian" | Released — full language surface, 87 tests |
| Phase 1.5 | v0.2.5 "Hardened" | Released — 13 bug fixes, 109 tests |
| Phase 2 | v0.4.0 "Mirror" | Released — self-host compiler, 124 tests |
| Phase 2C | v0.10.0 "Sovereign" | Released — production self-hosting, 208 tests |
| Phase 2C+ | v0.49.8 | **Current** — 40-module stdlib, xiom doctor, if let/while let, compound assignment, tuple structs, Debug derive, parallel compilation, sanitizers, package manager |
| Phase 2C+ | v0.12.0 "Production" | Released — 234 tests, WASM playground |
| Phase 2C+ | v0.13.0 "Production" | Released — 234 tests, WASM playground, production-grade stdlib (40 modules, 374 contracts) |
| Phase 2C | v0.11.0 "Self-Hosted" | Released — full self-hosting, 213 tests |

See [Compiler Version History](compiler.md#version-history) for the full changelog.
