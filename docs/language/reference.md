<!--
Copyright (c) 2026 Eleftherios Notas and XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# XIOM Language Reference

Complete reference for every XIOM language construct. For tutorials and concepts, see [Getting Started](getting-started.md) and [Concepts](concepts.md).

---

## Program Structure

A XIOM source file consists of top-level declarations: `fn`, `type`, `enum`, `interface`, `module`, `const`, `use`, `extern`.

```xiom
use xiom.io;

fn main() -> Int {
  io.println("Hello, world!");
  return 0;
}
```

Scripts (via `xiom run`) may omit `fn main()` -- the compiler wraps top-level code automatically. See [Scripting Mode](../M10_SCRIPTING_MODE.md).

---

## Variables and Constants

### `var` -- Mutable variable

```xiom
var x: Int = 0;        // type-annotated
var y = 42;            // type-inferred
var z: Float64 = 3.14;
```

### `let` -- Immutable binding

```xiom
let name: Str = "xiom";     // cannot be reassigned
let pi: Float64 = 3.14159;
```

### `const` -- Compile-time constant

```xiom
pub const MAX: Int = 1024;
pub const PI: Float64 = 3.1415926535;
```

---

## Types

### Primitives

| Type     | Description               | Example          |
|----------|---------------------------|------------------|
| `Int`    | Signed 64-bit integer     | `42`, `-1`       |
| `Float64`| 64-bit IEEE 754 float     | `3.14`, `-0.5`   |
| `Bool`   | Boolean                   | `true`, `false`  |
| `Str`    | Immutable string          | `"hello"`        |
| `Char`   | Single Unicode character  | `'a'`, `'\n'`    |
| `Unit`   | Void / no value           | `()`             |
| `UInt8`  | Unsigned 8-bit integer    | `255`            |
| `Int32`  | Signed 32-bit integer     | `-2147483648`    |

### Compound Types

| Type            | Syntax                           |
|-----------------|----------------------------------|
| Struct          | `type Point = { x: Float64; y: Float64; }` |
| Enum            | `enum Color { Red, Green, Blue }` |
| Enum with data  | `enum Option[T] { Some(T), None }` |
| Interface       | `interface Comparable { fn compare(self, other: &Self) -> Int; }` |
| Tuple           | `(Int, Str, Bool)`               |
| Array (fixed)   | `[3]Int`                         |
| Vec (dynamic)   | `Vec[Int]`                       |
| Slice           | `&Slice[Int]`                    |
| Map             | `Map[Str, Int]`                  |
| Set             | `Set[Int]`                       |
| Reference       | `&T`, `&mut T`                   |
| Raw pointer     | `*T`                             |

### Type Aliases

```xiom
type UserId = Int;
type Point3D = { x: Float64; y: Float64; z: Float64; };
```

---

## Functions

### Basic function

```xiom
fn add(a: Int, b: Int) -> Int {
  return a + b;
}
```

### Method on a type (receiver)

```xiom
pub fn Point.distance(self, other: &Point) -> Float64 {
  let dx = self.x - other.x;
  let dy = self.y - other.y;
  return math.sqrt(dx * dx + dy * dy);
}
```

### Generic function

```xiom
fn max[T: Comparable](a: T, b: T) -> T {
  if a > b { return a; }
  return b;
}
```

### `impl Trait` return type (M9.6)

```xiom
fn get_display() -> impl Display {
  return 42;
}
```

---

## Control Flow

### `if` / `elif` / `else`

```xiom
if x > 0 {
  io.println("positive");
} elif x < 0 {
  io.println("negative");
} else {
  io.println("zero");
}
```

### `match` -- Pattern matching

```xiom
match value {
  Some(v) => io.println(v);
  None => io.println("nothing");
}
```

Multi-line arms use braces:

```xiom
match result {
  Ok(data) => {
    process(data);
    return data;
  };
  Err(e) => {
    io.println(e.message);
    return defaultValue;
  };
}
```

### `if let` / `while let`

```xiom
if let Some(v) = maybe_val { use(v); }
while let Some(item) = iter.next() { process(item); }
```

### `while` loop

```xiom
var i = 0;
while i < 10 {
  io.println(i);
  i = i + 1;
}
```

### `for` loop (range-based)

```xiom
for i in [0, 1, 2, 3] {
  io.println(i);
}
```

### `loop` -- infinite loop

```xiom
loop {
  // ...
  if done { break; };
}
```

### `break` / `continue`

```xiom
while i < 100 {
  i = i + 1;
  if i % 2 == 0 { continue; };
  if i > 50 { break; };
  io.println(i);
}
```

---

## Expressions

### Arithmetic

```xiom
a + b    a - b    a * b    a / b    a % b
```

### Comparison

```xiom
a == b   a != b   a < b    a <= b   a > b    a >= b
```

### Logical

```xiom
a && b   a || b   !a
```

### Bitwise

```xiom
a & b    a | b    a ^ b    a << b   a >> b   ~a
```

### Assignment

```xiom
x = value;           // simple
x += 1;              // compound: +=, -=, *=, /=, %=, &=, |=, ^=
```

