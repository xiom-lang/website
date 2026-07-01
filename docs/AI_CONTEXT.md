# AXIOM — AI Coding Reference

> **Purpose:** Feed this document into any LLM context window to enable correct AXIOM code generation.
> **Version:** v0.16.0 | **Tests:** 234 passing | **Status:** Self-hosted compiler
> 
> This document is the single source of truth for AI-generated AXIOM code.
> Every rule stated here is enforced by the compiler. No exceptions.

---

## 1. Language Identity

AXIOM is a compiled, statically typed, memory-safe systems language.

```
Pipeline: .ax → Lexer → Parser → Type Checker → Borrow Checker → LLVM IR → clang → binary
```

**Three non-negotiable properties:**

| SAFE | No GC. No null. Ownership with lexical scope borrowing. Use-after-free and double-free are compile errors. |
| VERIFIED | `requires`, `ensures`, `invariant` are compiler-enforced, not comments. Runtime guards from Phase 1, static proof from Phase 3. |
| PRECISE | One canonical form per construct. No implicit coercions, hidden allocations, or surprising control flow. |

**What AXIOM rejects:**
- No `null` / `nil` / `undefined`. Use `Option[T]`.
- No exceptions. Use `Result[T, E]`.
- No implicit type conversions. All casts are explicit.
- No operator overloading. No hidden constructors.
- No preprocessor, macros, or templates. Only `comptime`.
- No lifetime annotations. Borrow scope is lexical (visible by braces).

---

## 2. Complete Syntax Rules

### 2.1 Variables

```axiom
let x: Int = 42           // immutable — cannot be reassigned
var y: Float64 = 3.14     // mutable — can be reassigned with =
let name = "AXIOM"        // type inferred — Str
let v = [1, 2, 3]         // type inferred — Vec[Int]
```

**Rules:**
- `let` = immutable. `var` = mutable.
- Type annotation optional when compiler can infer.
- Inference does NOT cross function boundaries. Function signatures always fully annotated.
- Every statement MUST end with `;`. The last expression in a block (tail expression) does NOT.

### 2.2 Functions

```axiom
fn add(a: Int, b: Int) -> Int {
  return a + b;
}

// Void function — no return type annotation
fn log(message: Str) {
  io.print(message);
}

// With contracts (between signature and body)
fn divide(a: Float64, b: Float64) -> Float64
  requires: b != 0.0
  ensures:  result * b == a
{
  return a / b;
}
```

**Rules:**
- All parameters must have type annotations.
- Return type is required unless the function returns nothing.
- `requires` and `ensures` go between signature and body.
- `return` always needs `;`. Tail expressions do not.
- Functions are not first-class values for assignment. Use closures.

### 2.3 Methods

```axiom
pub type Vec3 = { x: Float32; y: Float32; z: Float32; }

pub fn Vec3.dot(other: &Vec3) -> Float32 {
  return x * other.x + y * other.y + z * other.z;
  // self is IMPLICIT — never write self.x, just x
}

pub fn Vec3.set_x(value: Float32) {
  x = value;   // compiler infers self: &mut Self because field is mutated
}
```

**Rules:**
- Method syntax: `fn TypeName.methodName(params) -> ReturnType`
- `self` is IMPLICIT. Access fields directly: `x`, not `self.x`.
- Compiler infers `&Self` or `&mut Self` from body. If ANY field is mutated → `&mut Self`.
- Methods are defined OUTSIDE the type declaration, in the same module.

### 2.4 Control Flow

```axiom
if x > 0 {
  return 1;
} elif x < 0 {
  return -1;
} else {
  return 0;
}

while count > 0 {
  count = count - 1;
}

for item in items {
  process(item);
}

match value {
  Some(v) => process(v),
  None    => {},
}

match state {
  AgentState.Idle              => wait(),
  AgentState.Patrolling(route) => follow(route),
}
```

**Rules:**
- `if` / `elif` / `else` — exactly this spelling. Not `else if`.
- `match` arms use `=>` not `:`.
- Every `match` must cover ALL cases. Non-exhaustive = compile error.
- Wildcard is `_`, not `default` or `otherwise`.
- Match arms that are blocks need no separator. Single-expression arms end with `,`.

