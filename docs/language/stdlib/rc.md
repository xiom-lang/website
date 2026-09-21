<!--
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Reference Counting Module

Single-threaded reference-counted pointers (`Rc`) and weak references (`Weak`).

```
use xiom.rc;
```

## Rc

### `Rc[T]`
A single-threaded reference-counted pointer. The value is deallocated when the strong reference count reaches zero.

```
pub type Rc[T] = { ptr: *T; strong: Int; weak: Int; }
```

### `Rc.new(value)`
Creates a new `Rc` wrapping the given value, initializing the strong count to 1.

```
pub fn Rc.new[T](value: T) -> Rc[T];
```

### `Rc.clone(self)`
Clones the `Rc`, incrementing the strong reference count.

```
pub fn Rc.clone[T](self) -> Rc[T];
```

### `Rc.strong_count(self)`
Returns the current strong reference count.

```
pub fn Rc.strong_count[T](self) -> Int;
```

### `Rc.weak_count(self)`
Returns the current weak reference count.

```
pub fn Rc.weak_count[T](self) -> Int;
```

### `Rc.get(self)`
Returns a shared reference to the inner value.

```
pub fn Rc.get[T](self) -> &T;
```

### `Rc.ptr_eq(self, other)`
Returns `true` if two `Rc` pointers point to the same allocation.

```
pub fn Rc.ptr_eq[T, U](self, other: &Rc[U]) -> Bool;
```

### `Rc.downgrade(self)`
Creates a `Weak` reference from this `Rc`, without increasing the strong count.

```
pub fn Rc.downgrade[T](self) -> Weak[T];
```

### `Rc.unwrap_or_clone(self)`
Returns the inner value if the `Rc` has exactly one strong reference; otherwise clones the value.

```
pub fn Rc.unwrap_or_clone[T: Clone](self) -> T;
```

## Weak

### `Weak[T]`
A weak reference that does not prevent deallocation of the inner value.

```
pub type Weak[T] = { ptr: *T; }
```

### `Weak.upgrade(self)`
Attempts to upgrade the `Weak` reference to an `Rc`. Returns `None` if the inner value has been deallocated.

```
pub fn Weak.upgrade[T](self) -> Option<Rc[T]>;
```

### `Weak.strong_count(self)`
Returns the strong reference count of the pointed-to allocation, or 0 if the value has been deallocated.

```
pub fn Weak.strong_count[T](self) -> Int;
```
