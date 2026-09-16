<!--
Copyright (c) 2026 Eleftherios Notas and XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Random Module

Random number generation: the `Rng` trait, standard RNG, distributions, shuffle/pick, and UUID generation.

```
use xiom.rand;
```

## Rng Trait

### `Rng`
The trait for random number generators.

```
pub interface Rng {
    fn next_int(self) -> Int;
    fn next_float(self) -> Float64;
    fn next_bytes(self, buf: &mut Vec[UInt8]);
}
```

### `Rng.next_int(self)`
Generates a random integer.

### `Rng.next_float(self)`
Generates a random float in [0, 1).

### `Rng.next_bytes(self, buf)`
Fills the buffer with random bytes.

## StdRng

### `StdRng`
The standard cryptographically secure random number generator (where available).

```
pub type StdRng = { state: Int; } derive[Clone]
```

### `StdRng.new()`
Creates a new `StdRng` seeded from system entropy.

```
pub fn StdRng.new() -> StdRng;
```

### `StdRng.from_seed(seed)`
Creates a deterministic `StdRng` from a given seed value.

```
pub fn StdRng.from_seed(seed: Int) -> StdRng;
```

## Basic Random Values

### `random()`
Returns a random `Float64` in [0, 1).

```
pub fn random() -> Float64;
```

### `random_int(min, max)`
Returns a random integer in [min, max] (inclusive).

```
pub fn random_int(min: Int, max: Int) -> Int;
```

### `random_float(min, max)`
Returns a random `Float64` in [min, max) (exclusive upper bound).

```
pub fn random_float(min: Float64, max: Float64) -> Float64;
```

### `random_bool()`
Returns a random boolean with equal probability.

```
pub fn random_bool() -> Bool;
```

### `random_bytes(count)`
Returns a vector of `count` random bytes.

```
pub fn random_bytes(count: Int) -> Vec[UInt8];
```

## Distributions

### `sample_uniform(min, max)`
Samples from a uniform distribution over [min, max).

```
pub fn sample_uniform(min: Float64, max: Float64) -> Float64;
```

### `sample_normal(mean, stddev)`
Samples from a normal (Gaussian) distribution with the given mean and standard deviation.

```
pub fn sample_normal(mean: Float64, stddev: Float64) -> Float64;
```

### `sample_exponential(lambda)`
Samples from an exponential distribution with the given rate parameter.

```
pub fn sample_exponential(lambda: Float64) -> Float64;
```

### `sample_bernoulli(p)`
Samples from a Bernoulli distribution: returns `true` with probability `p`.

```
pub fn sample_bernoulli(p: Float64) -> Bool;
```

### `sample_binomial(n, p)`
Samples from a binomial distribution with `n` trials and success probability `p`.

```
pub fn sample_binomial(n: Int, p: Float64) -> Int;
```

### `sample_poisson(lambda)`
Samples from a Poisson distribution with the given rate.

```
pub fn sample_poisson(lambda: Float64) -> Int;
```

### `sample_gamma(shape, scale)`
Samples from a gamma distribution with the given shape and scale parameters.

```
pub fn sample_gamma(shape: Float64, scale: Float64) -> Float64;
```

### `sample_beta(alpha, beta)`
Samples from a beta distribution with the given alpha and beta parameters.

```
pub fn sample_beta(alpha: Float64, beta: Float64) -> Float64;
```

## Shuffle & Pick

### `shuffle(items)`
Randomly shuffles a vector in-place using the Fisher-Yates algorithm.

```
pub fn shuffle[T](items: &mut Vec[T]);
```

### `pick(items)`
Returns a reference to a random element, or `None` if the vector is empty.

```
pub fn pick[T](items: &Vec[T]) -> Option<&T>;
```

### `pick_n(items, n)`
Returns `n` random element references from the vector (with replacement).

```
pub fn pick_n[T](items: &Vec[T], n: Int) -> Vec<&T>;
```

### `weighted_pick(items, weights)`
Picks a random element using weighted probabilities. Returns `None` if the vector is empty.

```
pub fn weighted_pick[T](items: &Vec[T], weights: &Vec<Float64>) -> Option<&T>;
```

## UUID

### `uuid_v4()`
Generates a random UUID version 4 string (e.g., `"f47ac10b-58cc-4372-a567-0e02b2c3d479"`).

```
pub fn uuid_v4() -> Str;
```

### `uuid_v7()`
Generates a time-ordered UUID version 7 string.

```
pub fn uuid_v7() -> Str;
```

## Seeding

### `seed_from_entropy()`
Seeds the global random generator from system entropy.

```
pub fn seed_from_entropy();
```

### `seed_from_time()`
Seeds the global random generator from the current system time.

```
pub fn seed_from_time();
```

### `seed_from_value(seed)`
Seeds the global random generator with a specific value.

```
pub fn seed_from_value(seed: Int);
```
