<!--
Copyright (c) 2026 XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# XIOM Concepts -- For Programmers from Other Languages

> **You already know how to program.** This guide maps the concepts you know to how they work in XIOM. No fluff. Just translations.

---

## If You're Coming From...

| Language | Closest mental model to XIOM |
|----------|-------------------------------|
| **Rust** | Ownership, Result/Option, traits-as-interfaces, derive macros -> `derive[]`. You lose lifetimes and gain contracts. |
| **Go** | Structural interfaces (same!), `if err != nil` -> `Result[T,E]`, goroutines -> `spawn`. You lose GC and null. |
| **C++** | RAII, move semantics, templates -> generics, `std::optional` -> `Option[T]`. You lose inheritance, exceptions, and header files. |
| **Python** | Type hints become mandatory. `Optional` -> `Option[T]`. No `None`. No exceptions. |
| **Java/C#** | Interfaces without `implements`. No `null`. No exceptions. No `class` -- use structs + methods. |
| **JavaScript** | `undefined` doesn't exist. Promises -> async/await. No prototype chain. No `this`. |

---

## 1. No Null -- Option[T] Instead

Every language has null. XIOM doesn't.

| Language | Absence |
|----------|---------|
| Java/C# | `null` -- crashes at runtime |
| Python | `None` -- crashes at runtime |
| Rust | `Option<T>` -- compiler enforces handling |
| **XIOM** | **`Option[T]` -- compiler enforces handling** |

```xiom
// Instead of:  String name = null;
let name: Option[Str] = None;

// Instead of:  if (name != null) { use(name); }
match name {
  Some(n) => io.println("Hello, " + n),
  None    => io.println("no name"),
};
```

You cannot accidentally use `None` as a value. The compiler rejects it.

---

## 2. No Exceptions -- Result[T, E] Instead

Every language has exceptions. XIOM doesn't.

| Language | Error handling |
|----------|---------------|
| Java/C# | `try/catch` -- invisible control flow |
| Python | `try/except` -- any line can throw |
| Go | `if err != nil` -- explicit but verbose |
| Rust | `Result<T, E>` + `?` -- explicit, clean |
| **XIOM** | **`Result[T, E]` + `?` -- explicit, clean** |

```xiom
// Instead of:  throw new IOException("file not found");
fn read_config(path: Str) -> Result[Config, Str] {
  let file = io.read_file(path)?;    // ? returns the error immediately
  let config = parse(file)?;
  return Ok(config);
}

// At the call site -- must handle both cases
match read_config("config.json") {
  Ok(c)  => use(c),
  Err(e) => io.println("error: " + e),
};
```

The `?` operator is `try!` from Rust, `try` from Zig. It returns `Err(...)` immediately if the value is an error. Clean propagation without invisible control flow.

---

## 3. Ownership -- No GC, No Manual free()

| Language | Memory management |
|----------|------------------|
| Java/C#/Python/Go | Garbage collector -- pauses, unpredictable |
| C | `malloc`/`free` -- manual, error-prone |
| C++ | RAII + smart pointers -- complex rules |
| Rust | Ownership + borrow checker + lifetimes -- powerful but complex |
| **XIOM** | **Ownership + lexical scope borrowing -- same safety, no lifetimes** |

```xiom
// A value has ONE owner. Assignment moves ownership.
let a = Vec.new();
let b = a;       // a MOVED to b -- a is now invalid
// a.push(1);    // COMPILE ERROR: a was moved

// Borrow temporarily with & (read) or &mut (write)
read_only(&b);   // b is borrowed -- still valid after
mutate(&mut b);  // exclusive write borrow

// Clone to duplicate
let c = b.clone();  // explicit copy -- both valid
```

**The key difference from Rust:** No lifetime annotations. Ever. Borrows expire at the end of the block where they're created. You can see when a borrow ends by looking at the braces.

---

## 4. Structs + Methods -- No Classes, No Inheritance

XIOM has no `class`, no `extends`, no `implements`, no `virtual`, no `override`, no `protected`. Here's what you use instead:

| OOP Concept | XIOM Equivalent |
|-------------|-----------------|
| `class` | `type` (struct) |
| `extends` / inheritance | **Not supported.** Use composition or interfaces. |
| `implements` | **Not needed.** Any type with matching methods satisfies the interface automatically. |
| `public` / `private` | `pub` keyword. Private is the default. |
| `protected` | **Not supported.** Use separate modules. |
| `virtual` / `override` | **Not supported.** Use structural interfaces for polymorphism. |
| `abstract class` | **Not supported.** Use interfaces. |
| Constructor | `fn TypeName.new() -> Type` method |
| `this` / `self` | `self` is **implicit** -- access fields directly |
| `static` method | Free function `fn function_name()` |
| Property getter/setter | Direct field access. Use methods for logic. |

