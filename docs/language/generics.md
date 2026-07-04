# Generics

Generics are implemented through **comptime type parameters**. The type parameter is resolved at compile time, producing a monomorphised specialisation. No runtime dispatch, no boxing, no virtual calls unless explicitly requested via interface references.

## Basic Generics

```xiom
fn max[T: Comparable](a: T, b: T) -> T {
  if a > b { return a; }
  return b;
}

// Call sites — T inferred from arguments
let m1 = max(10, 20);          // T = Int
let m2 = max(1.5, 2.7);        // T = Float64
```

## Inline Type Constraints

Type-level requirements are declared **inline** with the type parameter. This separates type requirements from value-level preconditions:

```xiom
// Single constraint
fn sort[T: Ord](items: &mut Vec[T])

// Multiple constraints
fn dedup[T: Eq + Hash](items: &mut Vec[T])

// Constraint with interface
fn process[T: Comparable + Display](value: T) -> Str {
  return value.to_str();
}
```

## Explicit Type Parameters

If a type parameter appears only in the return type and not in any argument, it must be annotated explicitly at the call site:

```xiom
fn parse[T](s: Str) -> Result[T, ParseError] { ... }

let n = parse[Int]("42");   // T must be explicit — not inferrable from arguments
```

## Generic Types

```xiom
type Stack[T] = {
  items: Vec[T];
  capacity: UInt;
  invariant: items.len() <= capacity;
}

type Pair[A, B] = {
  first: A;
  second: B;
} derive[Eq, Clone]
```

## Monomorphisation

Generics use **two-pass monomorphisation**:

1. **Pass 1 — Register:** The compiler scans for concrete instantiations at call sites and registers them.
2. **Pass 2 — Specialize:** For each registered instantiation, the compiler emits a specialized version with full type substitution.

```xiom
// Source
fn identity[T](x: T) -> T { return x; }

let a = identity(42);      // T = Int
let b = identity("hi");    // T = Str

// Generated (conceptual)
fn identity_Int(x: Int) -> Int { return x; }
fn identity_Str(x: Str) -> Str { return x; }
```

This produces zero-overhead abstractions — generic code compiles to the same machine code as hand-specialized versions.

## Interface Satisfaction

Inline constraints are checked at monomorphisation time. If a type parameter `T: Ord` is declared, the compiler verifies that the concrete type satisfies `Ord` before specializing:

```xiom
type Score = { value: Int }

fn Score.compare(other: &Score) -> Int { ... }
// Score now satisfies Comparable

let winner = max(Score{ value: 10 }, Score{ value: 20 });
// Compiler verifies: Score satisfies Comparable ✓
// Generates: max_Score(Score, Score) -> Score
```

If a type does not satisfy the required interface, the compiler produces a clear error:

```
error[E0301]: type does not satisfy interface
  --> src/main.xi:12:10
   |
12 |   let s = sort[Point](points)
   |           ^^^^^^^^^ type `Point` does not satisfy `Ord`
   |
   = `sort` requires `T: Ord` because it must compare elements.
     Type `Point` is missing:  fn compare(other: &Point) -> Int
   = help: add `derive[Ord]` to the type definition of `Point`, or
     implement `fn Point.compare(other: &Point) -> Int` by hand.
```

## Comptime

`comptime` marks expressions and blocks to be evaluated at compile time. It is the single mechanism for all metaprogramming — generics, reflection, and specialisation all flow through it.

```xiom
let size = comptime expensive_computation();  // evaluated once, at compile time
```
