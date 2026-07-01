# Allocation Module

Memory allocation types and the global allocator interface.

```
use axiom.alloc;
```

## Layout

### `Layout`
Describes the layout of a block of memory: its size and alignment.

```
pub type Layout = { size: Int; align: Int; } derive[Eq, Clone]
```

### `Layout.new(size)`
Creates a new `Layout` for the given size with default alignment.

```
pub fn Layout.new(size: Int) -> Layout;
```

### `Layout.with_align(self, align)`
Creates a new `Layout` with the same size but a specific alignment.

```
pub fn Layout.with_align(self, align: Int) -> Layout;
```

### `Layout.padded_size(self)`
Returns the total padded size of the layout (size rounded up to the alignment).

```
pub fn Layout.padded_size(self) -> Int;
```

## Allocator Interface

### `Allocator`
The trait for memory allocators. Supports allocate, deallocate, zeroed allocation, grow, and shrink.

```
pub interface Allocator {
    fn allocate(self, layout: Layout) -> Result<*mut UInt8, AllocError>;
    fn deallocate(self, ptr: *mut UInt8, layout: Layout);
    fn allocate_zeroed(self, layout: Layout) -> Result<*mut UInt8, AllocError>;
    fn grow(self, ptr: *mut UInt8, old: Layout, new: Layout) -> Result<*mut UInt8, AllocError>;
    fn shrink(self, ptr: *mut UInt8, old: Layout, new: Layout) -> Result<*mut UInt8, AllocError>;
}
```

### `Allocator.allocate(self, layout)`
Allocates a block of memory matching the given layout.

### `Allocator.deallocate(self, ptr, layout)`
Deallocates a block of memory previously allocated through this allocator.

### `Allocator.allocate_zeroed(self, layout)`
Allocates a zeroed block of memory matching the given layout.

### `Allocator.grow(self, ptr, old, new)`
Grows an existing allocation from `old` size to `new` size.

### `Allocator.shrink(self, ptr, old, new)`
Shrinks an existing allocation from `old` size to `new` size.

### `AllocError`
The error returned when allocation fails.

```
pub type AllocError = { message: Str; } derive[Clone]
```

## Global Allocator

### `global_alloc()`
Returns the global allocator (wraps `malloc`/`free`).

```
pub fn global_alloc() -> Allocator;
```

### `alloc(size)`
Allocates a block of memory of the given size using the global allocator.

```
pub fn alloc(size: Int) -> *mut UInt8;
```

### `alloc_zeroed(size)`
Allocates a zeroed block of memory of the given size.

```
pub fn alloc_zeroed(size: Int) -> *mut UInt8;
```

### `realloc(ptr, old_size, new_size)`
Reallocates a block of memory to a new size.

```
pub fn realloc(ptr: *mut UInt8, old_size: Int, new_size: Int) -> *mut UInt8;
```

### `dealloc(ptr, size)`
Deallocates a block of memory previously allocated by `alloc` or `realloc`.

```
pub fn dealloc(ptr: *mut UInt8, size: Int);
```

## Sized Allocation

### `alloc_layout(layout)`
Allocates memory matching the given `Layout`.

```
pub fn alloc_layout(layout: Layout) -> *mut UInt8;
```

### `dealloc_layout(ptr, layout)`
Deallocates memory previously allocated with the given `Layout`.

```
pub fn dealloc_layout(ptr: *mut UInt8, layout: Layout);
```
