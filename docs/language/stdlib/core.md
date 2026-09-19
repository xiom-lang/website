<!--
Copyright (c) 2026 XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Core Library

The `core` module provides fundamental types, interfaces, and operations used throughout the XIOM standard library. It includes the `Option` and `Result` types for error handling, numeric conversions, collection contract predicates, core traits (interfaces), heap allocation via `Box`, the `BinaryHeap` priority queue, iterator support, numeric limits, and compile-time type introspection.

```
use xiom.core;
```

---

## Option Type

A sum type representing an optional value: either `Some(value)` or `None`. Internally represented as a struct with an `is_some` flag and a `value` field. Idiomatic XIOM uses `Option` for fallible operations that do not need an error payload.

```xiom
type Option[T] = { is_some: Bool; value: T; }
```

---

## Result Type

A sum type representing either success (`Ok(value)`) or failure (`Err(error)`). Used for fallible operations where the error carries information. Internally represented as a struct with `is_ok`, `value`, and `error` fields.

```xiom
type Result[T, E] = { is_ok: Bool; value: T; error: E; }
```

---

## Panic & Assert

### `panic(msg)`
Halts program execution immediately and emits `msg` as an error message. Compiler-recognized: translates to a trap instruction.

```xiom
fn panic(msg: Str);
```

### `assert(condition, msg)`
Evaluates `condition`; if false, calls `panic(msg)`. Used for runtime invariant checking.

```xiom
fn assert(condition: Bool, msg: Str);
```

### `panic_if(condition, msg)`
Conditionally panics -- if `condition` is true, calls `panic(msg)`. Useful for guard clauses.

```xiom
fn panic_if(condition: Bool, msg: Str);
```

---

## Numeric Conversions

### `to_int(x)`
Converts a `Float64` to `Int`, truncating the fractional part toward zero.

```xiom
fn to_int(x: Float64) -> Int;
```

### `to_float(x)`
Converts an `Int` to `Float64`.

```xiom
fn to_float(x: Int) -> Float64;
```

### `to_string(x)`
Converts an `Int` to its decimal string representation.

```xiom
fn to_string(x: Int) -> Str;
```

### `to_int_from_str(s)`
Parses a `Str` as a signed integer. Returns `Ok(Int)` on success or `Err(Str)` if the string is not a valid integer.

```xiom
fn to_int_from_str(s: Str) -> Result[Int, Str];
```

### `to_float_from_str(s)`
Parses a `Str` as a 64-bit floating-point number. Returns `Ok(Float64)` on success or `Err(Str)` if parsing fails.

```xiom
fn to_float_from_str(s: Str) -> Result[Float64, Str];
```

### `to_bool_from_str(s)`
Parses a `Str` as a boolean (e.g., `"true"` / `"false"`). Returns `Ok(Bool)` on success or `Err(Str)` if the string is not a valid boolean.

```xiom
fn to_bool_from_str(s: Str) -> Result[Bool, Str];
```

### `to_char(x)`
Converts an `Int` code point to its corresponding `Char`.

```xiom
fn to_char(x: Int) -> Char;
```

### `to_int_from_char(c)`
Converts a `Char` to its Unicode code point as `Int`.

```xiom
fn to_int_from_char(c: Char) -> Int;
```

---

## Collection Contract Predicates

These functions are used inside `requires`, `ensures`, and `invariant` clauses to describe properties of slices and collections.

### `is_sorted(items)`
Returns true if the elements in `items` are in non-decreasing order according to `Ord`.

```xiom
fn is_sorted[T: Ord](items: &Slice[T]) -> Bool;
```

### `all(items, predicate)`
Returns true if `predicate` returns true for every element in `items`.

```xiom
fn all[T](items: &Slice[T], predicate: fn(T) -> Bool) -> Bool;
```

### `none(items, predicate)`
Returns true if `predicate` returns false for every element in `items`.

```xiom
fn none[T](items: &Slice[T], predicate: fn(T) -> Bool) -> Bool;
```

### `contains(items, value)`
Returns true if any element in `items` is equal to `value`. Elements must implement `Eq`.

```xiom
fn contains[T: Eq](items: &Slice[T], value: T) -> Bool;
```

---

## Core Traits (Interfaces)

### `Clone`
Provides a `clone()` method that returns an independent copy of `self`.

