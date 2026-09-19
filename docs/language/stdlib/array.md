<!--
Copyright (c) 2026 XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Array Module

Fixed-size array operations for compile-time known-length arrays `[N]T`.

```
use xiom.array;
```

## Size & Access

### `len(arr)`
Returns the length (N) of the fixed-size array.

```
pub fn len[T, const N: Int](arr: &[N]T) -> Int;
```

### `is_empty(arr)`
Returns `true` if the array has length zero.

```
pub fn is_empty[T, const N: Int](arr: &[N]T) -> Bool;
```

### `first(arr)`
Returns a reference to the first element, or `None` if empty.

```
pub fn first[T](arr: &[N]T) -> Option<&T>;
```

### `last(arr)`
Returns a reference to the last element, or `None` if empty.

```
pub fn last[T](arr: &[N]T) -> Option<&T>;
```

### `get(arr, index)`
Returns a reference to the element at the given index, or `None` if out of bounds.

```
pub fn get[T](arr: &[N]T, index: Int) -> Option<&T>;
```

### `get_mut(arr, index)`
Returns a mutable reference to the element at the given index, or `None` if out of bounds.

```
pub fn get_mut[T](arr: &mut [N]T, index: Int) -> Option<&mut T>;
```

## Iteration & Transformation

### `map(arr, f)`
Transforms each element by applying `f`, producing a new array of the same size.

```
pub fn map[T, U, const N: Int](arr: [N]T, f: fn(T) -> U) -> [N]U;
```

### `zip(a, b)`
Combines two arrays element-wise into an array of tuples.

```
pub fn zip[T, U, const N: Int](a: [N]T, b: [N]U) -> [N](T, U);
```

### `fold(arr, init, f)`
Accumulates a value by applying `f` to each element and the current accumulator.

```
pub fn fold[T, B](arr: [N]T, init: B, f: fn(B, T) -> B) -> B;
```

## Slice Conversion

### `as_slice(arr)`
Returns a slice over the entire array.

```
pub fn as_slice[T](arr: &[N]T) -> Slice[T];
```

### `as_mut_slice(arr)`
Returns a mutable slice over the entire array.

```
pub fn as_mut_slice[T](arr: &mut [N]T) -> Slice[T];
```

### `each_ref(arr)`
Converts the array to an array of references.

```
pub fn each_ref[T](arr: &[N]T) -> [N]&T;
```

### `each_mut(arr)`
Converts the array to an array of mutable references.

```
pub fn each_mut[T](arr: &mut [N]T) -> [N]&mut T;
```

## Mutation

### `fill(arr, value)`
Fills all elements of the array with a cloned value.

```
pub fn fill[T: Clone](arr: &mut [N]T, value: T);
```

### `swap(arr, a, b)`
Swaps the elements at indices `a` and `b`.

```
pub fn swap[T](arr: &mut [N]T, a: Int, b: Int);
```

### `reverse(arr)`
Reverses the order of elements in the array.

```
pub fn reverse[T](arr: &mut [N]T);
```

### `rotate_left(arr, mid)`
Rotates the array left so that the element at `mid` becomes the first.

```
pub fn rotate_left[T](arr: &mut [N]T, mid: Int);
```

### `rotate_right(arr, k)`
Rotates the array right by `k` positions.

```
pub fn rotate_right[T](arr: &mut [N]T, k: Int);
```

## Sorting & Searching

### `sort(arr)`
Sorts the array using the element's `Ord` implementation.

```
pub fn sort[T: Ord](arr: &mut [N]T);
```

### `sort_by(arr, compare)`
Sorts the array using a custom comparison function.

```
pub fn sort_by[T](arr: &mut [N]T, compare: fn(&T, &T) -> Ordering);
```

### `binary_search(arr, x)`
Binary-searches the sorted array for a value. Returns `Ok(index)` if found, or `Err(insert_index)` if not found.

```
pub fn binary_search[T: Ord](arr: &[N]T, x: &T) -> Result[Int, Int];
```

### `contains(arr, x)`
Returns `true` if the array contains the given value.

```
pub fn contains[T: Eq](arr: &[N]T, x: &T) -> Bool;
```
