<!--
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# `xiom.async` -- Async Programming

Provides primitives for asynchronous task execution and message passing between concurrent tasks.

```xiom
use xiom.async;
```

---

## Task Spawning

### `spawn(task)`

Launches a new asynchronous task that runs the given closure. The task is scheduled on the runtime's thread pool and executes concurrently with the caller.

```xiom
fn spawn(task: fn())
```

---

## Channels

Communication primitives for sending values between concurrent tasks. Channels come in bounded (capacity-limited) and unbounded variants.

### `Channel[T]`

A typed channel for sending values of type `T` between tasks. Internally uses a ring buffer.

```xiom
type Channel[T] = { }
```

### `Channel.bounded(capacity)`

Creates a new bounded channel with the given buffer capacity. The channel can hold at most `capacity` messages before `send` blocks.

```xiom
fn Channel.bounded[T](capacity: Int) -> Channel[T]
```

### `Channel.unbounded()`

Creates a new unbounded channel with no limit on buffer size. `send` never blocks.

```xiom
fn Channel.unbounded[T]() -> Channel[T]
```

### `Channel.send(value)`

Sends a value into the channel. For bounded channels, this blocks if the buffer is full. For unbounded channels, this always succeeds immediately.

```xiom
fn Channel.send[T](value: T)
```

### `Channel.recv()`

Receives a value from the channel, blocking the current task until a message is available.

```xiom
fn Channel.recv[T]() -> T
```

### `Channel.try_recv()`

Attempts to receive a value without blocking. Returns `Some(value)` if a message is available, or `None` if the channel is empty.

```xiom
fn Channel.try_recv[T]() -> Option[T]
```

### `Channel.close()`

Closes the channel, preventing further sends. Outstanding messages can still be received. Once the buffer is drained, `recv` returns an error or signals the end of the stream.

```xiom
fn Channel.close[T]()
```
