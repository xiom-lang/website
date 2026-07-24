# XIOM — AI Coding Reference (Language + Standard Library)

> **Version:** v0.49.8 | **Status:** Production. Compiler (lexer → parser → checker → borrow-checker → LLVM → native) + 40-module standard library.
> This document is the single source of truth for XIOM code generation. Every syntax rule, stdlib function, and compiler flag documented here is part of the language. Write code against this reference as the complete, stable API.

> **⚠️ IMMUTABLE DOCUMENT.** This file is the XIOM language specification. Do NOT modify, add workarounds, or record compiler limitations in this document. Compiler gaps belong in `docs/ROADMAP.md` Phase 5c-E. If the compiler rejects code that matches this spec, the compiler has a bug — file it, do NOT alter the spec. Only the XIOM language team may update this file.

> **Scope:** Core language (sections 1–7), memory & contract model, error handling, module system, the complete 40-module standard library (section 8), the `xiom` compiler CLI (section 11), and code-generation guidance (sections 9, 16, 17).
> Every rule stated here is enforced by the compiler. No exceptions. Treat all documented stdlib types, functions, and CLI flags as fully implemented and callable.

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

> **Import rules:** All examples below include explicit `use xiom.io;` declarations.
> In scripting mode (`xiom run`), the compiler auto-adds `use xiom.io;` — but for
> standard compilation (`xiom file.xi`), `xiom --check`, and WASM targets, you MUST
> include `use xiom.io;` explicitly. AI agents should always include explicit imports
> to ensure code works in all compilation modes.

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
use xiom.io;

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

// if let — desugars to match
if let Some(v) = maybe_val { use(v); } else { fallback(); }

// while let — desugars to while true + match
while let Some(v) = next() { process(v); }
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

// Compound assignment (desugars to x = x + y)
x += 1;    x -= 2;    x *= 3;    x /= 4;    x %= 5;

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
unsafe  extern  is  and  or  not  where
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

// Tuple struct with synthesized field names _0, _1
type Pair = (Int, Int) derive[Eq, Clone]
var p = Pair{ _0: 1, _1: 2 };

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
- Supported derives: `Eq`, `Clone`, `Display`, `Hash`, `Ord`, `Debug`. `Debug` generates `.fmt()` which defaults to Display output.

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

## 8. Standard Library — Production API Reference

The standard library is 40 modules under `xiom.*`. Every module is fully implemented and callable. Import a module with `use xiom.<module>;` then call it.

**Calling conventions:**
- **Free functions** are called through their module: `math.sqrt(x)`, `string.str_concat(a, b)`, `io.println(msg)`, `rand.random()`.
- **Constructors / associated functions** use the type name: `Vec[Int].new()`, `Duration.from_secs(3)`, `Rc.new(value)`, `Regex.new("[a-z]+")`.
- **Methods** are called on a value with implicit `self`: `v.push(x)`, `s.len()`, `d.as_millis()`, `arc.clone()`.
- **`use` a single item** to call it unqualified: `use xiom.collections.Vec;` then `Vec[Int].new()`.

**Signatures below are copied verbatim from the source.** Some collection/method signatures show explicit type params like `Vec.push[T]` — at call sites the receiver's type is inferred, so you write `v.push(x)`.

### When generating code, follow these rules:

1. **Use the types** — `Option[T]`, `Result[T,E]`, `Vec[T]`, `Map[K,V]`, `Set[T]`, `Str` are fully defined. `Option`, `Result`, `Vec`, and arithmetic/comparison/control flow are compiler primitives and need no import.
2. **Use the stdlib** — all 40 modules are implemented. Import with `use xiom.<module>;` and call the documented functions. DO NOT reimplement stdlib functions.
3. **Call through the module** — `io.println(...)`, `math.sqrt(...)`, `string.str_split(...)`, `json = serialize.json_parse(...)`. Methods on stdlib types use dot syntax on the value.
4. **For FFI** — use `extern "C"` directly; the C runtime links standard libc plus the XIOM runtime automatically. See the C FFI block at the end of this section.

---

### 8.1 `core` — Fundamental types, interfaces, and intrinsics

Built into the type system; you can use `Option`, `Result`, and these interfaces without importing.

**Types**
```xiom
type Option[T]     = { is_some: Bool; value: T; }
type Result[T, E]  = { is_ok: Bool; value: T; error: E; }
type Box[T]        = { ptr: *T; }
type BinaryHeap[T] = { data: Vec[T]; invariant: data.len() >= 0; }
type Cow[T]        = { owned: Option[T]; borrowed: &T; }
type PhantomData[T] = { }
type MaybeUninit[T] = { value: T; initialized: Bool; }
```

**Interfaces**
```xiom
interface Clone   { fn clone() -> Self; }
interface Eq      { fn eq(other: &Self) -> Bool; }
interface Ord     { fn compare(other: &Self) -> Int; }        // -1, 0, 1
interface Display { fn to_str() -> Str; }
interface Hash    { fn hash() -> UInt64; }
interface Add { fn add(self, other: &Self) -> Self; }
interface Sub { fn sub(self, other: &Self) -> Self; }
interface Mul { fn mul(self, other: &Self) -> Self; }
interface Div { fn div(self, other: &Self) -> Self; }
interface Iterator[T]     { fn next(self) -> Option[T]; fn size_hint(self) -> (Int, Option[Int]); }
interface IntoIterator[T] { fn into_iter(self) -> Iterator[T]; }
interface Default { fn default() -> Self; }
interface Drop    { fn drop(self); }
interface FromStr { fn from_str(s: Str) -> Result[Self, Str]; }
interface Debug   { fn fmt(self, f: &mut Formatter) -> Result[Unit, FmtError]; }
interface Deref   { type Target; fn deref(self) -> &Self.Target; }
interface DerefMut { fn deref_mut(self) -> &mut Self.Target; }
interface AsRef[T]   { fn as_ref(self) -> &T; }
interface AsMut[T]   { fn as_mut(self) -> &mut T; }
```

**Functions & intrinsics**
```xiom
fn panic(msg: Str)
fn assert(condition: Bool, msg: Str)
fn panic_if(condition: Bool, msg: Str)
fn size_of[T]() -> Int                          // compiler intrinsic
fn align_of[T]() -> Int                         // compiler intrinsic
fn to_int(x: Float64) -> Int
fn to_float(x: Int) -> Float64
fn to_string(x: Int) -> Str
fn to_int_from_str(s: Str) -> Result[Int, Str]
fn to_float_from_str(s: Str) -> Result[Float64, Str]
fn to_bool_from_str(s: Str) -> Result[Bool, Str]
fn to_char(x: Int) -> Char
fn to_int_from_char(c: Char) -> Int
fn is_sorted[T: Ord](items: &Slice[T]) -> Bool
fn all[T](items: &Slice[T], predicate: fn(T) -> Bool) -> Bool
fn none[T](items: &Slice[T], predicate: fn(T) -> Bool) -> Bool
fn contains[T: Eq](items: &Slice[T], value: T) -> Bool
```

**Option methods**
```xiom
fn Option[T].unwrap_or(self, default: T) -> T
fn Option[T].unwrap_or_else(self, f: fn() -> T) -> T
fn Option[T].map[U](self, f: fn(T) -> U) -> Option[U]
fn Option[T].and_then[U](self, f: fn(T) -> Option[U]) -> Option[U]
fn Option[T].filter(self, predicate: fn(&T) -> Bool) -> Option[T]
fn Option[T].is_some_and(self, predicate: fn(&T) -> Bool) -> Bool
```

**Result methods**
```xiom
fn Result[T, E].unwrap_or(self, default: T) -> T
fn Result[T, E].unwrap_or_else(self, f: fn(E) -> T) -> T
fn Result[T, E].map[U](self, f: fn(T) -> U) -> Result[U, E]
fn Result[T, E].map_err[F](self, f: fn(E) -> F) -> Result[T, F]
fn Result[T, E].and_then[U](self, f: fn(T) -> Result[U, E]) -> Result[U, E]
fn Result[T, E].expect(self, msg: Str) -> T
fn Result[T, E].is_ok_and(self, predicate: fn(&T) -> Bool) -> Bool
```

**Box & BinaryHeap**
```xiom
fn Box.new[T](value: T) -> Box[T]
fn Box.get[T](b: &Box[T]) -> &T
fn Box.drop[T](b: Box[T])
fn BinaryHeap[T: Ord].new() -> BinaryHeap[T]
fn BinaryHeap[T: Ord].push(self, value: T)
fn BinaryHeap[T: Ord].pop(self) -> Option[T]
fn BinaryHeap[T: Ord].peek(self) -> Option[T]
fn BinaryHeap[T].len(self) -> Int
fn BinaryHeap[T].is_empty(self) -> Bool
```

**Constants**
```xiom
const INT_MAX: Int = 9223372036854775807;
const INT_MIN: Int = -9223372036854775808;
const FLOAT64_MAX: Float64 = 1.7976931348623157e308;
const FLOAT64_MIN: Float64 = 2.2250738585072014e-308;
const FLOAT64_EPSILON: Float64 = 2.220446049250313e-16;
```

---

### 8.2 `collections` — Vec, Map, Set, and more

```xiom
type Vec[T]        = { data: *T; len: Int; cap: Int; }
type Map[K, V]     = { keys: Vec[K]; values: Vec[V]; }
type Set[T]        = { items: Vec[T]; }
type LinkedList[T] = { items: Vec[T]; }
type Queue[T]      = { data: Vec[T]; head: Int; tail: Int; }
type Stack[T]      = { items: Vec[T]; }
type VecDeque[T]   = { data: Vec[T]; head: Int; tail: Int; }
type BTreeMap[K: Ord, V] = { keys: Vec[K]; values: Vec[V]; }
type BTreeSet[T: Ord]    = { items: Vec[T]; }
type Slice[T]      = { data: Vec[T]; }
```

**Vec** (`data`, `len`, `cap` are codegen primitives; `push`/`pop`/`get`/`len` are built in)
```xiom
fn Vec.new[T]() -> Vec[T]
fn Vec.with_capacity[T](cap: Int) -> Vec[T]
fn Vec.push[T](value: T)
fn Vec.pop[T]() -> Option[T]
fn Vec.get[T](index: Int) -> Option[T]
fn Vec.len[T]() -> Int
fn Vec.is_empty[T]() -> Bool
fn Vec.clear[T]()
fn Vec.insert[T](index: Int, value: T)
fn Vec.remove[T](index: Int) -> Option[T]
fn Vec.first[T]() -> Option[T]
fn Vec.last[T]() -> Option[T]
fn Vec.set[T](index: Int, value: T)
```
Element access via index also works: `v[i]`.

**Map**
```xiom
fn Map.new[K, V]() -> Map[K, V]
fn Map.insert[K, V](key: K, value: V)
fn Map.get[K, V](key: &K) -> Option[V]
fn Map.remove[K, V](key: &K) -> Option[V]
fn Map.contains[K, V](key: &K) -> Bool
fn Map.len[K, V]() -> Int
fn Map.keys[K, V]() -> Vec[K]
fn Map.values[K, V]() -> Vec[V]
fn Map.clear[K, V]()
```

**Set**
```xiom
fn Set.new[T]() -> Set[T]
fn Set.insert[T](value: T)
fn Set.remove[T](value: &T)
fn Set.contains[T](value: &T) -> Bool
fn Set.len[T]() -> Int
fn Set.union[T](other: &Set[T]) -> Set[T]
fn Set.intersection[T](other: &Set[T]) -> Set[T]
fn Set.difference[T](other: &Set[T]) -> Set[T]
```

**LinkedList / Queue / Stack / VecDeque**
```xiom
fn LinkedList.new[T]() -> LinkedList[T]
fn LinkedList.push_front[T](value: T)
fn LinkedList.push_back[T](value: T)
fn LinkedList.pop_front[T]() -> Option[T]
fn LinkedList.pop_back[T]() -> Option[T]
fn LinkedList.len[T]() -> Int
fn LinkedList.is_empty[T]() -> Bool

fn Queue.new[T]() -> Queue[T]
fn Queue.enqueue[T](value: T)
fn Queue.dequeue[T]() -> Option[T]
fn Queue.peek[T]() -> Option[T]
fn Queue.len[T]() -> Int
fn Queue.is_empty[T]() -> Bool

fn Stack.new[T]() -> Stack[T]
fn Stack.push[T](value: T)
fn Stack.pop[T]() -> Option[T]
fn Stack.peek[T]() -> Option[T]
fn Stack.len[T]() -> Int
fn Stack.is_empty[T]() -> Bool

fn VecDeque.new[T]() -> VecDeque[T]
fn VecDeque.with_capacity[T](cap: Int) -> VecDeque[T]
fn VecDeque.push_front[T](value: T)
fn VecDeque.push_back[T](value: T)
fn VecDeque.pop_front[T]() -> Option[T]
fn VecDeque.pop_back[T]() -> Option[T]
fn VecDeque.front[T]() -> Option[T]
fn VecDeque.back[T]() -> Option[T]
fn VecDeque.len[T]() -> Int
```

