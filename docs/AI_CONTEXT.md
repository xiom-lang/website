# XIOM — AI Coding Reference

> **Purpose:** Feed this document into any LLM context window to enable correct XIOM code generation.
> **Version:** v0.23.1 | **Tests:** 450+ (stdlib) + 186 (compiler) | **Status:** Rust bootstrap, stdlib hardened, C runtime complete

> **Current stdlib state:** All 39 modules have function body implementations (~8,500+ lines, 826+ functions) with 450+ tests across 8 test files. C runtime extended with 25 cross-platform functions (file I/O, stat, memory, CPU, disk, symlinks, pipes, args). This is a **hardened first-pass** — code is written and tested at the API level but has NOT been compiled/verified by the XIOM compiler. Concurrency is simplified single-threaded. Networking returns stub errors. See `docs/checklists/stdlib-implementation.md` for full status and remaining work items.
> 
> This document is the single source of truth for AI-generated XIOM code.
> Every rule stated here is enforced by the compiler. No exceptions.

---

## 1. Language Identity

XIOM is a compiled, statically typed, memory-safe systems language.

```
Pipeline: .xi → Lexer → Parser → Type Checker → Borrow Checker → LLVM IR → clang → binary
```

**Three non-negotiable properties:**

| SAFE | No GC. No null. Ownership with lexical scope borrowing. Use-after-free and double-free are compile errors. |
| VERIFIED | `requires`, `ensures`, `invariant` are compiler-enforced, not comments. Runtime guards from Phase 1, static proof from Phase 3. |
| PRECISE | One canonical form per construct. No implicit coercions, hidden allocations, or surprising control flow. |

**What XIOM rejects:**
- No `null` / `nil` / `undefined`. Use `Option[T]`.
- No exceptions. Use `Result[T, E]`.
- No implicit type conversions. All casts are explicit.
- No operator overloading. No hidden constructors.
- No preprocessor, macros, or templates. Only `comptime`.
- No lifetime annotations. Borrow scope is lexical (visible by braces).

---

## 2. Complete Syntax Rules

### 2.1 Variables

```xiom
let x: Int = 42           // immutable — cannot be reassigned
var y: Float64 = 3.14     // mutable — can be reassigned with =
let name = "XIOM"        // type inferred — Str
let v = [1, 2, 3]         // type inferred — Vec[Int]
```

**Rules:**
- `let` = immutable. `var` = mutable.
- Type annotation optional when compiler can infer.
- Inference does NOT cross function boundaries. Function signatures always fully annotated.
- Every statement MUST end with `;`. The last expression in a block (tail expression) does NOT.

### 2.2 Functions

```xiom
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

```xiom
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

```xiom
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

```xiom
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

```xiom
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

```xiom
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

```xiom
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

```xiom
interface Comparable {
  fn compare(other: &Self) -> Int;  // -1, 0, 1
}
```

**Rules:**
- A type satisfies an interface by HAVING the required methods. No `implements` keyword.
- Satisfaction checked at USE SITE.
- Interface methods in the declaration end with `;` (no body).

### 3.6 Generics

```xiom
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

```xiom
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

```xiom
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

```xiom
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

```xiom
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

```xiom
module myproject.math     // declare module (must be first line of file)

use xiom.io;             // import module
use xiom.collections.Vec;     // import single type
use xiom.collections.Vec as V; // alias
use xiom.collections.*;        // glob import (discouraged)

pub fn public_api() { }   // visible outside module
fn private_helper() { }   // module-private (default)
```

**Rules:**
- `module` declaration must be the FIRST statement in a file.
- All declarations are private by default. `pub` makes them visible.
- No `protected` or `friend` visibility.
- `package.xi` at project root defines dependencies.

---

## 8. Standard Library Quick Reference

**Current state:** All 39 modules have function body implementations (~8,500+ lines, 826+ functions). See `docs/checklists/stdlib-implementation.md` for full status per module.