### 2.5 Expressions

```axiom
// Literals
42              // Int
100_000         // Int with separators
3.14            // Float64
true | false    // Bool
"hello"         // Str — always double quotes
'A'             // Char — always single quotes

// Arithmetic
a + b   a - b   a * b   a / b   a % b   -a

// Comparison — returns Bool
a == b   a != b   a < b   a > b   a <= b   a >= b

// Logical — both operands must be Bool
!a          a && b          a || b

// Struct literal — TypeName{ field: value, ... }
let p = Point{ x: 1.0, y: 2.0 };

// Array literal
let nums = [1, 2, 3];
let empty: Vec[Int] = [];

// Field access
let dist = p.x * p.x + p.y * p.y;

// Function call
let result = add(10, 20);

// Generic call — explicit type parameter
let n = max[Int](10, 20);
let n = max(10, 20);       // inferred

// Error propagation
let f = open(path)?;

// Reference creation
let r = &x;
let rm = &mut x;

// Constructors
Some(value) | None
Ok(value) | Err(error)

// Closures
let doubler = fn(x: Int) -> Int { return x * 2; };
let tripler = |x| x * 3;

// Other
await fetch(url)           // async
comptime heavy()           // compile-time eval
x is Some                  // type test
items.len()@pre            // pre-state (contracts only)
```

### 2.6 Operator Precedence (Highest to Lowest)

| Level | Operators |
|-------|-----------|
| 10 | `.` `()` `[]` `@pre` |
| 9 | `!` `-`(unary) `&` `&mut` |
| 8 | `*` `/` `%` |
| 7 | `+` `-` |
| 6 | `==` `!=` `<` `>` `<=` `>=` |
| 5 | `is` |
| 4 | `&&` |
| 3 | `\|\|` |
| 2 | `=>` |
| 1 | `?` |

### 2.7 Keywords (Complete List)

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

`result` is only valid inside `ensures` clauses.
`self` is implicit in methods — never write it explicitly.
`is` is used for type testing: `value is Some`.

---

## 3. Type System

### 3.1 Primitive Types

| Type | Width | Example |
|------|-------|---------|
| `Bool` | 1 bit | `true`, `false` |
| `Int` | 64-bit signed | `42` |
| `Int8`–`Int64` | 8–64 bits | `let x: Int32 = 1;` |
| `UInt`–`UInt64` | 8–64 bits unsigned | `let n: UInt = 100;` |
| `Float32` | IEEE 754 single | `let f: Float32 = 1.0;` |
| `Float64` | IEEE 754 double | `3.14` (default) |
| `Char` | 32-bit Unicode | `'A'`, `'λ'` |
| `Str` | UTF-8 slice | `"hello"` |
| `Unit` | `()` | Void return, empty tuple |

### 3.2 Compound Types

```axiom
Option[T]        // Some(value) | None
Result[T, E]     // Ok(value) | Err(error)
Vec[T]           // Heap-allocated growable array
Map[K, V]        // Hash map (K: Hash + Eq)
Set[T]           // Hash set (T: Hash + Eq)
(T, U, ...)     // Tuple
[N]T             // Fixed-size array (N is comptime)
*T               // Raw pointer (unsafe only)
&T               // Read borrow
&mut T           // Write borrow
```

### 3.3 Structs

```axiom
type Point = {
  x: Float64;
  y: Float64;
} derive[Eq, Clone, Display]
```

**Rules:**
- Fields separated by `;` (not `,`).
- `derive` is optional. Supported: `Eq`, `Clone`, `Display`, `Hash`, `Ord`.
- Types with `invariant` cannot derive `Eq`, `Hash`, `Ord`.
- `invariant` clauses apply after every mutation.

### 3.4 Enums

```axiom
enum Option[T] { Some(value: T), None }
enum AgentState {
  Idle,
  Patrolling(route: Vec[Vector3]),
  Attacking(target: EntityId),
}
```

**Rules:**
- Variants separated by `,`.
- Variants can carry named fields: `VariantName(field: Type)`.
- Unit variants have no parentheses.
- Trailing commas allowed.

### 3.5 Interfaces

```axiom
interface Comparable {
  fn compare(other: &Self) -> Int;  // -1, 0, 1
}
```

