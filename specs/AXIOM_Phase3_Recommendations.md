# AXIOM — Phase 3 Recommendations & Phase 2 Enhancements

> Companion to AXIOM_Build_Strategy.md. Recommendations that enhance Phase 2
> tooling and Phase 3 ecosystem work, with a focus on AI-agent ergonomics.
> **Status: DECIDED** where marked. Recommendations otherwise.
> Nothing here contradicts the Three Pillars or the existing scope rejections.

---

## Scope Note

Phase 3 as currently scoped covers: Z3 static verification, package registry,
full LSP, formatter, doc generator, additional targets. This document adds
items that can be built during Phase 2 (low cost, high AI-tooling leverage)
and refinements for Phase 3 planning.

---

## Phase 2 Additions (Build These During Self-Hosting)

These items require no new language semantics. They expose data the compiler
already has in the AST. They cost days, not weeks. They give AI tooling
immediate leverage during the self-hosting effort itself.

---

### Decision 1: Structured Compiler Diagnostics (`--diagnostics=json`)

**Status: DECIDED.** Build during Phase 2 self-hosting.

Current contract violation messages are human-readable strings:

```
panic("contract violated: requires b != 0.0 at divide:2")
```

This is good for humans. It is bad for AI agents, who must string-parse or
regex this to extract structured meaning.

**Decision:** Add a `--diagnostics=json` compiler flag that emits structured
diagnostics for both compile errors and contract violations:

```json
{
  "kind": "contract_violation",
  "clause": "requires",
  "expression": "b != 0.0",
  "function": "divide",
  "location": { "file": "math.ax", "line": 2 },
  "expected": "b != 0.0",
  "actual_values": { "b": "0.0" }
}
```

**Why Phase 2, not Phase 3:** This is a second output format for diagnostics
that already exist. The cost is a 2-day addition to the error-reporting path.
The payoff is immediate: AI agents writing AXIOM during self-hosting get
structured feedback instead of parsing strings. Tight feedback loops let
agents iterate on fixes without human translation of error text.

---

### Decision 2: Queryable Contract Index (`--dump-contracts`)

**Status: DECIDED.** Build during Phase 2 self-hosting.

Today, to know what a function promises, an agent (or human) must read the
function body or trust a comment. AXIOM's contracts already make this data
exist in the AST — but nothing exposes it independent of parsing source.

**Decision:** Add a `--dump-contracts` flag to the Phase 2 compiler that
emits a structured index of every function's `requires`/`ensures`/`invariant`
clauses across a package, without requiring the body to be read at all.

```json
{
  "function": "Vec.pop",
  "type_params": ["T"],
  "requires": ["!stack.is_empty()"],
  "ensures": [],
  "signature": "fn pop[T](stack: &mut Stack[T]) -> Option[T]"
}
```

**Why Phase 2, not Phase 3:** This data already exists in the typed AST. It
costs a new output flag and a traversal. It's what AI tooling needs during
self-hosting to compose functions without reading every source file. Don't
wait for Phase 3. Build it during the self-hosting effort itself — it's how
the AI writing the compiler will understand what functions promise.

**Stretch goal (post-Phase 2):** Contract composition checking — verifying
that a chain of calls satisfies each link's `requires` from the prior link's
`ensures`, without re-deriving everything per call. This is a natural
extension of the contract index, not a new mechanism.

---

## Phase 3 Recommendations

---

### 1. Contract Semantics Audit Before Z3

**Status: DECIDED.** Sequencing risk. Audit before investing in SMT.

Phase 1 contracts have only been exercised by the team itself. Phase 2
self-hosting will be the first large, adversarial-scale corpus of contracts —
written by AI tooling, against AI-generated AXIOM code, at compiler scale.

**Decision:** Treat the first 1–2 months of Phase 2 output as a contract
semantics audit. Track:
- How often `requires`/`ensures` clauses are wrong, vague, or trivially true
- Whether contract violations caught real bugs or just noise
- Whether the runtime guard error format was sufficient for an agent to fix
  the violation without human intervention (the structured diagnostics from
  Decision 1 above are the delivery mechanism for this)

**Why it matters:** Z3 static proof is expensive to build against unstable
semantics. If contract authoring patterns shift during Phase 2, that shift
must happen *before* Phase 3 SMT work starts, not after.

---

### 2. Track Borrow-Error AI Friction (With Escape Hatch)

**Status: DECIDED — measurement with acknowledged revision path.**

Lexical scope borrowing is simpler for a human to read than Rust lifetimes.
It is not yet known whether it is easier for an LLM to *generate correctly*
under those constraints.

**Decision:** Track this empirically during Phase 2 self-hosting:
- Rate of borrow-related compile failures in AI-generated AXIOM code
- Whether the agent fixes them in 1 iteration or needs multiple retries /
  human intervention

