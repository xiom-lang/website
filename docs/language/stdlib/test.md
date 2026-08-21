# `xiom.test` -- Test Framework

A contract-aware testing framework with assertions, contract verification, test runners, formatters, and benchmarking.

```xiom
use xiom.test;
```

---

## Types

### `TestResult`

Represents the result of a single test, including whether it passed, the test name, a message, any contract violations that occurred, and the execution duration.

```xiom
pub type TestResult = {
  passed: Bool;
  name: Str;
  message: Str;
  contract_failures: Vec[ContractFailure];
  duration_ms: Int;
} derive[Clone]
```

### `ContractFailure`

Records a contract violation encountered during a test. Includes the clause type (`"requires"`, `"ensures"`, or `"invariant"`), the contract expression text, the actual values at the time of violation, and the source location.

```xiom
pub type ContractFailure = {
  clause: Str;
  expression: Str;
  values: Str;
  location: Str;
} derive[Clone]
```

---

## Assertions

### `assert(condition, name)`

Asserts that `condition` is truthy. The test passes if `condition` evaluates to `true`.

```xiom
pub fn assert(condition: Bool, name: Str) -> TestResult
```

### `assert_eq(expected, actual, name)`

Asserts that `expected` equals `actual`. Uses the `Eq` trait for comparison.

```xiom
pub fn assert_eq[T: Eq](expected: T, actual: T, name: Str) -> TestResult
```

### `assert_ne(expected, actual, name)`

Asserts that `expected` does not equal `actual`. Uses the `Eq` trait for comparison.

```xiom
pub fn assert_ne[T: Eq](expected: T, actual: T, name: Str) -> TestResult
```

### `assert_lt(left, right, name)`

Asserts that `left` is strictly less than `right`. Uses the `Ord` trait for comparison.

```xiom
pub fn assert_lt[T: Ord](left: T, right: T, name: Str) -> TestResult
```

### `assert_gt(left, right, name)`

Asserts that `left` is strictly greater than `right`. Uses the `Ord` trait for comparison.

```xiom
pub fn assert_gt[T: Ord](left: T, right: T, name: Str) -> TestResult
```

### `assert_contains(haystack, needle, name)`

Asserts that the string `haystack` contains the substring `needle`.

```xiom
pub fn assert_contains(haystack: Str, needle: Str, name: Str) -> TestResult
```

### `assert_ok(result, name)`

Asserts that `result` is the `Ok` variant of a `Result[T, E]`.

```xiom
pub fn assert_ok[T, E](result: Result[T, E], name: Str) -> TestResult
```

### `assert_err(result, name)`

Asserts that `result` is the `Err` variant of a `Result[T, E]`.

```xiom
pub fn assert_err[T, E](result: Result[T, E], name: Str) -> TestResult
```

### `assert_some(option, name)`

Asserts that `option` is the `Some` variant of an `Option[T]`.

```xiom
pub fn assert_some[T](option: Option[T], name: Str) -> TestResult
```

### `assert_none(option, name)`

Asserts that `option` is the `None` variant of an `Option[T]`.

```xiom
pub fn assert_none[T](option: Option[T], name: Str) -> TestResult
```

---

## Contract Assertions

### `assert_contract(value, predicate, name)```

Asserts that `value` satisfies the given `predicate`. Used for testing contract invariants at runtime -- the predicate receives a reference to the value and must return `true` for the assertion to pass.

```xiom
pub fn assert_contract[T](value: T, predicate: fn(&T) -> Bool, name: Str) -> TestResult
```

---

## Test Runner

### `run(test)`

Runs a single test function and returns the exit code. Returns `0` if the test passed, non-zero on failure.

```xiom
pub fn run(test: fn() -> TestResult) -> Int
```

### `run_all(tests)```

Runs all provided test functions sequentially and returns the total exit code. Each test is executed and its result is collected for reporting.

```xiom
pub fn run_all(tests: Vec[fn() -> TestResult]) -> Int
```

### `run_filtered(tests, filter)```

Runs only those test functions whose name matches the given filter string. Returns the total exit code for the matched tests.

```xiom
pub fn run_filtered(tests: Vec[fn() -> TestResult], filter: Str) -> Int
```

---

## Output Formatters

### `format_results(results)```

Formats a vector of test results into a human-readable summary string, showing passed/failed status, names, messages, contract failures, and durations.

```xiom
pub fn format_results(results: Vec[TestResult]) -> Str
```

### `format_results_json(results)```

Formats a vector of test results as a JSON string for machine consumption, enabling integration with CI/CD pipelines and reporting tools.

```xiom
pub fn format_results_json(results: Vec[TestResult]) -> Str
```

---

## Benchmarking

### `bench(name, f)```

Runs the function `f` as a benchmark, measuring its execution duration. Returns a `TestResult` with the `duration_ms` field set to the elapsed time.

```xiom
pub fn bench(name: Str, f: fn()) -> TestResult
```
