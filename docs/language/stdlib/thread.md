<!--
Copyright (c) 2026 Eleftherios Notas and XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Thread Module

OS thread management: spawning, joining, scoped threads, and concurrency utilities.

```
use xiom.thread;
```

## Types

### `Thread`
Represents a handle to an OS thread.

```
pub type Thread = { id: Int; } derive[Eq, Clone]
```

### `JoinHandle[T]`
Represents the owned handle to a spawned thread, providing access to its result.

```
pub type JoinHandle[T] = { thread: Thread; result: Option<T>; }
```

## Spawning

### `spawn(f)`
Spawns a new OS thread that executes the closure `f`. Returns a `JoinHandle` for joining.

```
pub fn spawn[T](f: fn() -> T) -> JoinHandle[T];
```

### `spawn_with_name(name, f)`
Spawns a new OS thread with a given name that executes the closure `f`.

```
pub fn spawn_with_name[T](name: Str, f: fn() -> T) -> JoinHandle[T];
```

## JoinHandle

### `JoinHandle.join(self)`
Waits for the thread to finish and returns its result. Returns an error if the thread panicked.

```
pub fn JoinHandle.join[T](self) -> Result[T, Str];
```

### `JoinHandle.is_finished(self)`
Returns `true` if the thread has finished executing.

```
pub fn JoinHandle.is_finished[T](self) -> Bool;
```

### `JoinHandle.thread(self)`
Returns a reference to the underlying `Thread` handle.

```
pub fn JoinHandle.thread[T](self) -> Thread;
```

## Thread

### `Thread.current()`
Returns the `Thread` handle for the currently executing thread.

```
pub fn Thread.current() -> Thread;
```

### `Thread.id(self)`
Returns the OS-assigned thread ID.

```
pub fn Thread.id(self) -> Int;
```

### `Thread.name(self)`
Returns the thread's name, if one was set.

```
pub fn Thread.name(self) -> Option<Str>;
```

## Scheduling

### `sleep(dur)`
Blocks the current thread for the given `Duration`.

```
pub fn sleep(dur: Duration);
```

### `yield_now()`
Cooperatively yields the current time slice to the OS scheduler, allowing other threads to run.

```
pub fn yield_now();
```

## Scoped Threads

### `scope(f)`
Creates a scope in which scoped threads can be spawned that may borrow from the parent scope. The function `f` receives a `&Scope` and returns a value. All scoped threads are joined before `scope` returns.

```
pub fn scope[T](f: fn(&Scope) -> T) -> T;
```

### `Scope`
An opaque handle representing a scoped thread environment.

```
pub type Scope = { ... }
```

### `Scope.spawn(self, f)`
Spawns a scoped thread that may borrow data from the parent scope. The thread is automatically joined when the scope exits.

```
pub fn Scope.spawn[T](self, f: fn() -> T) -> JoinHandle[T];
```

## System

### `available_parallelism()`
Returns the number of available parallel worker threads (typically the number of logical CPUs).

```
pub fn available_parallelism() -> Int;
```

### `hardware_threads()`
Returns the number of hardware threads (logical CPUs) on the system.

```
pub fn hardware_threads() -> Int;
```
