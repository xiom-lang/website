<!--
Copyright (c) 2026 XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
**XIOM**

Language Reference Specification

Version 0.3  --  Language Definition Only

This document defines the XIOM language. Applications are out of scope.

> **Revision note (2026-09-20).** The primitive type set below includes the
> 128-bit integers and the 128-bit float. The canonical spellings are
> exactly `Int128`, `UInt128` and `Float128` -- there are no language-level
> aliases (`i128`, `u128` and `I128` are ordinary user type names, and a
> bare `Float` is not an alias for `Float64`). Integer literals beyond
> `u64` are representable, so `Int128` / `UInt128` values need no suffix;
> `Float128` values are produced by conversion and have no literal suffix.

# Contents

1.  Overview & Core Goals
2.  Design Principles
3.  Formal Grammar (EBNF)
4.  Type System
5.  Memory Model
6.  Contract System
7.  Module System
8.  Concurrency
9.  Error Handling
10. Compiler Pipeline
11. Target Platforms
12. Error Message Philosophy
13. Complete Example Program
14. Comparison With Existing Languages
15. Build Roadmap

# 1. Overview & Core Goals

XIOM is a compiled, statically typed, memory-safe systems programming language. It is designed around three properties that no existing mainstream language provides simultaneously:

| SAFE | Ownership-based memory safety with no garbage collector and no runtime. Memory is freed deterministically when the owner leaves scope. |
| :---: | :---- |

| VERIFIED | Pre-conditions, post-conditions, and type invariants are first-class language constructs enforced by the compiler, not documentation conventions. |
| :---: | :---- |

| PRECISE | The grammar is unambiguous. Every construct has exactly one canonical form. There are no implicit coercions, no hidden allocations, and no surprising control flow. |
| :---: | :---- |

XIOM is designed for a world where code is increasingly written by AI and maintained by people who did not write the original. Contracts are machine-readable intent that the compiler enforces -- when AI generates a function, the contract layer catches what code review misses. The same mechanism protects human-written code against regressions, refactors, and team turnover.

XIOM compiles to native machine code via LLVM and to WebAssembly. It has zero-cost C interoperability. The compiler is intended to be self-hosted once the language reaches stability.

XIOM does not include a runtime, a garbage collector, or a virtual machine. It does not target any specific application domain. What you build with it is outside the scope of this document.

# 2. Design Principles

## 2.1  One Way To Write Each Thing

For every language construct there is exactly one canonical syntax. Formatting is part of the language specification. The canonical formatter is part of the compiler toolchain (`xiom fmt`). Code that deviates from canonical format is a warning by default and an error in strict mode.

## 2.2  Explicit Over Implicit

Nothing happens without being written. Memory allocation is visible. Type conversions are explicit. If a function can fail, its return type says so. If a value can be absent, its type says so. There are no default function arguments, no implicit constructors, and no implicit type widening.

## 2.3  Contracts Are Specification

Contracts (`requires`, `ensures`, `invariant`) are not assert statements. They are formal specifications that the compiler reasons about. At minimum they compile to checked runtime guards with precise error messages. Static proof via SMT solver is a planned later phase. A contract that is logically contradictory is a compile error.

## 2.4  No Null

The language has no null, nil, or undefined value. Absence of a value is expressed through `Option[T]`. The compiler enforces exhaustive handling of the absent case at every use site.

## 2.5  Errors Are Types

Functions that can fail return `Result[T, E]`. There are no exceptions and no panic-by-default. The `?` operator propagates errors explicitly. Unhandled error paths are compile errors, not runtime surprises.

## 2.6  Structural Interfaces

A type satisfies an interface if it has the required fields and methods. No `implements` declaration is needed. This allows composing types across module boundaries without shared ancestry.

## 2.7  Comptime Is The Only Metaprogramming

There is no preprocessor, no macro system, and no template language. All compile-time code generation is done through the `comptime` keyword, which marks expressions and blocks to be evaluated at compile time. Generics, reflection, and specialisation all flow through this single mechanism.

## 2.8  Derive -- Compiler-Generated Correctness

For common interfaces (`Eq`, `Clone`, `Display`, `Hash`, `Ord`), the programmer declares intent and the compiler generates the implementation. This eliminates a class of bugs where AI or humans write a structurally correct but semantically wrong implementation by hand. The generated code is always correct by construction.

# 3. Formal Grammar (EBNF)

The following grammar is the normative definition of XIOM syntax. Terminals are in double quotes or character classes. Nonterminals are in PascalCase.

### 3.1  Lexical Rules

```
Letter       = [a-zA-Z_]
Digit        = [0-9]
HexDigit     = [0-9a-fA-F]
Ident        = Letter { Letter | Digit }
IntLit       = Digit { Digit | "_" }
FloatLit     = Digit { Digit } "." Digit { Digit }
StrLit       = '"' { StrChar } '"'
StrChar      = any Unicode except '"' and newline | EscSeq
EscSeq       = "\\" ( "n" | "t" | "r" | "\\" | '"' | "u{" HexDigit+ "}" )
CharLit      = "'" ( StrChar ) "'"
Comment      = "//" { any } newline
BlockComment = "/*" { any } "*/"

Additional single-character tokens:  .  ,  ;  :  (  )  {  }  [  ]  @
  =  +  -  *  /  %  !  &  |  <  >  _
Keywords:  let  var  const  fn  return  if  elif  else  match  while  for  in
  spawn  async  await  comptime  module  use  pub  as  type  enum  interface
  derive  requires  ensures  invariant  true  false  self  result
  Some  None  Ok  Err  unsafe  extern  is
```

