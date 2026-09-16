<!--
Copyright (c) 2026 Eleftherios Notas and XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# XIOM by Example

> Copy, paste, compile, run. Every example is self-contained.
> **Types are built-in** (no import). **Functions need imports** (`use xiom.io;`).
> Compile: `xiom --run file.xi` (or `cargo run -p xiom -- --run file.xi` for dev).

---

## 1. Hello World

```xiom
// hello.xi -- your first XIOM program
// Run: xiom --run hello.xi
use xiom.io;

fn main() {
  io.println("Hello, World!");  // prints to console
}
```

```
$ xiom --run hello.xi
Hello, World!
```

`use xiom.io;` imports the I/O module. `io.println()` prints to console. Every file that uses I/O needs this import.

**Three ways to import -- all valid:**

```xiom
// Style A: module prefix (recommended -- clear origin)
use xiom.io;
fn main() { io.println("Hello"); }

// Style B: glob import (shorter -- for small programs)
use xiom.io.*;
fn main() { println("Hello"); }

// Style C: single import (precise -- import only what you need)
use xiom.io.println;
fn main() { println("Hello"); }
```

---

## 2. Variables & Arithmetic

```xiom
fn main() -> Int {
  let x: Int = 10;           // immutable -- cannot be reassigned
  var y = 3.14;              // mutable -- can be reassigned, type inferred as Float64
  let z = x * 2;             // type inferred: Int
  y = y + 1.0;               // reassign mutable var
  return x + z;              // 30 -- main() can return an exit code
}
```

```
$ xiom --run vars.xi
# exit code: 30
```

`let` = immutable. `var` = mutable. Type annotation optional when the compiler can infer. Every statement ends with `;`.

---

## 3. Functions

```xiom
use xiom.io;

// Functions with return values
fn add(a: Int, b: Int) -> Int {
  return a + b;
}

// Functions returning nothing (void)
fn greet(name: Str) {
  io.println("Hello, " + name + "!");
}

fn main() {
  greet("World");            // prints: Hello, World!
  let result = add(10, 20);  // 30
}
```

Every parameter must have a type. Return type is required unless void. Functions call other functions -- `greet()` calls `io.println()`.

---

## 4. Control Flow -- Fibonacci

```xiom
use xiom.io;

// Compute the nth Fibonacci number
fn fib(n: Int) -> Int
  requires: n >= 0        // contract: caller must pass non-negative n
{
  if n <= 1 { return n; }
  return fib(n - 1) + fib(n - 2);
}

fn main() {
  io.println("fib(10) = " + fib(10).to_str());  // fib(10) = 55
}
```

`if` / `elif` / `else` -- note `elif`, not `else if`. `to_str()` converts numbers to strings for printing.

---

## 5. Structs & Methods

```xiom
// A 2D point with compiler-generated equality, clone, and display
type Point = {
  x: Float64;
  y: Float64;
} derive[Eq, Clone, Display]

// Free function taking references (borrows)
fn distance(a: &Point, b: &Point) -> Float64 {
  let dx = a.x - b.x;
  let dy = a.y - b.y;
  return dx * dx + dy * dy;
}

// Method on Point -- self is implicit (no self.x, just x)
fn Point.magnitude() -> Float64 {
  return x * x + y * y;
}

fn main() -> Int {
  let p1 = Point{ x: 0.0, y: 0.0 };
  let p2 = Point{ x: 3.0, y: 4.0 };
  let d = distance(&p1, &p2);   // 25.0
  let m = p2.magnitude();       // 25.0
  return 0;
}
```

`derive[Eq, Clone, Display]` -- compiler generates `eq()`, `clone()`, `to_str()` automatically. Methods use `fn TypeName.methodName()` -- `self` is implicit.

---

## 6. Enums & Pattern Matching

```xiom
use xiom.io;

// Algebraic data type
enum Option { Some(value: Int), None }

// Match must cover all variants -- compiler enforces this
fn describe(opt: Option) -> Str {
  match opt {
    Some(v) => "got " + v.to_str(),
    None    => "nothing",
  }
}

fn main() {
  io.println(describe(Some{ value: 42 }));  // "got 42"
  io.println(describe(None));               // "nothing"
}
```

Every `match` must be exhaustive -- missing a variant is a compile error. Use `_` as wildcard. Variants carry named fields: `VariantName(field: Type)`.

---

## 7. Error Handling -- Result & ?

```xiom
use xiom.io;

// Returns Result instead of crashing on division by zero
fn divide_safe(a: Float64, b: Float64) -> Result[Float64, Str] {
  if b == 0.0 {
    return Err("division by zero");
  }
  return Ok(a / b);
}

// ? operator propagates errors up -- clean and readable
fn compute(x: Float64, y: Float64) -> Result[Float64, Str] {
  let step1 = divide_safe(x, y)?;
  let step2 = divide_safe(step1, 2.0)?;
  return Ok(step2);
}

fn main() {
  match compute(10.0, 2.0) {
    Ok(result) => io.println("result: " + result.to_str()),  // "result: 2.5"
    Err(msg)   => io.println("error: " + msg),
  };
}
```

`?` returns the error immediately. Only usable inside functions returning `Result` or `Option`. `E` in `Result[T, E]` can be any type -- no Error interface required.

---

## 8. Contracts -- Division by Zero Prevention