**Rules:**
- A type satisfies an interface by HAVING the required methods. No `implements` keyword.
- Satisfaction checked at USE SITE.
- Interface methods in the declaration end with `;` (no body).

### 3.6 Generics

```axiom
// Type constraint inline on parameter
fn max[T: Comparable](a: T, b: T) -> T { ... }

// Multiple constraints
fn dedup[T: Eq + Hash](items: &mut Vec[T]) { ... }

// Explicit type parameter at call site (required when not inferrable)
let n = parse[Int]("42");

// Generic type
type Stack[T] = { items: Vec[T]; capacity: UInt; }
```

**Rules:**
- Type constraints go inline: `[T: Interface]`, NOT `requires: T satisfies Interface`.
- `requires` is ONLY for value-level preconditions.
- Monomorphisation: two-pass (register + specialize). Zero runtime overhead.
- Type parameter MUST be annotatable if it appears only in return type.

---

## 4. Memory Model — CRITICAL

### 4.1 Ownership Rules

| Rule | Effect |
|------|--------|
| Single owner | Assignment MOVES ownership. Old binding invalid. |
| Scope lifetime | Value freed at end of owning scope. Deterministic. |
| `&T` (read borrow) | Multiple simultaneous. No mutation during reads. |
| `&mut T` (write borrow) | EXACTLY ONE. No other borrows active. |
| `.clone()` | Explicit deep copy. Required to duplicate. |
| Move on call | Passing value to function MOVES it. Use `&` to borrow. |

### 4.2 Borrow Scope

Borrows expire at end of block or statement. Visible by braces.

```axiom
fn consume(v: Vec[Int]) { }           // takes ownership
fn read(v: &Vec[Int]) { }             // read borrow
fn write(v: &mut Vec[Int]) { }        // write borrow

let v = [1, 2, 3];
read(&v);        // borrow — v still valid
write(&mut v);   // write borrow — exclusive
consume(v);      // move — v NO LONGER VALID
// read(&v);     // COMPILE ERROR: use after move
```

### 4.3 Restrictions (These Are Compile Errors)

- ❌ Borrow stored in struct field
- ❌ Borrow returned from function
- ❌ Use after move
- ❌ Write borrow while read borrow active
- ❌ Multiple write borrows simultaneously
- ❌ Mutation through `&T`
- ✅ Clone instead of borrow for struct storage
- ✅ Return owned type, not borrow

### 4.4 Unsafe

```axiom
unsafe {
  let raw: *Int = some_c_function();
  let value = *raw;
}
```

`unsafe` is a declaration of programmer responsibility. Only needed for C FFI and raw pointer ops.

---

## 5. Contract System

### 5.1 Keywords

| Keyword | Where | Meaning |
|---------|-------|---------|
| `requires:` | Function | Pre-condition. Caller responsible. |
| `ensures:` | Function | Post-condition. Implementation responsible. |
| `invariant:` | Type body | Must hold after every mutation. |
| `result` | Inside `ensures` | References the return value. |
| `self@pre` | Inside `ensures` | Value of self at function entry. |

### 5.2 Examples

```axiom
fn divide(a: Float64, b: Float64) -> Float64
  requires: b != 0.0
  ensures:  result * b == a
{
  return a / b;
}

type Health = {
  current: Int;
  maximum: Int;
  invariant: current >= 0;
  invariant: current <= maximum;
}

fn pop[T](stack: &mut Stack[T]) -> Option[T]
  requires: !stack.is_empty()
```

### 5.3 Contract Collection Methods

| Method | Meaning |
|--------|---------|
| `.is_sorted()` | Elements non-decreasing |
| `.all(\|x\| pred)` | All satisfy predicate |
| `.none(\|x\| pred)` | None satisfy predicate |
| `.contains(value)` | Collection contains value |
| `.len()` | Element count |
| `.is_empty()` | Equivalent to `.len() == 0` |

### 5.4 Verification Modes

| Mode | Behavior |
|------|----------|
| Default | Runtime guards. `@llvm.trap()` on violation with file/line message. |
| `--no-contracts` | Strips all checks. |
| Phase 3 | Z3 static proof (planned). |

---

