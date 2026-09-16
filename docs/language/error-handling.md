<!--
Copyright (c) 2026 Eleftherios Notas and XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Error Handling

XIOM has no exceptions. Functions that can fail return `Result[T, E]`. Absence of a value is expressed through `Option[T]`. The compiler enforces exhaustive handling of both at every use site.

## Result Type

```xiom
fn parse_int(s: Str) -> Result[Int, ParseError] {
  // ...
}
```

`E` in `Result[T, E]` is **any type**. No `Error` interface is required. The standard library provides a `StdError` interface for its own functions. Library authors are free to use any error type.

```xiom
// All valid
Result[Int, Str]
Result[Config, IOError]
Result[Data, MyCustomErrorEnum]
```

## The `?` Operator

The `?` operator returns the error from the current function if the `Result` is `Err`. It is syntactic sugar for an explicit match that returns the error.

```xiom
use xiom.io;

fn load_config(path: Str) -> Result[Config, AppError] {
  let file   = io.read_file(path)?;     // returns Err on failure
  let config = parse_config(file)?;     // returns Err on failure
  return Ok(config);
}
```

`?` can only appear inside a function that returns `Result`.

## Match Exhaustion

Every `match` expression must cover all cases. The compiler rejects non-exhaustive matches.

```xiom
use xiom.io;

match parse_int("42") {
  Ok(n)  => io.print(n.to_str()),
  Err(e) => io.print_err(e.message),
}

// Matching an enum -- all variants required
match state {
  AgentState.Idle              => wait(),
  AgentState.Patrolling(route) => follow(route),
  AgentState.Attacking(target) => engage(target),
  AgentState.Dead(cause)       => log(cause),
}
```

Use `_` as a wildcard to cover remaining cases:

```xiom
match value {
  Some(v) => process(v),
  _       => {}  // handle all other cases
}
```

## Option Type

```xiom
let val: Option[Int] = Some(10);

// Unwrap with default
let n = val.unwrap_or(0);

// Pattern match
match val {
  Some(n) => use(n),
  None    => handle_absent(),
}

// Propagate None with ? (inside a function returning Option)
let n = val?;
```

## Constructors

```xiom
// Option
let present = Some(42);
let absent: Option[Int] = None;

// Result
let success = Ok("done");
let failure: Result[Str, IOError] = Err(IOError.new("file not found"));
```

## `?` Propagation Rules

- `Result` functions can use `?` on both `Result` and `Option` values
- `Option` functions can use `?` on `Option` values
- The `?` operator requires `From<SourceError>` for automatic error conversion at propagation sites
- `?` cannot appear outside a function that returns `Result` or `Option`

## Error Messages

When an unhandled error path exists, the compiler provides a clear error:

```
error[E0401]: non-exhaustive match
  --> src/main.xi:12:3
   |
12 |   match result {
   |         ^^^^^^ missing arm: Err(_)
   |
   = help: add a wildcard arm or handle the Err case explicitly
```
