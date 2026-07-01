# Benchmark Module

Benchmarking framework: running benchmarks, collecting timing results, and preventing compiler optimizations.

```
use axiom.bench;
```

## BenchResult

### `BenchResult`
The result of a benchmark run, containing timing statistics.

```
pub type BenchResult = {
    name: Str;
    iterations: Int;
    total_ns: Int;
    mean_ns: Int;
    min_ns: Int;
    max_ns: Int;
    stddev_ns: Int;
} derive[Clone]
```

## Running Benchmarks

### `run_bench(name, f)`
Runs the function `f` enough iterations to get a stable timing measurement and returns the `BenchResult`.

```
pub fn run_bench(name: Str, f: fn()) -> BenchResult;
```

### `run_bench_n(name, iterations, f)`
Runs the function `f` for exactly `iterations` iterations and returns the `BenchResult`.

```
pub fn run_bench_n(name: Str, iterations: Int, f: fn()) -> BenchResult;
```

## Comparison

### `compare(a, b)|
Compares two `BenchResult` values and returns a human-readable string describing the performance difference.

```
pub fn compare(a: BenchResult, b: BenchResult) -> Str;
```

## Black Box

### `black_box(value)|
Prevents the compiler from optimizing away the value. Returns the value as-is but forces the compiler to treat it as an opaque side effect.

```
pub fn black_box[T](value: T) -> T;
```