## 6. Error Handling

```axiom
// Result type
fn parse(s: Str) -> Result[Int, ParseError] { ... }

// ? propagates error
fn load(path: Str) -> Result[Config, AppError] {
  let file = io.read_file(path)?;
  let config = parse(file)?;
  return Ok(config);
}

// Match must be exhaustive
match result {
  Ok(value) => use(value),
  Err(e)    => handle(e),
}

// Option
let val: Option[Int] = Some(10);
let n = val.unwrap_or(0);
```

**Rules:**
- `E` in `Result[T, E]` is ANY type. No Error interface required.
- `?` only inside functions returning `Result` or `Option`.
- Every `match` on `Result`/`Option`/enum MUST handle all variants.

---

## 7. Module System

```axiom
module myproject.math     // declare module (must be first line of file)

use axiom.io;             // import module
use axiom.collections.Vec;     // import single type
use axiom.collections.Vec as V; // alias
use axiom.collections.*;        // glob import (discouraged)

pub fn public_api() { }   // visible outside module
fn private_helper() { }   // module-private (default)
```

**Rules:**
- `module` declaration must be the FIRST statement in a file.
- All declarations are private by default. `pub` makes them visible.
- No `protected` or `friend` visibility.
- `package.ax` at project root defines dependencies.

---

## 8. Standard Library Quick Reference

43 modules. Import with `use axiom.<module>`. Full reference at `docs/language/stdlib.md`.

### All Modules

| Module | Key Items |
|--------|-----------|
| `core` | `Option[T]`, `Result[T, E]`, `panic()`, `assert()`, `is_sorted()`, `all()`, `none()` |
| `io` | `print()`, `println()`, `read_file()`, `write_file()`, `file_exists()`, `args()` |
| `collections` | `Vec[T]` (push, pop, get, len), `Map[K,V]` (insert, get), `Set[T]` |
| `string` | `str_len()`, `str_concat()`, `str_split()`, `str_trim()`, `format()`, `replace()` |
| `math` | `abs()`, `sqrt()`, `sin()`, `cos()`, `pow()`, `random()`, `PI` |
| `ffi` | `extern "C"`, `unsafe`, `*T` raw pointers |
| `async` | `spawn()`, `Channel.bounded()`, `.send()`, `.recv()` |
| `net` | `tcp_connect()`, `tcp_listen()`, `http_get()`, `http_post()` |
| `os` | `exec()`, `env()`, `exit()`, `platform()` |
| `time` | `now()`, `sleep()`, `Duration`, `Timer` |
| `sync` | `Mutex[T]`, `RwLock[T]`, `Arc[T]`, `Barrier` |
| `iter` | `map()`, `filter()`, `fold()`, `zip()`, `take()`, `skip()` |
| `test` | `test()`, `assert_eq()`, `assert_ok()`, `run_tests()` |
| `serialize` | `to_json()`, `from_json()`, `to_bincode()`, `from_bincode()` |
| `bench` | `bench()`, `BenchConfig`, `BenchResult` |
| `log` | `info()`, `warn()`, `error()`, `debug()`, `LogLevel` |
| `contracts` | `requires()`, `ensures()`, `invariant()` |
| `error` | `Error`, `ErrorKind`, `into()`, `from()` |
| `fmt` | `format()`, `print()`, `println()`, `Display` |
| `hash` | `hash()`, `Hash`, `Hasher`, `sip_hash()` |
| `num` | `Num`, `parse()`, `to_string()`, `from_str()` |
| `cmp` | `Ordering`, `max()`, `min()`, `clamp()` |
| `convert` | `From`, `Into`, `from()`, `into()` |
| `cell` | `Cell[T]`, `RefCell[T]` |
| `rc` | `Rc[T]`, `Weak[T]` |
| `path` | `Path`, `join()`, `parent()`, `extension()`, `exists()` |
| `mem` | `size_of()`, `align_of()`, `addr_of()` |
| `ptr` | `null()`, `is_null()`, `offset()` |
| `char` | `is_digit()`, `is_alpha()`, `to_upper()`, `to_lower()` |
| `array` | `Array[T; N]`, `repeat()`, `from_fn()` |
| `encoding` | `base64_encode()`, `base64_decode()`, `hex_encode()`, `hex_decode()` |
| `rand` | `random()`, `seed()`, `shuffle()`, `choose()` |
| `compress` | `gzip()`, `gunzip()`, `zlib()`, `unzlib()` |
| `crypto` | `sha256()`, `aes_encrypt()`, `aes_decrypt()` |
| `regex` | `Regex`, `is_match()`, `find()`, `replace()` |
| `alloc` | `alloc()`, `dealloc()`, `realloc()` |
| `thread` | `spawn()`, `join()`, `ThreadPool` |
| `reflect` | `type_name()`, `fields()`, `is_enum()`, `is_struct()` |
| `env` | `get_var()`, `set_var()`, `home_dir()`, `temp_dir()` |

