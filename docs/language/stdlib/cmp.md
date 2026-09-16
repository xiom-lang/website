<!--
Copyright (c) 2026 Eleftherios Notas and XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Comparison Module

Comparison and ordering types, traits, and utility functions.

```
use xiom.cmp;
```

## Ordering

### `Ordering`
An enum representing the result of a comparison.

```
pub type Ordering = enum { Less, Equal, Greater }
```

### `Ordering.reverse(self)`
Reverses the ordering: `Less` becomes `Greater` and vice versa; `Equal` stays `Equal`.

```
pub fn Ordering.reverse(self) -> Ordering;
```

### `Ordering.then(self, other)`
Chains orderings: returns `self` if not `Equal`, otherwise returns `other`.

```
pub fn Ordering.then(self, other: Ordering) -> Ordering;
```

### `Ordering.then_with(self, f)`
Chains orderings with a lazy fallback: returns `self` if not `Equal`, otherwise calls `f` and returns its result.

```
pub fn Ordering.then_with(self, f: fn() -> Ordering) -> Ordering;
```

## Comparison Functions

### `min(a, b)`
Returns the smaller of `a` and `b`.

```
pub fn min[T: Ord](a: T, b: T) -> T;
```

### `max(a, b)`
Returns the larger of `a` and `b`.

```
pub fn max[T: Ord](a: T, b: T) -> T;
```

### `clamp(value, min_val, max_val)`
Clamps `value` to the range `[min_val, max_val]`.

```
pub fn clamp[T: Ord](value: T, min_val: T, max_val: T) -> T;
```

### `min_by(a, b, compare)`
Returns the smaller of `a` and `b` using a custom comparison function.

```
pub fn min_by[T](a: T, b: T, compare: fn(&T, &T) -> Ordering) -> T;
```

### `max_by(a, b, compare)`
Returns the larger of `a` and `b` using a custom comparison function.

```
pub fn max_by[T](a: T, b: T, compare: fn(&T, &T) -> Ordering) -> T;
```

## Traits

### `PartialEq[Rhs]`
Trait for types that support partial equality comparison.

```
pub interface PartialEq[Rhs: Self] {
    fn eq(self, other: &Rhs) -> Bool;
    fn ne(self, other: &Rhs) -> Bool;
}
```

### `PartialEq.eq(self, other)`
Returns `true` if `self` is equal to `other`.

### `PartialEq.ne(self, other)`
Returns `true` if `self` is not equal to `other`.

### `PartialOrd[Rhs]`
Trait for types that support partial ordering comparison (types that may not always be comparable, such as floats with NaN).

```
pub interface PartialOrd[Rhs: Self] {
    fn partial_cmp(self, other: &Rhs) -> Option[Ordering];
    fn lt(self, other: &Rhs) -> Bool;
    fn le(self, other: &Rhs) -> Bool;
    fn gt(self, other: &Rhs) -> Bool;
    fn ge(self, other: &Rhs) -> Bool;
}
```

### `PartialOrd.partial_cmp(self, other)`
Returns `Some(Ordering)` if the values are comparable, or `None` if they are not.

### `PartialOrd.lt(self, other)`
Returns `true` if `self` is less than `other`.

### `PartialOrd.le(self, other)`
Returns `true` if `self` is less than or equal to `other`.

### `PartialOrd.gt(self, other)`
Returns `true` if `self` is greater than `other`.

### `PartialOrd.ge(self, other)`
Returns `true` if `self` is greater than or equal to `other`.

## Reverse Ordering

### `Reverse[T]`
A wrapper type that reverses the ordering of its inner value.

```
pub type Reverse[T] = { value: T; }
```

### `Reverse.new(value)`
Creates a new `Reverse` wrapper that reverses the ordering of `value`.

```
pub fn Reverse.new[T](value: T) -> Reverse[T];
```
