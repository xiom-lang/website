<!--
Copyright (c) 2026 Eleftherios Notas and XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Syntax Reference

> **Quick look:** `let x = 42;` - `fn name(args) -> Type { ... }` - `if/elif/else` - `match x { Arm => ..., }` - `;` on every statement

## Variables

```xiom
let x: Int = 42;           // immutable binding
var y: Float64 = 3.14;     // mutable binding
let name = "XIOM";        // type inferred as Str
let v = [1, 2, 3];         // type inferred as Vec[Int]
let t = (1, true);         // type inferred as (Int, Bool)
```

- `let` -- immutable binding. Cannot be reassigned.
- `var` -- mutable binding. Can be reassigned with `=`.
- Type annotations are optional when the compiler can infer the type.
- Type inference does not cross function boundaries.

## Functions

```xiom
use xiom.io;

fn add(a: Int, b: Int) -> Int {
  return a + b;
}

// Void return (no return type annotation)
fn log(message: Str) {
  io.print(message);
}

// With contracts
fn divide(a: Float64, b: Float64) -> Float64
  requires: b != 0.0
  ensures:  result * b == a
{
  return a / b;
}
```

- Function signatures are always fully annotated.
- Contracts (`requires`, `ensures`) appear between the signature and the body.
- The last expression in a block is the return value (tail expression).
- Every statement **must** end with `;`. Tail expressions do not.

## Methods

```xiom
pub type Vec3 = { x: Float32; y: Float32; z: Float32; }

// self is implicit -- fields accessed directly
pub fn Vec3.dot(other: &Vec3) -> Float32 {
  return x * other.x + y * other.y + z * other.z;
}

pub fn Vec3.set_x(value: Float32) {
  x = value;   // self is &mut Vec3 -- mutation detected
}
```

- Methods use `TypeName.methodName` syntax.
- `self` is synthesized implicitly by the compiler.
- The compiler infers `&Self` vs `&mut Self` from the method body.
- If a field is mutated anywhere, the receiver is `&mut Self`.

## Control Flow

### If / Elif / Else

```xiom
if x > 0 {
  return 1;
} elif x < 0 {
  return -1;
} else {
  return 0;
}
```

### While

```xiom
while count > 0 {
  count = count - 1;
}
```

### For

```xiom
for item in items {
  process(item);
}
```

### Match

```xiom
match value {
  Some(v) => process(v),
  None    => handle_absent(),
}

match state {
  AgentState.Idle              => wait(),
  AgentState.Patrolling(route) => follow(route),
  AgentState.Attacking(target) => engage(target),
  AgentState.Dead(cause)       => log(cause),
}
```

- Every `match` must cover all cases. Non-exhaustive matches are compile errors.
- Use `_` as a wildcard to cover remaining cases.
- Match arms can be blocks or expressions.

## Expressions

### Literals

```xiom
42              // Int
100_000         // Int with separators
3.14            // Float64
true | false    // Bool
"hello"         // Str
'A'             // Char
\n \t \\ \"     // Escape sequences
\u{1F600}       // Unicode codepoint
```

### Arithmetic

```xiom
a + b   a - b   a * b   a / b   a % b
-a      // negation
```

### Comparison

```xiom
a == b   a != b   a < b   a > b   a <= b   a >= b
```

### Logical

```xiom
!a          // not
a && b      // and
a || b      // or
```

### Struct Literals

```xiom
let p = Point{ x: 1.0, y: 2.0 };
let s = Stack[Int]{ items: [], capacity: 10 };
```

### Array Literals

```xiom
let nums = [1, 2, 3, 4, 5];
let empty: Vec[Int] = [];
```

### Field Access

```xiom
let dist = p.x * p.x + p.y * p.y;
```

### Function Calls

```xiom
let result = add(10, 20);
let x = max[Int](a, b);      // explicit type parameter
let y = max(a, b);           // inferred type parameter
```

### Closures

```xiom
// fn(params) { body } -- closure expression
let doubler = fn(x: Int) -> Int { return x * 2; };

// |params| body -- pipe closure
let tripler = |x| x * 3;
```

### Other Expressions

```xiom
// Error propagation
let f = open(path)?;

// Reference creation
let r = &x;
let rm = &mut x;

// Option constructors
Some(value)
None

// Result constructors
Ok(value)
Err(error)

// Await (async)
await fetch(url)

// Comptime evaluation
comptime expensive_computation()

// Type test
x is Some

// Pre-state reference (in contracts)
items.len()@pre
```

## Operators (Precedence)

| Precedence | Operators |
|-----------|-----------|
| 1 (lowest) | `?` (error propagation) |
| 2 | `=>` (implication) |
| 3 | `\|\|` (logical or) |
| 4 | `&&` (logical and) |
| 5 | `is` (type test) |
| 6 | `==` `!=` `<` `>` `<=` `>=` |
| 7 | `+` `-` |
| 8 | `*` `/` `%` |
| 9 | `!` `-` (unary) `&` `&mut` |
| 10 (highest) | `.` `()` `[]` `@pre` (postfix) |

## Comments

```xiom
// Single-line comment

/* Multi-line
   block comment */
```

## Keywords

```
let  var  const  fn  return
if  elif  else  match  while  for  in
spawn  async  await  comptime
module  use  pub  as
type  enum  interface  derive
requires  ensures  invariant
true  false  self  result
Some  None  Ok  Err
unsafe  extern  is
```
