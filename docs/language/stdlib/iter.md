# `xiom.iter` -- Iterators

Provides range types and iterator adapters for lazy, composable data processing over sequences.

```xiom
use xiom.iter;
```

---

## Range Types

### `Range`

A half-open range `[start, end)` that yields integers from `start` (inclusive) to `end` (exclusive).

```xiom
pub type Range = { start: Int; end: Int; }
```

### `RangeInclusive`

A fully-inclusive range `[start, end]` that yields integers from `start` through `end` inclusive.

```xiom
pub type RangeInclusive = { start: Int; end: Int; current: Int; done: Bool; }
```

### `range(start, end)`

Creates a half-open `Range` from `start` (inclusive) to `end` (exclusive). Panics if `start > end`.

```xiom
pub fn range(start: Int, end: Int) -> Range
```

### `range_inclusive(start, end)`

Creates a fully-inclusive `RangeInclusive` from `start` through `end`. Panics if `start > end`.

```xiom
pub fn range_inclusive(start: Int, end: Int) -> RangeInclusive
```

### `Range.next(self)`

Advances the range and returns the next value, or `None` when the range is exhausted.

```xiom
pub fn Range.next(self) -> Option[Int]
```

### `Range.len(self)`

Returns the number of elements remaining in the range (end minus start).

```xiom
pub fn Range.len(self) -> Int
```

### `Range.contains(self, x)`

Returns `true` if `x` is within the bounds of the range (start <= x < end).

```xiom
pub fn Range.contains(self, x: Int) -> Bool
```

### `RangeInclusive.next(self)```

Advances the inclusive range and returns the next value, or `None` when the range is exhausted.

```xiom
pub fn RangeInclusive.next(self) -> Option[Int]
```

---

## Iterator Adapters

These methods are available on any type implementing the `Iterator[T]` trait. They produce lazy wrapper iterators that transform the original sequence without allocating intermediate collections.

### `Iterator[T].map(f)`

Transforms each element by applying the function `f`, producing a `MapIter` that yields values of type `U`.

```xiom
pub fn Iterator[T].map[U](self, f: fn(T) -> U) -> MapIter[T, U]
```

### `Iterator[T].filter(predicate)`

Keeps only elements for which `predicate` returns `true`. The predicate receives a reference to each element.

```xiom
pub fn Iterator[T].filter(self, predicate: fn(&T) -> Bool) -> FilterIter[T]
```

### `Iterator[T].enumerate()`

Wraps the iterator, pairing each element with its zero-based index. Produces tuples of `(Int, T)`.

```xiom
pub fn Iterator[T].enumerate(self) -> EnumerateIter[T]
```

### `Iterator[T].take(n)`

Limits the iterator to the first `n` elements, ignoring the rest.

```xiom
pub fn Iterator[T].take(self, n: Int) -> TakeIter[T]
```

### `Iterator[T].skip(n)```

Skips the first `n` elements of the iterator, then yields the remaining elements.

```xiom
pub fn Iterator[T].skip(self, n: Int) -> SkipIter[T]
```

### `Iterator[T].chain(other)`

Concatenates two iterators of potentially different types. After `self` is exhausted, elements are drawn from `other`.

```xiom
pub fn Iterator[T].chain[U](self, other: Iterator[U]) -> ChainIter[T, U]
```

### `Iterator[T].zip(other)`

Zips two iterators together, producing tuples of `(T, U)`. The resulting iterator stops when either input iterator is exhausted.

```xiom
pub fn Iterator[T].zip[U](self, other: Iterator[U]) -> ZipIter[T, U]
```

---

## Collectors

These methods consume the iterator and produce a single value, eagerly evaluating the chain of adapters.

### `Iterator[T].collect()`

Consumes the iterator and collects all remaining elements into a new `Vec[T]`.

```xiom
pub fn Iterator[T].collect(self) -> Vec[T]
```

### `Iterator[T].fold(init, f)`

Folds every element into an accumulator by applying the function `f`, starting with the initial value `init`.

```xiom
pub fn Iterator[T].fold[B](self, init: B, f: fn(B, T) -> B) -> B
```

### `Iterator[T].count()`

Consumes the iterator and returns the number of remaining elements.

```xiom
pub fn Iterator[T].count(self) -> Int
```

### `Iterator[T].sum()`

Computes the sum of all elements in the iterator. Requires the element type to support addition.

```xiom
pub fn Iterator[T].sum(self) -> T
```

### `Iterator[T].product()`

Computes the product of all elements in the iterator. Requires the element type to support multiplication.

```xiom
pub fn Iterator[T].product(self) -> T
```

### `Iterator[T].max()`

Returns the maximum element in the iterator, or `None` if the iterator is empty.

```xiom
pub fn Iterator[T].max(self) -> Option[T]
```

### `Iterator[T].min()`

Returns the minimum element in the iterator, or `None` if the iterator is empty.

```xiom
pub fn Iterator[T].min(self) -> Option[T]
```

### `Iterator[T].find(predicate)`

Returns the first element for which `predicate` returns `true`, or `None` if no element matches.

```xiom
pub fn Iterator[T].find(self, predicate: fn(&T) -> Bool) -> Option[T]
```

### `Iterator[T].all(predicate)`

Returns `true` if `predicate` returns `true` for every element in the iterator. Short-circuits on the first `false`.

```xiom
pub fn Iterator[T].all(self, predicate: fn(&T) -> Bool) -> Bool
```

### `Iterator[T].any(predicate)`

Returns `true` if `predicate` returns `true` for at least one element in the iterator. Short-circuits on the first `true`.

```xiom
pub fn Iterator[T].any(self, predicate: fn(&T) -> Bool) -> Bool
```

### `Iterator[T].nth(n)`

Returns the `n`-th element (zero-indexed) of the iterator, consuming elements up to it. Returns `None` if the iterator has fewer than `n+1` elements.

```xiom
pub fn Iterator[T].nth(self, n: Int) -> Option[T]
```

### `Iterator[T].last()`

Consumes the entire iterator and returns the last element, or `None` if the iterator was empty.

```xiom
pub fn Iterator[T].last(self) -> Option[T]
```

---

## Adapter Types

These are the concrete types returned by the iterator adapter methods. Each holds a reference to the inner iterator and any additional state needed for the transformation.

| Type | Fields | Description |
|------|--------|-------------|
| `MapIter[T, U]` | `iter: Iterator[T]; f: fn(T) -> U` | Maps each element through a function |
| `FilterIter[T]` | `iter: Iterator[T]; predicate: fn(&T) -> Bool` | Filters elements by a predicate |
| `EnumerateIter[T]` | `iter: Iterator[T]; index: Int` | Pairs elements with their index |
| `TakeIter[T]` | `iter: Iterator[T]; remaining: Int` | Yields at most `n` elements |
| `SkipIter[T]` | `iter: Iterator[T]; to_skip: Int` | Skips the first `n` elements |
| `ChainIter[T, U]` | `first: Iterator[T]; second: Iterator[U]` | Concatenates two iterators |
| `ZipIter[T, U]` | `a: Iterator[T]; b: Iterator[U]` | Zips two iterators element-wise |