**BTreeMap / BTreeSet** (sorted, binary-search backed)
```xiom
fn BTreeMap.new[K: Ord, V]() -> BTreeMap[K, V]
fn BTreeMap.insert[K: Ord, V](key: K, value: V) -> Option[V]
fn BTreeMap.get[K: Ord, V](key: &K) -> Option[V]
fn BTreeMap.remove[K: Ord, V](key: &K) -> Option[V]
fn BTreeMap.contains_key[K: Ord, V](key: &K) -> Bool
fn BTreeMap.first_entry[K: Ord, V]() -> Option[(K, V)]
fn BTreeMap.last_entry[K: Ord, V]() -> Option[(K, V)]
fn BTreeMap.len[K: Ord, V]() -> Int

fn BTreeSet.new[T: Ord]() -> BTreeSet[T]
fn BTreeSet.insert[T: Ord](value: T) -> Bool
fn BTreeSet.remove[T: Ord](value: &T) -> Bool
fn BTreeSet.contains[T: Ord](value: &T) -> Bool
fn BTreeSet.first[T: Ord]() -> Option[T]
fn BTreeSet.last[T: Ord]() -> Option[T]
fn BTreeSet.len[T: Ord]() -> Int
```

**Slice**
```xiom
fn Slice.len[T]() -> Int
fn Slice.is_empty[T]() -> Bool
fn Slice.first[T]() -> Option[T]
fn Slice.last[T]() -> Option[T]
fn Slice.get[T](index: Int) -> Option[T]
```

---

### 8.3 `string` — UTF-8 string operations

Call as `string.<fn>(...)`.
```xiom
fn str_len(s: Str) -> Int
fn str_concat(a: Str, b: Str) -> Str
fn str_slice(s: Str, start: Int, end: Int) -> Str
fn str_contains(s: Str, substr: Str) -> Bool
fn str_starts_with(s: Str, prefix: Str) -> Bool
fn str_ends_with(s: Str, suffix: Str) -> Bool
fn str_split(s: Str, delimiter: Str) -> Vec[Str]
fn str_trim(s: Str) -> Str
fn str_to_int(s: Str) -> Result[Int, Str]
fn str_to_float(s: Str) -> Result[Float64, Str]
fn str_upper(s: Str) -> Str
fn str_lower(s: Str) -> Str
fn format(fmt: Str) -> Str
fn format1(fmt: Str, arg: Str) -> Str
fn format2(fmt: Str, arg1: Str, arg2: Str) -> Str
fn char_at(s: Str, pos: Int) -> Option[Char]
fn index_of(s: Str, substr: Str) -> Option[Int]
fn last_index_of(s: Str, substr: Str) -> Option[Int]
fn replace(s: Str, from: Str, to: Str) -> Str
fn lines(s: Str) -> Vec[Str]
fn words(s: Str) -> Vec[Str]
fn is_empty(s: Str) -> Bool
fn char_count(s: Str) -> Int
fn byte_count(s: Str) -> Int
```

---

### 8.4 `io` — Console, files, process, buffered I/O

Call as `io.<fn>(...)`.

**Types & interfaces**
```xiom
type IOError  = { message: Str; code: Int; }
type SeekFrom = enum { Start(Int), End(Int), Current(Int) }
type BufReader = { inner: Int; buf: Vec[UInt8]; }
type BufWriter = { inner: Int; buf: Vec[UInt8]; }
type Metadata  = { size: Int; is_file: Bool; is_dir: Bool; modified: Int; created: Int; permissions: Int; }
type Cursor    = { data: Vec[UInt8]; pos: Int; }
interface Read  { fn read(self, buf: &mut Vec[UInt8]) -> Result[Int, IOError]; fn read_to_end(self, buf: &mut Vec[UInt8]) -> Result[Int, IOError]; fn read_to_string(self) -> Result[Str, IOError]; fn read_exact(self, buf: &mut Vec[UInt8]) -> Result[Unit, IOError]; }
interface Write { fn write(self, buf: &Vec[UInt8]) -> Result[Int, IOError]; fn write_all(self, buf: &Vec[UInt8]) -> Result[Unit, IOError]; fn flush(self) -> Result[Unit, IOError]; }
interface Seek  { fn seek(self, pos: SeekFrom) -> Result[Int, IOError]; fn stream_position(self) -> Result[Int, IOError]; }
```

**Console**
```xiom
fn print(msg: Str)
fn println(msg: Str)
fn print_line(s: Str)
fn read_line() -> Str
fn read_int() -> Result[Int, Str]
fn read_float() -> Result[Float64, Str]
fn stdin() -> Int
fn stdout() -> Int
fn stderr() -> Int
```

**Filesystem**
```xiom
fn read_file(path: Str) -> Result[Str, IOError]
fn write_file(path: Str, content: Str) -> Result[Unit, IOError]
fn append_file(path: Str, content: Str) -> Result[Unit, IOError]
fn file_exists(path: Str) -> Bool
fn is_dir(path: Str) -> Bool
fn create_dir(path: Str) -> Result[Unit, IOError]
fn list_dir(path: Str) -> Result[Vec[Str], IOError]
fn remove_file(path: Str) -> Result[Unit, IOError]
fn copy_file(src: Str, dst: Str) -> Result[Unit, IOError]
fn rename(src: Str, dst: Str) -> Result[Unit, IOError]
fn metadata(path: Str) -> Result[Metadata, IOError]
fn set_permissions(path: Str, perm: Int) -> Result[Unit, IOError]
```

**Process, time & paths**
```xiom
fn exit(code: Int)
fn args() -> Vec[Str]
fn env_var(name: Str) -> Option[Str]
fn time_now() -> Int
fn sleep(ms: Int)
fn join_paths(base: Str, child: Str) -> Str
fn parent_path(path: Str) -> Option[Str]
fn file_name(path: Str) -> Option[Str]
fn extension(path: Str) -> Option[Str]
fn is_absolute(path: Str) -> Bool
```

**Buffered / memory I/O**
```xiom
fn BufReader.new(reader: Int) -> BufReader
fn BufReader.read_line(self, buf: &mut Str) -> Result[Int, IOError]
fn BufReader.lines(self) -> Vec[Str]
fn BufWriter.new(writer: Int) -> BufWriter
fn Cursor.new(data: Vec[UInt8]) -> Cursor
fn Cursor.into_inner(self) -> Vec[UInt8]
```

---

### 8.5 `fmt` — Formatting & Display

```xiom
interface Display { fn fmt(self, f: &mut Formatter) -> Result[Unit, FmtError]; }
type Formatter = { buf: Str; width: Int; precision: Int; align: Int; }
type FmtError  = { message: Str; }

fn Formatter.new() -> Formatter
fn Formatter.write_str(self, s: Str) -> Result[Unit, FmtError]
fn Formatter.write_int(self, n: Int) -> Result[Unit, FmtError]
fn Formatter.write_float(self, f: Float64) -> Result[Unit, FmtError]
fn Formatter.write_bool(self, b: Bool) -> Result[Unit, FmtError]
fn Formatter.finish(self) -> Str

fn Int.to_str() -> Str
fn Float64.to_str() -> Str
fn Bool.to_str() -> Str
fn Str.to_str() -> Str

fn format1[T](fmt: Str, arg: T) -> Str                       // "{}" placeholder
fn format2[T, U](fmt: Str, arg1: T, arg2: U) -> Str
fn format3[T, U, V](fmt: Str, arg1: T, arg2: U, arg3: V) -> Str
fn print(s: Str)
fn println(s: Str)
```

---

### 8.6 `math` — Math functions & constants

Call as `math.<fn>(...)`. libm-backed functions plus pure-XIOM fallbacks (`*_pure`).
```xiom
const PI: Float64  = 3.141592653589793;
const E: Float64   = 2.718281828459045;
const TAU: Float64 = 6.283185307179586;

fn sqrt(x: Float64) -> Float64
fn pow(base: Float64, exp: Float64) -> Float64
fn abs_int(x: Int) -> Int
fn abs_float(x: Float64) -> Float64
fn min_int(a: Int, b: Int) -> Int
fn max_int(a: Int, b: Int) -> Int
fn min_float(a: Float64, b: Float64) -> Float64
fn max_float(a: Float64, b: Float64) -> Float64
fn floor(x: Float64) -> Float64
fn ceil(x: Float64) -> Float64
fn round(x: Float64) -> Int
fn sin(x: Float64) -> Float64
fn cos(x: Float64) -> Float64
fn tan(x: Float64) -> Float64
fn asin(x: Float64) -> Float64
fn acos(x: Float64) -> Float64
fn atan(x: Float64) -> Float64
fn atan2(y: Float64, x: Float64) -> Float64
fn exp(x: Float64) -> Float64
fn ln(x: Float64) -> Float64
fn log10(x: Float64) -> Float64
fn log2(x: Float64) -> Float64
fn bit_and(a: Int, b: Int) -> Int
fn bit_or(a: Int, b: Int) -> Int
fn bit_xor(a: Int, b: Int) -> Int
fn bit_not(a: Int) -> Int
fn shl(a: Int, n: Int) -> Int
fn shr(a: Int, n: Int) -> Int
fn seed_rng(seed: Int)
fn random() -> Float64
fn random_range(min: Int, max: Int) -> Int
fn random_float() -> Float64
fn clamp(x: Float64, lo: Float64, hi: Float64) -> Float64
fn lerp(a: Float64, b: Float64, t: Float64) -> Float64
fn is_nan(x: Float64) -> Bool
fn is_inf(x: Float64) -> Bool
```
Pure fallbacks (no libm): `sqrt_pure`, `pow_pure`, `abs_float_pure`, `floor_pure`, `ceil_pure`, `sin_pure`, `cos_pure`, `tan_pure`, `asin_pure`, `acos_pure`, `atan_pure`, `atan2_pure`, `exp_pure`, `ln_pure`, `log10_pure`, `log2_pure` (same signatures as their non-pure counterparts).

---

### 8.7 `num` — Numeric traits & integer/float utilities (with merged crypto primitives)

```xiom
interface Neg  { fn neg(self) -> Self; }
interface Rem  { fn rem(self, other: Self) -> Self; }
interface Abs  { fn abs(self) -> Self; }
interface Pow  { fn pow(self, exp: Self) -> Self; }
interface Sqrt { fn sqrt(self) -> Self; }
interface Bounded { fn min_value() -> Self; fn max_value() -> Self; fn epsilon() -> Self; fn zero() -> Self; }

fn min_value[T: Bounded]() -> T
fn max_value[T: Bounded]() -> T
fn epsilon[T: Bounded]() -> T
fn gcd(a: Int, b: Int) -> Int
fn lcm(a: Int, b: Int) -> Int
fn is_power_of_two(n: Int) -> Bool
fn next_power_of_two(n: Int) -> Int
fn count_ones(n: Int) -> Int
fn count_zeros(n: Int) -> Int
fn leading_zeros(n: Int) -> Int
fn trailing_zeros(n: Int) -> Int
fn rotate_left(n: Int, k: Int) -> Int
fn rotate_right(n: Int, k: Int) -> Int
fn reverse_bits(n: Int) -> Int
fn to_be(n: Int) -> Int
fn to_le(n: Int) -> Int
fn from_be(n: Int) -> Int
fn from_le(n: Int) -> Int
fn is_finite(x: Float64) -> Bool
fn is_normal(x: Float64) -> Bool
fn classify(x: Float64) -> Int
fn floor(x: Float64) -> Int
fn ceil(x: Float64) -> Int
fn round(x: Float64) -> Int
fn trunc(x: Float64) -> Int
fn fract(x: Float64) -> Float64
fn recip(x: Float64) -> Float64
fn to_degrees(rad: Float64) -> Float64
fn to_radians(deg: Float64) -> Float64
fn hypot(x: Float64, y: Float64) -> Float64
fn saturating_add[T: Bounded + Ord + Add](a: T, b: T) -> T
fn saturating_sub[T: Bounded + Ord + Sub](a: T, b: T) -> T
fn saturating_mul[T: Bounded + Ord + Mul + Div](a: T, b: T) -> T
fn checked_add[T: Bounded + Ord + Add](a: T, b: T) -> Option[T]
fn checked_sub[T: Bounded + Ord + Sub](a: T, b: T) -> Option[T]
fn checked_mul[T: Bounded + Ord + Mul + Div](a: T, b: T) -> Option[T]
fn checked_div[T: Bounded + Eq + Div](a: T, b: T) -> Option[T]
fn wrapping_add[T: Bounded + Add](a: T, b: T) -> T
fn wrapping_sub[T: Bounded + Sub](a: T, b: T) -> T
fn wrapping_mul[T: Bounded + Mul](a: T, b: T) -> T
fn parse_int(s: Str) -> Result[Int, Str]
fn parse_float(s: Str) -> Result[Float64, Str]
fn parse_int_radix(s: Str, radix: Int) -> Result[Int, Str]
```