### 3.2  Top-Level

```
Program      = { TopDecl }
TopDecl      = [ "pub" ] ( TypeDecl | EnumDecl | InterfaceDecl | FnDecl | ConstDecl )
             | ModuleDecl | UseDecl
ModuleDecl   = "module" Ident "{" { TopDecl } "}"
UseDecl      = "use" ModulePath [ "as" Ident ] ";"
ModulePath   = Ident { "." Ident }
ConstDecl    = "const" Ident ":" Type "=" Expr ";"
```

### 3.3  Type Declarations

```
TypeDecl      = "type" Ident [ GenericParams ] "=" "{"
                  { FieldDecl }
                  { InvariantDecl }
                "}" [ DeriveClause ]
FieldDecl     = Ident ":" Type ";"
InvariantDecl = "invariant" ":" Expr ";"
DeriveClause  = "derive" "[" DeriveTrait { "," DeriveTrait } "]"
DeriveTrait   = "Eq" | "Clone" | "Display" | "Hash" | "Ord"
EnumDecl      = "enum" Ident [ GenericParams ] "{"
                  EnumVariant { "," EnumVariant }
                "}" [ DeriveClause ]
EnumVariant   = Ident [ "(" EnumVariantField { "," EnumVariantField } ")" ]
EnumVariantField = Ident ":" Type
InterfaceDecl = "interface" Ident [ GenericParams ] "{"
                  { FieldDecl | FnSignature }
                "}"

Note: `derived` fields (computed fields that auto-recompute when dependencies change)
are a planned Phase 2+ feature. Syntax: `Ident ":" Type "derived" "(" Expr ")" ";"`.
This feature is not part of the Phase 0 or Phase 1 grammar.
```

### 3.4  Functions

```
FnDecl        = [ "async" ] ( MethodDecl | FreeFnDecl )
MethodDecl    = "fn" TypeName "." Ident [ GenericParams ]
                "(" [ ParamList ] ")" [ "->" Type ]
                { ContractClause }
                Block
FreeFnDecl    = "fn" Ident [ GenericParams ]
                "(" [ ParamList ] ")" [ "->" Type ]
                { ContractClause }
                Block
FnSignature   = [ "async" ] "fn" Ident [ GenericParams ]
                "(" [ ParamList ] ")" [ "->" Type ]
                { ContractClause } ";"
ParamList     = Param { "," Param }
Param         = Ident ":" Type
ContractClause= ( "requires" | "ensures" ) ":" Expr
GenericParams = "[" Ident [ ":" InterfaceRef ] { "," Ident [ ":" InterfaceRef ] } "]"
InterfaceRef  = Ident { "+" Ident }
TypeName      = Ident   // refers to an existing type in scope
```

### 3.5  Types

```
Type          = RefType | TypeBase
RefType       = "&" [ "mut" ] TypeBase
TypeBase      = Ident [ GenericArgs ]
              | "Option" "[" Type "]"
              | "Result" "[" Type "," Type "]"
              | "Vec" "[" Type "]"
              | "Slice" "[" Type "]"
              | "Map" "[" Type "," Type "]"
              | "Set" "[" Type "]"
              | "(" Type { "," Type } ")"
              | "*" Type
              | "[" Expr "]" Type
GenericArgs   = "[" Type { "," Type } "]"
```

### 3.6  Patterns

```
Pattern       = Ident [ "(" PatternField { "," PatternField } ")" ]
              | "_"
              | LitPattern
PatternField  = Ident
LitPattern    = IntLit | FloatLit | StrLit | CharLit | "true" | "false"
              | "Some" "(" Pattern ")" | "None"
              | "Ok" "(" Pattern ")" | "Err" "(" Pattern ")"
```

### 3.7  Statements

```
Block         = "{" { Stmt } [ Expr ] "}"
Stmt          = LetStmt | VarStmt | AssignStmt | ReturnStmt
             | ExprStmt | IfStmt | MatchStmt | WhileStmt
             | ForStmt | SpawnStmt
LetStmt       = "let" Ident [ ":" Type ] "=" Expr ";"
VarStmt       = "var" Ident [ ":" Type ] "=" Expr ";"
AssignStmt    = Place "=" Expr ";"
ReturnStmt    = "return" [ Expr ] ";"
ExprStmt      = Expr ";"
IfStmt        = "if" Expr Block { "elif" Expr Block } [ "else" Block ]
MatchStmt     = "match" Expr "{" { MatchArm } "}"
MatchArm      = Pattern "=>" ( Block | Expr "," )
WhileStmt     = "while" Expr Block
ForStmt       = "for" Ident "in" Expr Block
SpawnStmt     = "spawn" Block
```

### 3.8  Expressions

