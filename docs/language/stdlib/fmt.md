# Format Module

String formatting via the `Display` trait and `Formatter` type.

```
use xiom.fmt;
```

## Display

### `Display`
The trait for types that can be formatted as human-readable strings.

```
pub interface Display {
    fn fmt(self, f: &mut Formatter) -> Result[Unit, FmtError];
}
```

### `Display.fmt(self, f)`
Writes the formatted representation of `self` to the given `Formatter`.

## Formatter

### `Formatter`
Accumulates formatted output with configurable width, precision, and alignment.

```
pub type Formatter = { buf: Str; width: Int; precision: Int; align: Int; } derive[Clone]
```

Alignment values: `0` = left, `1` = right, `2` = center.

### `Formatter.new()`
Creates a new empty `Formatter` with default settings.

```
pub fn Formatter.new() -> Formatter;
```

### `Formatter.write_str(self, s)`
Writes a string to the formatter's buffer.

```
pub fn Formatter.write_str(self, s: Str) -> Result[Unit, FmtError];
```

### `Formatter.write_int(self, n)`
Writes an integer to the formatter's buffer.

```
pub fn Formatter.write_int(self, n: Int) -> Result[Unit, FmtError];
```

### `Formatter.write_float(self, f)`
Writes a float to the formatter's buffer.

```
pub fn Formatter.write_float(self, f: Float64) -> Result[Unit, FmtError];
```

### `Formatter.write_bool(self, b)`
Writes a boolean (`"true"` or `"false"`) to the formatter's buffer.

```
pub fn Formatter.write_bool(self, b: Bool) -> Result[Unit, FmtError];
```

### `Formatter.finish(self)`
Finalizes formatting and returns the accumulated string.

```
pub fn Formatter.finish(self) -> Str;
```

## FmtError

### `FmtError`
An error returned when formatting fails.

```
pub type FmtError = { message: Str; } derive[Clone]
```