> **Note:** Several crypto primitive modules (`aes`, `sha`, `b64`, `ed25519`, `hex`, `md5`, `pbkdf`, `random`) were merged from packages into stdlib. Use `use xiom.crypto;` for the unified crypto API — see section 8.30.

---

### 8.8 `cmp` — Comparison & ordering

```xiom
type Ordering  = enum { Less, Equal, Greater }
type Reverse[T] = { value: T; }
interface PartialEq[Rhs: Self]  { fn eq(self, other: &Rhs) -> Bool; fn ne(self, other: &Rhs) -> Bool; }
interface PartialOrd[Rhs: Self] { fn partial_cmp(self, other: &Rhs) -> Option[Ordering]; fn lt(self, other: &Rhs) -> Bool; fn le(self, other: &Rhs) -> Bool; fn gt(self, other: &Rhs) -> Bool; fn ge(self, other: &Rhs) -> Bool; }

fn Ordering.reverse(self) -> Ordering
fn Ordering.then(self, other: Ordering) -> Ordering
fn Ordering.then_with(self, f: fn() -> Ordering) -> Ordering
fn min[T: Ord](a: T, b: T) -> T
fn max[T: Ord](a: T, b: T) -> T
fn clamp[T: Ord](value: T, min_val: T, max_val: T) -> T
fn min_by[T](a: T, b: T, compare: fn(&T, &T) -> Ordering) -> T
fn max_by[T](a: T, b: T, compare: fn(&T, &T) -> Ordering) -> T
fn max_int(a: Int, b: Int) -> Int
fn min_int(a: Int, b: Int) -> Int
fn clamp_int(value: Int, min_val: Int, max_val: Int) -> Int
fn max_float(a: Float64, b: Float64) -> Float64
fn min_float(a: Float64, b: Float64) -> Float64
fn clamp_float(value: Float64, min_val: Float64, max_val: Float64) -> Float64
fn Reverse.new[T](value: T) -> Reverse[T]
```

---

### 8.9 `hash` — Hashing

```xiom
interface Hash        { fn hash(self, hasher: Hasher); }
interface Hasher      { fn write(self, bytes: &Vec[UInt8]); fn write_int(self, n: Int); fn write_str(self, s: Str); fn finish(self) -> Int; }
interface BuildHasher { fn build_hasher(self) -> Hasher; }
type DefaultHasher = { state: Int; }

fn DefaultHasher.new() -> DefaultHasher
fn DefaultHasher.write(self, bytes: &Vec[UInt8])
fn DefaultHasher.write_int(self, n: Int)
fn DefaultHasher.write_str(self, s: Str)
fn DefaultHasher.finish(self) -> Int
fn Int.hash(self, hasher: Hasher)
fn Str.hash(self, hasher: Hasher)
fn Bool.hash(self, hasher: Hasher)
fn hash_value[T: Hash](value: &T) -> Int
fn hash_combine(seed: Int, hash: Int) -> Int
fn hash[T: Hash](value: T) -> UInt64
fn sip_hash(data: &Vec[UInt8]) -> UInt64
```

---

### 8.10 `char` — Character operations

```xiom
fn is_alphabetic(c: Char) -> Bool
fn is_alphanumeric(c: Char) -> Bool
fn is_ascii(c: Char) -> Bool
fn is_control(c: Char) -> Bool
fn is_digit(c: Char) -> Bool
fn is_lowercase(c: Char) -> Bool
fn is_uppercase(c: Char) -> Bool
fn is_numeric(c: Char) -> Bool
fn is_punctuation(c: Char) -> Bool
fn is_whitespace(c: Char) -> Bool
fn to_lowercase(c: Char) -> Char
fn to_uppercase(c: Char) -> Char
fn to_digit(c: Char, radix: Int) -> Option[Int]
fn from_digit(n: Int, radix: Int) -> Option[Char]
fn len_utf8(c: Char) -> Int
fn encode_utf8(c: Char, buf: &mut Vec[UInt8])
```

---

### 8.11 `convert` — Type conversions

```xiom
interface From[T]    { fn from(value: T) -> Self; }
interface Into[T]    { fn into(self) -> T; }
interface TryFrom[T] { fn try_from(value: T) -> Result[Self, Str]; }
interface TryInto[T] { fn try_into(self) -> Result[T, Str]; }

fn identity[T](x: T) -> T
fn int_to_float(n: Int) -> Float64
fn float_to_int(f: Float64) -> Int
fn int_to_string(n: Int) -> Str
fn float_to_string(f: Float64) -> Str
fn bool_to_string(b: Bool) -> Str
fn char_to_int(c: Char) -> Int
fn int_to_char(n: Int) -> Option[Char]
```

---

### 8.12 `iter` — Iterators & adapters

```xiom
type Range          = { start: Int; end: Int; }
type RangeInclusive = { start: Int; end: Int; current: Int; done: Bool; }
type MapIter[T, U]  = { iter: Iterator[T]; f: fn(T) -> U; }
type FilterIter[T]  = { iter: Iterator[T]; predicate: fn(&T) -> Bool; }
type EnumerateIter[T] = { iter: Iterator[T]; index: Int; }
type TakeIter[T]    = { iter: Iterator[T]; remaining: Int; }
type SkipIter[T]    = { iter: Iterator[T]; to_skip: Int; }
type ChainIter[T, U] = { first: Iterator[T]; second: Iterator[U]; }
type ZipIter[T, U]  = { a: Iterator[T]; b: Iterator[U]; }

fn range(start: Int, end: Int) -> Range
fn range_inclusive(start: Int, end: Int) -> RangeInclusive
fn Range.next(self) -> Option[Int]
fn Range.len(self) -> Int
fn Range.contains(self, x: Int) -> Bool
fn RangeInclusive.next(self) -> Option[Int]

fn Iterator[T].map[U](self, f: fn(T) -> U) -> MapIter[T, U]
fn Iterator[T].filter(self, predicate: fn(&T) -> Bool) -> FilterIter[T]
fn Iterator[T].enumerate(self) -> EnumerateIter[T]
fn Iterator[T].take(self, n: Int) -> TakeIter[T]
fn Iterator[T].skip(self, n: Int) -> SkipIter[T]
fn Iterator[T].chain[U](self, other: Iterator[U]) -> ChainIter[T, U]
fn Iterator[T].zip[U](self, other: Iterator[U]) -> ZipIter[T, U]
fn Iterator[T].collect(self) -> Vec[T]
fn Iterator[T].fold[B](self, init: B, f: fn(B, T) -> B) -> B
fn Iterator[T].count(self) -> Int
fn Iterator[T].sum(self) -> T
fn Iterator[T].product(self) -> T
fn Iterator[T].max(self) -> Option[T]
fn Iterator[T].min(self) -> Option[T]
fn Iterator[T].find(self, predicate: fn(&T) -> Bool) -> Option[T]
fn Iterator[T].all(self, predicate: fn(&T) -> Bool) -> Bool
fn Iterator[T].any(self, predicate: fn(&T) -> Bool) -> Bool
fn Iterator[T].nth(self, n: Int) -> Option[T]
fn Iterator[T].last(self) -> Option[T]
```

---

### 8.13 `array` — Fixed-size array `[N]T` operations

```xiom
fn len[T, const N: Int](arr: &[N]T) -> Int
fn is_empty[T, const N: Int](arr: &[N]T) -> Bool
fn first[T](arr: &[N]T) -> Option[&T]
fn last[T](arr: &[N]T) -> Option[&T]
fn get[T](arr: &[N]T, index: Int) -> Option[&T]
fn get_mut[T](arr: &mut [N]T, index: Int) -> Option[&mut T]
fn map[T, U, const N: Int](arr: [N]T, f: fn(T) -> U) -> [N]U
fn zip[T, U, const N: Int](a: [N]T, b: [N]U) -> [N](T, U)
fn fold[T, B](arr: [N]T, init: B, f: fn(B, T) -> B) -> B
fn as_slice[T](arr: &[N]T) -> Slice[T]
fn as_mut_slice[T](arr: &mut [N]T) -> Slice[T]
fn each_ref[T](arr: &[N]T) -> [N]&T
fn each_mut[T](arr: &mut [N]T) -> [N]&mut T
fn fill[T: Clone](arr: &mut [N]T, value: T)
fn swap[T](arr: &mut [N]T, a: Int, b: Int)
fn reverse[T](arr: &mut [N]T)
fn rotate_left[T](arr: &mut [N]T, mid: Int)
fn rotate_right[T](arr: &mut [N]T, k: Int)
fn sort[T: Ord](arr: &mut [N]T)
fn sort_by[T](arr: &mut [N]T, compare: fn(&T, &T) -> Ordering)
fn binary_search[T: Ord](arr: &[N]T, x: &T) -> Result[Int, Int]
fn contains[T: Eq](arr: &[N]T, x: &T) -> Bool
```

---

### 8.14 `mem` — Memory utilities

```xiom
type ManuallyDrop[T] = { value: T; }

fn swap[T](a: &mut T, b: &mut T)
fn replace[T](dest: &mut T, src: T) -> T
fn take[T: Default](dest: &mut T) -> T
fn drop[T](value: T)
fn size_of[T]() -> Int
fn align_of[T]() -> Int
fn size_of_val[T](value: &T) -> Int
fn min_align_of_val[T](value: &T) -> Int
fn zeroed[T]() -> T
fn uninitialized[T]() -> T
fn ManuallyDrop.new[T](value: T) -> ManuallyDrop[T]
fn ManuallyDrop.into_inner[T](self) -> T
fn ManuallyDrop.take[T](self) -> T
fn ManuallyDrop.drop[T](self)
```

---

### 8.15 `ptr` — Raw pointer operations (unsafe)

```xiom
fn null[T]() -> *T
fn null_mut[T]() -> *mut T
fn dangling[T]() -> *T
fn is_null[T](ptr: *const T) -> Bool
fn read[T](ptr: *const T) -> T
fn write[T](ptr: *mut T, value: T)
fn read_volatile[T](ptr: *const T) -> T
fn write_volatile[T](ptr: *mut T, value: T)
fn swap[T](a: *mut T, b: *mut T)
fn replace[T](dest: *mut T, src: T) -> T
fn copy[T](src: *const T, dst: *mut T, count: Int)
fn copy_nonoverlapping[T](src: *const T, dst: *mut T, count: Int)
fn eq[T](a: *const T, b: *const T) -> Bool
fn offset[T](ptr: *const T, count: Int) -> *const T
fn wrapping_offset[T](ptr: *const T, count: Int) -> *const T
fn add[T](ptr: *const T, count: Int) -> *const T
fn sub[T](ptr: *const T, count: Int) -> *const T
fn from_ref[T](r: &T) -> *const T
fn from_mut[T](r: &mut T) -> *mut T
```

---

### 8.16 `alloc` — Allocation