### C FFI

```axiom
extern "C" {
  fn malloc(size: UInt) -> *UInt8;
  fn free(ptr: *UInt8);
  fn printf(format: *UInt8, ...) -> Int32;
}

fn alloc(size: UInt) -> *UInt8 {
  unsafe { return malloc(size); }
}
```

---

## 9. Code Patterns & Best Practices

### 9.1 Return Early Pattern

```axiom
fn process(data: Option[Data]) -> Result[Output, AppError] {
  match data {
    None => return Err(AppError{ message: "no data" }),
    Some(d) => {
      // process d
    }
  }
  return Ok(output);
}
```

### 9.2 Ownership-Safe Patterns

```axiom
// BAD: borrow returned from function ❌
fn get_ref(v: &Vec[Int]) -> &Int {
  return &v[0];   // COMPILE ERROR: cannot return borrow
}

// GOOD: return owned value ✅
fn get_owned(v: &Vec[Int]) -> Int {
  return v[0];     // copy/clone at call site
}

// BAD: borrow stored in struct ❌
type Container = {
  ref: &Vec[Int];   // COMPILE ERROR: borrow in struct
}

// GOOD: owned type in struct ✅
type Container = {
  data: Vec[Int];
}
```

### 9.3 Contract-Driven Design

```axiom
// Write contracts BEFORE implementation
fn withdraw(account: &mut Account, amount: Float64) -> Result[Unit, Str]
  requires: amount > 0.0
  requires: account.balance >= amount
  ensures:  result is Ok => account.balance == account.balance@pre - amount
  ensures:  result is Err => account.balance == account.balance@pre
{
  if account.balance < amount {
    return Err("insufficient funds");
  }
  account.balance = account.balance - amount;
  return Ok(());
}
```

### 9.4 Error Propagation

```axiom
// Use ? for clean error propagation
fn load_config(path: Str) -> Result[Config, AppError] {
  let file   = io.read_file(path)?;
  let config = parse(file)?;
  return Ok(config);
}

// DON'T: manual match for every error
fn load_config_verbose(path: Str) -> Result[Config, AppError] {
  let file = match io.read_file(path) {
    Ok(f) => f,
    Err(e) => return Err(AppError{ message: e.message }),
  };
  // ...
}
```

### 9.5 Type-Driven Validation

```axiom
// Use types with invariants instead of runtime checks
type Email = {
  value: Str;
  invariant: value.contains("@");
  invariant: value.len() > 0;
}

type Port = {
  number: Int;
  invariant: number > 0;
  invariant: number < 65536;
}

fn connect(host: Str, port: Port) -> Result[Conn, NetError]
  requires: host.len() > 0
```

---

## 10. Common Mistakes (Compile Errors You Will Hit)

| Mistake | Error | Fix |
|---------|-------|-----|
| Missing `;` after statement | `expected ';', found ...` | Every statement needs `;` except tail expressions and block closers. |
| `else if` instead of `elif` | `expected identifier` | Use `elif`, not `else if`. |
| `self.x` in method | Not a compile error but stylistically wrong | Fields accessed directly: `x`, not `self.x`. |
| Returning a borrow | `cannot return borrow` | Return owned type or clone. |
| Storing borrow in struct | `borrow in struct not allowed` | Store owned type, not `&T`. |
| Using value after move | `value used after move` | Clone before move, or restructure to borrow. |
| Non-exhaustive match | `non-exhaustive match` | Add wildcard `_` or handle all variants. |
| `?` outside Result fn | `? cannot be used here` | Only use `?` in functions returning `Result` or `Option`. |
| Undefined variable | `undefined variable` | Check scope. Variables from outer scopes are accessible. |
| Type mismatch | `expected X, found Y` | Check function signature. No implicit conversions. |
| Missing contract fulfillment | `contract violated: requires ...` | Caller must satisfy `requires`. Implementation must satisfy `ensures`. |