```
Expr          = ImplyExpr [ "?" ]
ImplyExpr     = OrExpr [ "=>" OrExpr ]
OrExpr        = AndExpr { "||" AndExpr }
AndExpr       = IsExpr { "&&" IsExpr }
IsExpr        = CmpExpr [ "is" Pattern ]
CmpExpr       = AddExpr { ( "==" | "!=" | "<" | ">" | "<=" | ">=" ) AddExpr }
AddExpr       = MulExpr { ( "+" | "-" ) MulExpr }
MulExpr       = UnaryExpr { ( "*" | "/" | "%" ) UnaryExpr }
UnaryExpr     = ( "!" | "-" | "&" [ "mut" ] ) UnaryExpr | PostfixExpr
PostfixExpr   = Primary { "." Ident | "(" ArgList ")" | "[" Expr "]" | "@" "pre" }
Primary       = Ident | IntLit | FloatLit | StrLit | CharLit
             | "true" | "false" | "(" Expr ")"
             | StructLit | ArrayLit | ClosureExpr | PipeClosure
             | "await" Expr | "comptime" Expr
             | "Some" "(" Expr ")" | "None"
             | "Ok" "(" Expr ")" | "Err" "(" Expr ")"
StructLit     = Ident [ TypeGenericArgs ] "{" { Ident ":" Expr "," } "}"
ArrayLit      = "[" [ Expr { "," Expr } ] "]"
ClosureExpr   = "fn" "(" [ ParamList ] ")" Block
PipeClosure   = "|" Ident { "," Ident } "|" Expr
ArgList       = Expr { "," Expr }
TypeGenericArgs = "[" Type { "," Type } "]"
```

# 4. Type System

## 4.1  Primitive Types

| Type | Width | Notes |
| :---- | :---- | :---- |
| **Bool** | 1 bit logical | Only `true` or `false`. No integer coercion. |
| **Int** | Platform (64-bit) | Signed. Default integer type. |
| **Int8** | 8 bits | Signed byte. |
| **Int16** | 16 bits | Signed short. |
| **Int32** | 32 bits | Signed word. |
| **Int64** | 64 bits | Signed double word. |
| **Int128** | 128 bits | Signed, base-2, range `-2^127 .. 2^127-1`. Literals beyond `u64` are supported. |
| **UInt** | Platform (64-bit) | Unsigned. Use for sizes and indices. |
| **UInt8** | 8 bits | Byte. Alias: `Byte`. |
| **UInt16** | 16 bits | |
| **UInt32** | 32 bits | |
| **UInt64** | 64 bits | |
| **UInt128** | 128 bits | Unsigned, `0 .. 2^128-1`. |
| **Float32** | IEEE 754 single | |
| **Float64** | IEEE 754 double | Default float type. |
| **Float128** | IEEE 754 binary128 | Lowered to LLVM `fp128`. Values come from conversion; no literal suffix. |
| **Char** | 32 bits | Unicode scalar value. Not a byte. |
| **Str** | Fat pointer | Immutable UTF-8 slice. Not null-terminated. |

## 4.2  Compound Types

| Syntax | Description |
| :---- | :---- |
| **Option[T]** | Either `Some(value)` or `None`. Replaces null. |
| **Result[T, E]** | Either `Ok(value)` or `Err(error)`. Replaces exceptions. |
| **Vec[T]** | Heap-allocated growable array. Owns its elements. |
| **Slice[T]** | Non-owning view into contiguous `T` values. |
| **Map[K, V]** | Hash map. `K` must satisfy `Hash` and `Eq`. |
| **Set[T]** | Hash set. `T` must satisfy `Hash` and `Eq`. |
| **(T, U, ...)** | Tuple. Fixed arity, mixed types, accessed by index. |
| ***T** | Raw pointer. Only usable inside `unsafe` blocks. |
| **[N]T** | Fixed-size array of N elements of type T. `N` is comptime. |

## 4.3  Type Inference

The compiler infers types from context in `let` and `var` bindings and in closure parameters. Type inference does not cross function boundaries. Function signatures are always fully annotated. This keeps inference local and error messages clear.

```xiom
let x = 42          // inferred: Int
let f = 3.14        // inferred: Float64
let s = "hello"     // inferred: Str
let v = [1, 2, 3]   // inferred: Vec[Int]
let t = (1, true)   // inferred: (Int, Bool)
```

## 4.4  Generics via Comptime

Generics are implemented through comptime type parameters. The type parameter is resolved at compile time, producing a monomorphised specialisation. No runtime dispatch, no boxing, no virtual calls unless explicitly requested via interface references.

Type-level constraints are declared inline with the type parameter, not as separate `requires` clauses. This separates type-level requirements from value-level preconditions.

```xiom
fn max[T: Comparable](a: T, b: T) -> T {
  if a > b { return a }
  return b
}

// Multiple constraints
fn dedup[T: Eq + Hash](items: &mut Vec[T]) { ... }

// Call sites -- T inferred from arguments
let m1 = max(10, 20)          // T = Int
let m2 = max(1.5, 2.7)        // T = Float64
```

If a type parameter appears only in the return type and not in any argument, it must be annotated explicitly at the call site:

```xiom
fn parse[T](s: Str) -> Result[T, ParseError] { ... }

let n = parse[Int]("42")   // T must be explicit -- not inferrable from arguments
```

## 4.5  Structural Interface Satisfaction

A type satisfies an interface if it provides all required fields and methods with matching signatures. No `implements` keyword. Satisfaction is checked at the use site.

