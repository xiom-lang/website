<!--
Copyright (c) 2026 Eleftherios Notas and XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Math Library

The `math` module provides mathematical constants, basic arithmetic functions, trigonometric functions, logarithmic and exponential functions, bitwise operations, random number generation, and utility functions for floating-point values.

```
use xiom.math;
```

---

## Constants

### `PI`
The mathematical constant pi (pi), approximately 3.141592653589793.

```xiom
const PI: Float64;
```

### `E`
The mathematical constant e (Euler's number), approximately 2.718281828459045.

```xiom
const E: Float64;
```

### `TAU`
The mathematical constant tau (tau), equal to 2pi, approximately 6.283185307179586.

```xiom
const TAU: Float64;
```

---

## Basic Arithmetic

### `sqrt(x)`
Returns the non-negative square root of `x`. Returns `NaN` if `x` is negative.

```xiom
fn sqrt(x: Float64) -> Float64;
```

### `pow(base, exp)`
Returns `base` raised to the power of `exp`.

```xiom
fn pow(base: Float64, exp: Float64) -> Float64;
```

### `abs_int(x)`
Returns the absolute value of `x`. For the minimum negative value, returns `x` (overflow).

```xiom
fn abs_int(x: Int) -> Int;
```

### `abs_float(x)`
Returns the absolute value of `x`. Returns `NaN` if `x` is `NaN`, `Inf` if `x` is infinite.

```xiom
fn abs_float(x: Float64) -> Float64;
```

### `min_int(a, b)`
Returns the smaller of `a` and `b`.

```xiom
fn min_int(a: Int, b: Int) -> Int;
```

### `max_int(a, b)`
Returns the larger of `a` and `b`.

```xiom
fn max_int(a: Int, b: Int) -> Int;
```

### `min_float(a, b)`
Returns the smaller of `a` and `b`. If either argument is `NaN`, returns `NaN`.

```xiom
fn min_float(a: Float64, b: Float64) -> Float64;
```

### `max_float(a, b)`
Returns the larger of `a` and `b`. If either argument is `NaN`, returns `NaN`.

```xiom
fn max_float(a: Float64, b: Float64) -> Float64;
```

### `floor(x)`
Returns the largest integer less than or equal to `x`, as an `Int`.

```xiom
fn floor(x: Float64) -> Int;
```

### `ceil(x)`
Returns the smallest integer greater than or equal to `x`, as an `Int`.

```xiom
fn ceil(x: Float64) -> Int;
```

### `round(x)`
Returns the integer nearest to `x`, rounding half away from zero.

```xiom
fn round(x: Float64) -> Int;
```

---

## Trigonometric Functions

All trigonometric functions operate on radians.

### `sin(x)`
Returns the sine of `x`.

```xiom
fn sin(x: Float64) -> Float64;
```

### `cos(x)`
Returns the cosine of `x`.

```xiom
fn cos(x: Float64) -> Float64;
```

### `tan(x)`
Returns the tangent of `x`.

```xiom
fn tan(x: Float64) -> Float64;
```

### `asin(x)`
Returns the arcsine of `x` in the range [-pi/2, pi/2]. Returns `NaN` if `|x| > 1`.

```xiom
fn asin(x: Float64) -> Float64;
```

### `acos(x)`
Returns the arccosine of `x` in the range [0, pi]. Returns `NaN` if `|x| > 1`.

```xiom
fn acos(x: Float64) -> Float64;
```

### `atan(x)`
Returns the arctangent of `x` in the range [-pi/2, pi/2].

```xiom
fn atan(x: Float64) -> Float64;
```

### `atan2(y, x)`
Returns the four-quadrant arctangent of `y / x` in the range [-pi, pi]. Uses the signs of both arguments to determine the correct quadrant.

```xiom
fn atan2(y: Float64, x: Float64) -> Float64;
```

---

## Logarithmic & Exponential

### `exp(x)`
Returns e raised to the power of `x`.

```xiom
fn exp(x: Float64) -> Float64;
```

### `ln(x)`
Returns the natural logarithm (base e) of `x`. Returns `-Inf` for `x = 0`, `NaN` for negative `x`.

```xiom
fn ln(x: Float64) -> Float64;
```

### `log10(x)`
Returns the base-10 logarithm of `x`. Returns `-Inf` for `x = 0`, `NaN` for negative `x`.

```xiom
fn log10(x: Float64) -> Float64;
```

### `log2(x)`
Returns the base-2 logarithm of `x`. Returns `-Inf` for `x = 0`, `NaN` for negative `x`.

```xiom
fn log2(x: Float64) -> Float64;
```

---

## Bitwise Operations

Int arguments are treated as two's-complement signed integers.

### `bit_and(a, b)`
Returns the bitwise AND of `a` and `b`.

```xiom
fn bit_and(a: Int, b: Int) -> Int;
```

### `bit_or(a, b)`
Returns the bitwise OR of `a` and `b`.

```xiom
fn bit_or(a: Int, b: Int) -> Int;
```

### `bit_xor(a, b)`
Returns the bitwise XOR of `a` and `b`.

```xiom
fn bit_xor(a: Int, b: Int) -> Int;
```

### `bit_not(a)`
Returns the bitwise NOT (one's complement) of `a`.

```xiom
fn bit_not(a: Int) -> Int;
```

### `shl(a, n)`
Returns `a` shifted left by `n` bits. Low-order bits are filled with zeros.

```xiom
fn shl(a: Int, n: Int) -> Int;
```

### `shr(a, n)`
Returns `a` shifted right by `n` bits, preserving the sign bit (arithmetic shift).

```xiom
fn shr(a: Int, n: Int) -> Int;
```

---

## Random Number Generation

### `seed_rng(seed)`
Initializes the global random number generator with `seed`. If not called, the generator is seeded from system entropy.

```xiom
fn seed_rng(seed: Int);
```

### `random()`
Returns a pseudo-random `Float64` in the range [0.0, 1.0).

```xiom
fn random() -> Float64;
```

### `random_range(min, max)`
Returns a pseudo-random `Int` in the range [`min`, `max`] (inclusive on both ends).

```xiom
fn random_range(min: Int, max: Int) -> Int;
```

### `random_float()`
Returns a pseudo-random `Float64` in the range [0.0, 1.0). Synonymous with `random()`.

```xiom
fn random_float() -> Float64;
```

---

## Utility Functions

### `clamp(x, min, max)`
Clamps `x` to the range [`min`, `max`]: returns `min` if `x < min`, `max` if `x > max`, otherwise `x`.

```xiom
fn clamp(x: Float64, min: Float64, max: Float64) -> Float64;
```

### `lerp(a, b, t)`
Performs linear interpolation between `a` and `b` by factor `t`. Returns `a + (b - a) * t`. When `t = 0.0`, returns `a`; when `t = 1.0`, returns `b`.

```xiom
fn lerp(a: Float64, b: Float64, t: Float64) -> Float64;
```

### `is_nan(x)`
Returns true if `x` is a `NaN` (not-a-number) value.

```xiom
fn is_nan(x: Float64) -> Bool;
```

### `is_inf(x)`
Returns true if `x` is positive or negative infinity.

```xiom
fn is_inf(x: Float64) -> Bool;
```
