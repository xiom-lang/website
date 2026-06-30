# AXIOM — Build Strategy & Decision Log

> This document captures how we are building AXIOM, in what order, and why.
> It is a living document. Decisions made here are binding until explicitly revised.

---

## The Core Principle

**Build on working foundations. Nothing gets built on speculation.**

Every phase ends with a compiler that compiles and runs real code.
The next phase only starts when the previous one is provably working.

---

## Why Ownership Does Not Block Phase 0

The ownership model does not block Phase 0.

The lexer, parser, AST, and LLVM codegen are completely independent
of how borrows work. The borrow syntax (`&`, `&mut`) is included in
the grammar from day one. The checker that enforces it is a Phase 1 problem.

Phase 0 parses borrow syntax correctly. It does not enforce borrow rules.
That is not a gap — it is the correct sequencing.

---

## Decision: Ownership Model

**Status: DECIDED**

AXIOM uses **lexical scope borrowing**.

### What That Means

- Borrows expire at the end of the block or statement they are created in
- No lifetime annotations. Ever.
- No lifetime parameters on functions or types
- The compiler infers borrow validity from scope nesting alone
- Borrows cannot be stored in structs or returned from functions

```axiom
fn example() {
    let v = Vec.new()
    read_only(&v)      // borrow created and expires inside this call — safe
    mutate(&mut v)     // write borrow — exclusive for duration of call
    consume(v)         // ownership moves — v no longer usable
}
```

### Why This Model

| Property | Outcome |
|---|---|
| No lifetime annotations | Genuine simplification over Rust, not a marketing claim |
| Implementable in weeks | Not months. Scope nesting is checkable without a solver |
| Readable code | You can see exactly when a borrow ends by looking at the braces |
| AI-friendly | No hidden lifetime relationships to infer across function boundaries |
| Pushes toward clean ownership | Patterns that require escaping borrows are solved with owned types instead |

### What It Explicitly Rejects

| Alternative | Why Not |
|---|---|
| Full Rust lifetimes | Correct but complex. Defeats the "simpler than Rust" goal entirely |
| ARC like Swift | Runtime overhead. Contradicts "no GC, no runtime" |
| Pony reference capabilities | Unproven, exotic, near-zero adoption |

---

## Decision: Contract System

**Status: DECIDED**

Phase 1 contracts are **runtime checks only**. No Z3. No SMT solver.

`requires`, `ensures`, and `invariant` compile to runtime guards that
panic with a clear, structured error message on violation.

```axiom
fn divide(a: Float64, b: Float64) -> Float64
  requires: b != 0.0
  ensures:  result * b == a
{
  return a / b
}

// Compiled Phase 1 output (conceptual):
// if !(b != 0.0) { panic("contract violated: requires b != 0.0 at divide:2") }
// let result = a / b
// if !(result * b == a) { panic("contract violated: ensures result * b == a at divide:3") }
// return result
```

Contract collection methods (`.is_sorted()`, `.all()`, `.none()`, `.contains()`)
are standard library functions that the contract system treats as assertion expressions.
No new language machinery is required.

Z3 static verification is a Phase 3 problem. The language must be
stable enough that contract semantics are proven by real usage before
we wire in a theorem prover.

---

## Decision: WASM Target

**Status: DECIDED**

WASM is a co-equal target alongside native from Phase 0.

If the LLVM pipeline works for native x86-64, WASM costs almost nothing extra —
it is the same IR with a different LLVM backend flag.

Proving both targets work in Phase 0 validates the entire deployment story early.

---

## Decision: `derive` — Compiler-Generated Interfaces

**Status: DECIDED**

The `derive` clause instructs the compiler to generate correct-by-construction
implementations of common interfaces. Supported derivations: `Eq`, `Clone`, `Display`, `Hash`, `Ord`.

```axiom
type Point = {
  x: Float64;
  y: Float64;
} derive[Eq, Clone, Display]
```

- **Phase 0:** Parser accepts `derive` clauses and stores them in the AST. No codegen.
- **Phase 1:** Type checker generates the implementations at interface satisfaction time.

**Rationale:** Every hand-written `eq` or `clone` method is a chance for AI or a tired
programmer to miss a field. The compiler never misses. This is not syntactic sugar —
it is correctness by construction. It also reduces token consumption for AI-generated code
by eliminating boilerplate that AI frequently gets wrong.