```xiom
interface Comparable {
  fn compare(other: &Self) -> Int  // -1, 0, 1
}

type Score = { value: Int }

fn Score.compare(other: &Score) -> Int {
  if value < other.value { return -1 }
  if value > other.value { return  1 }
  return 0
}

// Score now satisfies Comparable -- no declaration needed
let result = max(Score{ value: 10 }, Score{ value: 20 })
```

## 4.6  Derive -- Compiler-Generated Interfaces

The `derive` clause on a type or enum declaration instructs the compiler to generate the implementation of common interfaces. The generated code is guaranteed correct by construction -- no hand-written bug can slip in.

| Interface | Generated Behaviour |
| :---- | :---- |
| **Eq** | Structural equality -- every field compared. Two values are equal if all fields are equal. |
| **Clone** | Deep copy -- every field cloned recursively. |
| **Display** | Canonical string representation. Structs format as `TypeName{ field: value, ... }`. |
| **Hash** | Structural hash -- every field hashed and combined. Compatible with `Eq`. |
| **Ord** | Lexicographic ordering -- fields compared in declaration order. |

```xiom
type Point = {
  x: Float64;
  y: Float64;
} derive[Eq, Clone, Display]

// Compiler generates:
//   fn Point.eq(other: &Point) -> Bool        -- x == x && y == y
//   fn Point.clone() -> Point                 -- deep copy of both fields
//   fn Point.to_str() -> Str                  -- "Point{ x: 1.0, y: 2.0 }"

// Type with invariants can only derive Clone and Display
type Health = {
  current: Int;
  maximum: Int;
  invariant: current >= 0;
  invariant: current <= maximum;
} derive[Clone, Display]
// Eq, Hash, Ord are rejected -- invariants make equality/hashing semantically ambiguous

// Enums support derive too
enum Option[T] {
  Some(value: T),
  None
} derive[Eq, Clone]

// Enums with variant data can derive Clone, Display
// Enums with only unit variants can also derive Eq, Hash, Ord
```

`derive` is not syntactic sugar. It is correctness by construction. Every hand-written `eq` method is a chance for AI or a tired programmer to miss a field comparison. The compiler never misses.

# 5. Memory Model

XIOM uses ownership semantics for memory management. There is no garbage collector. Memory is freed when the owning binding leaves its scope. The model uses lexical scope borrowing -- simpler than Rust's lifetime system while providing the same core safety guarantee: use-after-free and double-free are compile errors.

## 5.1  Ownership Rules

| Rule | Description |
| :---- | :---- |
| **Single Owner** | Every value has exactly one owner at any time. Assignment moves ownership. |
| **Scope Lifetime** | A value is freed when its owning binding leaves scope. No GC, no manual free. |
| **Read Borrow (`&T`)** | Multiple simultaneous read borrows allowed. No mutation during active read borrows. |
| **Write Borrow (`&mut T`)** | Exactly one write borrow at a time. No other borrows active simultaneously. |
| **Explicit Clone** | Duplicating a value requires `.clone()`. No implicit deep copy. |
| **Move On Call** | Passing a value to a function moves ownership unless the parameter is a borrow. |

Borrows cannot be stored in struct fields. Borrows cannot be returned from functions. These patterns require owned types or explicit cloning. This is a constraint, not a bug -- it is the design. Lexical scope means you can always see when a borrow ends by looking at the braces.

```xiom
fn consume(data: Vec[Int]) {
  // data owned here -- freed at end of this scope
}

fn read_only(data: &Vec[Int]) {
  // read borrow -- caller retains ownership
}

fn mutate(data: &mut Vec[Int]) {
  data.push(99)   // write borrow -- exclusive access
}

let v = [1, 2, 3]
read_only(&v)        // borrow, v still valid
mutate(&mut v)       // write borrow, v still valid
consume(v)           // move -- v no longer usable here
// read_only(&v)     // COMPILE ERROR: v was moved
```

## 5.2  Unsafe Blocks

Raw pointer arithmetic and C interop that cannot be verified by the compiler are permitted only inside explicit `unsafe { }` blocks. The `unsafe` keyword is a declaration that the programmer takes responsibility for memory safety inside that scope. Unsafe blocks are visible in code review and audits. They cannot be hidden.

```xiom
unsafe {
  let raw: *Int = some_c_function()
  let value = *raw   // dereference -- programmer guarantees validity
}
```

# 6. Contract System

Contracts are the formal specification layer of XIOM. They transform function signatures from documentation into machine-checkable specifications. In Phase 1, contracts compile to runtime guards with precise error messages. Static proof via Z3 SMT solver is a planned Phase 3 integration.

## 6.1  Keywords

| Keyword | Semantics |
| :---- | :---- |
| **requires** | Pre-condition. Must hold when the function is called. Caller is responsible. |
| **ensures** | Post-condition. Must hold when the function returns. Implementation is responsible. |
| **invariant** | Type-level contract. Must hold after every mutation of a value of this type. |
| **result** | Refers to the return value inside an `ensures` clause. |
| **self@pre** | Value of `self` at the moment the function was entered. For use in `ensures`. |

## 6.2  Function Contracts

```xiom
fn divide(a: Float64, b: Float64) -> Float64
  requires: b != 0.0
  ensures:  result * b == a
{
  return a / b
}
```

Type-level constraints (which interfaces a generic parameter must satisfy) are declared inline with the type parameter, not as `requires` clauses. This separates type requirements from value preconditions:

