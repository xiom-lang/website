# AXIOM Language Documentation

> **Compiler:** v0.11.0 "Self-Hosted" · **Spec:** v0.3 · **Tests:** 213 passing

## Contents

| Section | Description |
|---------|-------------|
| [Getting Started](getting-started.md) | Installation, first program, CLI reference |
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

## Language Overview

AXIOM is a compiled, statically typed, memory-safe systems programming language.

```
.ax source → Lexer → Parser → Type Checker → Borrow Checker
           → LLVM IR (+ Contracts + Derive + Generics)
           → clang → native .exe / .wasm
```

### Three Pillars

| SAFE | Ownership-based memory safety. No garbage collector. No null. Memory freed deterministically when the owner leaves scope. |
| VERIFIED | Contracts (requires, ensures, invariant) are first-class language constructs enforced by the compiler. |
| PRECISE | The grammar is unambiguous. One canonical form for every construct. No implicit coercions, hidden allocations, or surprising control flow. |

## Quick Example

```axiom
fn fib(n: Int) -> Int
  requires: n >= 0
{
  if n <= 1 { return n }
  return fib(n - 1) + fib(n - 2)
}

fn main() -> Int {
  return fib(10)  // → 55
}
```

```axiom
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
  return a / b
}
```

## Current Status

| Phase | Version | Status |
|-------|---------|--------|
| Phase 0 | v0.1.0 "Pipeline" | Released — working pipeline, 36 tests |
| Phase 1 | v0.2.0 "Guardian" | Released — full language surface, 87 tests |
| Phase 1.5 | v0.2.5 "Hardened" | Released — 13 bug fixes, 109 tests |
| Phase 2 | v0.4.0 "Mirror" | Released — self-host compiler, 124 tests |
| Phase 2C | v0.10.0 "Sovereign" | Released — production self-hosting, 208 tests |
| Phase 2C+ | v0.11.0 "Self-Hosted" | **Current** — 213 tests, WASM playground |

See [Compiler Version History](compiler.md#version-history) for the full changelog.
