<!--
Copyright (c) 2026 Eleftherios Notas and XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Pointer Module

Low-level pointer utilities: null pointers, read/write, volatile access, pointer arithmetic, and copy operations.

```
use xiom.ptr;
```

## Null & Dangling Pointers

### `null()`
Returns a null const pointer of type `T`.

```
pub fn null[T]() -> *T;
```

### `null_mut()`
Returns a null mutable pointer of type `T`.

```
pub fn null_mut[T]() -> *mut T;
```

### `dangling()`
Returns a non-null dangling pointer of type `T` (alignment-correct but not dereferenceable).

```
pub fn dangling[T]() -> *T;
```

### `is_null(ptr)`
Returns `true` if the pointer is null.

```
pub fn is_null[T](ptr: *const T) -> Bool;
```

## Read & Write

### `read(ptr)`
Reads a value from the given pointer. The pointer must be properly aligned and dereferenceable.

```
pub fn read[T](ptr: *const T) -> T;
```

### `write(ptr, value)`
Writes a value to the given pointer. The pointer must be properly aligned and dereferenceable.

```
pub fn write[T](ptr: *mut T, value: T);
```

### `read_volatile(ptr)`
Performs a volatile read from the given pointer (reads directly from memory, bypassing caches).

```
pub fn read_volatile[T](ptr: *const T) -> T;
```

### `write_volatile(ptr, value)`
Performs a volatile write to the given pointer.

```
pub fn write_volatile[T](ptr: *mut T, value: T);
```

## Swap & Replace

### `swap(a, b)`
Swaps the values at two mutable pointers.

```
pub fn swap[T](a: *mut T, b: *mut T);
```

### `replace(dest, src)`
Replaces the value at `dest` with `src`, returning the old value.

```
pub fn replace[T](dest: *mut T, src: T) -> T;
```

## Memory Copy

### `copy(src, dst, count)`
Copies `count * size_of[T]` bytes from `src` to `dst`. The source and destination regions may overlap.

```
pub fn copy[T](src: *const T, dst: *mut T, count: Int);
```

### `copy_nonoverlapping(src, dst, count)`
Copies `count * size_of[T]` bytes from `src` to `dst`. The source and destination regions must not overlap.

```
pub fn copy_nonoverlapping[T](src: *const T, dst: *mut T, count: Int);
```

## Comparison

### `eq(a, b)`
Returns `true` if the two pointers point to the same address.

```
pub fn eq[T](a: *const T, b: *const T) -> Bool;
```

## Pointer Arithmetic

### `offset(ptr, count)`
Computes the offset pointer by `count * size_of[T]` bytes. The offset must be within bounds of the original allocation.

```
pub fn offset[T](ptr: *const T, count: Int) -> *const T;
```

### `wrapping_offset(ptr, count)`
Computes the offset pointer by `count * size_of[T]` bytes, wrapping around on overflow rather than causing UB.

```
pub fn wrapping_offset[T](ptr: *const T, count: Int) -> *const T;
```

### `add(ptr, count)`
Equivalent to `offset(ptr, count)`. Advances the pointer by `count` elements.

```
pub fn add[T](ptr: *const T, count: Int) -> *const T;
```

### `sub(ptr, count)`
Equivalent to `offset(ptr, -count)`. Moves the pointer back by `count` elements.

```
pub fn sub[T](ptr: *const T, count: Int) -> *const T;
```

## Conversion

### `from_ref(r)`
Converts a reference to a const pointer.

```
pub fn from_ref[T](r: &T) -> *const T;
```

### `from_mut(r)`
Converts a mutable reference to a mutable pointer.

```
pub fn from_mut[T](r: &mut T) -> *mut T;
```