```xiom
use xiom.io;

// requires: caller must ensure b != 0
// ensures:  the implementation guarantees result * b == a
fn divide(a: Float64, b: Float64) -> Float64
  requires: b != 0.0
  ensures:  result * b == a
{
  return a / b;
}

// Type with invariant -- compiler checks after every mutation
type PositiveInt = {
  value: Int;
  invariant: value > 0;
}

fn main() {
  let x = divide(10.0, 2.0);     // 5.0 -- contract passes
  io.println("10.0 / 2.0 = " + x.to_str());

  // let y = divide(10.0, 0.0);  // RUNTIME PANIC: contract violated
}
```

Contracts are compiler-enforced. `requires` = caller's responsibility. `ensures` = implementation's responsibility. `invariant` = always true after any mutation.

---

## 9. Ownership & Borrowing

```xiom
use xiom.io;

// Takes ownership -- x moved here, caller can't use it anymore
fn take_ownership(x: Int) -> Int {
  return x + 1;
}

// Borrows immutably -- caller retains ownership, can still use x
fn read_borrow(x: &Int) -> Int {
  return x + 0;
}

// Borrows mutably -- exclusive access, no other borrows active
fn write_borrow(x: &mut Int) {
  x = x + 10;
}

fn main() -> Int {
  let a = take_ownership(41);   // a = 42 -- moved into function
  let b = read_borrow(&a);      // &a = read borrow, a still valid
  var c = 5;
  write_borrow(&mut c);         // c = 15 -- exclusive write
  return a + b + c;             // 42 + 42 + 15 = 99
}
```

- `&T` -- read borrow (multiple allowed, no mutation)
- `&mut T` -- write borrow (exclusive, one at a time)
- No `&` -- move ownership (old binding invalid)
- `.clone()` -- explicit deep copy
- Borrows expire where you see the braces

---

## 10. Generics -- Typed Stack

```xiom
use xiom.io;
use xiom.collections.Vec;

// Generic stack with contract-verified invariants
type Stack[T] = {
  items: Vec[T];
  capacity: Int;
  invariant: items.len() <= capacity;  // never overflow
  invariant: capacity > 0;             // always usable
}

fn Stack.new[T](capacity: Int) -> Result[Stack[T], Str]
  requires: capacity > 0
{
  if capacity <= 0 {
    return Err("capacity must be positive");
  }
  return Ok(Stack[T]{ items: Vec[T].new(), capacity: capacity });
}

fn Stack.push[T](value: T) -> Result[Unit, Str]
  requires: items.len() < capacity
  ensures:  result is Ok => items.len() == items.len()@pre + 1
{
  if items.len() >= capacity {
    return Err("stack is full");
  }
  items.push(value);
  return Ok(());
}

fn Stack.pop[T]() -> Option[T] {
  return items.pop();
}

fn Stack.is_empty[T]() -> Bool {
  return items.len() == 0;
}

fn main() -> Result[Unit, Str] {
  var s = Stack.new[Int](3)?;     // ? propagates error from new()
  s.push(10)?;                     // ? propagates error from push()
  s.push(20)?;
  s.push(30)?;

  // This push should fail -- stack is full
  match s.push(40) {
    Ok(()) => io.println("unexpected"),
    Err(e) => io.println("rejected: " + e),  // prints: rejected: stack is full
  };

  io.println("popping:");
  while !s.is_empty() {
    match s.pop() {
      Some(v) => io.println("  " + v.to_str()),
      None    => {},
    };
  }
  return Ok(());
}
```

Generics + contracts + error handling + ownership -- all in one program. The Stack's capacity invariant is checked after every mutation. The push contract verifies the element was actually added.

---

## 11. Interfaces -- No `implements` Keyword

```xiom
// Define an interface
interface Comparable {
  fn compare(other: &Self) -> Int;  // returns -1, 0, or 1
}

// Create a type
type Score = { value: Int; }

// Implement the interface -- just write the method
fn Score.compare(other: &Score) -> Int {
  if value < other.value { return -1; }
  if value > other.value { return  1; }
  return 0;
}

// Generic function constrained by interface
fn max[T: Comparable](a: T, b: T) -> T {
  if a.compare(&b) > 0 { return a; }
  return b;
}

fn main() -> Int {
  let s1 = Score{ value: 10 };
  let s2 = Score{ value: 20 };
  let winner = max(s1, s2);
  return winner.value;   // 20
}
```

No `implements` keyword. A type satisfies an interface by having the right methods. Structural typing -- compose types across module boundaries without shared ancestry.

---

## 12. Sort with Contract Verification

```xiom
use xiom.io;
use xiom.collections.Vec;

// Contract ensures the output IS sorted -- verified at runtime
fn sort(items: &mut Vec[Int])
  ensures: items.is_sorted()
{
  // Bubble sort -- simple but correct
  let n = items.len();
  var i = 0;
  while i < n {
    var j = 0;
    while j < n - i - 1 {
      let a = items.get(j).unwrap();
      let b = items.get(j + 1).unwrap();
      if a > b {
        items.set(j, b);
        items.set(j + 1, a);
      }
      j = j + 1;
    }
    i = i + 1;
  }
  // Contract checked HERE -- if items is NOT sorted, program panics
}

fn main() {
  var nums: Vec[Int] = [4, 1, 3, 2];
  sort(&mut nums);
  io.println("sorted: " + nums.get(0).unwrap().to_str());  // 1
}
```

The `ensures: items.is_sorted()` contract is verified after `sort()` returns. If the implementation is buggy, the program panics with a clear message -- no silent corruption.

---

## Next Steps

- **21 example programs** ship in `examples/` -- compile any with `xiom --run examples/phase1_full.xi`
- **Full stdlib reference** -- [40 modules with API documentation](api.md)
- **AI coding guide** -- [AI_CONTEXT.md](../AI_CONTEXT.md) for LLM-powered XIOM code generation
