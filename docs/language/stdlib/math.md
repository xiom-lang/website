# Math Library

The `math` module provides mathematical constants, basic arithmetic functions, trigonometric functions, logarithmic and exponential functions, bitwise operations, random number generation, and utility functions for floating-point values.

```
use axiom.math;
```

---

## Constants

### `PI`
The mathematical constant π (pi), approximately 3.141592653589793.

```axiom
const PI: Float64;
```

### `E`
The mathematical constant e (Euler's number), approximately 2.718281828459045.

```axiom
const E: Float64;
```

### `TAU`
The mathematical constant τ (tau), equal to 2π, approximately 6.283185307179586.

```axiom
const TAU: Float64;
```

---

## Basic Arithmetic

### `sqrt(x)`
Returns the non-negative square root of `x`. Returns `NaN` if `x` is negative.

```axiom
fn sqrt(x: Float64) -> Float64;
```

### `pow(base, exp)`
Returns `base` raised to the power of `exp`.

```axiom
fn pow(base: Float64, exp: Float64) -> Float64;
```

### `abs_int(x)`
Returns the absolute value of `x`. For the minimum negative value, returns `x` (overflow).

```axiom
fn abs_int(x: Int) -> Int;
```

### `abs_float(x)`
Returns the absolute value of `x`. Returns `NaN` if `x` is `NaN`, `Inf` if `x` is infinite.

```axiom
fn abs_float(x: Float64) -> Float64;
```

### `min_int(a, b)`
Returns the smaller of `a` and `b`.

```axiom
fn min_int(a: Int, b: Int) -> Int;
```

### `max_int(a, b)`
Returns the larger of `a` and `b`.

```axiom
fn max_int(a: Int, b: Int) -> Int;
```

### `min_float(a, b)`
Returns the smaller of `a` and `b`. If either argument is `NaN`, returns `NaN`.

```axiom
fn min_float(a: Float64, b: Float64) -> Float64;
```

### `max_float(a, b)`
Returns the larger of `a` and `b`. If either argument is `NaN`, returns `NaN`.

```axiom
fn max_float(a: Float64, b: Float64) -> Float64;
```

### `floor(x)`
Returns the largest integer less than or equal to `x`, as an `Int`.

```axiom
fn floor(x: Float64) -> Int;
```

### `ceil(x)`
Returns the smallest integer greater than or equal to `x`, as an `Int`.

```axiom
fn ceil(x: Float64) -> Int;
```

### `round(x)`
Returns the integer nearest to `x`, rounding half away from zero.

```axiom
fn round(x: Float64) -> Int;
```

---

## Trigonometric Functions

All trigonometric functions operate on radians.

### `sin(x)`
Returns the sine of `x`.

```axiom
fn sin(x: Float64) -> Float64;
```

### `cos(x)`
Returns the cosine of `x`.

```axiom
fn cos(x: Float64) -> Float64;
```

### `tan(x)`
Returns the tangent of `x`.

```axiom
fn tan(x: Float64) -> Float64;
```

### `asin(x)`
Returns the arcsine of `x` in the range [-π/2, π/2]. Returns `NaN` if `|x| > 1`.

```axiom
fn asin(x: Float64) -> Float64;
```

### `acos(x)`
Returns the arccosine of `x` in the range [0, π]. Returns `NaN` if `|x| > 1`.

```axiom
fn acos(x: Float64) -> Float64;
```

### `atan(x)`
Returns the arctangent of `x` in the range [-π/2, π/2].

```axiom
fn atan(x: Float64) -> Float64;
```

### `atan2(y, x)`
Returns the four-quadrant arctangent of `y / x` in the range [-π, π]. Uses the signs of both arguments to determine the correct quadrant.

```axiom
fn atan2(y: Float64, x: Float64) -> Float64;
```

---

## Logarithmic & Exponential

### `exp(x)`
Returns e raised to the power of `x`.

```axiom
fn exp(x: Float64) -> Float64;
```

### `ln(x)`
Returns the natural logarithm (base e) of `x`. Returns `-Inf` for `x = 0`, `NaN` for negative `x`.

```axiom
fn ln(x: Float64) -> Float64;
```

### `log10(x)`
Returns the base-10 logarithm of `x`. Returns `-Inf` for `x = 0`, `NaN` for negative `x`.

```axiom
fn log10(x: Float64) -> Float64;
```

### `log2(x)`
Returns the base-2 logarithm of `x`. Returns `-Inf` for `x = 0`, `NaN` for negative `x`.

```axiom
fn log2(x: Float64) -> Float64;
```

---

## Bitwise Operations

Int arguments are treated as two's-complement signed integers.

### `bit_and(a, b)`
Returns the bitwise AND of `a` and `b`.

```axiom
fn bit_and(a: Int, b: Int) -> Int;
```

### `bit_or(a, b)`
Returns the bitwise OR of `a` and `b`.

```axiom
fn bit_or(a: Int, b: Int) -> Int;
```

### `bit_xor(a, b)`
Returns the bitwise XOR of `a` and `b`.

```axiom
fn bit_xor(a: Int, b: Int) -> Int;
```

### `bit_not(a)`
Returns the bitwise NOT (one's complement) of `a`.

```axiom
fn bit_not(a: Int) -> Int;
```

### `shl(a, n)`
Returns `a` shifted left by `n` bits. Low-order bits are filled with zeros.

```axiom
fn shl(a: Int, n: Int) -> Int;
```

### `shr(a, n)`
Returns `a` shifted right by `n` bits, preserving the sign bit (arithmetic shift).

```axiom
fn shr(a: Int, n: Int) -> Int;
```

---

## Random Number Generation

### `seed_rng(seed)`
Initializes the global random number generator with `seed`. If not called, the generator is seeded from system entropy.

```axiom
fn seed_rng(seed: Int);
```

### `random()`
Returns a pseudo-random `Float64` in the range [0.0, 1.0).

```axiom
fn random() -> Float64;
```

### `random_range(min, max)`
Returns a pseudo-random `Int` in the range [`min`, `max`] (inclusive on both ends).

```axiom
fn random_range(min: Int, max: Int) -> Int;
```

### `random_float()`
Returns a pseudo-random `Float64` in the range [0.0, 1.0). Synonymous with `random()`.

```axiom
fn random_float() -> Float64;
```

---

## Utility Functions

### `clamp(x, min, max)`
Clamps `x` to the range [`min`, `max`]: returns `min` if `x < min`, `max` if `x > max`, otherwise `x`.

```axiom
fn clamp(x: Float64, min: Float64, max: Float64) -> Float64;
```

### `lerp(a, b, t)`
Performs linear interpolation between `a` and `b` by factor `t`. Returns `a + (b - a) * t`. When `t = 0.0`, returns `a`; when `t = 1.0`, returns `b`.

```axiom
fn lerp(a: Float64, b: Float64, t: Float64) -> Float64;
```

### `is_nan(x)`
Returns true if `x` is a `NaN` (not-a-number) value.

```axiom
fn is_nan(x: Float64) -> Bool;
```

### `is_inf(x)`
Returns true if `x` is positive or negative infinity.

```axiom
fn is_inf(x: Float64) -> Bool;
```