```xiom
type Layout      = { size: Int; align: Int; }
type AllocError  = { message: Str; }
type GlobalAlloc = { }
interface Allocator {
  fn allocate(self, layout: Layout) -> Result[*mut UInt8, AllocError];
  fn deallocate(self, ptr: *mut UInt8, layout: Layout);
  fn allocate_zeroed(self, layout: Layout) -> Result[*mut UInt8, AllocError];
  fn grow(self, ptr: *mut UInt8, old: Layout, new: Layout) -> Result[*mut UInt8, AllocError];
  fn shrink(self, ptr: *mut UInt8, old: Layout, new: Layout) -> Result[*mut UInt8, AllocError];
}

fn Layout.new(size: Int) -> Layout
fn Layout.with_align(self, align: Int) -> Layout
fn Layout.padded_size(self) -> Int
fn global_alloc() -> Allocator
fn alloc(size: Int) -> *mut UInt8
fn alloc_zeroed(size: Int) -> *mut UInt8
fn realloc(ptr: *mut UInt8, old_size: Int, new_size: Int) -> *mut UInt8
fn dealloc(ptr: *mut UInt8, size: Int)
fn alloc_layout(layout: Layout) -> *mut UInt8
fn dealloc_layout(ptr: *mut UInt8, layout: Layout)
```

---

### 8.17 `error` — Error trait hierarchy

```xiom
interface Error { fn source(self) -> Option[Error]; fn description(self) -> Str; fn cause(self) -> Option[Error]; }
type ErrorChain = { errors: Vec[Str]; }
type Backtrace  = { frames: Vec[Str]; }

fn Error.chain(self) -> ErrorChain
fn ErrorChain.display(self) -> Str
fn wrap_error[T, E: Error](result: Result[T, E], context: Str) -> Result[T, Str]
fn context[T, E](result: Result[T, E], msg: Str) -> Result[T, Str]
fn capture_backtrace() -> Backtrace
fn Backtrace.display(self) -> Str
```

---

### 8.18 `path` — Path manipulation

```xiom
type Path    = { inner: Str; }
type PathBuf = { inner: Str; }

fn Path.new(s: Str) -> Path
fn Path.parent(self) -> Option[Path]
fn Path.file_name(self) -> Option[Str]
fn Path.extension(self) -> Option[Str]
fn Path.file_stem(self) -> Option[Str]
fn Path.is_absolute(self) -> Bool
fn Path.is_relative(self) -> Bool
fn Path.has_root(self) -> Bool
fn Path.components(self) -> Vec[Str]
fn Path.to_str(self) -> Str
fn Path.join(self, child: Str) -> PathBuf
fn Path.with_extension(self, ext: Str) -> PathBuf
fn Path.with_file_name(self, name: Str) -> PathBuf
fn Path.exists(self) -> Bool
fn Path.is_file(self) -> Bool
fn Path.is_dir(self) -> Bool
fn Path.metadata(self) -> Result[Metadata, Str]
fn Path.canonicalize(self) -> Result[PathBuf, Str]
fn Path.starts_with(self, base: &Path) -> Bool
fn Path.ends_with(self, child: &Path) -> Bool
fn PathBuf.new() -> PathBuf
fn PathBuf.from(s: Str) -> PathBuf
fn PathBuf.push(self, component: Str)
fn PathBuf.pop(self) -> Bool
fn PathBuf.as_path(self) -> Path
fn PathBuf.clear(self)
fn path_separator() -> Str
```

---

### 8.19 `time` — Duration, Instant, SystemTime, DateTime

```xiom
type Duration   = { secs: Int; nanos: Int; }
type Instant    = { t: Int; }
type SystemTime = { secs: Int; nanos: Int; }
type DateTime   = { year: Int; month: Int; day: Int; hour: Int; minute: Int; second: Int; weekday: Int; }

fn Duration.new(secs: Int, nanos: Int) -> Duration
fn Duration.from_secs(s: Int) -> Duration
fn Duration.from_secs_f64(secs: Float64) -> Duration
fn Duration.from_millis(ms: Int) -> Duration
fn Duration.from_micros(us: Int) -> Duration
fn Duration.from_nanos(ns: Int) -> Duration
fn Duration.as_secs(self) -> Int
fn Duration.as_millis(self) -> Int
fn Duration.as_micros(self) -> Int
fn Duration.as_nanos(self) -> Int
fn Duration.as_secs_f64(self) -> Float64
fn Duration.subsec_nanos(self) -> Int
fn Duration.add(self, other: Duration) -> Duration
fn Duration.sub(self, other: Duration) -> Duration
fn Duration.mul(self, factor: Int) -> Duration
fn Duration.div(self, divisor: Int) -> Duration
fn Duration.checked_add(self, other: Duration) -> Option[Duration]
fn Duration.checked_sub(self, other: Duration) -> Option[Duration]
fn Instant.now() -> Instant
fn Instant.elapsed(self) -> Duration
fn Instant.duration_since(self, earlier: Instant) -> Duration
fn Instant.add(self, d: Duration) -> Instant
fn Instant.sub(self, d: Duration) -> Instant
fn SystemTime.now() -> SystemTime
fn SystemTime.unix_epoch() -> SystemTime
fn SystemTime.duration_since(self, earlier: SystemTime) -> Result[Duration, Str]
fn SystemTime.secs_since_epoch(self) -> Int
fn DateTime.now() -> DateTime
fn DateTime.year(self) -> Int
fn DateTime.month(self) -> Int
fn DateTime.day(self) -> Int
fn DateTime.hour(self) -> Int
fn DateTime.minute(self) -> Int
fn DateTime.second(self) -> Int
fn DateTime.weekday(self) -> Int
fn utc_now() -> DateTime
fn local_now() -> DateTime
fn sleep(dur: Duration)
fn sleep_ms(ms: Int)
fn sleep_until(instant: Instant)
```

---

### 8.20 `env` — Environment & directories

```xiom
const OS: Str     = "windows";
const ARCH: Str   = "x86_64";
const FAMILY: Str = "windows";   // "unix" or "windows"

fn var(name: Str) -> Result[Str, Str]
fn var_opt(name: Str) -> Option[Str]
fn set_var(name: Str, value: Str)
fn remove_var(name: Str)
fn vars() -> Vec[(Str, Str)]
fn args() -> Vec[Str]
fn args_os() -> Vec[Str]
fn current_exe() -> Result[Str, Str]
fn current_dir() -> Result[Str, Str]
fn set_current_dir(path: Str) -> Result[Unit, Str]
fn temp_dir() -> Str
fn home_dir() -> Option[Str]
fn data_dir() -> Option[Str]
fn cache_dir() -> Option[Str]
fn config_dir() -> Option[Str]
fn executable_dir() -> Option[Str]
fn join_paths(a: Str, b: Str) -> Str
fn path_separator() -> Str
```

---

### 8.21 `os` — Platform, processes, filesystem walk

```xiom
type ChildProcess = { pid: Int; stdin: Int; stdout: Int; stderr: Int; }
type FileWatcher  = { path: Str; recursive: Bool; }
type FileEvent    = enum { Created(path: Str), Modified(path: Str), Deleted(path: Str), Renamed(from: Str, to: Str) }
type Pipe         = { read_fd: Int; write_fd: Int; }

fn platform() -> Str
fn cpu_count() -> Int
fn total_memory() -> Int
fn free_memory() -> Int
fn env_set(name: Str, value: Str)
fn env_unset(name: Str)
fn current_dir() -> Str
fn set_current_dir(path: Str) -> Result[Unit, Str]
fn temp_dir() -> Str
fn home_dir() -> Option[Str]
fn walk_dir(path: Str, callback: fn(Str, Metadata) -> Unit) -> Result[Unit, Str]
fn walk_dir_filtered(path: Str, pattern: Str, callback: fn(Str, Metadata) -> Unit) -> Result[Unit, Str]
fn watch_file(path: Str) -> Result[FileWatcher, Str]
fn watch_dir(path: Str, recursive: Bool) -> Result[FileWatcher, Str]
fn FileWatcher.poll(self) -> Result[Vec[FileEvent], Str]
fn FileWatcher.close(self)
fn ChildProcess.wait(self) -> Result[Int, Str]
fn ChildProcess.kill(self) -> Result[Unit, Str]
fn ChildProcess.id(self) -> Int
fn on_signal(signal: Int, handler: fn(Int) -> Unit)
fn raise_signal(signal: Int)
fn create_pipe() -> Result[Pipe, Str]
fn Pipe.read(self, buf: &mut Vec[UInt8]) -> Result[Int, Str]
fn Pipe.write(self, data: &Vec[UInt8]) -> Result[Int, Str]
fn Pipe.close_read(self)
fn Pipe.close_write(self)
fn disk_free(path: Str) -> Result[Int, Str]
fn disk_total(path: Str) -> Result[Int, Str]
fn file_size_bytes(path: Str) -> Result[Int, Str]

const SIGINT: Int = 2;  const SIGTERM: Int = 15;  const SIGKILL: Int = 9;
const SIGUSR1: Int = 10;  const SIGUSR2: Int = 12;
```

---

### 8.22 `sync` — Synchronization primitives

```xiom
type Mutex[T]      = { inner: *UInt8; data: *T; }
type MutexGuard[T] = { mutex: Mutex[T]; }
type RwLock[T]     = { inner: *UInt8; rcond: *UInt8; wcond: *UInt8; data: *T; state: *Int; }
type ReadGuard[T]  = { lock: RwLock[T]; }
type WriteGuard[T] = { lock: RwLock[T]; }
type Condvar       = { inner: *UInt8; }
type Once          = { inner: *UInt8; state: *Int; }
type Barrier       = { inner: *UInt8; cond: *UInt8; count: Int; waiting: *Int; generation: *Int; }
type Arc[T]        = { ptr: *ArcInner[T]; }
type ArcInner[T]   = { count: *Int; value: T; }
type AtomicBool    = { ptr: *Int; }
type AtomicInt     = { ptr: *Int; }

fn Mutex.new[T](value: T) -> Mutex[T]
fn Mutex.lock[T](self) -> MutexGuard[T]
fn Mutex.try_lock[T](self) -> Option[MutexGuard[T]]
fn Mutex.into_inner[T](self) -> T
fn MutexGuard.get[T](self) -> T
fn MutexGuard.get_mut[T](self) -> T
fn MutexGuard.drop[T](self)
fn RwLock.new[T](data: T) -> RwLock[T]
fn RwLock.read[T](self) -> ReadGuard[T]
fn RwLock.write[T](self) -> WriteGuard[T]
fn RwLock.try_read[T](self) -> Option[ReadGuard[T]]
fn RwLock.try_write[T](self) -> Option[WriteGuard[T]]
fn ReadGuard.get[T](self) -> T
fn WriteGuard.get[T](self) -> T
fn WriteGuard.get_mut[T](self) -> T
fn Condvar.new() -> Condvar
fn Condvar.wait[T](self, guard: MutexGuard[T]) -> MutexGuard[T]
fn Condvar.notify_one(self)
fn Condvar.notify_all(self)
fn Once.new() -> Once
fn Once.call_once(self, f: fn())
fn Once.is_completed(self) -> Bool
fn Barrier.new(n: Int) -> Barrier
fn Barrier.wait(self)
fn Arc.new[T](value: T) -> Arc[T]
fn Arc.clone[T](self) -> Arc[T]
fn Arc.get[T](self) -> T
fn Arc.strong_count[T](self) -> Int
fn Arc.ptr_eq[T, U](self, other: &Arc[U]) -> Bool
fn Arc.drop[T](self)
fn AtomicBool.new(val: Bool) -> AtomicBool
fn AtomicBool.load(self) -> Bool
fn AtomicBool.store(self, val: Bool)
fn AtomicBool.swap(self, val: Bool) -> Bool
fn AtomicBool.compare_exchange(self, current: Bool, new: Bool) -> Bool
fn AtomicInt.new(val: Int) -> AtomicInt
fn AtomicInt.load(self) -> Int
fn AtomicInt.store(self, val: Int)
fn AtomicInt.fetch_add(self, val: Int) -> Int
fn AtomicInt.fetch_sub(self, val: Int) -> Int
fn AtomicInt.swap(self, val: Int) -> Int
fn AtomicInt.compare_exchange(self, current: Int, new: Int) -> Bool
```

---

### 8.23 `thread` — Threads & scopes

