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
// Type constraint — inline
fn sort[T: Ord](items: &mut Vec[T])

// Value precondition — requires clause
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

// The compiler rejects any code that could violate these invariants.
// No runtime crash — compile error.
```

The compiler guarantees these invariants hold after every mutation. Any code path that could violate them is a compile error.

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
| **Runtime guard (default)** | Inserted when static proof fails or is unavailable. Panics with a clear message on violation. |
| **Static (Phase 3)** | Compiler attempts Z3 SMT proof. Zero runtime cost if proven. |
| **Disabled (`--no-contracts`)** | Strips all contracts in release builds when explicitly requested. Opt-in only. |
| **Contradictory** | Compile error. The specification is logically impossible to satisfy. |

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
2. The compiler checks the implementation against that intent
3. Violations are caught at compile time or the first test run
4. The contract is machine-readable, so the AI itself can reason about it when composing functions

This is not about making AI better at writing code. It is about making the output **verifiable by construction** rather than by human review.
