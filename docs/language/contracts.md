<!--
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Contracts

Contracts are the formal specification layer of XIOM. They transform function signatures from documentation into machine-checkable specifications.

Contracts compile to runtime guards with precise error messages. Static proof via Z3 SMT solver is planned for Phase 3.

## Keywords

| Keyword | Semantics |
|---------|-----------|
| `requires` | Pre-condition. Must hold when the function is called. Caller is responsible. |
| `ensures` | Post-condition. Must hold when the function returns. Implementation is responsible. |
| `invariant` | Type-level contract. Must hold after every mutation of a value of this type. |
| `result` | Refers to the return value inside an `ensures` clause. |
| `self@pre` | Value of `self` at the moment the function was entered. For use in `ensures`. |

## Function Contracts

```xiom
fn divide(a: Float64, b: Float64) -> Float64
  requires: b != 0.0
  ensures:  result * b == a
{
  return a / b;
}
```

**Type-level constraints** (which interfaces a generic parameter must satisfy) are declared **inline** with the type parameter, not as `requires` clauses. This separates type requirements from value preconditions:

```xiom
// Type constraint -- inline
fn sort[T: Ord](items: &mut Vec[T])

// Value precondition -- requires clause
fn pop[T](stack: &mut Stack[T]) -> Option[T]
  requires: !stack.is_empty()
```

## Type Invariants

```xiom
type Health = {
  current: Int;
  maximum: Int;
  invariant: current >= 0;
  invariant: current <= maximum;
  invariant: maximum > 0;
}

// Invariants remain part of the type contract.
// Enforcement coverage in the current compiler is partial.
```

Invariants are intended to hold after every mutation. The current compiler does not reject every code path that could violate one, and runtime invariant checking is not applied on every mutation path yet; treat invariants as binding and test the paths that matter.

## Contract Collection Methods

To reduce verbosity, the standard library provides contract-focused methods on collections:

| Method | Meaning |
|--------|---------|
| `.is_sorted()` | Elements are in non-decreasing order |
| `.all(closure)` | All elements satisfy the predicate |
| `.none(closure)` | No element satisfies the predicate |
| `.contains(value)` | Collection contains the given value |
| `.len()` | Number of elements |
| `.is_empty()` | Collection is empty. Equivalent to `.len() == 0` |

```xiom
fn sort(items: &mut Vec[Int])
  ensures: items.is_sorted()
{
  // ... sorting implementation
}

fn filter_positive(items: &Vec[Int]) -> Vec[Int]
  ensures: result.all(|x| x > 0)
  ensures: result.len() <= items.len()
{
  // ... filter implementation
}
```

## Verification Modes

| Mode | Behavior |
|------|----------|
| **Runtime guard (default)** | Contracts compile to checks that trap on violation. This is the default enforcement. |
| **`--no-contracts`** | Removes the guards at compile time. |
| **`--release`** | Strips guards unless `--runtime-contracts` forces them. |
| **Exported obligations (`--verify`)** | Writes SMT-LIB proof obligations and makes no proof claim. |
| **Checked (`xiom-verify --check`)** | Runs the bundled z3 over the exported obligations and returns Proven, Violated or UNKNOWN. Only `unsat` counts as proved. |

Contradiction detection is specified but not implemented in the current
compiler: a logically impossible `requires` is not rejected at compile time.

## Verification Scope and the Trusted Base

The verifier reasons about contracts, not about implementations. When it
proves one of your functions, it has discharged the obligations that follow
from the contracts of the functions that function calls; it has not inspected
the bodies of those functions. That boundary matters for the standard library:

- Standard library functions carry contracts and are enforced like any other
  code, but the verifier treats their `ensures` clauses as assumptions it may
  use when reasoning about a caller.
- Some standard library hot paths are implemented in hand-written x86_64
  assembly - crypto primitives, bulk memory operations and context switching -
  with portable equivalents used when the assembly paths are not built in
  (the toolchain compiles the runtime without them when NASM is unavailable;
  see the toolchain's `xiom doctor` output). Those implementations sit inside
  the trusted base: the verifier does not prove assembly.
- Equivalence between accelerated and portable paths is an engineering
  property kept by testing the same inputs through both, not something the
  solver establishes.

So a proof carries one assumption: that the standard library honors its
contracts. Where a function is accelerated is an implementation detail; the
contract is the interface, and the contract is what gets verified. The
repository audits that track which symbols are assembly-backed live in the
standard library, not on this page.

## Runtime Behavior

When a contract is violated at runtime, the compiler emits:

```
contract violated: requires b != 0.0 at divide:2
```

Followed by a trap (`@llvm.trap()`). The program terminates with a clear, structured error message identifying the function, line, and the violated clause.

Enable structured diagnostics with `--diagnostics=json` for machine-readable output:

```json
{
  "kind": "contract_violation",
  "clause": "requires",
  "expression": "b != 0.0",
  "function": "divide",
  "location": { "file": "math.xi", "line": 2 }
}
```

## AI and Contracts

Contracts are machine-readable intent. When AI generates code:

1. AI writes a function with stated intent (`requires` and `ensures`)
2. The toolchain enforces the contract at runtime and exports supported obligations to the verifier
3. Violations surface on the first run that exercises them; proven obligations are reported per the verdict rules above
4. The contract is machine-readable, so the AI itself can reason about it when composing functions

This is not about making AI better at writing code. It is about making the output **verifiable by construction** rather than by human review.