```xiom
// Type constraint -- inline
fn sort[T: Ord](items: &mut Vec[T])

// Value precondition -- requires clause
fn pop[T](stack: &mut Stack[T]) -> Option[T]
  requires: !stack.is_empty()
```

## 6.3  Type Invariants

```xiom
type Health = {
  current: Int;
  maximum: Int;
  invariant: current >= 0;
  invariant: current <= maximum;
  invariant: maximum > 0;
}

// The compiler rejects any code that could violate these invariants.
// No runtime crash -- compile error.
```

## 6.4  Contract Collection Methods

To reduce verbosity and prevent quantifier syntax errors (especially in AI-generated code), the standard library provides contract-focused methods on collections:

| Method | Meaning | Replaces |
| :---- | :---- | :---- |
| `.is_sorted()` | Elements are in non-decreasing order | `forall i in 0..len-1 => items[i] <= items[i+1]` |
| `.all(closure)` | All elements satisfy the predicate | `forall i in 0..len => pred(items[i])` |
| `.none(closure)` | No element satisfies the predicate | `forall i in 0..len => !pred(items[i])` |
| `.contains(value)` | Collection contains the given value | `exists i in 0..len => items[i] == value` |
| `.len()` | Number of elements (already present, used in contracts) | -- |
| `.is_empty()` | Collection is empty. Equivalent to `.len() == 0`. | -- |

```xiom
fn sort(items: &mut Vec[Int])
  ensures: items.is_sorted()
{
  // ... sorting implementation
}

fn filter_positive(items: &Vec[Int]) -> Vec[Int]
  ensures: result.all(|x| x > 0)
  ensures: result.len() <= items.len()
{
  // ... filter implementation
}

fn validate_all(values: &Vec[Int], min: Int) -> Bool
  ensures: result == true => values.all(|x| x >= min)
  ensures: result == false => values.none(|x| x >= min)
```

These are ordinary standard library functions with ordinary semantics. The contract verifier treats them as assertions at the expression level. No new language machinery is required.

## 6.5  Contract Verification Modes

| Mode | Behaviour |
| :---- | :---- |
| **Static (Phase 3)** | Compiler attempts SMT proof. Zero runtime cost if proven. |
| **Runtime guard (default)** | Inserted when static proof fails or is unavailable. Panics with a clear message on violation. |
| **Disabled (`#[no_contracts]`)** | Strips all contracts in release builds when explicitly requested. Opt-in only. |
| **Contradictory** | Compile error. The specification is logically impossible to satisfy. |

# 7. Module System

## 7.1  Declaring Modules

A module is a named namespace. Every source file begins with a module declaration. Modules can be nested. A module hierarchy corresponds to the directory structure.

```xiom
module math.vector

// Everything declared here is in the math.vector namespace.
```

## 7.2  Importing

```xiom
use math.vector              // imports the module -- access as vector.Vec3
use math.vector.Vec3         // imports one type -- access as Vec3
use math.vector.Vec3 as V3   // alias -- access as V3
use math.vector.*            // imports all public symbols (discouraged)
```

## 7.3  Visibility

All declarations are private to their module by default. The `pub` keyword makes a declaration visible to other modules. There is no `protected` or `friend` visibility.

```xiom
pub type Vec3 = {        // visible outside math.vector
  x: Float32;
  y: Float32;
  z: Float32;
} derive[Eq, Clone, Display]

fn internal_helper() {  // private to this module
  // ...
}
```

## 7.4  Method Declarations

Methods on a type are declared using the `TypeName.methodName` syntax. The receiver (`self`) is synthesized implicitly by the compiler -- it does not appear in the parameter list. The compiler infers the receiver type from the method body:

- Methods that do not mutate fields get `self: &Self` (read borrow)
- Methods that mutate fields get `self: &mut Self` (write borrow)
- If a field is mutated anywhere in the method body, the receiver is `&mut Self`

```xiom
// In math/vector.xi
pub type Vec3 = { x: Float32; y: Float32; z: Float32; } derive[Eq, Clone, Display]

pub fn Vec3.dot(other: &Vec3) -> Float32 {
  return x * other.x + y * other.y + z * other.z  // self is &Vec3 -- read-only
}

pub fn Vec3.normalize() -> Vec3 {
  let mag = (x*x + y*y + z*z).sqrt()
  return Vec3{ x: x / mag, y: y / mag, z: z / mag }
}

pub fn Vec3.set_x(value: Float32) {
  x = value   // self is &mut Vec3 -- field mutation detected
}
```

## 7.5  Package Manifest

Packages are defined by a `package.xi` manifest file at the project root. Dependencies are resolved at build time. Version pinning uses semantic versioning.

```xiom
// package.xi
package {
  name:    "myproject"
  version: "1.0.0"
  deps: {
    "xiom-std": "0.4.*"
    "xiom-net":  "0.2.1"
  }
}
```

# 8. Concurrency

Concurrency primitives are part of the language, not a library. The ownership model guarantees data-race freedom at compile time. The same rules that prevent use-after-free prevent concurrent mutation of shared data.

## 8.1  Async / Await

Async functions return a future. They do not block the calling thread. The runtime drives futures to completion. An async function is called with `await` inside another async context.

