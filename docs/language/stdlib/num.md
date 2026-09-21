<!--
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Numeric Module

Extended numeric traits, operations, bounds, bit manipulation, float classification, and checked/saturating/wrapping arithmetic.

```
use xiom.num;
```

## Numeric Traits

### `Neg`
Trait for types that support negation.

```
pub interface Neg { fn neg(self) -> Self; }
```

### `Rem`
Trait for types that support the remainder operation.

```
pub interface Rem { fn rem(self, other: Self) -> Self; }
```

### `Abs`
Trait for types that support absolute value.

```
pub interface Abs { fn abs(self) -> Self; }
```

### `Pow`
Trait for types that support exponentiation.

```
pub interface Pow { fn pow(self, exp: Self) -> Self; }
```

### `Sqrt`
Trait for types that support square root.

```
pub interface Sqrt { fn sqrt(self) -> Self; }
```

## Numeric Bounds

### `min_value()`
Returns the minimum finite value of a numeric type.

```
pub fn min_value[T]() -> T;
```

### `max_value()`
Returns the maximum finite value of a numeric type.

```
pub fn max_value[T]() -> T;
```

### `epsilon()`
Returns the machine epsilon of a floating-point type.

```
pub fn epsilon[T]() -> T;
```

## Integer Operations

### `gcd(a, b)`
Computes the greatest common divisor of two integers.

```
pub fn gcd(a: Int, b: Int) -> Int;
```

### `lcm(a, b)`
Computes the least common multiple of two integers.

```
pub fn lcm(a: Int, b: Int) -> Int;
```

### `is_power_of_two(n)`
Returns `true` if `n` is a power of two.

```
pub fn is_power_of_two(n: Int) -> Bool;
```

### `next_power_of_two(n)`
Returns the smallest power of two greater than or equal to `n`.

```
pub fn next_power_of_two(n: Int) -> Int;
```

### `count_ones(n)`
Returns the number of ones in the binary representation of `n`.

```
pub fn count_ones(n: Int) -> Int;
```

### `count_zeros(n)`
Returns the number of zeros in the binary representation of `n`.

```
pub fn count_zeros(n: Int) -> Int;
```

### `leading_zeros(n)`
Returns the number of leading zeros in the binary representation of `n`.

```
pub fn leading_zeros(n: Int) -> Int;
```

### `trailing_zeros(n)`
Returns the number of trailing zeros in the binary representation of `n`.

```
pub fn trailing_zeros(n: Int) -> Int;
```

### `rotate_left(n, k)`
Rotates the bits of `n` left by `k` positions.

```
pub fn rotate_left(n: Int, k: Int) -> Int;
```

### `rotate_right(n, k)`
Rotates the bits of `n` right by `k` positions.

```
pub fn rotate_right(n: Int, k: Int) -> Int;
```

### `reverse_bits(n)`
Reverses the bit order of `n`.

```
pub fn reverse_bits(n: Int) -> Int;
```

### `to_be(n)`
Converts `n` from little-endian to big-endian (native-to-big-endian byte swap).

```
pub fn to_be(n: Int) -> Int;
```

### `to_le(n)`
Converts `n` from big-endian to little-endian (native-to-little-endian byte swap).

```
pub fn to_le(n: Int) -> Int;
```

### `from_be(n)`
Converts `n` from big-endian to native endianness.

```
pub fn from_be(n: Int) -> Int;
```

### `from_le(n)`
Converts `n` from little-endian to native endianness.

```
pub fn from_le(n: Int) -> Int;
```

## Float Operations

### `is_finite(x)`
Returns `true` if the float is finite (not infinite and not NaN).

```
pub fn is_finite(x: Float64) -> Bool;
```

### `is_normal(x)`
Returns `true` if the float is a normal number (not zero, subnormal, infinite, or NaN).

```
pub fn is_normal(x: Float64) -> Bool;
```

### `classify(x)`
Classifies the float: `0` = NaN, `1` = infinite, `2` = zero, `3` = subnormal, `4` = normal.

```
pub fn classify(x: Float64) -> Int;
```

### `floor(x)`
Returns the largest integer less than or equal to `x`.

```
pub fn floor(x: Float64) -> Int;
```

### `ceil(x)`
Returns the smallest integer greater than or equal to `x`.

```
pub fn ceil(x: Float64) -> Int;
```

### `round(x)`
Rounds `x` to the nearest integer, with half rounding away from zero.

```
pub fn round(x: Float64) -> Int;
```

### `trunc(x)`
Truncates the fractional part of `x`, returning the integer part.

```
pub fn trunc(x: Float64) -> Int;
```

### `fract(x)`
Returns the fractional part of `x`.

```
pub fn fract(x: Float64) -> Float64;
```

### `recip(x)`
Returns the reciprocal (1/x) of `x`.

```
pub fn recip(x: Float64) -> Float64;
```

### `to_degrees(rad)`
Converts radians to degrees.

```
pub fn to_degrees(rad: Float64) -> Float64;
```

### `to_radians(deg)`
Converts degrees to radians.

```
pub fn to_radians(deg: Float64) -> Float64;
```

### `hypot(x, y)`
Computes the Euclidean norm `sqrt(x^2 + y^2)`.

```
pub fn hypot(x: Float64, y: Float64) -> Float64;
```

## Saturation Arithmetic

### `saturating_add(a, b)`
Adds `a` and `b`, saturating at the numeric bounds instead of overflowing.

```
pub fn saturating_add[T](a: T, b: T) -> T;
```

### `saturating_sub(a, b)`
Subtracts `b` from `a`, saturating at the numeric bounds instead of overflowing.

```
pub fn saturating_sub[T](a: T, b: T) -> T;
```

### `saturating_mul(a, b)`
Multiplies `a` and `b`, saturating at the numeric bounds instead of overflowing.

```
pub fn saturating_mul[T](a: T, b: T) -> T;
```

## Checked Arithmetic

### `checked_add(a, b)`
Adds `a` and `b`, returning `None` on overflow.

```
pub fn checked_add[T](a: T, b: T) -> Option[T];
```

### `checked_sub(a, b)`
Subtracts `b` from `a`, returning `None` on overflow.

```
pub fn checked_sub[T](a: T, b: T) -> Option[T];
```

### `checked_mul(a, b)`
Multiplies `a` and `b`, returning `None` on overflow.

```
pub fn checked_mul[T](a: T, b: T) -> Option[T];
```

### `checked_div(a, b)`
Divides `a` by `b`, returning `None` if `b` is zero.

```
pub fn checked_div[T](a: T, b: T) -> Option[T];
```

## Wrapping Arithmetic

### `wrapping_add(a, b)`
Adds `a` and `b`, wrapping around on overflow.

```
pub fn wrapping_add[T](a: T, b: T) -> T;
```

### `wrapping_sub(a, b)`
Subtracts `b` from `a`, wrapping around on overflow.

```
pub fn wrapping_sub[T](a: T, b: T) -> T;
```

### `wrapping_mul(a, b)`
Multiplies `a` and `b`, wrapping around on overflow.

```
pub fn wrapping_mul[T](a: T, b: T) -> T;
```

## Parsing

### `parse_int(s)`
Parses a string as a decimal integer.

```
pub fn parse_int(s: Str) -> Result[Int, Str];
```

### `parse_float(s)`
Parses a string as a 64-bit float.

```
pub fn parse_float(s: Str) -> Result[Float64, Str];
```

### `parse_int_radix(s, radix)`
Parses a string as an integer in the given radix (2-36).

```
pub fn parse_int_radix(s: Str, radix: Int) -> Result[Int, Str];
```
