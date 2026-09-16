<!--
Copyright (c) 2026 Eleftherios Notas and XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Memory Module

Memory management utilities: swap, replace, drop, type size/alignment queries, and zeroed/uninitialized memory.

```
use xiom.mem;
```

## Manipulation

### `swap(a, b)`
Swaps the values at two mutable references without copying intermediate state.

```
pub fn swap[T](a: &mut T, b: &mut T);
```

### `replace(dest, src)`
Replaces the value at `dest` with `src`, returning the old value.

```
pub fn replace[T](dest: &mut T, src: T) -> T;
```

### `take(dest)`
Replaces the value at `dest` with the default value of `T`, returning the original value.

```
pub fn take[T: Default](dest: &mut T) -> T;
```

### `drop(value)`
Explicitly drops a value, running its destructor immediately.

```
pub fn drop[T](value: T);
```

## Size Queries

### `size_of()`
Returns the size in bytes of type `T`.

```
pub fn size_of[T]() -> Int;
```

### `align_of()`
Returns the alignment in bytes required for type `T`.

```
pub fn align_of[T]() -> Int;
```

### `size_of_val(value)`
Returns the size in bytes of the value `value`. For dynamically sized types, this returns the runtime size.

```
pub fn size_of_val[T](value: &T) -> Int;
```

### `min_align_of_val(value)`
Returns the minimum alignment in bytes required for the value.

```
pub fn min_align_of_val[T](value: &T) -> Int;
```

## Zeroed Memory

### `zeroed()`
Returns a value of type `T` with all bytes set to zero. Safe only when the all-zeroes bit pattern is a valid representation of `T`.

```
pub fn zeroed[T]() -> T;
```

## Uninitialized Memory

### `uninitialized()`
Returns an uninitialized value of type `T`. Unsafe: reading the value before writing valid data is undefined behavior.

```
pub fn uninitialized[T]() -> T;
```

## ManuallyDrop

### `ManuallyDrop[T]`
A wrapper that prevents the compiler from calling the destructor of the inner value automatically.

```
pub type ManuallyDrop[T] = { value: T; }
```

### `ManuallyDrop.new(value)`
Wraps a value in `ManuallyDrop`, suppressing its destructor.

```
pub fn ManuallyDrop.new[T](value: T) -> ManuallyDrop[T];
```

### `ManuallyDrop.into_inner(self)`
Extracts the inner value, enabling its destructor again.

```
pub fn ManuallyDrop.into_inner[T](self) -> T;
```