```xiom
async fn fetch(url: Str) -> Result[Str, NetError] {
  let response = await http.get(url)?
  return Ok(response.body_text())
}

async fn main() {
  match await fetch("https://example.com") {
    Ok(body) => io.print(body)
    Err(e)   => io.print_err(e.message)
  }
}
```

## 8.2  Spawn

`spawn` launches a concurrent task. The spawned block may not capture mutable references from the outer scope -- the compiler enforces this. Communication between tasks goes through channels.

```xiom
spawn {
  let result = heavy_computation()
  sender.send(result)
}
```

## 8.3  Channels

Channels are typed, bounded or unbounded message queues. Send and receive are the only operations. Ownership of the sent value transfers to the channel.

```xiom
let (tx, rx) = Channel[Int].bounded(32)   // capacity 32

spawn { tx.send(compute()) }

match rx.recv() {
  Ok(value) => use(value)
  Err(_)    => io.print("channel closed")
}
```

## 8.4  Parallel Iterators

```xiom
let results = items.par_map(fn(item) { expensive(item) })
// Distributes across available cores.
// Ownership rules ensure no data races.
```

# 9. Error Handling

## 9.1  Result Type

```xiom
fn parse_int(s: Str) -> Result[Int, ParseError] {
  // ...
}
```

`E` in `Result[T, E]` is any type. No `Error` interface is required. The standard library provides a `StdError` interface for its own functions. Library authors are free to use any error type that suits their domain.

```xiom
// All valid
Result[Int, Str]
Result[Config, IOError]
Result[Data, MyCustomErrorEnum]
```

## 9.2  Propagation With ?

The `?` operator returns the error from the current function if the `Result` is `Err`. It is syntactic sugar for an explicit match that returns the error. `?` can only appear inside a function that returns `Result`.

```xiom
fn load_config(path: Str) -> Result[Config, AppError] {
  let file   = io.read_file(path)?     // returns Err on failure
  let config = parse_config(file)?     // returns Err on failure
  return Ok(config)
}
```

## 9.3  Match Exhaustion

Every `match` expression must cover all cases. The compiler rejects non-exhaustive matches. A wildcard arm `_` covers remaining cases.

```xiom
match parse_int("42") {
  Ok(n)  => io.print(n.to_str())
  Err(e) => io.print_err(e.message)
}

// Matching an enum -- all variants required
match state {
  AgentState.Idle              => ...
  AgentState.Patrolling(route) => ...
  AgentState.Attacking(target) => ...
  AgentState.Dead(cause)       => ...
}
```

## 9.4  Option Handling

```xiom
let val: Option[Int] = Some(10)

// Unwrap with default
let n = val.unwrap_or(0)

// Pattern match
match val {
  Some(n) => use(n)
  None    => handle_absent()
}

// Propagate None with ?  (inside a function returning Option)
let n = val?
```

# 10. Compiler Pipeline

| Stage | Description |
| :---- | :---- |
| **Lexer** | Converts UTF-8 source text into a flat token stream. Whitespace is not significant except for string literals. |
| **Parser** | Converts the token stream into an AST. Grammar is LL(1). Single deterministic parse path. No backtracking. |
| **Name Resolution** | Resolves all identifiers to their declarations. Detects undefined names, shadowing, and circular dependencies. |
| **Type Checker** | Infers and verifies types throughout the AST. Checks interface satisfaction, generic bounds, and ownership constraints. Generates `derive` implementations. |
| **Contract Verifier** | Phase 1: emits runtime guards for `requires`/`ensures`/`invariant`. Phase 3: feeds contracts to Z3 SMT solver for static proof. |
| **XIOM IR** | Lowers typed AST to a simple, explicit, fully-typed intermediate representation. Human-readable. Platform-independent. |
| **Optimizer** | Performs dead code elimination, inlining, and constant folding at the IR level. Elides statically-proven contract checks. |
| **LLVM Backend** | Lowers XIOM IR to LLVM IR. LLVM performs backend optimisation and emits machine code or WASM. |

## 10.1  XIOM IR

XIOM IR is an explicit, typed, SSA-form intermediate representation. Every operation has an explicit type. Control flow is explicit. Ownership transfers are annotated. The IR is designed to be readable by both humans and AI systems.

```
; XIOM IR -- illustrative excerpt
fn @add(%a: Int, %b: Int) -> Int {
block entry:
  %result = add.Int %a, %b
  ret.Int %result
}
```

## 10.2  Bootstrapping Phases

| Phase | Compiler Written In | What It Compiles |
| :---- | :---- | :---- |
| **0** | Rust | Minimal XIOM subset (no generics, no contracts, no ownership) |
| **1** | XIOM subset | Full XIOM language -- compiled by Phase 0 |
| **2** | Full XIOM | Full XIOM compiler -- compiled by Phase 1 |
| **3** | Full XIOM | Self-hosting. Phase 0 Rust compiler retired. |

# 11. Target Platforms

XIOM produces output via two paths: LLVM for native and WASM for portable bytecode. Both paths are first-class. Platform-specific code is isolated in standard library platform modules. GPU and console targets are library concerns accessed through C FFI -- they are not language features.

## 11.1  Native Targets via LLVM