**Escape hatch:** If empirical data from Phase 2 shows agents cannot reliably
generate correct borrow patterns under lexical scope — and structured
diagnostics don't reduce the failure rate to acceptable levels — **the
ownership model is on the table for revision.** This is not a commitment to
change it. It is an acknowledgment that a model designed for human readability
may need adjustment if agents systematically fail against it. The measurement
is free. The acknowledgment is honest. The decision to act on the data is
deferred until the data exists.

The diagnostic message format (Decision 1) is the first lever to pull. If it
doesn't help, the model itself is the second lever.

---

### 3. FFI as the Real Adoption Lever

**Status: DECIDED — ecosystem priority within Phase 3 scope.**

Regardless of AI framing, the largest practical determinant of adoption for a
new systems language is frictionless wrapping of existing C/C++/Rust
libraries. This is explicitly in scope (C FFI). The decision is about *how*
to prioritize it:

- Make the FFI binding surface mechanical: minimal manual marshalling
  decisions per binding. Generating a binding should be a repetitive,
  well-specified task — exactly what an agent does well and a human finds
  tedious.
- Where possible, auto-infer contracts from C header metadata during binding
  generation (e.g., non-null pointer annotations → `requires` clauses). This
  gives FFI bindings the same safety net as native AXIOM code with no extra
  authoring cost.

This is the unglamorous but highest-ROI ecosystem investment. Language design
rarely decides adoption for a new systems language — packaging and interop
friction does.

---

### 4. WASM Compiler Distribution Path

**Status: DECIDED — unique to AXIOM.**

The AXIOM compiler itself compiles to WASM (proven in Phase 0 — same
pipeline flag as user programs). This enables a distribution path no other
systems language currently offers:

- A web-based AXIOM playground where the compiler runs client-side in the
  browser via WASM — no install, no backend server, no account
- Instant-on for new users: open a URL, write AXIOM, see compiled output or
  run the WASM binary directly in the browser
- The compiler WASM is a distribution artifact built by the same CI matrix
  that builds native binaries

**Implementation in Phase 3:** The same `--target wasm` flag that compiles
user programs to WASM is applied to the compiler itself. The playground is a
static HTML page that loads the compiler WASM and presents an editor. No
backend required. This is a competitive differentiator worth investing in.

---

### 5. Standard Library Conformance Testing

**Status: DECIDED — Phase 1 addition.**

The showcase projects (AxiomDB, AxiomVDB) will test the language features.
But the stdlib itself needs a conformance suite that tests whether every
function satisfies its own contracts:

- Does `Vec.push` maintain the capacity invariant?
- Does `Map.get` return `None` for missing keys?
- Does `Result.unwrap` panic on `Err`?

This is separate from compiler tests. It validates that the stdlib
implementation is correct against its own stated contracts — the same
contracts that user code relies on.

**Implementation:** A `test` package in the stdlib that provides a contract-
aware test runner. `fn test_push_respects_capacity` — the contract IS the
test. Start during Phase 1 stdlib implementation.

---

### 6. No "AGI-Oriented" Feature Creep

**Status: DECIDED — reaffirming existing decision.**

The Purpose document already rejects "AGI infrastructure framing" as out of
scope. Everything in this document is framed around today's AI coding agents
and their concrete, observable failure modes (context limits, need for
structured feedback, reliance on local reasoning) — not speculation about
what a future AGI might want. Keep this boundary explicit.

---

## Summary Table

| # | Item | Status | Phase | Effort |
|---|------|--------|-------|--------|
| D1 | `--diagnostics=json` flag | **DECIDED** | Phase 2 | Low — new output format |
| D2 | `--dump-contracts` contract index | **DECIDED** | Phase 2 | Low — AST traversal + output flag |
| 1 | Contract semantics audit before Z3 | **DECIDED** | Phase 2→3 gate | No new scope — timing only |
| 2 | Track borrow-error AI friction | **DECIDED** | Phase 2 | Measurement only |
| 2b | Ownership model revision escape hatch | **DECIDED** (acknowledged) | Deferred to data | No action now — acknowledged path |
| 3 | Mechanical FFI generation | **DECIDED** | Phase 3 | Medium — within existing FFI scope |
| 4 | WASM compiler distribution | **DECIDED** | Phase 3 | Medium — compiler WASM + static playground |
| 5 | Stdlib conformance testing | **DECIDED** | Phase 1 | Low — test package + contract runner |
| 6 | No AGI-oriented feature creep | **DECIDED** | Ongoing | None — reaffirms existing decision |

---

## What Was Rejected / Moved

| Item | Original location | Final decision |
|------|------------------|----------------|
| `--contracts-json` (contract index) | Proposed for Phase 3 | **Moved to Phase 2** (Decision 2). Data exists in AST. Build it during self-hosting. |
| Ownership model concerns | Proposed as measurement-only | **Added escape hatch** (Item 2b). If data shows systematic agent failure, the model is revisable. |

---

*AXIOM Phase 3 Recommendations — Version 1.0. Decisions made 2026-06-30.*
*Recorded in AXIOM_Build_Strategy.md decision log.*
