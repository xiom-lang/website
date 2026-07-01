# Conversion Module

Type conversion traits (`From`, `Into`, `TryFrom`, `TryInto`) and common conversion functions.

```
use axiom.convert;
```

## Traits

### `From[T]`
The trait for infallible conversions from one type to another.

```
pub interface From[T] { fn from(value: T) -> Self; }
```

### `From.from(value)`
Converts a value of type `T` into `Self`.

### `Into[T]`
The reciprocal of `From`. Implementing `From[T] for U` automatically provides `Into[U] for T`.

```
pub interface Into[T] { fn into(self) -> T; }
```

### `Into.into(self)`
Converts `self` into a value of type `T`.

### `TryFrom[T]`
The trait for fallible conversions that may fail at runtime.

```
pub interface TryFrom[T] { fn try_from(value: T) -> Result<Self, Str>; }
```

### `TryFrom.try_from(value)`
Attempts to convert a value of type `T` into `Self`, returning an error on failure.

### `TryInto[T]`
The reciprocal of `TryFrom`. Implementing `TryFrom[T] for U` automatically provides `TryInto[U] for T`.

```
pub interface TryInto[T] { fn try_into(self) -> Result<T, Str>; }
```

### `TryInto.try_into(self)`
Attempts to convert `self` into a value of type `T`, returning an error on failure.

## Identity

### `identity(x)`
Returns the input value unchanged.

```
pub fn identity[T](x: T) -> T;
```

## Common Conversions

### `int_to_float(n)`
Converts an integer to a `Float64`.

```
pub fn int_to_float(n: Int) -> Float64;
```

### `float_to_int(f)`
Converts a `Float64` to an integer, truncating the fractional part.

```
pub fn float_to_int(f: Float64) -> Int;
```

### `int_to_string(n)`
Converts an integer to its string representation.

```
pub fn int_to_string(n: Int) -> Str;
```

### `float_to_string(f)`
Converts a `Float64` to its string representation.

```
pub fn float_to_string(f: Float64) -> Str;
```

### `bool_to_string(b)`
Converts a boolean to its string representation (`"true"` or `"false"`).

```
pub fn bool_to_string(b: Bool) -> Str;
```

### `char_to_int(c)`
Converts a character to its Unicode scalar value (code point).

```
pub fn char_to_int(c: Char) -> Int;
```

### `int_to_char(n)`
Converts a Unicode scalar value to a character. Returns `None` if the value is not a valid Unicode code point.

```
pub fn int_to_char(n: Int) -> Option[Char];
```