### Type cast

```xiom
x as Float64;         // safe numeric cast
x as Int;             // truncating float->int
```

### `is` -- Type check

```xiom
result is Ok;         // true if result matches Ok pattern
value is Some;        // true if value is Some variant
```

### `?` -- Error propagation

```xiom
let file = io.read_file(path)?;
// Equivalent to:
//   match io.read_file(path) {
//     Ok(f) => f,
//     Err(e) => return Err(e.into()),
//   }
```

### `=>` -- Implication (contracts only)

```xiom
requires: x > 0 => result > 0
```

### String interpolation via `+`

```xiom
var msg = "Hello, " + name + "!";
```

### Array/Vec indexing

```xiom
arr[0]            // 0-indexed access
vec[i]            // bounds-checked at runtime
```

### Field access

```xiom
point.x             // struct field
enum_type.Variant   // enum variant
type.method()       // method call
```

---

## Contracts

Contracts are compile-time verified safety annotations.

```xiom
fn divide(a: Float64, b: Float64) -> Float64
  requires: b != 0.0
  ensures:  result * b == a
{
  return a / b;
}
```

```xiom
type NonEmptyStack[T] = {
  items: Vec[T];
  invariant: items.len() > 0;
}
```

| Clause       | Where           | Meaning                             |
|--------------|-----------------|-------------------------------------|
| `requires:`  | fn              | Must be true when function is called |
| `ensures:`   | fn              | Must be true when function returns   |
| `invariant:` | type, enum      | Must hold for all instances of type  |

---

## Error Handling

### `Result[T, E]`

```xiom
fn parse_int(s: Str) -> Result[Int, Str] {
  // ...
  return Ok(value);
  // or
  return Err("invalid integer");
}
```

### `Option[T]`

```xiom
fn find_user(id: Int) -> Option[User] {
  // ...
  return Some(user);
  // or
  return None;
}
```

### Unwrapping

```xiom
let val = result.unwrap();           // panics on Err
let val = result.unwrap_or(default); // safe fallback
let val = option.unwrap_or(42);     // safe fallback for Option
```

---

## Modules and Visibility

```xiom
module mylib.data;           // namespace declaration

pub fn public_api() { ... }; // visible outside module
fn private_impl() { ... };   // module-private

use xiom.io;                 // import module
use xiom.collections.Map;    // import specific type
```

---

## Ownership and Borrowing

XIOM uses lexical-scope ownership. When a value leaves scope, it is freed.

```xiom
fn take_ownership(v: Vec[Int]) { ... } // v is moved -- caller loses access
fn borrow_read(v: &Vec[Int]) { ... }   // v is borrowed -- caller keeps access
fn borrow_write(v: &mut Vec[Int]) { ... } // exclusive mutable borrow
```

See [Memory Model](memory-model.md) for the complete ownership and borrowing rules.

---

## Generics

```xiom
fn identity[T](x: T) -> T { return x; }

type Pair[A, B] = { first: A; second: B; }

enum Option[T] { Some(T), None }

interface Add {
  fn add(self, other: &Self) -> Self;
}

// Bounded generic
fn sum[T: Add](a: T, b: T) -> T {
  return a.add(&b);
}
```

---

## Unsafe and FFI

```xiom
unsafe {
  let ptr = malloc(1024);
  free(ptr);
}

extern "C" {
  fn printf(format: *UInt8, ...) -> Int32;
  fn malloc(size: UInt) -> *UInt8;
}
```

---

## Scripting Mode

XIOM supports a scripting workflow via `xiom run`:

```bash
xiom run script.xi          # JIT compile and execute
xiom run --watch script.xi  # auto-recompile on changes
xiom repl                   # interactive REPL
xiom --standalone script.xi # produce standalone binary
```

Shebangs are supported:

```xiom
#!/usr/bin/env xiom
io.println("Hello from script!");
```

---

## CLI Reference

| Command | Description |
|---------|-------------|
| `xiom build file.xi` | Compile to native binary |
| `xiom run file.xi` | JIT compile and execute |
| `xiom --check file.xi` | Type-check only (no codegen) |
| `xiom doctor` | Verify toolchain (clang, opt) |
| `xiom pkg search <q>` | Search registry |
| `xiom pkg install <pkg>` | Install package |
| `xiom pkg publish` | Publish package to registry |
| `xiom doc file.xi` | Generate markdown docs |
| `xiom doc file.xi --html` | Generate HTML docs |
| `xiom fmt file.xi` | Format source code |
| `xiom repl` | Start interactive REPL |
| `xiom clean --cache` | Clean build cache |

---

## See Also

| Document | Covers |
|----------|--------|
| [Syntax](syntax.md) | Detailed grammar and expression syntax |
| [Type System](types.md) | Full type hierarchy, inference rules |
| [Contracts](contracts.md) | Deep dive on requires/ensures/invariant |
| [Memory Model](memory-model.md) | Ownership, borrowing, move semantics |
| [Generics](generics.md) | Comptime monomorphisation, bounds |
| [Standard Library](stdlib.md) | Complete API reference |
