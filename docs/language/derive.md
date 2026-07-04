# Derive

The `derive` clause instructs the compiler to generate correct-by-construction implementations of common interfaces. Every hand-written `eq` or `clone` method is a chance for error. The compiler never misses.

## Supported Derivations

| Derive | Generated Behavior |
|--------|-------------------|
| `Eq` | Structural equality — every field compared. Two values are equal if all fields are equal. |
| `Clone` | Deep copy — every field cloned recursively. |
| `Display` | Canonical string representation. Structs format as `TypeName{ field: value, ... }`. |
| `Hash` | Structural hash — every field hashed and combined. Compatible with `Eq`. |
| `Ord` | Lexicographic ordering — fields compared in declaration order. |

## Usage

```xiom
type Point = {
  x: Float64;
  y: Float64;
} derive[Eq, Clone, Display]

// Compiler generates:
//   fn Point.eq(other: &Point) -> Bool     — x == x && y == y
//   fn Point.clone() -> Point              — deep copy of both fields
//   fn Point.to_str() -> Str               — "Point{ x: 1.0, y: 2.0 }"
```

## Invariant Restriction

Types with `invariant` clauses cannot derive `Eq`, `Hash`, or `Ord`. Invariants make structural equality semantically ambiguous — two values with different internal state may both satisfy the same invariant. `Clone` and `Display` remain available.

```xiom
type Health = {
  current: Int;
  maximum: Int;
  invariant: current >= 0;
  invariant: current <= maximum;
} derive[Clone, Display]
// Eq, Hash, Ord are rejected — invariants make equality/hashing ambiguous
```

## Enums

Enums support derive too:

```xiom
enum Option[T] {
  Some(value: T),
  None,
} derive[Eq, Clone]

// Enums with variant data can derive Clone, Display
// Enums with only unit variants can also derive Eq, Hash, Ord
```

## Codegen Details

### Eq

```llvm
; Structural comparison over all fields
%eq_x = fcmp oeq double %self.x, %other.x
%eq_y = fcmp oeq double %self.y, %other.y
%result = and i1 %eq_x, %eq_y
```

### Clone

```llvm
; Deep copy via alloca + GEP per field
%clone = alloca %struct.Point
%x_ptr = getelementptr %struct.Point, %struct.Point* %clone, i32 0, i32 0
store double %self.x, double* %x_ptr
; ... repeat for each field
```

### Display

```llvm
; Canonical string via printf format concatenation
; "Point{ x: 1.0, y: 2.0 }"
```

### Hash

```llvm
; Multiplicative hash (DJB2 variant) combining all fields
%hash = mul i64 %hash, 33
%hash = add i64 %hash, %field_hash
```

### Ord

```llvm
; Lexicographic field-by-field comparison with branch dispatch
; Compare field 0 → if not equal, return; else compare field 1...
```

## Custom Implementations

You can always write a manual implementation instead of using `derive`:

```xiom
type Point = { x: Float64; y: Float64 }

fn Point.eq(other: &Point) -> Bool {
  return x == other.x && y == other.y;
}
```

Manual implementations take precedence over derived ones. This is useful when the structural definition doesn't match the semantic definition (e.g., a type that should compare only a subset of fields).