**PROVEN working (compiler built-ins + C runtime):**
- `Option[T]`, `Result[T, E]` — built into the type checker
- `Vec[T]` — push, pop, get, len are codegen primitives
- Arithmetic, comparison, control flow — built into the compiler
- `extern "C"` FFI — via C runtime (`xiom_runtime.c`), standard libc functions
- `@malloc`, `@free`, `@realloc` — LLVM declarations emit automatically
- `@llvm.trap()` — contract guard emission
- `@xiom_str_len` — Str length via C runtime
- File I/O: `xiom_read_file`, `xiom_file_size`, `xiom_free` (C runtime)

**Implemented but NOT YET COMPILED OR TESTED:** All other stdlib functions. See tier breakdown below. 24 custom `xiom_*` C runtime functions declared by stdlib modules are missing from `xiom_runtime.c` and will cause linker errors. Concurrency is simplified single-threaded. Network returns stub errors.

39 modules listed below. Import with `use xiom.<module>`. Types and function bodies are present. File sizes reflect implementations.

### Tier 1 — Foundation (fully implemented)

| Module | Lines | Key Types & Functions |
|--------|-------|----------------------|
| `core` | 560 | Option[T], Result[T,E], Box[T], BinaryHeap[T], 13 interfaces (Eq, Ord, Hash, Clone, Display, Default, Add, Sub, Mul, Div, Iterator, IntoIterator, Drop) — is_sorted, all, none, contains, panic, assert, constants |
| `cmp` | ~120 | Ordering, max, min, clamp (generic + Int/Float64 overloads) |
| `num` | 352 | Numeric traits (Neg, Rem, Abs, Pow, Sqrt, Bounded), parse, saturating/checked/wrapping ops, gcd, lcm, float classification |
| `convert` | ~60 | identity, int↔float↔string↔bool↔char conversions |
| `fmt` | ~110 | Formatter (write_str/int/float/bool), Display impls, format1/2/3, print/println |
| `hash` | 105 | DefaultHasher (DJB2), Hash impls for Int/Str/Bool, sip_hash fallback |
| `error` | ~80 | Error interface, chain walking, context wrapping, Backtrace |
| `char` | ~90 | 16 classification funcs (is_digit/alpha/whitespace/punctuation/control), to_upper/lower, to_digit/from_digit, UTF-8 encode |
| `iter` | 324 | Range, Map, Filter, Enumerate, Take, Skip, Chain, Zip — fold, collect, count, sum, product, max, min, find, all, any, nth, last |
| `mem` | ~75 | swap, replace, take, drop, size_of/align_of, ManuallyDrop |
| `ptr` | ~100 | 19 pointer ops (null, read, write, swap, replace, copy, offset, add, sub, eq) — all unsafe-wrapped |
| `alloc` | ~80 | Layout, GlobalAlloc, extern {malloc, free, realloc, memset} |
| `array` | ~120 | 22 functions: map, fold, zip, fill, swap, reverse, rotate, sort, binary_search, contains |

### Tier 2 — Data & I/O (fully implemented)

| Module | Lines | Key Types & Functions |
|--------|-------|----------------------|
| `collections` | 699 | Vec, Map, Set, LinkedList, Queue, Stack, VecDeque, BTreeMap, BTreeSet, Slice — 78 methods total |
| `string` | 294 | 22 functions: concat, slice, split, trim, parse, upper/lower, replace, lines, words, format1/2, char_at, index_of |
| `io` | ~360 | Console I/O, file system (read/write/append/exists/list/remove/copy/rename), process (exit/args/env), buffered I/O, Cursor, path ops, Read/Write/Seek interfaces |
| `math` | 405 | 36 functions: sqrt (Newton), pow, abs, min/max, floor/ceil/round, sin/cos/tan (Taylor), exp/ln/log10/log2, bitwise ops, random (LCG), clamp/lerp, is_nan/is_inf |
| `path` | ~180 | Path, PathBuf — join, parent, file_name, extension, file_stem, is_absolute, exists, components |
| `time` | 338 | Duration, Instant, SystemTime, DateTime — arithmetic, calendar decomposition, sleep |
| `env` | 190 | OS/ARCH/FAMILY constants, get_var/set_var/remove_var, home_dir/temp_dir/current_dir, args |

