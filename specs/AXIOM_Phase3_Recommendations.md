# AXIOM — Phase 3 Recommendations, Concerns & Suggestions

> Companion document to AXIOM_Build_Strategy.md. Written from the perspective of
> AI-agent ergonomics and ecosystem leverage, not new language pillars.
> Nothing here contradicts the Three Pillars or the existing scope rejections
> (no AGI infrastructure framing, no lifetimes, no GC).

---

## Context

Phase 3 as currently scoped covers: Z3 static verification, package registry,
full LSP, formatter, doc generator, additional targets. This document adds
recommendations layered on top of that scope — it does not propose new pillars
or reopen DECIDED items.

---

## 1. Concern: Contract Semantics May Need Revision Before Z3

**Status: Recommendation — sequencing risk**

Phase 1 contracts have only been exercised by the team itself. Self-hosting
(Phase 2) will be the first large, adversarial-scale corpus of contracts —
written by AI tooling, against AI-generated AXIOM code, at compiler scale.

**Recommendation:** Treat the first 1–2 months of Phase 2 output as a contract
semantics audit, not just a bootstrap milestone. Specifically track:

- How often `requires`/`ensures` clauses are wrong, vague, or trivially true
- Whether contract violations caught real bugs or just noise
- Whether the runtime guard error format was sufficient for an agent to fix
  the violation without human intervention

**Why it matters:** Z3 static proof is expensive to build against unstable
semantics. If contract authoring patterns shift during Phase 2, that shift
should happen *before* Phase 3 SMT work starts, not after.

---

## 2. Recommendation: Structured (JSON) Compiler Diagnostics

**Status: New recommendation, additive to existing LSP/tooling scope**

Current contract violation messages are human-readable strings:

```
panic("contract violated: requires b != 0.0 at divide:2")
```

This is good for humans. It is bad for AI agents, who currently must
string-parse or regex this to extract structured meaning.

**Recommendation:** Add a `--diagnostics=json` compiler flag (Phase 3) that
emits structured diagnostics for both compile errors and contract violations:

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

**Why it matters:** This is the single highest-leverage, lowest-risk addition
for AI-agent tooling. It requires no new language semantics — only a second
output format for diagnostics that already exist. Tight feedback loops are
what let agents iterate on fixes without human translation of error text.

---

## 3. Recommendation: Queryable Contract Index ("Contracts as Spec Database")

**Status: New recommendation — the genuinely differentiated idea**

Today, to know what a function promises, an agent (or human) must read the
function body or trust a comment. AXIOM's contracts already make this data
exist in the language — but nothing currently exposes it independent of
parsing source.

**Recommendation:** Extend the planned `axiom doc` generator (already in
Phase 3 scope) with a `--contracts-json` mode that emits a structured,
queryable index of every function's `requires`/`ensures`/`invariant` clauses
across a package, without requiring the body to be read at all.

```json
{
  "function": "Vec.pop",
  "type_params": ["T"],
  "requires": ["!stack.is_empty()"],
  "ensures": [],
  "signature": "fn pop[T](stack: &mut Stack[T]) -> Option[T]"
}
```

**Why it matters:** This turns "the compiler is the reviewer" (Purpose doc)
into "the compiler also produces a spec database an agent can plan against."
It is the one item in this document that is unique to AXIOM's premise rather
than generic AI-tooling hygiene — no mainstream systems language currently
exposes this. It costs nothing new in the type checker; the data already
exists in the AST.

**Stretch goal (post-Phase 3, not now):** Contract composition checking —
verifying that a chain of calls satisfies each link's `requires` from the
prior link's `ensures`, without re-deriving everything per call. This is a
natural extension of the contract index, not a new mechanism.

---

## 4. Concern: Lexical Scope Borrowing — Unverified for AI-Generated Code

**Status: Concern, not a recommendation to change course**

Lexical scope borrowing is simpler for a *human* to read than Rust lifetimes.
It is not yet known whether it is easier for an LLM to *generate correctly*
under those constraints. Rust's lifetime errors, while harder to read, give
the compiler enough information to produce a precise, iterable error — which
is exactly what agents currently rely on to self-correct.

**Recommendation:** Track this empirically rather than assuming either way.
During Phase 2 self-hosting (large AI-assisted corpus), measure:

- Rate of borrow-related compile failures in AI-generated AXIOM code
- Whether the agent fixes them in 1 iteration based on the error message, or
  needs multiple retries / human intervention

This is a metric to collect, not a design decision to revisit now. If the
data shows agents struggle disproportionately with borrow errors compared to
type errors, the diagnostic message format (see #2) is the first lever to
pull — not the ownership model itself.

---

## 5. Recommendation: FFI as the Real Adoption Lever

**Status: Recommendation — ecosystem priority, not language feature**

Regardless of AI framing, the largest practical determinant of adoption for
a new systems language is whether it's frictionless to wrap one existing
C/C++/Rust library. This is explicitly in scope already (C FFI, "AXIOM is
not trying to be the only language"). The recommendation is about *how* to
prioritize it under AI-assisted development specifically.

**Recommendation:**
- Make the FFI binding surface mechanical, not judgment-based: minimal
  manual marshalling decisions per binding, so generating a binding is a
  repetitive, well-specified task — exactly what an agent does well and a
  human finds tedious.
- Where possible, auto-infer contracts from C header metadata during binding
  generation (e.g. non-null pointer annotations → `requires` clauses). This
  is additive to the contract system, not a new mechanism, and gives FFI
  bindings the same safety net as native AXIOM code with no extra authoring
  cost.

**Why it matters:** This is the unglamorous but highest-ROI ecosystem
investment. Language design rarely decides adoption for a non-Rust,
non-Zig systems language — packaging and interop friction does.

---

## 6. Explicit Non-Recommendation: No "AGI-Oriented" Features

**Status: Scope guard, reaffirming existing decision**

The Purpose document already rejects "AGI infrastructure framing" as out of
scope. This document does not propose reopening that. Everything above is
framed around *today's* AI coding agents and their concrete, observable
failure modes (context limits, need for structured feedback, reliance on
local reasoning) — not speculation about what a future AGI might want.
Recommendation: keep this boundary explicit in any future Phase 3 planning
discussion, since "AI-native language" framing tends to attract speculative
feature requests that don't trace back to an observed agent failure mode.

---

## Summary Table

| # | Item | Type | Effort vs. Phase 3 scope |
|---|------|------|---------------------------|
| 1 | Contract semantics audit during Phase 2 | Process recommendation | No new scope — timing only |
| 2 | `--diagnostics=json` flag | Tooling addition | Low — new output format only |
| 3 | `--contracts-json` index | Tooling addition | Low–medium — extends planned `axiom doc` |
| 4 | Track borrow-error agent friction | Metric to collect | No new scope — measurement only |
| 5 | Mechanical, contract-inferring FFI generation | Ecosystem priority | Medium — within existing FFI scope |
| 6 | No AGI-oriented feature creep | Scope guard | None — reaffirms existing decision |

---

*Companion to AXIOM_Build_Strategy.md — recommendations only, not binding
decisions. Promote any item to the Build Strategy's decision log if and when
it is actually decided.*