```xiom
type Thread        = { handle: *UInt8; id: Int; }
type JoinHandle[T] = { thread: Thread; result_buf: *UInt8; }
type Scope         = {}

fn spawn[T](f: fn() -> T) -> JoinHandle[T]
fn spawn_with_name[T](name: Str, f: fn() -> T) -> JoinHandle[T]
fn JoinHandle.join[T](self) -> Result[T, Str]
fn JoinHandle.is_finished[T](self) -> Bool
fn JoinHandle.thread[T](self) -> Thread
fn JoinHandle.detach[T](self)
fn Thread.current() -> Thread
fn Thread.id(self) -> Int
fn Thread.name(self) -> Option[Str]
fn sleep_ms(ms: Int)
fn sleep(ms: Int)
fn yield_now()
fn scope[T](f: fn(&Scope) -> T) -> T
fn Scope.spawn[T](self, f: fn() -> T) -> JoinHandle[T]
fn available_parallelism() -> Int
fn hardware_threads() -> Int
fn current_thread_id() -> Int
```

---

### 8.24 `async` — Cooperative executor & channels

```xiom
type Executor   = { ready: Vec[fn()]; timers: Vec[Timer]; }
type Channel[T] = { items: Vec[T]; closed: Bool; cap: Int; }

fn Executor.new() -> Executor
fn Executor.spawn(self, task: fn())
fn Executor.at(self, deadline: Int, task: fn())
fn Executor.step(self) -> Bool
fn Executor.fire_due_timers(self)
fn Executor.run(self)
fn Executor.block_on(self, task: fn())
fn spawn(task: fn())
fn run()
fn block_on(task: fn())
fn delay(ms: Int, task: fn())
fn sleep_ms(ms: Int)
fn Channel.bounded[T](capacity: Int) -> Channel[T]
fn Channel.unbounded[T]() -> Channel[T]
fn Channel.send[T](value: T)
fn Channel.recv[T]() -> T
fn Channel.try_recv[T]() -> Option[T]
fn Channel.close[T]()
```

---

### 8.25 `net` — TCP, UDP, HTTP, DNS, URL

```xiom
type TcpStream    = { fd: Int; }
type TcpListener  = { fd: Int; }
type UdpSocket    = { fd: Int; }
type NetError     = { message: Str; code: Int; }
type HttpResponse = { status: Int; body: Str; }
type HttpMethod   = enum { GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS }
type UrlParts     = { scheme: Str; host: Str; port: Int; path: Str; query: Str; fragment: Str; }

fn tcp_connect(host: Str, port: Int) -> Result[TcpStream, NetError]
fn tcp_listen(host: Str, port: Int) -> Result[TcpListener, NetError]
fn TcpStream.read(self, buf: &mut Vec[UInt8]) -> Result[Int, NetError]
fn TcpStream.write(self, data: &Vec[UInt8]) -> Result[Int, NetError]
fn TcpStream.close(self) -> Result[Unit, NetError]
fn TcpListener.accept(self) -> Result[(TcpStream, Str), NetError]
fn http_get(url: Str) -> Result[HttpResponse, NetError]
fn http_post(url: Str, body: Str) -> Result[HttpResponse, NetError]
fn udp_bind(host: Str, port: Int) -> Result[UdpSocket, NetError]
fn UdpSocket.send_to(self, data: &Vec[UInt8], addr: Str, port: Int) -> Result[Int, NetError]
fn UdpSocket.recv_from(self, buf: &mut Vec[UInt8]) -> Result[(Int, Str, Int), NetError]
fn UdpSocket.close(self) -> Result[Unit, NetError]
fn resolve_host(hostname: Str) -> Result[Vec[Str], NetError]
fn local_addr(port: Int) -> Result[Str, NetError]
fn parse_url(url: Str) -> Result[UrlParts, NetError]
```

---

### 8.26 `ffi` — Thin C FFI wrappers

```xiom
fn extern_c(name: Str) -> Int
fn alloc(size: Int) -> *UInt8
fn free(ptr: *UInt8)
fn memcpy(dest: *UInt8, src: *UInt8, size: Int)
fn size_of[T]() -> Int
fn align_of[T]() -> Int
```

---

### 8.27 `cell` — Interior mutability

```xiom
type Cell[T]    = { value: T; }
type RefCell[T] = { value: T; borrows: Int; }
type Ref[T]     = { cell: RefCell[T]; }
type RefMut[T]  = { cell: RefCell[T]; }

fn Cell.new[T](value: T) -> Cell[T]
fn Cell.get[T](self) -> T
fn Cell.set[T](self, value: T)
fn Cell.replace[T](self, value: T) -> T
fn Cell.swap[T](self, other: &Cell[T])
fn RefCell.new[T](value: T) -> RefCell[T]
fn RefCell.borrow[T](self) -> Ref[T]
fn RefCell.borrow_mut[T](self) -> RefMut[T]
fn RefCell.try_borrow[T](self) -> Option[Ref[T]]
fn RefCell.try_borrow_mut[T](self) -> Option[RefMut[T]]
fn RefCell.replace[T](self, value: T) -> T
fn Ref.get[T](self) -> T
fn RefMut.get[T](self) -> T
fn RefMut.set[T](self, value: T)
```

---

### 8.28 `rc` — Reference counting

```xiom
type RcInner[T] = { strong: Int; weak: Int; value: T; }
type Rc[T]      = { ptr: *RcInner[T]; }
type Weak[T]    = { ptr: *RcInner[T]; }

fn Rc.new[T](value: T) -> Rc[T]
fn Rc.clone[T](self) -> Rc[T]
fn Rc.strong_count[T](self) -> Int
fn Rc.weak_count[T](self) -> Int
fn Rc.get[T](self) -> T
fn Rc.ptr_eq[T, U](self, other: &Rc[U]) -> Bool
fn Rc.downgrade[T](self) -> Weak[T]
fn Rc.unwrap_or_clone[T: Clone](self) -> T
fn Rc.drop[T](self)
fn Weak.upgrade[T](self) -> Option[Rc[T]]
fn Weak.strong_count[T](self) -> Int
fn Weak.weak_count[T](self) -> Int
fn Weak.drop[T](self)
```

---

### 8.29 `serialize` — JSON serialization

```xiom
interface Serialize   { fn serialize(self) -> Result[Str, SerializeError]; fn serialize_json(self) -> Result[Str, SerializeError]; fn serialize_bytes(self) -> Result[Vec[UInt8], SerializeError]; }
interface Deserialize { fn deserialize(data: Str) -> Result[Self, SerializeError]; fn deserialize_json(data: Str) -> Result[Self, SerializeError]; fn deserialize_bytes(data: Vec[UInt8]) -> Result[Self, SerializeError]; }
type SerializeError = { kind: Int; message: Str; path: Str; line: Int; col: Int; }
type JsonValue = enum {
  Null,
  Bool(value: Bool),
  Number(value: Float64),
  String(value: Str),
  Array(items: Vec[JsonValue]),
  Object(entries: Map[Str, JsonValue]),
}

fn SerializeError.format_error() -> Str
fn detect_format(data: &Vec[UInt8]) -> Str
fn is_valid_json(data: Str) -> Bool
fn is_valid_bytes(data: &Vec[UInt8]) -> Bool
fn json_string(s: Str) -> Str
fn json_number(n: Float64) -> Str
fn json_bool(b: Bool) -> Str
fn json_null() -> Str
fn json_array(items: Vec[Str]) -> Str
fn json_object(pairs: Vec[(Str, Str)]) -> Str
fn to_json[T: Serialize](value: T) -> Result[Str, SerializeError]
fn from_json[T: Deserialize](s: Str) -> Result[T, SerializeError]
fn json_parse(data: Str) -> Result[JsonValue, SerializeError]
fn parse_json(s: Str) -> Result[JsonValue, SerializeError]
fn JsonValue.to_str(self) -> Str
fn JsonValue.get(self, key: Str) -> Option[JsonValue]
fn JsonValue.index(self, i: Int) -> Option[JsonValue]
fn little_endian() -> Bool
fn big_endian() -> Bool
```

---

### 8.30 `crypto` — Hashing, HMAC, AES, RSA, KDFs

```xiom
type KeyPair = { public: Vec[UInt8]; private: Vec[UInt8]; }

fn sha256(data: &Vec[UInt8]) -> Vec[UInt8]
fn sha256_accelerated(data: &Vec[UInt8]) -> Vec[UInt8]
fn sha256_hex(data: &Vec[UInt8]) -> Str
fn sha512(data: &Vec[UInt8]) -> Vec[UInt8]
fn md5(data: &Vec[UInt8]) -> Vec[UInt8]
fn blake3(data: &Vec[UInt8]) -> Vec[UInt8]
fn hmac_sha256(key: &Vec[UInt8], data: &Vec[UInt8]) -> Vec[UInt8]
fn aes_encrypt(key: &Vec[UInt8], plaintext: &Vec[UInt8]) -> Result[Vec[UInt8], Str]
fn aes_decrypt(key: &Vec[UInt8], ciphertext: &Vec[UInt8]) -> Result[Vec[UInt8], Str]
fn aes_encrypt_gcm(key: &Vec[UInt8], nonce: &Vec[UInt8], plaintext: &Vec[UInt8], aad: &Vec[UInt8]) -> Result[(Vec[UInt8], Vec[UInt8]), Str]
fn aes_decrypt_gcm(key: &Vec[UInt8], nonce: &Vec[UInt8], ciphertext: &Vec[UInt8], tag: &Vec[UInt8], aad: &Vec[UInt8]) -> Result[Vec[UInt8], Str]
fn generate_rsa_keypair(bits: Int) -> Result[KeyPair, Str]
fn rsa_encrypt(public_key: &Vec[UInt8], data: &Vec[UInt8]) -> Result[Vec[UInt8], Str]
fn rsa_decrypt(private_key: &Vec[UInt8], data: &Vec[UInt8]) -> Result[Vec[UInt8], Str]
fn rsa_sign(private_key: &Vec[UInt8], data: &Vec[UInt8]) -> Result[Vec[UInt8], Str]
fn rsa_verify(public_key: &Vec[UInt8], data: &Vec[UInt8], signature: &Vec[UInt8]) -> Result[Bool, Str]
fn pbkdf2(password: &Str, salt: &Vec[UInt8], iterations: Int, key_len: Int) -> Vec[UInt8]
fn argon2(password: &Str, salt: &Vec[UInt8], memory: Int, iterations: Int, parallelism: Int) -> Vec[UInt8]
fn secure_random_bytes(count: Int) -> Vec[UInt8]
fn constant_time_compare(a: &Vec[UInt8], b: &Vec[UInt8]) -> Bool
```

---

### 8.31 `compress` — gzip, zlib, deflate, brotli, lz4, snappy

```xiom
interface Compressor { fn compress(self, data: &Vec[UInt8]) -> Result[Vec[UInt8], Str]; fn decompress(self, data: &Vec[UInt8]) -> Result[Vec[UInt8], Str]; }
type GzipCompressor = { level: Int; }

fn GzipCompressor.new() -> GzipCompressor
fn GzipCompressor.with_level(level: Int) -> GzipCompressor
fn gzip_compress(data: &Vec[UInt8]) -> Result[Vec[UInt8], Str]
fn gzip_compress_level(data: &Vec[UInt8], level: Int) -> Result[Vec[UInt8], Str]
fn gzip_decompress(data: &Vec[UInt8]) -> Result[Vec[UInt8], Str]
fn deflate_compress(data: &Vec[UInt8]) -> Result[Vec[UInt8], Str]
fn deflate_decompress(data: &Vec[UInt8]) -> Result[Vec[UInt8], Str]
fn deflate_compress_level(data: &Vec[UInt8], level: Int) -> Result[Vec[UInt8], Str]
fn zlib_compress(data: &Vec[UInt8]) -> Result[Vec[UInt8], Str]
fn zlib_compress_level(data: &Vec[UInt8], level: Int) -> Result[Vec[UInt8], Str]
fn zlib_decompress(data: &Vec[UInt8]) -> Result[Vec[UInt8], Str]
fn brotli_compress(data: &Vec[UInt8]) -> Result[Vec[UInt8], Str]
fn brotli_compress_level(data: &Vec[UInt8], quality: Int) -> Result[Vec[UInt8], Str]
fn brotli_decompress(data: &Vec[UInt8]) -> Result[Vec[UInt8], Str]
fn lz4_compress(data: &Vec[UInt8]) -> Result[Vec[UInt8], Str]
fn lz4_decompress(data: &Vec[UInt8]) -> Result[Vec[UInt8], Str]
fn snappy_compress(data: &Vec[UInt8]) -> Result[Vec[UInt8], Str]
fn snappy_decompress(data: &Vec[UInt8]) -> Result[Vec[UInt8], Str]
fn compression_ratio(original: Int, compressed: Int) -> Float64
fn is_compressed(data: &Vec[UInt8]) -> Bool
fn detect_format(data: &Vec[UInt8]) -> Str
```