```xiom
interface Clone {
  fn clone() -> Self;
}
```

### `Eq`
Provides equality comparison via `eq(other)`. Implementations must be reflexive, symmetric, and transitive.

```xiom
interface Eq {
  fn eq(other: &Self) -> Bool;
}
```

### `Ord`
Provides total ordering via `compare(other)`. Returns a negative value if `self < other`, zero if equal, positive if `self > other`.

```xiom
interface Ord {
  fn compare(other: &Self) -> Int;
}
```

### `Display`
Provides a human-readable string representation via `to_str()`.

```xiom
interface Display {
  fn to_str() -> Str;
}
```

### `Hash`
Provides a hash value via `hash()` returning a `UInt64`. Implementations must be deterministic and consistent with `Eq`.

```xiom
interface Hash {
  fn hash() -> UInt64;
}
```

### `Add`
Supports addition via `add(self, other)`, consuming self.

```xiom
interface Add {
  fn add(self, other: &Self) -> Self;
}
```

### `Sub`
Supports subtraction via `sub(self, other)`, consuming self.

```xiom
interface Sub {
  fn sub(self, other: &Self) -> Self;
}
```

### `Mul`
Supports multiplication via `mul(self, other)`, consuming self.

```xiom
interface Mul {
  fn mul(self, other: &Self) -> Self;
}
```

### `Div`
Supports division via `div(self, other)`, consuming self.

```xiom
interface Div {
  fn div(self, other: &Self) -> Self;
}
```

### `Iterator[T]`
Defines a sequence of values. Calling `next()` returns `Some(value)` for each element and `None` once exhausted. `size_hint()` returns a lower bound and optional upper bound on remaining length.

```xiom
interface Iterator[T] {
  fn next(self) -> Option[T];
  fn size_hint(self) -> (Int, Option[Int]);
}
```

### `IntoIterator[T]`
Converts a collection into an `Iterator[T]` via `into_iter()`.

```xiom
interface IntoIterator[T] {
  fn into_iter(self) -> Iterator[T];
}
```

### `Default`
Provides a default/zero value for a type via `default()`.

```xiom
interface Default {
  fn default() -> Self;
}
```

### `Drop`
Deterministic cleanup: the compiler calls `drop()` when a value goes out of scope.

```xiom
interface Drop {
  fn drop(self);
}
```

---

## Box Type

A heap-allocated pointer providing ownership semantics. `Box[T]` stores a value on the heap and drops it when the `Box` goes out of scope.

```xiom
type Box[T] = { ptr: *T; }
```

### `Box.new(value)`
Allocates `value` on the heap and returns a `Box[T]` owning it.

```xiom
fn Box.new[T](value: T) -> Box[T];
```

### `Box.get(b)`
Returns an immutable reference to the heap-allocated value.

```xiom
fn Box.get[T](b: &Box[T]) -> &T;
```

### `Box.drop(b)`
Explicitly drops the `Box` and deallocates the heap memory. The compiler also calls this automatically when the `Box` goes out of scope if it implements `Drop`.

```xiom
fn Box.drop[T](b: Box[T]);
```

---

## BinaryHeap (Priority Queue)

A priority queue implemented as a binary heap. The largest element (according to `Ord`) is always at the front.

```xiom
type BinaryHeap[T] = { data: Vec[T]; }
```

### `BinaryHeap.new()`
Creates an empty binary heap.

```xiom
fn BinaryHeap[T: Ord].new() -> BinaryHeap[T];
```

### `BinaryHeap.push(value)`
Inserts a value into the heap.

```xiom
fn BinaryHeap[T: Ord].push(self, value: T);
```

### `BinaryHeap.pop()`
Removes and returns the largest element. Returns `None` if the heap is empty.

```xiom
fn BinaryHeap[T: Ord].pop(self) -> Option[T];
```

### `BinaryHeap.peek()`
Returns a reference to the largest element without removing it. Returns `None` if empty.

```xiom
fn BinaryHeap[T: Ord].peek(self) -> Option[&T];
```

### `BinaryHeap.len()`
Returns the number of elements in the heap.

```xiom
fn BinaryHeap[T].len(self) -> Int;
```

### `BinaryHeap.is_empty()`
Returns true if the heap contains no elements.