**Constraint:** Types with `invariant` clauses cannot derive `Eq`, `Hash`, or `Ord`.
Invariants make structural equality semantically ambiguous (two values with different
internal state may both satisfy the same invariant). `Clone` and `Display` remain available.

---

## Decision: Inline Type Constraints

**Status: DECIDED**

Type-level interface requirements are declared inline with the type parameter,
not as separate `requires` clauses. This separates type requirements from
value-level preconditions — two different verification mechanisms that should
not share syntax.

```axiom
// Type constraint — inline with the parameter
fn sort[T: Ord](items: &mut Vec[T])

// Multiple constraints
fn dedup[T: Eq + Hash](items: &mut Vec[T])

// Value precondition — requires clause
fn pop[T](stack: &mut Stack[T]) -> Option[T]
  requires: !stack.is_empty()
```

**Rationale:** Mixing type-level and value-level requirements in `requires` conflates
two different verification stages (compile-time type checking vs. runtime contract guarding).
Rust, Swift, and Haskell all separate these — for good reason. The inline syntax
(`[T: Ord]`) is familiar, concise, and unambiguous.

---

## Pre-Phase 1 Decisions

These decisions do not block Phase 0. They must be settled before Phase 1 implementation begins.

---

### Decision: Method Receiver Syntax

**Status: DECIDED**

`self` is synthesized implicitly by the compiler. It does not appear in the parameter list.
Methods are declared using `TypeName.methodName` syntax.

```axiom
fn Vec3.dot(other: &Vec3) -> Float32 {
  return x * other.x + y * other.y + z * other.z
  // self is &Vec3 — read-only, inferred from body
}

fn Vec3.set_x(value: Float32) {
  x = value
  // self is &mut Vec3 — field mutation detected in body
}
```

The compiler infers the receiver type:
- Method body does not mutate fields → `self: &Self`
- Method body mutates any field → `self: &mut Self`
- Mut anywhere in the body wins — the receiver is `&mut Self`

**Rationale:** Explicit receiver parameters are boilerplate that add no information.
Rust, Swift, and Python all synthesize or implicitly pass the receiver. The programmer
declares what they intend; the compiler infers the borrow kind.

---

### Decision: Comptime Generics Boundary

**Status: DECIDED**

**Rule:** All type parameters must be resolvable at the call site from argument types.
If a type parameter appears only in the return type and not in any argument,
it must be annotated explicitly at the call site.

```axiom
fn parse[T](s: Str) -> Result[T, ParseError] { ... }

// T cannot be inferred — must be explicit
let n = parse[Int]("42")

// T inferred from argument
fn identity[T](x: T) -> T { return x }
let n = identity(42)   // T = Int, inferred
```

**Rationale:** Prevents the return-only generic ambiguity that C++ templates
and Rust turbofish both struggle with. The rule is simple, consistent,
and produces clear error messages when violated.

---

### Decision: Package Manifest Location

**Status: DECIDED**

`package.ax` lives at the **project root**. Always. No exceptions.

**Rationale:** One file, findable without directory traversal.
Same convention as `Cargo.toml`, `go.mod`, `package.json`, `zig.zon`.
This is not a place to innovate. Familiarity wins.

---

### Decision: Error Type Hierarchy

**Status: DECIDED**

`E` in `Result[T, E]` is **any type**. No `Error` interface required.

The `?` operator requires only that `E` implements `From<SourceError>`
for automatic error conversion at propagation sites. The standard library
offers a `StdError` interface for its own functions. Users are not forced to use it.

```axiom
// All of these are valid
Result[Int, Str]
Result[Config, IOError]
Result[Data, MyCustomErrorEnum]
```

**Rationale:** Rust required `Error` trait bounds early and spent years unwinding it.
Forcing an interface on `E` constrains library authors for no safety benefit.
The type system already ensures `E` is handled — that is sufficient.

---

## Build Order

### Phase 0 — Working Pipeline (2–3 weeks, AI-assisted)

**Goal:** Hello World compiles to native binary and WASM binary.
Nothing more. Nothing less.

