<!--
Copyright (c) 2026 XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# `xiom.sync` -- Synchronization Primitives

Provides thread-safe synchronization primitives for coordinating access to shared state across concurrent tasks.

```xiom
use xiom.sync;
```

---

## Mutex

A mutual exclusion primitive that guards shared data. Only one thread may hold the lock at a time.

### `Mutex[T]`

A type wrapping a value `T` with a lock flag. The data can only be accessed through a `MutexGuard`.

```xiom
pub type Mutex[T] = { data: T; locked: Bool; }
```

### `Mutex.new(data)`

Creates a new `Mutex` protecting the given value. The mutex starts in the unlocked state.

```xiom
pub fn Mutex.new[T](data: T) -> Mutex[T]
```

### `Mutex.lock(self)`

Blocks the current thread until the lock is acquired, then returns a `MutexGuard` that provides access to the protected data. The guard releases the lock when dropped.

```xiom
pub fn Mutex.lock[T](self) -> MutexGuard[T]
```

### `Mutex.try_lock(self)`

Attempts to acquire the lock without blocking. Returns `Some(guard)` if the lock was acquired, or `None` if another thread holds the lock.

```xiom
pub fn Mutex.try_lock[T](self) -> Option[MutexGuard[T]]
```

### `MutexGuard[T]`

An RAII guard that holds a locked `Mutex`. The lock is released when this value is dropped.

```xiom
pub type MutexGuard[T] = { mutex: Mutex[T]; }
```

### `MutexGuard.get(self)`

Returns an immutable reference to the data protected by the mutex.

```xiom
pub fn MutexGuard.get[T](self) -> &T
```

### `MutexGuard.get_mut(self)`

Returns a mutable reference to the data protected by the mutex.

```xiom
pub fn MutexGuard.get_mut[T](self) -> &mut T
```

---

## RwLock

A reader-writer lock allowing concurrent reads or exclusive writes.

### `RwLock[T]`

A type wrapping a value `T` with reader and writer tracking for fine-grained concurrency control.

```xiom
pub type RwLock[T] = { data: T; readers: Int; writer: Bool; }
```

### `RwLock.new(data)`

Creates a new `RwLock` protecting the given value.

```xiom
pub fn RwLock.new[T](data: T) -> RwLock[T]
```

### `RwLock.read(self)`

Acquires a shared read lock, blocking if a writer holds the lock. Multiple readers may hold the lock simultaneously.

```xiom
pub fn RwLock.read[T](self) -> ReadGuard[T]
```

### `RwLock.write(self)`

Acquires an exclusive write lock, blocking until all readers and writers have released the lock.

```xiom
pub fn RwLock.write[T](self) -> WriteGuard[T]
```

### `RwLock.try_read(self)`

Attempts to acquire a read lock without blocking. Returns `Some(ReadGuard)` on success, `None` if a writer holds the lock.

```xiom
pub fn RwLock.try_read[T](self) -> Option<ReadGuard[T]>
```

### `RwLock.try_write(self)`

Attempts to acquire a write lock without blocking. Returns `Some(WriteGuard)` on success, `None` if the lock is contended.

```xiom
pub fn RwLock.try_write[T](self) -> Option<WriteGuard[T]>
```

### `ReadGuard[T]`

An RAII guard that holds a shared read lock on an `RwLock`. The read count is decremented when dropped.

```xiom
pub type ReadGuard[T] = { lock: RwLock[T]; }
```

### `WriteGuard[T]`

An RAII guard that holds an exclusive write lock on an `RwLock`. The writer flag is cleared when dropped.

```xiom
pub type WriteGuard[T] = { lock: RwLock[T]; }
```

---

## Condvar

A condition variable for blocking threads until a condition is signaled. Typically used with a `Mutex`.

### `Condvar`

A synchronization primitive that blocks threads until notified.

```xiom
pub type Condvar = { waiters: Int; }
```

### `Condvar.new()`

Creates a new condition variable with no waiters.

```xiom
pub fn Condvar.new() -> Condvar
```

### `Condvar.wait(self, guard)`

Blocks the current thread, temporarily releasing the `MutexGuard`. The guard is re-acquired when the thread wakes.

```xiom
pub fn Condvar.wait[T](self, guard: MutexGuard[T]) -> MutexGuard[T]
```

### `Condvar.notify_one(self)`

Wakes up one blocked thread waiting on this condition variable.

```xiom
pub fn Condvar.notify_one(self)
```

