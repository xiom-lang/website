<!--
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Type System

## Primitive Types

| Type | Width | Description |
|------|-------|-------------|
| `Bool` | 1 bit logical | Only `true` or `false`. No integer coercion. |
| `Int` | Platform (64-bit) | Signed. Default integer type. |
| `Int8` | 8 bits | Signed byte. |
| `Int16` | 16 bits | Signed short. |
| `Int32` | 32 bits | Signed word. |
| `Int64` | 64 bits | Signed double word. |
| `Int128` | 128 bits | Signed 128-bit integer. Integer literals beyond 64 bits are supported. |
| `UInt` | Platform (64-bit) | Unsigned. Use for sizes and indices. |
| `UInt8` | 8 bits | Unsigned byte. Use `UInt8` in source: the `Byte` alias name is not accepted by the current compiler. |
| `UInt16` | 16 bits | |
| `UInt32` | 32 bits | |
| `UInt64` | 64 bits | |
| `UInt128` | 128 bits | Unsigned 128-bit integer. |
| `Float32` | IEEE 754 single | |
| `Float64` | IEEE 754 double | Default float type. |
| `Float128` | IEEE 754 binary128 | Lowered to LLVM `fp128`. Values come from conversion; there is no `Float128` literal suffix. |
| `Char` | 32 bits | Unicode scalar value. Not a byte. |
| `Str` | Fat pointer | Immutable UTF-8 slice. Not null-terminated. |

## Compound Types

| Type | Description |
|------|-------------|
| `Option[T]` | Either `Some(value)` or `None`. Replaces null. |
| `Result[T, E]` | Either `Ok(value)` or `Err(error)`. Replaces exceptions. |
| `Vec[T]` | Heap-allocated growable array. Owns its elements. |
| `Slice[T]` | Non-owning view into contiguous `T` values. |
| `Map[K, V]` | Hash map. `K` must satisfy `Hash` and `Eq`. |
| `Set[T]` | Hash set. `T` must satisfy `Hash` and `Eq`. |
| `(T, U, ...)` | Tuple. Fixed arity, mixed types, accessed by index. |
| `*T` | Raw pointer. Only usable inside `unsafe` blocks. |
| `[N]T` | Fixed-size array of N elements of type T. `N` is comptime. |

## Type Inference

Types are inferred from context in `let` and `var` bindings and in closure parameters. Inference does not cross function boundaries -- function signatures are always fully annotated.

```xiom
let x = 42;          // inferred: Int
let f = 3.14;        // inferred: Float64
let s = "hello";     // inferred: Str
let v = [1, 2, 3];   // inferred: Vec[Int]
let t = (1, true);   // inferred: (Int, Bool)
```

## Numeric Literals and Casts

- An integer literal binds to an annotated built-in integer width: `let x: Int8 = 1;`, `let n: UInt = 100;` and `let b: UInt8 = 1;` are all valid.
- Integer literals beyond 64 bits are supported with `Int128` and `UInt128`.
- Mixing `Int` and `Float64` in arithmetic, comparisons or typed bindings requires an explicit `as`. An integer literal alone may adopt the float type: `1 + 2.5` is valid.
- Same-family widening is automatic (`Int8 + Int` becomes `Int`, `Float32 + Float64` becomes `Float64`); narrowing always needs `as`: `1 as Int8`, `200 as UInt8`.
- `Float128` has no literal form. Produce it by conversion: `let q = 1.0 as Float128;`. Binding a plain `Float64` value to `Float128` is a compile error.

```xiom
let a: Int8 = 1;              // integer literal adopts the annotated width
let n = 1 as Float64 + 2.5;   // explicit mixed-family conversion
let q = 1.0 as Float128;      // Float128 comes from conversion only
let b: UInt8 = 200;           // UInt8 accepts a literal in range
```

## Structs

```xiom
type Point = {
  x: Float64;
  y: Float64;
} derive[Eq, Clone, Display]
```

- Fields are separated by `;`.
- Optional `derive` clause generates common interface implementations.
- Optional `invariant` clauses enforce type-level contracts.

## Enums

```xiom
enum Option[T] {
  Some(value: T),
  None,
}

enum AgentState {
  Idle,
  Patrolling(route: Vec[Vector3]),
  Attacking(target: EntityId),
  Dead(cause: DamageCause),
}
```

- Variants can carry named fields.
- Unit variants (no fields) have no parentheses.
- Variants are separated by commas.
- Trailing commas are allowed.
- Optional `derive` clause for common interfaces.

## Structural Interfaces

A type satisfies an interface if it provides all required fields and methods with matching signatures. No `implements` keyword is needed.

```xiom
interface Comparable {
  fn compare(other: &Self) -> Int  // -1, 0, 1
}

type Score = { value: Int }

fn Score.compare(other: &Score) -> Int {
  if value < other.value { return -1; }
  if value > other.value { return  1; }
  return 0;
}

// Score now satisfies Comparable -- no declaration needed
let result = max(Score{ value: 10 }, Score{ value: 20 });
```

## Type Constraints (Inline)

Type-level interface requirements are declared inline with the type parameter:

```xiom
fn sort[T: Ord](items: &mut Vec[T])

// Multiple constraints
fn dedup[T: Eq + Hash](items: &mut Vec[T])
```

This separates type requirements from value preconditions -- `requires` is for value-level conditions only.

## Derive

The `derive` clause generates correct-by-construction implementations:

| Derive | Generates |
|--------|-----------|
| `Eq` | Structural equality -- every field compared |
| `Clone` | Deep copy -- every field cloned recursively |
| `Display` | Canonical string representation |
| `Hash` | Structural hash -- every field hashed and combined |
| `Ord` | Lexicographic ordering -- fields compared in declaration order |

**Constraint:** Types with `invariant` clauses cannot derive `Eq`, `Hash`, or `Ord`. Invariants make equality semantically ambiguous. `Clone` and `Display` remain available.

```xiom
type Point = {
  x: Float64;
  y: Float64;
} derive[Eq, Clone, Display, Hash, Ord]
```

See [Derive](derive.md) for full details.
