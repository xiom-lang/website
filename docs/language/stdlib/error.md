<!--
Copyright (c) 2026 Eleftherios Notas and XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Error Module

Provides the `Error` interface, error chaining, backtrace capture, and error context wrapping.

```
use xiom.error;
```

## Error Interface

### `Error`
The base trait for all error types. Provides introspection into the error chain.

```
pub interface Error {
    fn source(self) -> Option<Error>;
    fn description(self) -> Str;
    fn cause(self) -> Option<Error>;
}
```

### `Error.source(self)`
Returns the lower-level source of this error, if any.

### `Error.description(self)`
Returns a human-readable description of the error.

### `Error.cause(self)`
Alias for `source`. Returns the lower-level cause of this error.

## Error Chain

### `ErrorChain`
A flattened chain of error messages collected by walking the `source` chain.

```
pub type ErrorChain = { errors: Vec<Str>; } derive[Clone]
```

### `Error.chain(self)`
Walks the error's source chain and collects all error descriptions into an `ErrorChain`.

### `ErrorChain.display(self)`
Formats the error chain as a multi-line string, with each error indented.

## Error Context

### `wrap_error(result, context)`
Wraps a `Result[T, E]` error with additional contextual information, producing a `Result[T, Str]`.

```
pub fn wrap_error[T, E: Error](result: Result[T, E], context: Str) -> Result[T, Str];
```

### `context(result, msg)`
Attaches a contextual message to a `Result` error without changing its type. If the result is already an error, prepends the message.

```
pub fn context[T, E](result: Result[T, E], msg: Str) -> Result[T, Str];
```

## Backtrace

### `Backtrace`
Captured stack backtrace information.

```
pub type Backtrace = { frames: Vec<Str>; } derive[Clone]
```

### `capture_backtrace()`
Captures the current call stack and returns it as a `Backtrace`.

### `Backtrace.display(self)`
Formats the backtrace as a human-readable multi-line string.