| Target Triple | Platform |
| :---- | :---- |
| **x86_64-unknown-linux-gnu** | Linux 64-bit |
| **x86_64-pc-windows-msvc** | Windows 64-bit |
| **x86_64-apple-darwin** | macOS Intel |
| **aarch64-apple-darwin** | macOS Apple Silicon |
| **aarch64-apple-ios** | iOS |
| **aarch64-linux-android** | Android |
| **riscv64gc-unknown-linux-gnu** | RISC-V Linux |

## 11.2  WebAssembly

The WASM target produces wasm32 binaries via LLVM's WebAssembly backend. WASI is supported for system-interface access outside the browser. The WASM binary contains no XIOM runtime -- it is self-contained.

## 11.3  C Interoperability

XIOM has zero-cost C FFI. C functions and types are declared in `extern` blocks. The compiler generates no wrapper code. C ABI calling conventions are used directly. `unsafe` is required because the compiler cannot verify C memory safety.

```xiom
extern "C" {
  fn malloc(size: UInt) -> *UInt8
  fn free(ptr: *UInt8)
  fn strlen(s: *UInt8) -> UInt
}

fn c_string_length(ptr: *UInt8) -> UInt {
  unsafe { return strlen(ptr) }
}
```

# 12. Error Message Philosophy

Error messages are part of the language design. A compiler that produces cryptic errors is a language that is hard to use. Every error in XIOM must satisfy four criteria:

| LOCATION | Point to the exact source location causing the error. Not a line range. The exact token. |
| :---: | :---- |

| CAUSE | Explain what the compiler expected and what it found. In plain language, not compiler jargon. |
| :---: | :---- |

| IMPLICATION | Explain why this is an error. Not every programmer knows why you cannot have two mutable borrows. |
| :---: | :---- |

| SUGGESTION | Offer a concrete fix where one can be inferred. The compiler should solve problems, not just report them. |
| :---: | :---- |

### Example -- Ownership Error

```
error[E0101]: value used after move
  --> src/main.xi:14:5
   |
12 |   consume(v)         // v moved here
   |           ^ ownership of `v` moved into `consume`
13 |
14 |   read_only(&v)      // v used here after move
   |             ^ `v` no longer valid here
   |
   = Values can only have one owner. When you passed `v` to `consume`,
     ownership transferred. You cannot use `v` after that point.
   = help: if `consume` does not need to own the data, change its
     parameter to a borrow:  fn consume(data: &Vec[Int])
```

### Example -- Contract Violation

```
error[E0202]: contract pre-condition cannot be satisfied
  --> src/main.xi:8:3
   |
 6 |   fn divide(a: Float64, b: Float64) -> Float64
 7 |     requires: b != 0.0
 8 |   let result = divide(x, 0.0)
   |                ^^^^^^^^^^^^^^
   |
   = The `requires` clause of `divide` states that `b` must not be 0.0.
     You are passing the literal 0.0 as `b`, which always violates this.
   = help: check `b` before calling, or use a checked division function
     that returns Option[Float64].
```

### Example -- Interface Satisfaction

```
error[E0301]: type does not satisfy interface
  --> src/main.xi:12:10
   |
12 |   let s = sort[Point](points)
   |           ^^^^^^^^^ type `Point` does not satisfy `Ord`
   |
   = `sort` requires `T: Ord` because it must compare elements.
     Type `Point` is missing:  fn compare(other: &Point) -> Int
   = help: add `derive[Ord]` to the type definition of `Point`, or
     implement `fn Point.compare(other: &Point) -> Int` by hand.
```

# 13. Complete Example Program

The following program demonstrates: module declaration, types with invariants and derive, structural interface satisfaction, generics with inline constraints, error handling, and ownership -- in a single working program. It implements a statically-bounded generic stack.

```xiom
module collections.stack

use xiom.io;

// -- Type with invariants ----------------------------------

pub type Stack[T] = {
  items:    Vec[T];
  capacity: UInt;
  invariant: items.len() <= capacity;
  invariant: capacity > 0;
}

// -- Constructor -------------------------------------------

pub fn Stack.new[T](capacity: UInt) -> Result[Stack[T], Str]
  requires: capacity > 0
  ensures:  result is Ok
{
  if capacity == 0 {
    return Err("capacity must be greater than zero")
  }
  return Ok(Stack[T] {
    items:    Vec[T].with_capacity(capacity),
    capacity: capacity,
  })
}

// -- Push --------------------------------------------------

pub fn Stack.push[T](value: T) -> Result[(), Str]
  requires: items.len() < capacity
  ensures:  result is Ok => items.len() == items.len()@pre + 1
{
  if items.len() == capacity {
    return Err("stack is full")
  }
  items.push(value)
  return Ok(())
}

// -- Pop ---------------------------------------------------

pub fn Stack.pop[T]() -> Option[T] {
  return items.pop()
}

pub fn Stack.is_empty[T]() -> Bool {
  return items.len() == 0
}

pub fn Stack.len[T]() -> UInt {
  return items.len()
}

// -- Entry point -------------------------------------------

fn main() -> Result[(), Str] {
  var s = Stack.new[Int](3)?

  s.push(10)?
  s.push(20)?
  s.push(30)?

  match s.push(40) {
    Ok(_)  => io.print("unexpected success")
    Err(e) => io.print("correctly rejected: " + e)
  }

  while !s.is_empty() {
    match s.pop() {
      Some(v) => io.print(v.to_str())
      None    => {}
    }
  }

  return Ok(())
}
```