---

### 8.32 `encoding` — base64, hex, URL, UTF-8

```xiom
fn base64_encode(data: &Vec[UInt8]) -> Str
fn base64_decode(encoded: Str) -> Result[Vec[UInt8], Str]
fn base64url_encode(data: &Vec[UInt8]) -> Str
fn base64url_decode(encoded: Str) -> Result[Vec[UInt8], Str]
fn hex_encode(data: &Vec[UInt8]) -> Str
fn hex_decode(encoded: Str) -> Result[Vec[UInt8], Str]
fn hex_encode_upper(data: &Vec[UInt8]) -> Str
fn url_encode(data: Str) -> Str
fn url_decode(encoded: Str) -> Result[Str, Str]
fn percent_encode(data: Str) -> Str
fn percent_decode(encoded: Str) -> Result[Str, Str]
fn utf8_encode(s: Str) -> Vec[UInt8]
fn utf8_decode(data: &Vec[UInt8]) -> Result[Str, Str]
fn utf8_valid(data: &Vec[UInt8]) -> Bool
fn utf8_char_len(first_byte: UInt8) -> Int
fn binary_to_text(data: &Vec[UInt8], format: Int) -> Str
fn text_to_binary(text: Str, format: Int) -> Result[Vec[UInt8], Str]
```

---

### 8.33 `regex` — Regular expressions

Supported: `.  *  +  ?  ^  $  [abc]  [a-z]  [^abc]  \d \w \s  \D \W \S`.
```xiom
type Regex    = { pattern: Str; compiled: Int; }
type Match    = { start: Int; end: Int; text: Str; }
type Captures = { groups: Vec[Option[Match]]; }

fn Regex.new(pattern: Str) -> Result[Regex, Str]
fn Regex.is_match(self, text: Str) -> Bool
fn Regex.find(self, text: Str) -> Option[Match]
fn Regex.find_all(self, text: Str) -> Vec[Match]
fn Regex.captures(self, text: Str) -> Option[Captures]
fn Regex.replace(self, text: Str, replacement: Str) -> Str
fn Regex.replace_all(self, text: Str, replacement: Str) -> Str
fn Regex.split(self, text: Str) -> Vec[Str]
fn Regex.match_count(self, text: Str) -> Int
fn Captures.get(self, index: Int) -> Option[Match]
fn Captures.get_named(self, name: Str) -> Option[Match]
fn Captures.len(self) -> Int
fn regex_escape(pattern: Str) -> Str
fn is_valid_regex(pattern: Str) -> Bool
```

---

### 8.34 `rand` — Random numbers & distributions

```xiom
interface Rng { fn next_int(self) -> Int; fn next_float(self) -> Float64; fn next_bytes(self, buf: &mut Vec[UInt8]); }
type StdRng = { state: Int; }

fn StdRng.new() -> StdRng
fn StdRng.from_seed(seed: Int) -> StdRng
fn random() -> Float64
fn random_int(min: Int, max: Int) -> Int
fn random_float(min: Float64, max: Float64) -> Float64
fn random_bool() -> Bool
fn random_bytes(count: Int) -> Vec[UInt8]
fn sample_uniform(min: Float64, max: Float64) -> Float64
fn sample_normal(mean: Float64, stddev: Float64) -> Float64
fn sample_exponential(lambda: Float64) -> Float64
fn sample_bernoulli(p: Float64) -> Bool
fn sample_binomial(n: Int, p: Float64) -> Int
fn sample_poisson(lambda: Float64) -> Int
fn sample_gamma(shape: Float64, scale: Float64) -> Float64
fn sample_beta(alpha: Float64, beta: Float64) -> Float64
fn shuffle[T](items: &mut Vec[T])
fn pick[T](items: &Vec[T]) -> Option[&T]
fn pick_n[T](items: &Vec[T], n: Int) -> Vec[&T]
fn weighted_pick[T](items: &Vec[T], weights: &Vec[Float64]) -> Option[&T]
fn uuid_v4() -> Str
fn uuid_v7() -> Str
fn seed_from_entropy()
fn seed_from_time()
fn seed_from_value(seed: Int)
```

---

### 8.35 `log` — Structured logging

```xiom
type LogLevel = enum { Trace, Debug, Info, Warn, Error, Fatal }
type LogEntry = { level: LogLevel; message: Str; file: Str; line: Int; timestamp: Int; data: Map[Str, Str]; }

fn trace(msg: Str)
fn debug(msg: Str)
fn info(msg: Str)
fn warn(msg: Str)
fn error(msg: Str)
fn fatal(msg: Str)
fn trace_with(msg: Str, data: Map[Str, Str])
fn debug_with(msg: Str, data: Map[Str, Str])
fn info_with(msg: Str, data: Map[Str, Str])
fn warn_with(msg: Str, data: Map[Str, Str])
fn error_with(msg: Str, data: Map[Str, Str])
fn set_level(level: LogLevel)
fn get_level() -> LogLevel
fn set_output(file: Str) -> Result[Unit, Str]
fn set_output_json(enabled: Bool)
fn set_output_color(enabled: Bool)
fn entries_since(instant: Instant) -> Vec[LogEntry]
fn clear_log()
```

---

### 8.36 `test` — Contract-aware test framework

```xiom
type TestResult      = { passed: Bool; name: Str; message: Str; contract_failures: Vec[ContractFailure]; duration_ms: Int; }
type ContractFailure = { clause: Str; expression: Str; values: Str; location: Str; }

fn assert(condition: Bool, name: Str) -> TestResult
fn assert_eq[T: Eq](expected: T, actual: T, name: Str) -> TestResult
fn assert_ne[T: Eq](expected: T, actual: T, name: Str) -> TestResult
fn assert_lt[T: Ord](left: T, right: T, name: Str) -> TestResult
fn assert_gt[T: Ord](left: T, right: T, name: Str) -> TestResult
fn assert_contains(haystack: Str, needle: Str, name: Str) -> TestResult
fn assert_ok[T, E](result: Result[T, E], name: Str) -> TestResult
fn assert_err[T, E](result: Result[T, E], name: Str) -> TestResult
fn assert_some[T](option: Option[T], name: Str) -> TestResult
fn assert_none[T](option: Option[T], name: Str) -> TestResult
fn assert_contract[T](value: T, predicate: fn(&T) -> Bool, name: Str) -> TestResult
fn run(test: fn() -> TestResult) -> Int
fn run_all(tests: Vec[fn() -> TestResult]) -> Int
fn run_filtered(tests: Vec[fn() -> TestResult], filter: Str) -> Int
fn format_results(results: Vec[TestResult]) -> Str
fn format_results_json(results: Vec[TestResult]) -> Str
fn bench(name: Str, f: fn()) -> TestResult
```

---

### 8.37 `bench` — Benchmarking

```xiom
type BenchResult = { name: Str; iterations: Int; total_ns: Int; mean_ns: Int; min_ns: Int; max_ns: Int; stddev_ns: Int; }

fn run_bench(name: Str, f: fn()) -> BenchResult
fn run_bench_n(name: Str, iterations: Int, f: fn()) -> BenchResult
fn compare(a: BenchResult, b: BenchResult) -> Str
fn black_box[T](value: T) -> T
```

---

### 8.38 `contracts` — Contract introspection & coverage

```xiom
type ContractClause      = { ... }
type FunctionContracts   = { ... }
type TypeContracts       = { ... }
type ContractIndex       = { ... }
type ContractCheckResult = { ... }

fn verify_invariants[T](value: &T) -> Vec[ContractCheckResult]
fn verify_function_contracts(func: Str, args: Map[Str, Str]) -> Vec[ContractCheckResult]
fn check_invariant[T](value: &T, invariant: Str) -> ContractCheckResult
fn build_contract_index() -> ContractIndex
fn get_function_contracts(name: Str) -> Option[Vec[FunctionContracts]]
fn get_type_contracts(name: Str) -> Option[Vec[TypeContracts]]
fn find_functions_using_type(type_name: Str) -> Vec[Str]
fn find_invariants_using_field(type_name: Str, field_name: Str) -> Vec[ContractClause]
fn export_contracts_json() -> Str
fn export_contracts_markdown() -> Str
fn export_contracts_openapi() -> Str
fn reset_contract_coverage()
fn record_contract_hit(clause: ContractClause, input_values: Map[Str, Str])
fn get_contract_coverage() -> Map[Str, Bool]
fn get_uncovered_contracts() -> Vec[ContractClause]
fn coverage_percentage() -> Float64
fn can_compose(f_requires: Vec[ContractClause], g_ensures: Vec[ContractClause]) -> Str
fn verify_chain(fns: Vec[Str]) -> Result[Unit, Vec[ContractCheckResult]]
fn total_contracts() -> Int
fn total_requires() -> Int
fn total_ensures() -> Int
fn total_invariants() -> Int
fn functions_with_contracts() -> Int
fn types_with_invariants() -> Int
fn contract_density() -> Float64
```

---

### 8.39 `reflect` — Runtime type information

```xiom
type TypeId    = { id: Int; }
type TypeInfo  = { ... }
type FieldInfo = { ... }
interface Any  { ... }

fn type_count() -> Int
fn type_name_by_id(id: Int) -> Str
fn type_id_by_name(name: Str) -> Int
fn type_field_count(id: Int) -> Int
fn TypeId.of[T]() -> TypeId
fn type_name[T]() -> Str
fn type_size[T]() -> Int
fn type_align[T]() -> Int
fn downcast_ref[T: Any](value: &dyn Any) -> Option[&T]
fn downcast_mut[T: Any](value: &mut dyn Any) -> Option[&mut T]
fn reflect_type[T]() -> TypeInfo
fn type_info_by_name(name: Str) -> Option[TypeInfo]
fn all_types() -> Vec[TypeInfo]
```

---

### C FFI

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

Standard libc functions link automatically. The XIOM C runtime (`stdlib/runtime/*.c`) provides the `xiom_*` helpers used by `io`, `os`, `sync`, `thread`, `net`, and `async`, and is linked by `xiom` on every native build — no manual setup needed. Use `--link`, `--link-path`, and `--c-source` (section 11) to link additional native libraries.

---

### 8.40 `vulkan` — GPU Graphics & Compute (Ecosystem Package)

First-party Vulkan GPU bindings for XIOM (`packages/xiom-vulkan/`). Uses a flat C-ABI bridge (`xiom_vk_bridge.c`) that wraps Vulkan + GLFW into a compact API. All GPU resources are opaque handles validated by magic numbers. Import with `use xiom.vulkan;`.

**Prerequisites:** Vulkan SDK >= 1.3 (`VULKAN_SDK`), GLFW 3.4 (`GLFW_DIR`), LLVM/clang, Rust toolchain. Build via `packages/xiom-vulkan/build.ps1` (Windows) or `build.sh` (Linux/macOS).

```powershell
# Build 2D demo (default)
.\packages\xiom-vulkan\build.ps1
# Build and run 3D cube
.\packages\xiom-vulkan\build.ps1 -Target demo3d -Run
# GPU particle fountain
.\packages\xiom-vulkan\build.ps1 -Target particles -Run
```

Build pipeline: `GLSL → glslc → SPIR-V header → clang → bridge.obj → xiom --c-source bridge.obj --link vulkan-1 --link glfw3`

#### Architecture

```
XIOM Application
    │
xiom.vulkan  (safe wrappers with contracts)
    │
extern "C" FFI  (xvk_* flat C bridge)
    │
xiom_vk_bridge.c  (~4000 lines C)
    │
vulkan-1.dll + glfw3.dll  (native)
```

#### Lifecycle API

```xiom
fn create_app(title: Str, width: Int, height: Int) -> Result[Int, Str]
  requires: width > 0; requires: height > 0

fn destroy_app(app: Int)
  requires: app != 0

fn should_close(app: Int) -> Bool
fn poll(app: Int)
fn now() -> Float64
fn device_type(app: Int) -> Int
fn last_error() -> Str
fn get_framebuffer_size(app: Int) -> (Int, Int)
```

#### Frame API

