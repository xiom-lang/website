<!--
Copyright (c) 2026 Eleftherios Notas and XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Time Module

Time types: `Duration`, `Instant`, `SystemTime`, `DateTime`, and sleep functions.

```
use xiom.time;
```

## Duration

### `Duration`
A span of time measured in seconds and nanoseconds.

```
pub type Duration = {
    secs: Int;
    nanos: Int;
} derive[Eq, Clone, Ord]
```

### `Duration.from_secs(s)`
Creates a `Duration` from a whole number of seconds.

```
pub fn Duration.from_secs(s: Int) -> Duration;
```

### `Duration.from_millis(ms)`
Creates a `Duration` from a whole number of milliseconds.

```
pub fn Duration.from_millis(ms: Int) -> Duration;
```

### `Duration.from_micros(us)`
Creates a `Duration` from a whole number of microseconds.

```
pub fn Duration.from_micros(us: Int) -> Duration;
```

### `Duration.from_nanos(ns)`
Creates a `Duration` from a whole number of nanoseconds.

```
pub fn Duration.from_nanos(ns: Int) -> Duration;
```

### `Duration.as_secs(self)`
Returns the total duration in whole seconds.

```
pub fn Duration.as_secs(self) -> Int;
```

### `Duration.as_millis(self)`
Returns the total duration in whole milliseconds.

```
pub fn Duration.as_millis(self) -> Int;
```

### `Duration.subsec_nanos(self)`
Returns the fractional part of the duration in nanoseconds (less than 1 second).

```
pub fn Duration.subsec_nanos(self) -> Int;
```

### `Duration.checked_add(self, other)`
Adds two durations, returning `None` on overflow.

```
pub fn Duration.checked_add(self, other: Duration) -> Option[Duration];
```

### `Duration.checked_sub(self, other)`
Subtracts two durations, returning `None` if the result would be negative.

```
pub fn Duration.checked_sub(self, other: Duration) -> Option[Duration];
```

## Instant

### `Instant`
A monotonic point in time (always increasing, not affected by system clock adjustments).

```
pub type Instant = { t: Int; }
```

### `Instant.now()`
Returns the current instant from the monotonic clock.

```
pub fn Instant.now() -> Instant;
```

### `Instant.elapsed(self)`
Returns the `Duration` since this instant was created.

```
pub fn Instant.elapsed(self) -> Duration;
```

### `Instant.duration_since(self, earlier)`
Returns the `Duration` from `earlier` to `self`. Panics if `earlier` is later than `self`.

```
pub fn Instant.duration_since(self, earlier: Instant) -> Duration;
```

## SystemTime

### `SystemTime`
A point in time relative to the system clock (wall clock).

```
pub type SystemTime = { secs: Int; nanos: Int; }
```

### `SystemTime.now()`
Returns the current system time.

```
pub fn SystemTime.now() -> SystemTime;
```

### `SystemTime.unix_epoch()`
Returns the system time corresponding to the Unix epoch (1970-01-01T00:00:00Z).

```
pub fn SystemTime.unix_epoch() -> SystemTime;
```

### `SystemTime.duration_since(self, earlier)`
Returns the `Duration` from `earlier` to `self`. Returns an error if `earlier` is later than `self`.

```
pub fn SystemTime.duration_since(self, earlier: SystemTime) -> Result[Duration, Str];
```

### `SystemTime.secs_since_epoch(self)`
Returns the number of seconds since the Unix epoch.

```
pub fn SystemTime.secs_since_epoch(self) -> Int;
```

## DateTime

### `DateTime`
A calendar date and time with year, month, day, hour, minute, second, and weekday.

```
pub type DateTime = {
    year: Int;
    month: Int;
    day: Int;
    hour: Int;
    minute: Int;
    second: Int;
    weekday: Int;
}
```

### `utc_now()`
Returns the current UTC date and time as a `DateTime`.

```
pub fn utc_now() -> DateTime;
```

### `local_now()`
Returns the current local date and time as a `DateTime`.

```
pub fn local_now() -> DateTime;
```

## Sleep

### `sleep(dur)`
Blocks the current thread for the given `Duration`.

```
pub fn sleep(dur: Duration);
```

### `sleep_ms(ms)`
Blocks the current thread for the given number of milliseconds.

```
pub fn sleep_ms(ms: Int);
```

### `sleep_until(instant)`
Blocks the current thread until the given `Instant`.

```
pub fn sleep_until(instant: Instant);
```
