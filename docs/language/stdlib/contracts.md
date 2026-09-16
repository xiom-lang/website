<!--
Copyright (c) 2026 Eleftherios Notas and XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Contracts Module

Runtime queryable contract API: inspect `requires`, `ensures`, and `invariant` clauses for functions and types, verify contracts at runtime, export contract specs, and measure contract coverage.

```
use xiom.contracts;
```

## Contract Metadata Types

### `ContractClause`
A single contract clause. `kind` values: `0` = requires, `1` = ensures, `2` = invariant.

```
pub type ContractClause = {
    kind: Int;
    expression: Str;
    location: Str;
    function: Str;
    type_name: Str;
} derive[Eq, Clone]
```

### `FunctionContracts`
All contracts associated with a single function.

```
pub type FunctionContracts = {
    name: Str;
    requires: Vec[ContractClause];
    ensures: Vec[ContractClause];
    return_type: Str;
    params: Vec[(Str, Str)];
} derive[Clone]
```

### `TypeContracts`
All invariants associated with a single type.

```
pub type TypeContracts = {
    name: Str;
    invariants: Vec[ContractClause];
    fields: Vec[(Str, Str)];
} derive[Clone]
```

### `ContractIndex`
A complete contract index for a package.

```
pub type ContractIndex = {
    package: Str;
    version: Str;
    functions: Vec[FunctionContracts];
    types: Vec[TypeContracts];
    total_clauses: Int;
    requires_count: Int;
    ensures_count: Int;
    invariant_count: Int;
} derive[Clone]
```

## Runtime Verification

### `ContractCheckResult`
The result of checking a contract clause at runtime.

```
pub type ContractCheckResult = {
    passed: Bool;
    clause: ContractClause;
    actual_values: Map[Str, Str];
    message: Str;
} derive[Clone]
```

### `verify_invariants(value)`
Verifies all invariants of a type against a value at runtime. Returns a list of failures (empty = all passed).

```
pub fn verify_invariants[T](value: &T) -> Vec[ContractCheckResult]
    ensures: result.len() == 0 => value satisfies all invariants
```

### `verify_function_contracts(func, args)`
Verifies all contracts of a function against its actual call. Automatically invoked by the compiler at runtime.

```
pub fn verify_function_contracts(func: Str, args: Map[Str, Str]) -> Vec[ContractCheckResult];
```

### `check_invariant(value, invariant)`
Checks a single invariant expression against a value at runtime.

```
pub fn check_invariant[T](value: &T, invariant: Str) -> ContractCheckResult;
```

## Contract Index -- Queryable Spec Database

### `build_contract_index()`
Builds a complete `ContractIndex` for the current package, containing all functions, types, and their contracts.

```
pub fn build_contract_index() -> ContractIndex;
```

### `get_function_contracts(name)`
Returns the contracts for a specific function by name.

```
pub fn get_function_contracts(name: Str) -> Option[Vec[FunctionContracts]];
```

### `get_type_contracts(name)`
Returns the contracts for a specific type by name.

```
pub fn get_type_contracts(name: Str) -> Option[Vec[TypeContracts]];
```

### `find_functions_using_type(type_name)`
Finds all functions whose contracts reference the given type name.

```
pub fn find_functions_using_type(type_name: Str) -> Vec<Str>;
```

### `find_invariants_using_field(type_name, field_name)`
Finds all invariants that reference a given field of a given type.

```
pub fn find_invariants_using_field(type_name: Str, field_name: Str) -> Vec<ContractClause>;
```

## Contract Serialization

### `export_contracts_json()`
Exports the contract index as a JSON string.

```
pub fn export_contracts_json() -> Str;
```

### `export_contracts_markdown()`
Exports the contract index as structured Markdown documentation.

```
pub fn export_contracts_markdown() -> Str;
```

### `export_contracts_openapi()`
Exports the contract index as an OpenAPI/Swagger-like specification.

```
pub fn export_contracts_openapi() -> Str;
```

## Contract Coverage

### `reset_contract_coverage()`
Resets all contract coverage tracking data.

```
pub fn reset_contract_coverage();
```

### `record_contract_hit(clause, input_values)`
Records that a contract clause was exercised during testing, along with the input values that triggered it.

```
pub fn record_contract_hit(clause: ContractClause, input_values: Map[Str, Str]);
```

### `get_contract_coverage()`
Returns a map of clause descriptions to booleans indicating whether each clause was exercised.

```
pub fn get_contract_coverage() -> Map[Str, Bool];
```

### `get_uncovered_contracts()`
Returns all contract clauses that have not been exercised by tests.

```
pub fn get_uncovered_contracts() -> Vec<ContractClause>;
```

### `coverage_percentage()`
Returns the percentage of contract clauses that have been covered by tests.

```
pub fn coverage_percentage() -> Float64;
```

## Contract Composition

### `can_compose(f_requires, g_ensures)|
Determines whether function `g`'s output can satisfy function `f`'s requires. Returns the condition that must hold, or `"impossible"` if composition is never valid.

```
pub fn can_compose(f_requires: Vec[ContractClause], g_ensures: Vec[ContractClause]) -> Str;
```

### `verify_chain(fns)|
Verifies that a chain of function calls satisfies contract propagation throughout the chain.

```
pub fn verify_chain(fns: Vec<Str>) -> Result[Unit, Vec[ContractCheckResult]];
```

## Contract Statistics

### `total_contracts()`
Returns the total number of contract clauses across all functions and types.

```
pub fn total_contracts() -> Int;
```

### `total_requires()`
Returns the total number of `requires` clauses.

```
pub fn total_requires() -> Int;
```

### `total_ensures()`
Returns the total number of `ensures` clauses.

```
pub fn total_ensures() -> Int;
```

### `total_invariants()`
Returns the total number of `invariant` clauses.

```
pub fn total_invariants() -> Int;
```

### `functions_with_contracts()`
Returns the number of functions that have at least one contract clause.

```
pub fn functions_with_contracts() -> Int;
```

### `types_with_invariants()`
Returns the number of types that have at least one invariant.

```
pub fn types_with_invariants() -> Int;
```

### `contract_density()`
Returns the average number of contract clauses per function (contracts per function).

```
pub fn contract_density() -> Float64;
```