```xiom
fn set_clear_color(app: Int, r: Float32, g: Float32, b: Float32)
  // Must be called BEFORE begin_frame.

fn begin_frame(app: Int) -> Int
  // Returns: 1=OK, 0=skip (resize), -1=fatal

fn end_frame(app: Int)
```

#### Drawing API (Legacy, Hardcoded Pipelines)

```xiom
fn draw_triangle_2d(app: Int, r: Float32, g: Float32, b: Float32)
fn draw_quad_2d(app: Int, cx: Float32, cy: Float32, hw: Float32, hh: Float32, r: Float32, g: Float32, b: Float32)
fn draw_cube_3d(app: Int, angle: Float32)
fn draw_cube_3d_at(app: Int, angle: Float32, px: Float32, py: Float32, pz: Float32, scale: Float32)
fn particles_enable(app: Int, count: Int) -> Bool
fn draw_particles(app: Int, dt: Float32)
```

#### Buffer API

```xiom
fn buffer_create(app: Int, size: Int, usage: Int, memory: Int) -> Result[Int, Str]
  // usage: 1=vertex, 2=index, 4=uniform, 8=storage, 16=transfer-src, 32=transfer-dst
  // memory: 1=device-local, 2=host-visible+coherent, 3=host-visible+cached

fn buffer_destroy(app: Int, buf: Int)
fn buffer_size(app: Int, buf: Int) -> Int
fn buffer_map(app: Int, buf: Int) -> Bool
fn buffer_unmap(app: Int, buf: Int)
fn buffer_write_float(app: Int, buf: Int, offset: Int, data: Vec[Float32])
fn buffer_read_float(app: Int, buf: Int, offset: Int, count: Int) -> Vec[Float32]
```

#### Image & Texture API

```xiom
fn image_create_2d(app: Int, width: Int, height: Int, format: Int, usage: Int, mip_levels: Int) -> Result[Int, Str]
  // format: 1=RGBA8_UNORM, 2=RGBA8_SRGB, 3=RGBA32_SFLOAT, 4=R32_SFLOAT, 5=D32_SFLOAT
  // usage: 1=sampled, 2=color-attachment, 4=depth, 8=transfer-src, 16=transfer-dst, 32=storage

fn image_destroy(app: Int, img: Int)
fn image_view_create(app: Int, img: Int, format: Int, aspect: Int) -> Result[Int, Str]
fn image_view_destroy(app: Int, view: Int)
fn image_transition(app: Int, img: Int, old_layout: Int, new_layout: Int)
  // layout: 0=undefined, 1=color-attachment, 2=shader-read, 3=transfer-src, 4=transfer-dst, 5=depth, 6=present
```

#### Sampler API

```xiom
fn sampler_create(app: Int, filter: Int, address_u: Int, address_v: Int, mip_mode: Int, max_lod: Float32) -> Result[Int, Str]
  // filter: 0=nearest, 1=linear
  // address: 0=repeat, 1=clamp-edge, 2=clamp-border
  // mip_mode: 0=nearest, 1=linear

fn sampler_destroy(app: Int, sampler: Int)
```

#### Shader Module API

```xiom
fn shader_create(app: Int, code: Vec[UInt32]) -> Result[Int, Str]
fn shader_create_named(app: Int, name: Str) -> Result[Int, Str]
  // Names: "triangle_vert", "triangle_frag", "cube_vert", "cube_frag",
  //   "quad_vert", "quad_frag", "particle_vert", "particle_frag",
  //   "particle_render_vert", "particle_render_frag", "compute_particles",
  //   "texture_quad_vert", "texture_quad_frag", "uniform_cube_vert", "uniform_cube_frag"

fn shader_destroy(app: Int, shader: Int)
```

#### Pipeline Layout & Descriptor Set Layout API

```xiom
fn pipeline_layout_create(app: Int, push_size: Int, push_stages: Int, desc_layouts: Vec[Int]) -> Result[Int, Str]
  // push_stages: 1=vertex, 2=fragment, 3=both, 4=compute

fn pipeline_layout_destroy(app: Int, layout: Int)

fn desc_set_layout_create(app: Int, bindings: Vec[Int32]) -> Result[Int, Str]
  // bindings: flat array [binding, type, count, stage, ...] per binding
  //   type: 0=uniform-buffer, 1=storage-buffer, 2=combined-image-sampler
  //   stage: 1=vertex, 2=fragment, 3=both, 4=compute

fn desc_set_layout_destroy(app: Int, layout: Int)
```

#### Pipeline API

```xiom
fn pipeline_create_graphics(app: Int,
    topology: Int,       // 0=triangle-list, 1=point-list, 2=line-list
    cull_mode: Int,      // 0=none, 1=front, 2=back
    depth_test: Bool, depth_write: Bool, blend: Bool,
    vert_shader: Int, frag_shader: Int,
    layout: Int, render_pass: Int,
    bindings: Vec[Int32],   // flat [binding, stride, input_rate] repeated
    attributes: Vec[Int32]  // flat [location, binding, format, offset] repeated
  ) -> Result[Int, Str]

fn pipeline_create_compute(app: Int, shader: Int, layout: Int) -> Result[Int, Str]
fn pipeline_destroy(app: Int, pipeline: Int)
```

#### Descriptor Pool & Set API

```xiom
fn desc_pool_create(app: Int, pool_sizes: Vec[Int32], max_sets: Int) -> Result[Int, Str]
  // pool_sizes: [type, count, ...] pairs
fn desc_pool_destroy(app: Int, pool: Int)
fn desc_set_allocate(app: Int, pool: Int, layout: Int) -> Result[Int, Str]
fn desc_set_write_buffer(app: Int, set: Int, binding: Int, buf: Int, offset: Int, range: Int, desc_type: Int)
fn desc_set_write_image(app: Int, set: Int, binding: Int, sampler: Int, image_view: Int)
```

#### Render Pass & Framebuffer API

```xiom
fn render_pass_create(app: Int, color_formats: Vec[Int32], depth_format: Int) -> Result[Int, Str]
  // color_formats: [format, load_op, store_op, final_layout] repeated

fn render_pass_destroy(app: Int, rp: Int)
fn framebuffer_create(app: Int, render_pass: Int, attachments: Vec[Int], width: Int, height: Int) -> Result[Int, Str]
fn framebuffer_destroy(app: Int, fb: Int)
```

#### Command Recording API (between begin_frame/end_frame)

```xiom
fn cmd_bind_vertex_buffer(app: Int, binding: Int, buf: Int, offset: Int)
fn cmd_bind_index_buffer(app: Int, buf: Int, offset: Int, index_type: Int)  // 0=uint16, 1=uint32
fn cmd_bind_pipeline(app: Int, pipeline: Int)
fn cmd_bind_descriptor_sets(app: Int, layout: Int, first_set: Int, sets: Vec[Int])
fn cmd_push_constants_float(app: Int, layout: Int, stages: Int, offset: Int, data: Vec[Float32])
fn cmd_draw(app: Int, vertex_count: Int, instance_count: Int, first_vertex: Int, first_instance: Int)
fn cmd_draw_indexed(app: Int, index_count: Int, instance_count: Int, first_index: Int, vertex_offset: Int, first_instance: Int)
```

#### Multi-Pass & Compute API

```xiom
fn begin_custom_pass(app: Int, render_pass: Int, framebuffer: Int, width: Int, height: Int, r: Float32, g: Float32, b: Float32) -> Int
fn end_custom_pass(app: Int) -> Int
fn compute_dispatch(app: Int, pipeline: Int, layout: Int, x: Int, y: Int, z: Int)
```

#### Offscreen API (headless testing)

```xiom
fn offscreen_create(width: Int, height: Int) -> Result[Int, Str]
fn offscreen_render_triangle(app: Int, r: Float32, g: Float32, b: Float32) -> Bool
fn offscreen_pixel(app: Int, x: Int, y: Int) -> Int       // 0xRRGGBBAA
fn offscreen_hash(app: Int) -> Int                          // FNV-1a of framebuffer
fn offscreen_destroy(app: Int)
```

#### Convenience Wrapper (`xiom.vulkan.wrapper` in `src/wrapper.xi`)

```xiom
type VulkanApp = { handle: Int; width: Int; height: Int; }

fn VulkanApp.new(title: Str, width: Int, height: Int) -> Result[VulkanApp, Str]
fn VulkanApp.is_open() -> Bool
fn VulkanApp.frame_2d(r: Float32, g: Float32, b: Float32)
fn VulkanApp.frame_3d(angle: Float32)
fn VulkanApp.frame_particles(dt: Float32)
fn VulkanApp.close()
```

#### Complete XIOM Program (Particles Demo)

```xiom
module xiom.vulkan.demo_particles
use xiom.io;
use xiom.vulkan;

fn main() -> Int {
  let app = create_app("XIOM Vulkan — Particle Fountain", 800, 600);
  match app {
    Err(e) => { io.println(e); return 1; }
    Ok(a) => {
      particles_enable(a, 3000);
      var last = now();
      while !should_close(a) {
        poll(a);
        let t = now();
        let dt = (t - last) as Float32;
        last = t;
        set_clear_color(a, 0.02, 0.02, 0.05);
        let status = begin_frame(a);
        if status == 1 {
          draw_particles(a, dt);
          end_frame(a);
        } elif status == -1 { break; }
      }
      destroy_app(a);
      return 0;
    }
  }
}
```

#### Available Demos

| Target | File | Description |
|--------|------|-------------|
| `demo2d` | `examples/demo_2d.xi` | 2D triangle with cycling sinusoidal colors |
| `demo3d` | `examples/demo_3d.xi` | Rotating 3D cube |
| `particles` | `examples/demo_particles.xi` | 3000-particle fountain |
| `shapes` | `examples/demo_shapes.xi` | 4 colored quads + rainbow triangle |
| `cubes` | `examples/demo_cubes.xi` | 3x3 grid of spinning cubes |
| `vertex_buffer` | `examples/demo_vertex_buffer.xi` | Vertex + index buffer workflow |
| `test` | `tests/test_vulkan.xi` | Headless CI-safe tests |

#### Embedded Shaders (compiled offline by glslc)

The C bridge embeds 15 SPIR-V shader arrays in `xvk_shaders_generated.h`. Create shader modules at runtime via `shader_create_named(app, "name")`.

**Pipeline configurations (hardcoded for legacy draw calls):**

| Pipeline | Shaders | Topology | Depth | Culling |
|----------|---------|----------|-------|---------|
| 2D triangle | `triangle_vert`, `triangle_frag` | triangle list | off | CW front, back cull |
| 3D cube | `cube_vert`, `cube_frag` | triangle list | on | CW front, back cull |
| 2D quad | `quad_vert`, `quad_frag` | triangle list | off | CW front, back cull |
| Particle | `particle_vert`, `particle_frag` | point list | off | none |

#### Compiler Flags for Vulkan

| Flag | Purpose |
|------|---------|
| `--link vulkan-1` | Link Vulkan loader library |
| `--link glfw3` | Link GLFW library |
| `--link-path <dir>` | Library search path |
| `--c-source <file>` | Compile + link C source/object file |

#### Important Rules

- **Clear color timing**: `set_clear_color` MUST be called BEFORE `begin_frame`. The clear values are consumed at render-pass-begin time.
- **Winding order**: All shaders use CW winding with `VK_FRONT_FACE_COUNTER_CLOCKWISE`. CCW triangles are back-face culled.
- **Handle validation**: All handles use magic-number validation. Zero handles are rejected.
- **Push constants**: Maximum 128 bytes per call.
- **Multi-pass**: `begin_custom_pass` ends the default render pass. `end_custom_pass` re-begins it.
- **Compute dispatch**: Automatically ends the active render pass before dispatching.

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

## 11. Compiler CLI (`xiom`)

