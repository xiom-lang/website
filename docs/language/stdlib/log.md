<!--
Copyright (c) 2026 XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Log Module

Structured logging with log levels, structured key-value pairs, runtime configuration, and in-memory log querying.

```
use xiom.log;
```

## Types

### `LogLevel`
The severity level of a log entry.

```
pub type LogLevel = enum { Trace, Debug, Info, Warn, Error, Fatal }
```

### `LogEntry`
A single log entry with metadata.

```
pub type LogEntry = {
    level: LogLevel;
    message: Str;
    file: Str;
    line: Int;
    timestamp: Int;
    data: Map[Str, Str];
} derive[Clone]
```

## Core Logging

### `trace(msg)`
Logs a message at the `Trace` level.

```
pub fn trace(msg: Str);
```

### `debug(msg)`
Logs a message at the `Debug` level.

```
pub fn debug(msg: Str);
```

### `info(msg)`
Logs a message at the `Info` level.

```
pub fn info(msg: Str);
```

### `warn(msg)`
Logs a message at the `Warn` level.

```
pub fn warn(msg: Str);
```

### `error(msg)`
Logs a message at the `Error` level.

```
pub fn error(msg: Str);
```

### `fatal(msg)`
Logs a message at the `Fatal` level and then aborts the program.

```
pub fn fatal(msg: Str);
```

## Structured Logging

### `trace_with(msg, data)`
Logs a `Trace` message with structured key-value pairs.

```
pub fn trace_with(msg: Str, data: Map[Str, Str]);
```

### `debug_with(msg, data)`
Logs a `Debug` message with structured key-value pairs.

```
pub fn debug_with(msg: Str, data: Map[Str, Str]);
```

### `info_with(msg, data)`
Logs an `Info` message with structured key-value pairs.

```
pub fn info_with(msg: Str, data: Map[Str, Str]);
```

### `warn_with(msg, data)`
Logs a `Warn` message with structured key-value pairs.

```
pub fn warn_with(msg: Str, data: Map[Str, Str]);
```

### `error_with(msg, data)`
Logs an `Error` message with structured key-value pairs.

```
pub fn error_with(msg: Str, data: Map[Str, Str]);
```

## Configuration

### `set_level(level)`
Sets the minimum log level. Messages below this level are filtered out.

```
pub fn set_level(level: LogLevel);
```

### `get_level()`
Returns the current minimum log level.

```
pub fn get_level() -> LogLevel;
```

### `set_output(file)|
Redirects log output to a file. Returns an error if the file cannot be opened.

```
pub fn set_output(file: Str) -> Result[Unit, Str];
```

### `set_output_json(enabled)|
When enabled, log output is formatted as JSON.

```
pub fn set_output_json(enabled: Bool);
```

### `set_output_color(enabled)|
When enabled, log output uses ANSI color codes.

```
pub fn set_output_color(enabled: Bool);
```

## Query

### `entries_since(instant)|
Returns all log entries recorded since the given `Instant`.

```
pub fn entries_since(instant: Instant) -> Vec[LogEntry];
```

### `clear_log()`
Clears all in-memory log entries.

```
pub fn clear_log();
```