### Tier 3 — Concurrency & Platform (implemented, simplified)

| Module | Lines | Key Types & Functions | Notes |
|--------|-------|----------------------|-------|
| `sync` | 189 | Mutex, RwLock, Condvar, Once, Arc[T], AtomicBool, AtomicInt, Barrier | Single-threaded; Arc uses heap alloc |
| `thread` | 83 | Thread, JoinHandle, Scope, spawn, yield, sleep | Executes immediately (single-threaded) |
| `async` | ~60 | Channel (bounded/unbounded), spawn, send, recv | Queue-backed, single-threaded |
| `os` | 486 | Process, Command, platform, arch, env ops, file ops, walk_dir, pipe, disk | Delegates to io/env where possible |
| `net` | 360 | TcpStream, TcpListener, UdpSocket, http_get/post, resolve_host, parse_url | **Returns stub errors** — needs OS socket FFI |
| `ffi` | ~30 | extern_c, alloc, free, memcpy, size_of wrapping | Thin wrappers over extern C |
| `cell` | 124 | Cell (unsafe interior mutation), RefCell (runtime borrow tracking) | Uses unsafe ptr casts |
| `rc` | 125 | Rc, Weak — heap-allocated RcInner, ref counting, Drop destruction | Uses alloc + unsafe |

### Tier 4 — Ecosystem (fully implemented)