---

## 11. Compiler CLI

```bash
axiomc source.ax                              # print LLVM IR
axiomc --emit-ir source.ax                    # print LLVM IR
axiomc -o prog.exe source.ax                  # compile to native
axiomc --run source.ax                        # compile + run
axiomc --target wasm -o prog.wasm source.ax   # compile to WASM
axiomc --no-contracts source.ax               # disable runtime checks

# Via cargo
cargo run -p axiomc -- --run source.ax
```

---

## 12. Complete AXIOM Program (Reference)

```axiom
module examples.bounded_stack

use axiom.io;
use axiom.collections.Vec;

pub type Stack[T] = {
  items: Vec[T];
  capacity: Int;
  invariant: items.len() <= capacity;
  invariant: capacity > 0;
}

pub fn Stack.new[T](capacity: Int) -> Result[Stack[T], Str]
  requires: capacity > 0
  ensures:  result is Ok
{
  if capacity <= 0 {
    return Err("capacity must be positive");
  }
  return Ok(Stack[T]{ items: Vec[T].new(), capacity: capacity });
}

pub fn Stack.push[T](value: T) -> Result[Unit, Str]
  requires: items.len() < capacity
  ensures:  result is Ok => items.len() == items.len()@pre + 1
{
  if items.len() >= capacity {
    return Err("stack is full");
  }
  items.push(value);
  return Ok(());
}

pub fn Stack.pop[T]() -> Option[T] {
  return items.pop();
}

fn main() -> Result[Unit, Str] {
  var s = Stack.new[Int](3)?;
  s.push(10)?;
  s.push(20)?;
  s.push(30)?;

  match s.push(40) {
    Ok(()) => io.println("unexpected"),
    Err(e) => io.println(e),
  };

  while !s.is_empty() {
    match s.pop() {
      Some(v) => io.println(v.to_string()),
      None    => {},
    };
  }

  return Ok(());
}
```

---

## 13. File Extensions & Project Structure

```
project/
├── package.ax           # package manifest
├── src/
│   ├── main.ax          # entry point (must have module declaration)
│   └── lib.ax           # library code
├── deps/                # resolved dependencies (generated)
└── tests/               # test files
```

- AXIOM source: `.ax`
- Package manifest: `package.ax`
- C FFI bindings: `.axiom-bind`
- One `module` declaration per file. Must be first statement.
- Modules correspond to directory structure.

---

## 14. Testing

```axiom
use axiom.test;

fn test_push_updates_length() {
  var s = Stack.new[Int](5).unwrap();
  s.push(42).unwrap();
  assert_eq(s.len(), 1);
}

fn test_pop_empty_returns_none() {
  var s = Stack.new[Int](5).unwrap();
  assert_none(s.pop());
}

fn test_contract_violation_caught() {
  var s = Stack.new[Int](1).unwrap();
  s.push(1).unwrap();
  let result = s.push(2);
  assert_err(result);
}

fn main() {
  run_tests();
}
```

**Rules:**
- Test functions prefixed with `test_`.
- `assert_eq`, `assert_ne`, `assert_true`, `assert_ok`, `assert_err`, `assert_some`, `assert_none`.
- `run_tests()` executes all registered tests.
- Contracts ARE tests — `requires`/`ensures` check at runtime.

---

## 15. Self-Hosting Note

The AXIOM compiler is written in AXIOM (`selfhost/` directory), compiled by the Rust bootstrap compiler. The Rust compiler is permanent — never deleted. When fixing compiler bugs, verify with differential tests: compile same program with Rust compiler AND AXIOM compiler, diff the LLVM IR. They must be identical.

---

**This document is the AI's complete reference for AXIOM code generation.**
**When in doubt, refer to the exact syntax and rules above. The compiler enforces everything stated here.**
