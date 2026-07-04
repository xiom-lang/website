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
| `UInt` | Platform (64-bit) | Unsigned. Use for sizes and indices. |
| `UInt8` | 8 bits | Byte. Alias: `Byte`. |
| `UInt16` | 16 bits | |
| `UInt32` | 32 bits | |
| `UInt64` | 64 bits | |
| `Float32` | IEEE 754 single | |
| `Float64` | IEEE 754 double | Default float type. |
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

Types are inferred from context in `let` and `var` bindings and in closure parameters. Inference does not cross function boundaries — function signatures are always fully annotated.

```xiom
let x = 42;          // inferred: Int
let f = 3.14;        // inferred: Float64
let s = "hello";     // inferred: Str
let v = [1, 2, 3];   // inferred: Vec[Int]
let t = (1, true);   // inferred: (Int, Bool)
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

// Score now satisfies Comparable — no declaration needed
let result = max(Score{ value: 10 }, Score{ value: 20 });
```

## Type Constraints (Inline)

Type-level interface requirements are declared inline with the type parameter:

```xiom
fn sort[T: Ord](items: &mut Vec[T])

// Multiple constraints
fn dedup[T: Eq + Hash](items: &mut Vec[T])
```

This separates type requirements from value preconditions — `requires` is for value-level conditions only.

## Derive

The `derive` clause generates correct-by-construction implementations:

| Derive | Generates |
|--------|-----------|
| `Eq` | Structural equality — every field compared |
| `Clone` | Deep copy — every field cloned recursively |
| `Display` | Canonical string representation |
| `Hash` | Structural hash — every field hashed and combined |
| `Ord` | Lexicographic ordering — fields compared in declaration order |

**Constraint:** Types with `invariant` clauses cannot derive `Eq`, `Hash`, or `Ord`. Invariants make equality semantically ambiguous. `Clone` and `Display` remain available.

```xiom
type Point = {
  x: Float64;
  y: Float64;
} derive[Eq, Clone, Display, Hash, Ord]
```

See [Derive](derive.md) for full details.