### `Condvar.notify_all(self)`

Wakes up all threads blocked on this condition variable.

```xiom
pub fn Condvar.notify_all(self)
```

---

## Once

A synchronization primitive for one-time initialization of a function or value.

### `Once`

Tracks whether a one-time operation has been executed.

```xiom
pub type Once = { done: Bool; }
```

### `Once.new()`

Creates a new `Once` in the uninitialized state.

```xiom
pub fn Once.new() -> Once
```

### `Once.call_once(self, f)`

Calls the provided function `f` exactly once, even if invoked from multiple threads concurrently. Subsequent calls are no-ops.

```xiom
pub fn Once.call_once(self, f: fn())
```

---

## Arc (Atomic Reference Counting)

A thread-safe reference-counted pointer for sharing ownership across threads.

### `Arc[T]`

An atomically reference-counted pointer to a value of type `T`.

```xiom
pub type Arc[T] = { ptr: *T; count: Int; }
```

### `Arc.new(value)`

Creates a new `Arc` wrapping the given value with an initial reference count of 1.

```xiom
pub fn Arc.new[T](value: T) -> Arc[T]
```

### `Arc.clone(self)`

Increments the reference count and returns a new `Arc` pointing to the same data.

```xiom
pub fn Arc.clone[T](self) -> Arc[T]
```

### `Arc.get(self)`

Returns an immutable reference to the inner value.

```xiom
pub fn Arc.get[T](self) -> &T
```

### `Arc.strong_count(self)`

Returns the current strong reference count of the `Arc`.

```xiom
pub fn Arc.strong_count[T](self) -> Int
```

### `Arc.ptr_eq(self, other)`

Returns `true` if two `Arc` pointers reference the same heap allocation.

```xiom
pub fn Arc.ptr_eq[T, U](self, other: &Arc[U]) -> Bool
```

---

## Atomic Types

Lock-free atomic primitives for safe concurrent access to boolean and integer values.

### `AtomicBool`

A boolean value that can be safely read and modified from multiple threads.

```xiom
pub type AtomicBool = { val: Bool; }
```

### `AtomicBool.new(val)`

Creates a new `AtomicBool` with the given initial value.

```xiom
pub fn AtomicBool.new(val: Bool) -> AtomicBool
```

### `AtomicBool.load(self)`

Atomically reads the current value of the atomic boolean.

```xiom
pub fn AtomicBool.load(self) -> Bool
```

### `AtomicBool.store(self, val)`

Atomically writes a new value to the atomic boolean.

```xiom
pub fn AtomicBool.store(self, val: Bool)
```

### `AtomicBool.swap(self, val)`

Atomically stores a value and returns the previous value.

```xiom
pub fn AtomicBool.swap(self, val: Bool) -> Bool
```

### `AtomicInt`

An integer value that can be safely read and modified from multiple threads using atomic operations.

```xiom
pub type AtomicInt = { val: Int; }
```

### `AtomicInt.new(val)`

Creates a new `AtomicInt` with the given initial value.

```xiom
pub fn AtomicInt.new(val: Int) -> AtomicInt
```

### `AtomicInt.load(self)`

Atomically reads the current value of the atomic integer.

```xiom
pub fn AtomicInt.load(self) -> Int
```

### `AtomicInt.store(self, val)`

Atomically writes a new value to the atomic integer.

```xiom
pub fn AtomicInt.store(self, val: Int)
```

### `AtomicInt.fetch_add(self, val)`

Atomically adds `val` to the current value and returns the previous value.

```xiom
pub fn AtomicInt.fetch_add(self, val: Int) -> Int
```

### `AtomicInt.fetch_sub(self, val)`

Atomically subtracts `val` from the current value and returns the previous value.

```xiom
pub fn AtomicInt.fetch_sub(self, val: Int) -> Int
```

---

## Barrier

A barrier that blocks a fixed set of threads until all have arrived.

### `Barrier`

Synchronizes `n` threads so that each waits at the barrier until all have reached it.

```xiom
pub type Barrier = { count: Int; generation: Int; }
```

### `Barrier.new(n)`

Creates a new barrier that blocks until `n` threads have called `wait`.

```xiom
pub fn Barrier.new(n: Int) -> Barrier
```

### `Barrier.wait(self)`

Blocks the current thread until all threads in the barrier set have called `wait`. After the barrier is reached, all threads are released.

```xiom
pub fn Barrier.wait(self)
```