| Step | What | Done? |
|---|---|---|
| 1 | Project structure — Rust workspace, crate layout | |
| 2 | Lexer — tokenise all AXIOM keywords, literals, operators | |
| 3 | Parser — recursive descent, produce typed AST | |
| 4 | Basic type checker — primitives, structs, enums, functions | |
| 5 | Parse `derive` clauses, inline type constraints, method syntax — store in AST | |
| 6 | LLVM IR emission — arithmetic, control flow, function calls | |
| 7 | Native binary output — link and run | |
| 8 | WASM binary output — same IR, WASM backend | |
| 9 | Test suite — 200+ parser tests, 100+ type checker tests | |

**No generics. No ownership checking. No contracts.**
A working pipeline first. Parse everything. Enforce nothing (yet).

---

### Phase 1 — Full Language Surface (3–6 months)

Starts only when Phase 0 is complete and verified.

- Ownership model — lexical scope borrowing
- Generics via comptime monomorphisation with inline constraints
- Contracts as runtime guards — `requires`, `ensures`, `invariant`
- Contract collection methods — `is_sorted`, `all`, `none`, `contains`
- `derive` code generation — `Eq`, `Clone`, `Display`, `Hash`, `Ord`
- Enums with pattern matching and exhaustion checking
- Module system and `use` declarations
- Basic standard library: core, io, collections, string, math, ffi
- Standard library conformance testing — `test` package with contract-aware runner
- Error handling — `Result`, `Option`, `?` operator
- Async runtime and channel primitives
- Package manager prototype — local resolution only
- Canonical formatter (`axiom fmt`)
- Language server (LSP) prototype

---

### Phase 2 — Self-Hosting (6–12 months after Phase 1)

Starts only when Phase 1 is stable enough to write the compiler in AXIOM itself.

#### 2A — Core Compiler Rewrite

- Rewrite lexer in AXIOM — compiled by Phase 1 compiler
- Rewrite parser in AXIOM
- Rewrite type checker in AXIOM
- Rewrite IR emitter and LLVM bindings in AXIOM
- Compile new compiler with Phase 1 compiler
- New compiler compiles itself — bootstrap complete
- **Phase 0 Rust compiler kept as permanent bootstrap fallback** — never deleted

#### 2B — AI Tooling (Built During Self-Hosting)

- **`--diagnostics=json`** — structured compiler output. Enables AI agents to parse errors without string-matching. 2-day addition to error-reporting path.
- **`--dump-contracts`** — queryable contract index across a package. Emits JSON of every function's `requires`/`ensures`/`invariant`. AST traversal + output flag. AI tooling uses this during self-hosting to compose functions without reading source.
- **Contract semantics audit** — track contract quality during Phase 2 corpus generation. Gate on Phase 3 Z3 work. Audit before building SMT integration.
- **Borrow-error AI friction tracking** — measure agent failure rate on borrow errors. Data collection only. Informs ownership model revision decision.

---

### Phase 3 — Ecosystem & Static Contracts (ongoing)

- Z3 SMT integration for static contract verification (gated on Phase 2 contract audit)
- Package registry
- Language server (LSP) full implementation
- Canonical formatter (`axiom fmt`)
- Documentation generator (`axiom doc`)
- Additional compiler targets
- **WASM compiler distribution** — the compiler itself as WASM module for browser playground
- **Mechanical FFI binding generation** with contract inference from C headers
- **Showcase projects:** AxiomDB (KV store → transactions) → AxiomVDB (vector store)

---

## What We Are Not Doing (And Why)

| Dropped | Reason |
|---|---|
| GPU / Vulkan as language features | Library domain. C FFI covers it when needed. |
| Console targets | Platform SDK constraints. Add in Phase 3 when the language is stable. |
| Z3 in Phase 1 | The language must be stable before contract semantics are proven enough to feed a theorem prover. |
| Lifetime annotations | Committed to lexical scope model. Lifetimes are not part of AXIOM. |
| AGI infrastructure framing | Out of scope for a language specification. Separate concern entirely. |
| `requires` for type constraints | Separated. Type constraints go inline (`[T: Ord]`), value conditions stay in `requires`. |

---

## Toolchain Decisions

| Choice | Decision |
|---|---|
| Phase 0 compiler language | **Rust** |
| LLVM bindings | **inkwell** (safe Rust LLVM bindings) |
| WASM target | **LLVM wasm32-unknown-unknown** |
| Test framework | **Rust built-in + insta** for snapshot testing |
| SMT solver (Phase 3) | **Z3** via C FFI |
| LSP framework (Phase 3) | **tower-lsp** |