```xiom
// Instead of:  class Point { private float x; public float getX()... }
type Point = {
  x: Float64;               // private by default
  y: Float64;
} derive[Eq, Clone, Display]  // auto-generate equality, clone, to-string

pub fn Point.distance(other: &Point) -> Float64 {
  // self is implicit -- x means self.x
  let dx = x - other.x;
  let dy = y - other.y;
  return dx * dx + dy * dy;
}
```

---

## 5. Polymorphism -- Structural Interfaces

XIOM has no inheritance. Polymorphism works through **structural interfaces** -- if a type has the required methods, it satisfies the interface. No declaration needed.

```xiom
// Define what "comparable" means
interface Comparable {
  fn compare(other: &Self) -> Int;  // -1, 0, 1
}

// Create two completely unrelated types
type Score = { value: Int; }
type Temperature = { kelvin: Float64; }

// Implement compare for each -- NO "implements" keyword needed
fn Score.compare(other: &Score) -> Int { return value - other.value; }
fn Temperature.compare(other: &Temperature) -> Int { ... }

// A generic function that works with ANY comparable type
fn max[T: Comparable](a: T, b: T) -> T {
  if a.compare(&b) > 0 { return a; }
  return b;
}

let winner = max(Score{ value: 10 }, Score{ value: 20 });
// Both Score and Temperature satisfy Comparable automatically
```

This is Go's interface model. It's also how Python's duck typing works, except compile-time verified.

---

## 6. Contracts -- Unique to XIOM

No mainstream language has contracts as compiler-enforced specifications. This is XIOM's defining feature.

```xiom
fn divide(a: Float64, b: Float64) -> Float64
  requires: b != 0.0           // PRE-CONDITION: caller must guarantee this
  ensures:  result * b == a    // POST-CONDITION: implementation must guarantee this
{
  return a / b;
}

type Health = {
  current: Int;
  maximum: Int;
  invariant: current >= 0;      // TYPE INVARIANT: always true
  invariant: current <= maximum;
}
```

| Contract | Like... | But... |
|----------|---------|--------|
| `requires:` | `assert()` at function entry | Compiler can check at call sites, not just runtime |
| `ensures:` | `assert()` at function exit + unit test | Compiler-verified, not just hoped-for |
| `invariant:` | A database CHECK constraint | On every mutation, checked at compile time or runtime |

When a contract is violated at runtime, the program panics with the **exact** contract that failed, the file, and the line number. In debug mode, this replaces most unit tests.

---

## 7. Public / Private -- Module-Based Visibility

| Language | Privacy model |
|----------|--------------|
| Java/C# | `public`/`private`/`protected` on classes and members |
| C++ | `public:`/`private:` sections in class body |
| Python | `_convention` -- not enforced |
| Rust | `pub` -- everything private by default |
| **XIOM** | **`pub` -- everything private by default** |

```xiom
module myproject.data;

pub type User = {              // visible outside this module
  name: Str;
  email: Str;
} derive[Clone]

pub fn User.validate() -> Bool {  // visible outside
  return email.contains("@");
}

fn hash_email(user: &User) -> Int {  // PRIVATE -- only visible in this module
  // ...
}
```

No `protected`. No `friend`. No `package-private`. Just `pub` or private.

---

## 8. Generics -- Like Templates, But Type-Checked Before Instantiation

| Language | Generics |
|----------|----------|
| C++ | Templates -- duck-typed, errors at instantiation |
| Java | Type erasure -- limited, no primitives |
| C# | Reified generics -- better, still class-based |
| Rust/Go | Monomorphised -- zero-cost, checked at definition |
| **XIOM** | **Monomorphised -- zero-cost, checked at definition** |

```xiom
// Instead of:  template<typename T> T max(T a, T b) { return a > b ? a : b; }
fn max[T: Comparable](a: T, b: T) -> T {
  if a > b { return a; }
  return b;
}

// Works with any type that satisfies Comparable
let m1 = max(10, 20);             // T = Int
let m2 = max(1.5, 2.7);           // T = Float64
let m3 = max(Score{value:10}, Score{value:20});  // T = Score
```

The `[T: Comparable]` constraint means: "T must have a `compare` method." The compiler checks this before generating code. No template-instantiation-error soup.

---

## 9. Pattern Matching -- Like switch, But Exhaustive

