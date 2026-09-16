<!--
Copyright (c) 2026 Eleftherios Notas and XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# FFI Module

Zero-cost C foreign function interface: external function declaration, raw memory allocation, and type size/alignment queries.

```
use xiom.ffi;
```

## External Calls

### `extern_c(name, ...)`
Declares and calls an external C function by name. The variadic arguments are passed to the C function. Returns an `Int` result.

```
fn extern_c(name: Str, ...) -> Int;
```

## Memory Management

### `alloc(size)|
Allocates raw memory of the given size using the system allocator. Returns a pointer to the allocated memory.

```
fn alloc(size: Int) -> *UInt8;
```

### `free(ptr)|
Frees raw memory previously allocated by `alloc`.

```
fn free(ptr: *UInt8);
```

### `memcpy(dest, src, size)|
Copies `size` bytes from `src` to `dest`. The source and destination regions must not overlap.

```
fn memcpy(dest: *UInt8, src: *UInt8, size: Int);
```

## Compile-Time Queries

### `size_of()`
Returns the size in bytes of type `T` (comptime).

```
fn size_of[T]() -> Int;
```

### `align_of()`
Returns the alignment in bytes of type `T` (comptime).

```
fn align_of[T]() -> Int;
```