---

## Ecosystem & Distribution Decisions

These were recommendations promoted to decisions on 2026-06-30.

| Decision | Status | Source |
|----------|--------|--------|
| **Single `main` branch** — no per-OS forks. Conditional compilation for platform-specific code. CI build matrix per commit. | DECIDED | AXIOM_CrossPlatform_Distribution.md |
| **Three distribution paths:** pre-built binaries (primary), build-from-source (secondary), WASM compiler playground (tertiary). | DECIDED | AXIOM_CrossPlatform_Distribution.md |
| **Version manager** (`axiomup`) deferred to Phase 3. Design distribution infrastructure to support it from the start. | DEFERRED | AXIOM_CrossPlatform_Distribution.md |
| **Showcase projects:** AxiomDB first (KV store → transactions), AxiomVDB second (built on AxiomDB storage engine). | DECIDED | AXIOM_Showcase_Projects.md |
| **AxiomDB scoped to Phase A (KV store, no transactions) before AxiomVDB.** Transactions are Phase B, post-AxiomVDB. | DECIDED | AXIOM_Showcase_Projects.md |
| **Both showcase projects expose C-ABI surface** for consumption from Rust/Python/Tauri. First outbound FFI test. | DECIDED | AXIOM_Showcase_Projects.md |
| **`--diagnostics=json`** structured compiler output. Built during Phase 2 self-hosting. | DECIDED | AXIOM_Phase3_Recommendations.md |
| **`--dump-contracts`** queryable contract index. Built during Phase 2 self-hosting. | DECIDED | AXIOM_Phase3_Recommendations.md |
| **Contract semantics audit** before Z3 integration. Phase 2 output audited for contract quality. Gate on Phase 3 SMT work. | DECIDED | AXIOM_Phase3_Recommendations.md |
| **Borrow-error AI friction tracking** during Phase 2. Ownership model revisable if data shows systematic agent failure. | DECIDED | AXIOM_Phase3_Recommendations.md |
| **Mechanical FFI binding generation** prioritized in Phase 3. Auto-infer contracts from C headers where possible. | DECIDED | AXIOM_Phase3_Recommendations.md |
| **WASM compiler distribution** — the compiler itself as a WASM module for browser playground. Phase 3. | DECIDED | AXIOM_Phase3_Recommendations.md |
| **Stdlib conformance testing** — `test` package with contract-aware runner. Phase 1 addition. | DECIDED | AXIOM_Phase3_Recommendations.md |
| **No AGI-oriented feature creep** — reaffirmed. All AI-tooling decisions trace to observable agent failure modes, not speculation. | DECIDED | AXIOM_Phase3_Recommendations.md |

---

## Total Timeline

| Scenario | Phase 0 | Phase 1 | Phase 2 | Total to Self-Hosting |
|----------|---------|---------|---------|----------------------|
| AI-assisted | 2-3 weeks | 3-6 months | 6-12 months | **12-24 months** |
| Conventional team | 6-10 months | 12-18 months | 12-18 months | **30-46 months** |

Both scenarios assume the language specification is complete before implementation begins (which it is as of v0.3).

---

## Deferred Features

| Feature | Status | Notes |
|---------|--------|-------|
| `derived` fields (computed/reactive) | DEFERRED to Phase 2+ | Grammar defined but not implemented. AST supports storage. No codegen. |
| Static contract verification (Z3) | DEFERRED to Phase 3 | Runtime guards in Phase 1. SMT proof requires stable contract semantics after real-world usage. |
| GPU / Vulkan bindings | Not in scope | Library domain. C FFI covers it. |
| Console targets | Not in scope | Platform SDK constraints. Add when language is stable. |

---

## How This Document Gets Updated

Every design decision made during implementation gets recorded here.
Format: decision name, status (DECIDED / DEFERRED / OPEN), rationale, and what it rejects.

If a decision changes, the old rationale stays visible with a strikethrough and the new one is added below it.
Decisions do not disappear. We keep a record of what we tried and why we moved on.

---

*AXIOM Build Strategy — living document, updated as decisions are made.*