```xiom
// Instead of:  switch (value) { case 1: ... break; default: ... }
match value {
  Some(v) => io.println("got " + v.to_str()),
  None    => io.println("nothing"),
};

// Instead of:  if (state == IDLE) ... else if (state == ATTACKING) ...
match state {
  AgentState.Idle              => wait(),
  AgentState.Patrolling(route) => follow(route),
  AgentState.Attacking(target) => engage(target),
  AgentState.Dead(cause)       => log(cause),
};
```

The compiler forces you to handle **every** variant. Missing a case is a compile error. This eliminates an entire class of runtime bugs.

---

## 10. Async -- Like async/await, With Channels

```xiom
use xiom.async;

// Instead of:  async function fetch() { const r = await http.get(url); }
async fn fetch(url: Str) -> Result[Str, NetError] {
  let response = await net.http_get(url)?;
  return Ok(response.body);
}

// Instead of:  new Thread(() -> { channel.send(compute()); }).start();
let (tx, rx) = Channel.bounded[Int](32);
spawn {
  tx.send(expensive_computation());
};

match rx.recv() {
  Ok(value) => use(value),
  Err(_)    => io.println("channel closed"),
};
```

| Other Language | XIOM |
|---------------|-------|
| `async function` / `async fn` | `async fn` |
| `await` | `await` |
| `Promise` / `Future` | Future (implicit) |
| `Go` goroutine | `spawn` |
| `Go` channel | `Channel[T]` |

---

## 11. Compile-Time Code -- comptime

No preprocessor. No macros. No templates. One keyword: `comptime`.

```xiom
// Evaluated at compile time -- zero runtime cost
let size = comptime expensive_computation();

// Generics are just comptime type parameters
fn max[T: Comparable](a: T, b: T) -> T { ... }
```

`comptime` is Zig's model -- any expression can be marked compile-time. This is how generics, reflection, and specialization all work. One mechanism.

---

## 12. C FFI -- Call Any C Library

```xiom
extern "C" {
  fn malloc(size: UInt) -> *UInt8;
  fn free(ptr: *UInt8);
  fn printf(format: *UInt8, ...) -> Int32;
}

fn alloc(size: UInt) -> *UInt8
  requires: size > 0
{
  unsafe { return malloc(size); }
}
```

XIOM does not rewrite C libraries. It wraps them with safe interfaces and contracts. SQLite, OpenSSL, Vulkan, BLAS -- all accessed through FFI with contract-verified preconditions.

---

## Quick Comparison Table

| Concept | Java/C# | C++ | Python | Rust | Go | **XIOM** |
|---------|---------|-----|--------|------|----|-----------|
| Absence | `null` | `nullptr` | `None` | `Option<T>` | `nil` | **`Option[T]`** |
| Errors | exceptions | exceptions | exceptions | `Result<T,E>` | `if err != nil` | **`Result[T,E]` + `?`** |
| Memory | GC | RAII/manual | GC | ownership+lifetimes | GC | **ownership+scope** |
| Classes | `class` | `class` | `class` | no classes | no classes | **`type` struct** |
| Inheritance | `extends` | `: public` | `(Base)` | no inheritance | no inheritance | **composition only** |
| Interfaces | `implements` | pure virtual | ABC | `impl Trait` | structural | **structural** |
| Generics | `<T>` | `template<T>` | duck | `<T>` | `[T]` | **`[T: Bound]`** |
| Contracts | no | no | no | no | no | **`requires/ensures/invariant`** |
| Privacy | `public/private` | `public:/private:` | `_` convention | `pub` | capitalization | **`pub`** |
| Compile-time | annotations | templates | decorators | macros | code gen | **`comptime`** |
| Pattern match | `switch` (limited) | `switch` (limited) | `match` (3.10+) | `match` | `switch` | **`match` (exhaustive)** |
| Async | `async/await` | `std::future` | `async/await` | `async/await` | goroutines | **`async/await` + `spawn`** |

---

## What XIOM Does NOT Have (On Purpose)

| Feature | Why It's Missing |
|---------|-----------------|
| **Inheritance** | Composition + structural interfaces cover all use cases without the fragile base class problem. |
| **Exceptions** | Invisible control flow. `Result[T, E]` makes error paths explicit. |
| **Null** | Billion-dollar mistake. `Option[T]` with exhaustive match. |
| **Lifetime annotations** | Lexical scope is simpler and covers 95% of cases. |
| **Function overloading** | One canonical form for each function name. |
| **Operator overloading** | Surprising behavior at a distance. |
| **Implicit conversions** | What you read is what runs. |
| **Default parameters** | Explicitness over convenience. Use method chaining or builder pattern. |
| **Macros / preprocessor** | `comptime` covers all compile-time needs. |
| **Header files** | Module system replaces them. |