```
USAGE:
  xiom [OPTIONS] <source.xi> [more.xi ...]
  xiom doctor             Check for required toolchain dependencies
  xiom build              Build a project (directory containing package.xi)
  xiom pkg install <name> Install a package from the registry

OPTIONS:
  --help                Show help message and exit
  --version             Print compiler version and exit
  -o <output>           Output binary path (default per target: a.exe / a.wasm / a.out)
  --run                 Compile and run, then print the exit code (native target only)
   --emit-ir             Print LLVM IR to stdout (no binary produced)
   --emit-tokens         Print token stream to stdout (lexer output, for debugging/playground)
  --target <target>     Target backend: native (default), wasm, arm, riscv
  --no-contracts        Disable contract runtime checks (strips requires/ensures/invariant guards)
  --runtime-contracts   Force contract checks in release builds (overrides --no-contracts)
  --sanitize=<type>     Enable sanitizer: address, undefined, leak, thread
  --stack-protector     Enable stack canaries
  --diagnostics=json    Emit diagnostics as JSON (type/borrow/codegen errors, or {"status":"ok"})
  --dump-contracts      Print the program's contract index as JSON and exit
  --verify              Generate SMT-LIB contract verification output (to stdout)
  --verify-output <f>   Write SMT-LIB verification output to file <f>
  --graph               Print dependency graph (DOT format)
  --graph=mermaid       Print dependency graph (Mermaid format)
  --parallel            Enable parallel compilation
  --jobs <N>            Set number of parallel compilation jobs
  --timeout <seconds>   Compilation timeout watchdog (default: 60; 0 disables)
  --max-memory-mb <N>   Memory budget in MB; abort if exceeded (default: 0 = disabled)
  --link <name>         Link a native library (repeatable; emits -l<name>, e.g. --link vulkan-1)
  --link-path <dir>     Add a library search path (repeatable; emits -L<dir>)
  --c-source <file>     Link an extra C or object file (repeatable)

SUBCOMMANDS:
  doctor                Check for required toolchain dependencies (clang, opt, nasm)
  build                 Build an entire project directory (looks for package.xi)
  pkg install <name>    Install a package from the XIOM package registry
  doc --html            Generate HTML documentation from source
  run <file.xi>         JIT/scripting execution — run a .xi script immediately
  run -e "<code>"       Execute inline XIOM code
  run -                 Read script from stdin and execute
  run --watch <file>    Watch a script file and re-run on changes
  --standalone <file>   Convert a script to a standalone production binary (-o <out>)
  --scaffold            With --standalone: also create a project directory structure
```

### 11.1 Scripting Mode (`xiom run`)

> **IMPORTANT:** `xiom run` does NOT relax type checking. All XIOM type rules apply
> identically in scripting mode and AOT compilation. The only differences are:
> 1. Auto-added `use xiom.io;` (if not already present)
> 2. Auto-wrapped `fn main() { ... }` around top-level code
> 3. Shebang (`#!`) line is skipped
>
> `io.println(5 + 3)` is a type error in ALL modes — use `io.println((5+3).to_str())`.

XIOM supports a scripting mode where top-level code is automatically wrapped
in `fn main()` — no boilerplate required.

**Implicit main wrapping:**
```xiom
// myscript.xi — just write statements:
io.println("hello world");

// xiom run myscript.xi automatically wraps this as:
//   use xiom.io;
//   fn main() { io.println("hello world"); }
```

**Shebang support:**
```xiom
#!/usr/bin/env xiom
io.println("executable script!");
```
```bash
chmod +x myscript.xi
./myscript.xi  # or: xiom run myscript.xi
```

**Standalone binary:**
```bash
# Convert a script to a production binary
xiom --standalone myscript.xi -o mytool
./mytool

# With project scaffolding
xiom --standalone --scaffold myscript.xi
# Creates: myscript/
#   src/main.xi     (canonicalized script)
#   package.xi      (project manifest)
```

**Script cache:**
Repeated runs of the same script are instant — compiled binaries are
content-hash cached in `~/.xiom/jit/`.

**Watch mode:**
```bash
xiom run --watch myscript.xi
# Polls every 500ms, re-runs on file change. Ctrl+C to stop.
```

**Behavior notes**
- With no `-o`, no `--run`, and `--target native`, `xiom` prints LLVM IR to stdout (same as `--emit-ir`).
- Contracts are **enabled by default**; runtime guards trap via `@llvm.trap()` on violation. Use `--no-contracts` to strip them.
- Multiple source files are merged into one program (see section 17). Passing a directory containing `package.xi` loads the modules it lists; otherwise all `.xi` files in the directory are compiled.
- The `use xiom.*` standard library resolves automatically for any program (via the compiler's stdlib search path; override with the `XIOM_STDLIB` env var).

**Targets** (LLVM triple → default output)
| `--target` | Triple | Default output |
|------------|--------|----------------|
| `native` (default) | `x86_64-pc-windows-msvc` | `a.exe` |
| `wasm` | `wasm32-unknown-unknown` | `a.wasm` |
| `arm` | `aarch64-unknown-linux-gnu` | `a.out` |
| `riscv` | `riscv64gc-unknown-linux-gnu` | `a.out` |

**Toolchain dependencies**
- Required: `clang` (LLVM) — compiles IR to a native binary.
- Optional: `opt` (LLVM) — runs an `-O1` optimization pass over the IR.
- Optional: `nasm` — assembles hardware-accelerated crypto/memcpy runtime objects.

**Examples**
```bash
xiom source.xi                              # print LLVM IR (native, no -o/--run)
xiom --emit-tokens source.xi                 # lexer output: token stream
xiom --emit-ir source.xi                    # print LLVM IR explicitly
xiom -o prog.exe source.xi                  # compile to native binary
xiom --run source.xi                        # compile + run, print exit code
xiom --target wasm -o prog.wasm source.xi   # compile to WebAssembly
xiom --target arm -o prog.out source.xi     # cross-compile to aarch64
xiom --no-contracts -o prog.exe source.xi   # release build without contract guards
xiom --runtime-contracts -o prog.exe source.xi  # force contracts in release
xiom --diagnostics=json source.xi           # machine-readable diagnostics
xiom --dump-contracts source.xi             # contract index as JSON
xiom --verify source.xi                      # emit SMT-LIB for Z3
xiom --verify-output out.smt2 source.xi     # write SMT-LIB to a file
xiom --graph source.xi                      # dependency graph (DOT)
xiom --graph=mermaid source.xi             # dependency graph (Mermaid)
xiom --parallel --jobs 4 source.xi          # parallel compilation, 4 jobs
xiom --sanitize=address --run source.xi     # compile with address sanitizer
xiom --stack-protector -o prog.exe source.xi # enable stack canaries
xiom --timeout 120 --max-memory-mb 2048 big.xi
xiom --link vulkan-1 --link-path C:/VulkanSDK/lib -o app.exe app.xi
xiom --c-source glue.c -o app.exe app.xi
xiom --run src/main.xi src/types.xi src/utils.xi   # multi-file merge
xiom doctor                                 # check toolchain dependencies
xiom build                                  # build project from current directory
xiom pkg install xiom-vulkan               # install package from registry
xiom doc --html                             # generate HTML documentation

# Via cargo
cargo run -p xiom -- --run source.xi
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

## 15. Debugging

XIOM provides full source-level debugging through `xiom-dbg`, a Debug Adapter Protocol (DAP) server
compatible with VS Code, JetBrains IDEs, and any DAP-compliant editor. Under the hood it wraps
GDB/MI (or CDB on Windows) giving you breakpoints, stepping, variable inspection, and expression
evaluation on XIOM source code.

### 15.1 Compiling for Debug

Compile with debug symbols using the `-g` flag:

```bash
xiom -g -o app.exe main.xi
```

This emits DWARF debug information that GDB (and `xiom-dbg`) use for source-level debugging.
Without `-g`, breakpoints and variable names are not available.

### 15.2 Launching the Debugger

**VS Code / IDE (DAP mode):**

Add a launch configuration to `.vscode/launch.json`:

```json
{
    "type": "xiom",
    "request": "launch",
    "program": "${workspaceFolder}/app.exe",
    "stopOnEntry": true,
    "contractTraps": true,
    "cwd": "${workspaceFolder}"
}
```

The `"type": "xiom"` extension launches `xiom-dbg` as the DAP adapter.

**CLI (JSON API mode):**

`xiom-dbg` also exposes a structured JSON API for scripting and custom tooling:

```bash
xiom-dbg --json
```

Commands: `launch`, `set-breakpoint <file> <line>`, `delete-breakpoint <id>`,
`step`, `step-in`, `continue`, `stack`, `variables`, `registers`,
`memory <addr> <size>`, `evaluate <expr>`, `threads`, `terminate`, `help`.

**Fallback (raw GDB):**

Debug symbols are standard DWARF. Any GDB-compatible debugger works directly:

```bash
gdb ./app.exe
(gdb) break main.xi:10
(gdb) run
(gdb) print variable_name
```

### 15.3 Breakpoints

Source-level breakpoints are set by file and line number:

```xiom
// Set a breakpoint here (line 42 in main.xi)
fn calculate(x: Int) -> Int {
    return x * 2;  // <- breakpoint at main.xi:43
}
```

In VS Code: click the gutter next to the line number.
In JSON API: `set-breakpoint main.xi 43`
In GDB directly: `break main.xi:43`

**Breakpoint capabilities:**
- **Source-level**: Set at any executable line in a `.xi` file
- **Function entry**: `breakpoint set fn_name` — set at function prologue
- **Contract violation**: `contractTraps: true` in DAP mode catches `requires`/`ensures`/`invariant` violations as exception breakpoints
- **Conditional breakpoints**: Not yet supported (planned Phase 4)
- **Hit-count breakpoints**: Not yet supported (planned Phase 4)
- **Logpoints/tracepoints**: Not yet supported (planned Phase 4)

### 15.4 Stepping Commands

| Command | DAP | JSON API | GDB | Description |
|---------|-----|----------|-----|-------------|
| Continue | `continue` | `continue` | `c` | Resume execution until next breakpoint |
| Step over | `next` | `step` | `n` | Execute current line, stop at next line |
| Step into | `stepIn` | `step-in` | `s` | Enter function call on current line |
| Pause | `pause` | (not exposed) | Ctrl+C | Interrupt running program |

### 15.5 Variable Inspection

When stopped at a breakpoint, you can inspect:

**Local variables:**
```bash
# JSON API
>> variables

# GDB
(gdb) info locals
```

**Arbitrary expressions** (hover in VS Code, or explicit eval):
```bash
# JSON API
>> evaluate "items.len() + count"

# GDB
(gdb) print items.len() + count
```

**Memory inspection:**
```bash
# JSON API — read 256 bytes at address 0x7fff1234
>> memory 0x7fff1234 256

# GDB
(gdb) x/256xb 0x7fff1234
```

### 15.6 Contract Violation Debugging

When a `requires`, `ensures`, or `invariant` fails at runtime, the program traps
with file/line information. With `contractTraps: true` in the DAP launch config,
the debugger catches these as exception breakpoints, showing you exactly which
contract failed and where:

```
Contract violation: requires: b != 0.0
  at main.xi:15 in fn divide(a: Float64, b: Float64) -> Float64
```

### 15.7 Architecture

`xiom-dbg` has a dual-mode architecture:

```
VS Code / IDE
     │ DAP (stdin/stdout JSON)
     ▼
┌──────────┐     GDB/MI protocol      ┌─────┐
│ xiom-dbg │ ───────────────────────► │ GDB │ ──► target process
└──────────┘                           └─────┘
     │
     │ JSON API mode (--json)
     ▼
Custom GUI / scripts / AI agents
```

Two debugger backends:
- **GDB/MI** (primary, cross-platform): Full breakpoint, step, variable, memory support
- **CDB/WinDbg** (Windows): Basic breakpoints and stepping

---

## 16. Self-Hosting Note

The XIOM compiler is written in XIOM (`selfhost/` directory), compiled by the Rust bootstrap compiler. The Rust compiler is permanent — never deleted. When fixing compiler bugs, verify with differential tests: compile same program with Rust compiler AND XIOM compiler, diff the LLVM IR. They must be identical.

---

## 17. AI Coding Best Practices for XIOM

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

## 18. Multi-File Projects & Module System — AI Guide

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
xiom --run src/main.xi src/types.xi src/utils.xi src/lib.xi
```
The compiler merges all files into one program. Use this for projects with 2-30 files.

**Option B — Single file with lazy loading (catalog):**
```bash
xiom --run src/main.xi
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
| Multi-file merge (pass all files to xiom) | ✓ |
| ModuleCatalog lazy loading | ✓ |
| Cross-file type resolution | ✓ |
| Cross-file function calls | ✓ (via merge path) |
| 30+ file projects | ✓ (benchmark suite verified) |
| Package manager / `xiom pkg install` | ✓ |
| Build system / `xiom build` | ✓ |

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