```xiom
fn BinaryHeap[T].is_empty(self) -> Bool;
```

---

## Option Methods

### `Option.unwrap_or(default)`
Returns the inner value if `Some`, otherwise returns `default`.

```xiom
fn Option[T].unwrap_or(self, default: T) -> T;
```

### `Option.unwrap_or_else(f)`
Returns the inner value if `Some`, otherwise calls `f()` and returns its result.

```xiom
fn Option[T].unwrap_or_else(self, f: fn() -> T) -> T;
```

### `Option.map(f)`
If `Some`, applies `f` to the inner value and wraps the result in `Some`. Returns `None` if `None`.

```xiom
fn Option[T].map[U](self, f: fn(T) -> U) -> Option[U];
```

### `Option.and_then(f)`
If `Some`, applies `f` to the inner value and returns the `Option[U]` directly (no double-wrapping). Returns `None` if `None`.

```xiom
fn Option[T].and_then[U](self, f: fn(T) -> Option[U]) -> Option[U];
```

### `Option.filter(predicate)`
If `Some` and `predicate` returns true for the inner value, returns `self`. Otherwise returns `None`.

```xiom
fn Option[T].filter(self, predicate: fn(&T) -> Bool) -> Option[T];
```

### `Option.is_some_and(predicate)`
Returns true if `self` is `Some` and `predicate` returns true for the inner value.

```xiom
fn Option[T].is_some_and(self, predicate: fn(&T) -> Bool) -> Bool;
```

---

## Result Methods

### `Result.unwrap_or(default)`
Returns the inner value if `Ok`, otherwise returns `default`.

```xiom
fn Result[T, E].unwrap_or(self, default: T) -> T;
```

### `Result.unwrap_or_else(f)`
Returns the inner value if `Ok`, otherwise calls `f` with the error and returns its result.

```xiom
fn Result[T, E].unwrap_or_else(self, f: fn(E) -> T) -> T;
```

### `Result.map(f)`
If `Ok`, applies `f` to the inner value and returns `Ok(result)`. Returns `Err(error)` unchanged.

```xiom
fn Result[T, E].map[U](self, f: fn(T) -> U) -> Result[U, E];
```

### `Result.map_err(f)`
If `Err`, applies `f` to the error value and returns `Err(new_error)`. Returns `Ok(value)` unchanged.

```xiom
fn Result[T, E].map_err[F](self, f: fn(E) -> F) -> Result[T, F];
```

### `Result.and_then(f)`
If `Ok`, applies `f` to the inner value and returns the `Result[U, E]` directly. Returns `Err(error)` unchanged.

```xiom
fn Result[T, E].and_then[U](self, f: fn(T) -> Result[U, E]) -> Result[U, E];
```

### `Result.expect(msg)`
Returns the inner value if `Ok`, otherwise calls `panic(msg)`.

```xiom
fn Result[T, E].expect(self, msg: Str) -> T;
```

### `Result.is_ok_and(predicate)`
Returns true if `self` is `Ok` and `predicate` returns true for the inner value.

```xiom
fn Result[T, E].is_ok_and(self, predicate: fn(&T) -> Bool) -> Bool;
```

---

## Type-Level Operations

### `size_of[T]()`
Returns the size (in bytes) of type `T` as determined by the compiler.

```xiom
fn size_of[T]() -> Int;
```

### `align_of[T]()`
Returns the alignment requirement (in bytes) of type `T` as determined by the compiler.

```xiom
fn align_of[T]() -> Int;
```

---

## Numeric Limits

Compile-time constants representing the minimum and maximum values of built-in numeric types.

```xiom
const INT_MAX: Int;
const INT_MIN: Int;
const FLOAT64_MAX: Float64;
const FLOAT64_MIN: Float64;
const FLOAT64_EPSILON: Float64;
```

| Constant         | Description                                 |
|------------------|---------------------------------------------|
| `INT_MAX`        | Maximum representable `Int` value.          |
| `INT_MIN`        | Minimum representable `Int` value.          |
| `FLOAT64_MAX`    | Maximum finite `Float64` value.             |
| `FLOAT64_MIN`    | Minimum positive normalized `Float64` value. |
| `FLOAT64_EPSILON`| Difference between 1.0 and the next representable `Float64`. |