| Module | Lines | Key Types & Functions | Notes |
|--------|-------|----------------------|-------|
| `serialize` | 509 | JsonValue, full recursive-descent JSON parser, to_json/from_json, string/number/array/object serialization | |
| `crypto` | 1291 | SHA-256 (full), SHA-512, MD5, HMAC-SHA256, AES-128/192/256 (full S-box + GF(2^8)), PBKDF2, RSA (toy), constant_time_compare | Algorithmically complete |
| `compress` | 657 | RLE engine, CRC32, Adler32, gzip/zlib/brotli/lz4/snappy format detection and decompression | |
| `encoding` | ~200 | base64 (std+url), hex (upper+lower), url/percent encoding, UTF-8 validate/encode/decode | |
| `regex` | 450 | Backtracking engine: . * + ? ^ $ [a-z] [^abc] \d \w \s, captures, replace, split, find_all | Simplified — no lookahead/backrefs |
| `rand` | 387 | LCG PRNG, Box-Muller normal, exponential/bernoulli/poisson/gamma/beta, Fisher-Yates shuffle, UUID v4/v7 | |
| `log` | 193 | LogLevel (Trace–Fatal), Logger, file/console output, JSON formatting, structured logging | |
| `bench` | ~115 | run_bench (Welford's mean/min/max/stddev), black_box | |
| `test` | 241 | 11 assertions, test registry, run_all/filtered, JSON results formatting | |
| `contracts` | 400 | ContractIndex, verification, coverage tracking, JSON/Markdown/OpenAPI export, statistics | Placeholder data — needs compiler metadata |
| `reflect` | 74 | TypeId, TypeInfo, FieldInfo, Any, type_name/type_size/type_align | Placeholder — needs compiler RTTI |

### C FFI (Works Now)

```xiom
extern "C" {
  fn malloc(size: UInt) -> *UInt8;
  fn free(ptr: *UInt8);
  fn printf(format: *UInt8, ...) -> Int32;
}

fn alloc(size: UInt) -> *UInt8 {
  unsafe { return malloc(size); }
}
```

### When generating code, follow these rules:

1. **Use the types** — they're real. `Option[T]`, `Result[T,E]`, `Vec[T]`, `Map[K,V]` are well-defined with full implementations.
2. **Use the stdlib** — all 39 modules have function bodies. Import with `use xiom.<module>`. DO NOT reimplement stdlib functions.
3. **Built-ins don't need stdlib** — `Option`, `Result`, `Vec` operations are compiler primitives. You don't need to import `xiom.core` to use them.
4. **For FFI** — use `extern "C"` directly. Standard C lib functions link from the system. Custom `xiom_*` functions may need runtime additions — check `stdlib/runtime/xiom_runtime.c` before declaring new ones.
4. **For FFI** — use `extern "C"` directly. The C runtime handles linking.

---

## 9. Code Patterns & Best Practices

### 9.1 Return Early Pattern

```xiom
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

```xiom
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

```xiom
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

```xiom
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

```xiom
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
xiomc source.xi                              # print LLVM IR
xiomc --emit-ir source.xi                    # print LLVM IR
xiomc -o prog.exe source.xi                  # compile to native
xiomc --run source.xi                        # compile + run
xiomc --target wasm -o prog.wasm source.xi   # compile to WASM
xiomc --no-contracts source.xi               # disable runtime checks

# Via cargo
cargo run -p xiomc -- --run source.xi
```

---

## 12. Complete XIOM Program (Reference)

```xiom
module examples.bounded_stack

use xiom.io;
use xiom.collections.Vec;

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
├── package.xi           # package manifest
├── src/
│   ├── main.xi          # entry point (must have module declaration)
│   └── lib.xi           # library code
├── deps/                # resolved dependencies (generated)
└── tests/               # test files
```

- XIOM source: `.xi`
- Package manifest: `package.xi`
- C FFI bindings: `.xiom-bind`
- One `module` declaration per file. Must be first statement.
- Modules correspond to directory structure.

---

## 14. Testing

```xiom
use xiom.test;

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

The XIOM compiler is written in XIOM (`selfhost/` directory), compiled by the Rust bootstrap compiler. The Rust compiler is permanent — never deleted. When fixing compiler bugs, verify with differential tests: compile same program with Rust compiler AND XIOM compiler, diff the LLVM IR. They must be identical.

---

## 16. AI Coding Best Practices for XIOM

> Use this section as system prompt when generating XIOM code with an LLM.

### Core Mindset

1. **Always prioritize contracts** (`requires`, `ensures`, `invariant`) — this is XIOM's biggest strength over every other language. Write contracts BEFORE the function body.
2. **Make code explicit and readable** — no hidden behavior, no magic numbers, no implicit conversions.
3. **Ownership first** — prefer `&T` borrows when possible. Move when ownership transfer is needed. Clone sparingly.
4. **Think in terms of verification, not just "it works"** — contracts are the specification. The compiler is the verifier.

### Code Structure Rules

- Start with contracts before implementation
- Use `derive[Eq, Clone, Display]` liberally on types
- Prefer `let` over `var` unless mutation is required
- Keep functions small (≤50 lines) and focused on one task
- Use structural interfaces — no `implements` keyword
- Methods are defined OUTSIDE the type, using `fn Type.method()` syntax

### Good Patterns (DO)

```xiom
// 1. Contracts before body
fn process_order(order: Order) -> Result[Receipt, OrderError]
  requires: order.items.len() > 0
  requires: order.total > 0.0
  ensures:  result is Ok => result.total == order.total
{
  ...
}

// 2. Borrow for read-only access
fn analyze(data: &Vec[Int]) -> Int {
  var sum = 0;
  var i = 0;
  while i < data.len() {
    sum = sum + data[i];  // read through borrow
    i = i + 1;
  }
  return sum;
}

// 3. Return owned values (not borrows)
fn create_report(data: &Data) -> Report {
  return Report{ summary: summarize(data), total: data.total };
}

// 4. Error handling with ?
fn load_config(path: Str) -> Result[Config, AppError] {
  let file = io.read_file(path)?;
  let config = parse(file)?;
  return Ok(config);
}

// 5. Type invariants for validation
type Email = {
  value: Str;
  invariant: value.contains("@");
  invariant: value.len() > 0;
}
```

### Bad Patterns (AVOID)

```xiom
// ❌ Writing self.x in methods
fn Point.get_x() -> Int { return self.x; }  // WRONG
fn Point.get_x() -> Int { return x; }        // CORRECT — self is implicit

// ❌ else if instead of elif
if x > 0 { ... } else if x < 0 { ... }       // WRONG
if x > 0 { ... } elif x < 0 { ... }           // CORRECT

// ❌ Forgetting ; after statements
let x = 5                                     // WRONG — needs ;
let x = 5;                                    // CORRECT

// ❌ Storing borrows in structs
type Container = { ref: &Vec[Int]; }          // COMPILE ERROR

// ❌ Returning borrows from functions
fn get_ref(v: &Vec[Int]) -> &Int { return &v[0]; }  // COMPILE ERROR

// ❌ Using to_string() for Display
value.to_string()                              // WRONG
value.to_str()                                 // CORRECT (derive Display)

// ❌ Ignoring contract clauses
fn divide(a: Float64, b: Float64) -> Float64
  requires: b != 0.0                           // Must satisfy or trap
{ return a / b; }                              // No check in body — contract handles it
```

### Method Design Rules

```
✓ fn Vec3.dot(other: &Vec3) -> Float32           // method on type
✓ fn Vec3.normalize() -> Vec3                    // returns new value
✓ fn Vec3.set_x(value: Float32)                  // mutates self (inferred &mut Self)
✗ fn Vec3.dot(self: &Vec3, ...)                  // never write self explicitly
✗ fn dot(v: &Vec3, other: &Vec3) -> Float32     // use method syntax, not free function
```

### Contract Design Hierarchy

| When | Use |
|------|-----|
| Parameter must satisfy condition | `requires:` |
| Return value must satisfy condition | `ensures:` |
| Type state must always be valid | `invariant:` on type |
| Function cannot fail | `ensures: result is Ok` |
| Multiple conditions | Multiple `requires:` / `ensures:` clauses |

### AI Coding Workflow (Step by Step)

1. **Understand requirements** — what should this function do?
2. **Design types first** — structs, enums with invariants
3. **Write function signatures + contracts** — BEFORE the body
4. **Implement body** — contracts guide the implementation
5. **Add tests** — contracts ARE tests at runtime; add explicit test cases for edge conditions
6. **Verify** — `xiom test` runs runtime checks; Phase 3 Z3 proves statically

### Performance-Aware Patterns

```xiom
// Clone before move when you need the value later
var original = make_expensive_data();
var copy = original.clone();   // deep copy
process(original);             // move original
use_copy(copy);                // copy still valid

// Borrow instead of clone when you don't need ownership
fn inspect(data: &Data) { ... }   // zero-cost read

// Move into collections instead of cloning
var items = Vec[Data].new();
items.push(create_data());        // move — no clone
items.push(create_data());        // move — no clone
```

---

## 17. Multi-File Projects & Module System — AI Guide

> When generating large XIOM projects across multiple files, follow these rules to ensure the compiler resolves everything correctly.

### File Structure Convention

```
myproject/
├── package.xi           ← manifest (name, version, deps)
├── src/
│   ├── main.xi          ← entry point: module myproject
│   ├── types.xi         ← module myproject.types
│   ├── utils.xi         ← module myproject.utils
│   └── lib.xi           ← module myproject.lib
└── tests/
    └── test_main.xi     ← tests
```

**Rule:** Every `.xi` file MUST start with `module <name>;` as the FIRST statement (after comments).

### Module Resolution (How the Compiler Finds Files)

The compiler uses **dotted path matching** between `use` declarations and `module` declarations:

```xiom
// In src/main.xi:
module myproject
use myproject.types;       // looks for a file declaring `module myproject.types`
use myproject.utils;       // looks for a file declaring `module myproject.utils`

// In src/types.xi:
module myproject.types     // matches `use myproject.types` in main.xi
pub type User = { name: Str; age: Int; }

// In src/utils.xi:
module myproject.utils     // matches `use myproject.utils` in main.xi
pub fn helper() -> Int { return 42; }
```

**The file NAME doesn't matter — the `module` DECLARATION matters.** A file called `foo.xi` that declares `module myproject.utils` will be found when `use myproject.utils` is encountered.

### How to Compile Multi-File Projects

**Option A — Compile all files at once (recommended for AI-generated code):**
```bash
xiomc --run src/main.xi src/types.xi src/utils.xi src/lib.xi
```
The compiler merges all files into one program. Use this for projects with 2-30 files.

**Option B — Single file with lazy loading (catalog):**
```bash
xiomc --run src/main.xi
```
The compiler lazy-loads other files via the ModuleCatalog. Works for files in the same directory or `examples/` root.

### Dependency & Import Rules for AI

1. **`module` MUST be first.** The very first non-comment line in every file:
   ```xiom
   // Comments OK here
   module myproject.models    // ← MUST be line 1 (after comments)
   ```

2. **`use` for cross-file imports.** After the module declaration:
   ```xiom
   module myproject
   use myproject.types;       // import another module
   use myproject.types.User;  // import single type
   use xiom.io;               // import stdlib module
   ```

3. **`pub` for visibility.** Functions/types are PRIVATE by default. Add `pub` to export:
   ```xiom
   pub fn public_api() { }    // visible to other modules
   fn private_helper() { }    // only visible in this file
   ```

4. **Shared types go in a types module.** If multiple files need the same struct:
   ```xiom
   // src/types.xi
   module myproject.types
   pub type BenchResult = {
     name: Str;
     score: Int;
     max_score: Int;
     passed: Bool;
     elapsed_ms: Int;
   } derive[Clone]

   // src/main.xi
   use myproject.types.BenchResult;
   ```

5. **No circular imports.** Module A cannot `use` module B if B also `use`s A. Keep dependencies a DAG.

6. **One module per file.** Don't declare multiple `module` blocks in one file. One file = one module.

### Common Multi-File Patterns

**Pattern 1: Library + Binary**
```
src/types.xi     → module myproject.types
src/lib.xi       → module myproject (use types, export pub fn)
src/main.xi      → module myproject.main (use myproject, call pub fns)
```

**Pattern 2: Feature Modules**
```
src/main.xi      → module myproject (use math, use net, use db)
src/math.xi      → module myproject.math (pub fn run_all() -> BenchResult)
src/net.xi       → module myproject.net (pub fn run_all() -> BenchResult)
src/db.xi        → module myproject.db (pub fn run_all() -> BenchResult)
```

**Pattern 3: Data + Logic Separation**
```
src/types.xi     → module myproject.types (all type definitions)
src/logic.xi     → module myproject.logic (use types, all business logic)
src/main.xi      → module myproject (use logic, entry point)
```

### What the Compiler CAN Handle Today

| Capability | Status |
|-----------|--------|
| Single-file programs | ✓ |
| Multi-file merge (pass all files to xiomc) | ✓ |
| ModuleCatalog lazy loading | ✓ |
| Cross-file type resolution | ✓ |
| Cross-file function calls | ✓ (via merge path) |
| 30+ file projects | ✓ (benchmark suite verified) |
| Package manager / `xiom install` | ✗ (Phase 5) |
| Build system / `xiom build` | ✗ (Phase 5) |

### When AI Generates Multi-File Code

1. **Generate all files with correct `module` declarations**
2. **Share types via a `types.xi` file**
3. **Compile with all file paths** — the merge path is most reliable
4. **If the catalog path is used**, ensure files are in the same directory or under `examples/`
5. **Use `pub` on everything that crosses file boundaries**

---

**This document is the AI's complete reference for XIOM code generation.**
**When in doubt, refer to the exact syntax and rules above. The compiler enforces everything stated here.**
**Section 16 is the recommended system prompt for AI coding assistants generating XIOM code.**
**Section 17 is required reading for multi-file project generation.**