# 14. Comparison With Existing Languages

| Feature | XIOM | Rust | Go | Zig |
| :---- | :---- | :---- | :---- | :---- |
| **Memory model** | Ownership, lexical borrows | Full borrow checker + lifetimes | GC | Manual |
| **Contracts** | First-class, compiler-enforced | None (assertions only) | None | None |
| **Null safety** | No null -- `Option[T]` | No null -- `Option<T>` | Null exists | Null exists |
| **Error handling** | `Result[T, E]`, `?` operator | `Result<T, E>`, `?` operator | Multi-return, `if err != nil` | Error unions + try |
| **Generics** | Comptime monomorphised, inline constraints | Monomorphised, trait bounds | Generics (limited) | comptime |
| **Interfaces** | Structural, no `implements` | Nominal (`impl Trait for Type`) | Structural (interfaces) | -- |
| **Derive** | Compiler-generated `Eq`, `Clone`, `Display`, `Hash`, `Ord` | `#[derive(...)]` macros | None (manual) | None |
| **GC** | None | None | Yes | None |
| **WASM target** | First-class, co-equal with native | Supported | Limited | Supported |
| **C FFI** | Zero-cost, first-class | Zero-cost, first-class | Cgo (overhead) | First-class |
| **Self-hosted** | Planned (Phase 2) | Yes | Yes | In progress |
| **Grammar ambiguity** | None -- canonical form | Some | Minimal | Minimal |
| **Method receiver** | Implicit `self`, inferred | Explicit `&self` / `&mut self` | Explicit receiver | Explicit `self: *T` |

# 15. Build Roadmap

The following estimates assume a team of two to three compiler engineers with prior experience in at least one systems language. All timelines are realistic minimums, not targets. Compiler development consistently takes longer than estimated.

## Phase 0 -- Prototype Compiler  (2-3 weeks, AI-assisted)

Written in Rust. Compiles a minimal subset of XIOM: primitives, functions, let/var bindings, if/match, basic structs and enums. Parses the full grammar including `derive`, inline type constraints, and method syntax -- but does not enforce ownership or contracts. Goal: Hello World compiles to native binary and to WASM.

- Define EBNF grammar fully before writing any code
- Implement Lexer -- tokenise all valid XIOM source
- Implement Parser -- produce typed AST from token stream
- Implement basic type checker -- primitives and function signatures
- Parse `derive` clauses -- codegen deferred to Phase 1
- Emit LLVM IR for subset -- link and run
- Emit WASM via LLVM WebAssembly backend
- Test suite: 200+ parser tests, 100+ type checker tests

## Phase 1 -- Full Language Surface  (3-6 months)

Still compiled by Phase 0 Rust compiler. Adds the full language surface: generics, ownership checker, contracts as runtime guards, modules, async, channels, error handling, C FFI, standard library core, and `derive` codegen.

- Ownership model -- lexical scope borrow checker
- Generic type parameters via comptime with inline constraints
- Contract syntax -- `requires` / `ensures` / `invariant` as runtime guards
- Contract collection methods -- `is_sorted`, `all`, `none`, `contains`
- `derive` code generation -- `Eq`, `Clone`, `Display`, `Hash`, `Ord`
- Module system and package manifest
- Async runtime and channel primitives
- Standard library: core, io, collections, string, math, ffi
- Package manager prototype -- local resolution only
- Canonical formatter (`xiom fmt`)
- Language server (LSP) prototype for editor integration

## Phase 2 -- Self-Hosting  (6-12 months after Phase 1)

Rewrite the XIOM compiler in XIOM itself. Compiled by Phase 1. This is the most difficult phase -- the language must be stable enough that the compiler can be its own largest test case.

- Rewrite Lexer in XIOM -- compiled by Phase 1 compiler
- Rewrite Parser in XIOM
- Rewrite type checker in XIOM
- Rewrite IR emitter and LLVM bindings in XIOM
- Compile new compiler with Phase 1 compiler
- New compiler compiles itself -- bootstrap complete
- Phase 0 Rust compiler retired

## Phase 3 -- Stability & Ecosystem  (ongoing)

Language specification locked. Breaking changes require a formal proposal and deprecation period. Ecosystem development -- Z3 static contract verification, package registry, LSP, formatter, documentation tooling, additional compiler targets.

- Z3 SMT integration for static contract verification
- Public package registry
- Language server (LSP) production implementation
- Canonical formatter (`xiom fmt`) -- production implementation
- Documentation generator (`xiom doc`)
- Additional LLVM targets as needed
- WASI full compliance
- Formal specification document -- normative, implementer-facing
- Third-party compiler implementations welcomed

## Realistic Total Timeline

Phase 0 through self-hosting with AI-assisted development: 12 to 24 months.
Conventional team (2-3 engineers, no AI tooling): 30 to 46 months.

For context: Rust took approximately 8 years from start to 1.0. Go took 3 years with a large Google team. Zig is still pre-1.0 after 8 years. These timelines are normal. A language that cuts corners to ship faster will have the wrong corners cut forever.

The build strategy document contains the authoritative timeline with per-phase breakdowns.

---

**XIOM Language Reference -- Version 0.3**

This specification defines the language only. Standard library, toolchain, and ecosystem are separate documents.

All syntax and semantics subject to revision until Version 1.0.
