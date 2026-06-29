  
**AXIOM**

Language Reference Specification

Version 0.2  —  Language Definition Only

This document defines the AXIOM language. Applications are out of scope.

# **Contents**

1\.  Overview & Core Goals

2\.  Design Principles

3\.  Formal Grammar (EBNF)

4\.  Type System

5\.  Memory Model

6\.  Contract System

7\.  Module System

8\.  Concurrency

9\.  Error Handling

10\. Compiler Pipeline

11\. Target Platforms

12\. Error Message Philosophy

13\. Complete Example Program

14\. Comparison With Existing Languages

15\. Build Roadmap

# **1\. Overview & Core Goals**

AXIOM is a compiled, statically typed, memory-safe systems programming language. It is designed around three properties that no existing mainstream language provides simultaneously:

| SAFE | Ownership-based memory safety with no garbage collector and no runtime. Memory is freed deterministically when the owner leaves scope. |
| :---: | :---- |

| VERIFIED | Pre-conditions, post-conditions, and type invariants are first-class language constructs enforced by the compiler, not documentation conventions. |
| :---: | :---- |

| PRECISE | The grammar is unambiguous. Every construct has exactly one canonical form. There are no implicit coercions, no hidden allocations, and no surprising control flow. |
| :---: | :---- |

AXIOM compiles to native machine code via LLVM and to WebAssembly. It has zero-cost C interoperability. The compiler is intended to be self-hosted once the language reaches stability.

AXIOM does not include a runtime, a garbage collector, or a virtual machine. It does not target any specific application domain. What you build with it is outside the scope of this document.

# **2\. Design Principles**

## **2.1  One Way To Write Each Thing**

For every language construct there is exactly one canonical syntax. Formatting is part of the language specification. The canonical formatter is part of the compiler toolchain (axiom fmt). Code that deviates from canonical format is a warning by default and an error in strict mode.

## **2.2  Explicit Over Implicit**

Nothing happens without being written. Memory allocation is visible. Type conversions are explicit. If a function can fail, its return type says so. If a value can be absent, its type says so. There are no default function arguments, no implicit constructors, and no implicit type widening.

## **2.3  Contracts Are Specification**

Contracts (requires, ensures, invariant) are not assert statements. They are formal specifications that the compiler reasons about. Statically provable contracts have zero runtime cost. Contracts that cannot be proven statically are compiled to checked runtime guards. A contract that is logically contradictory is a compile error.

## **2.4  No Null**

The language has no null, nil, or undefined value. Absence of a value is expressed through Option\[T\]. The compiler enforces exhaustive handling of the absent case at every use site.

## **2.5  Errors Are Types**

Functions that can fail return Result\[T, E\]. There are no exceptions and no panic-by-default. The ? operator propagates errors explicitly. Unhandled error paths are compile errors, not runtime surprises.

## **2.6  Structural Interfaces**

A type satisfies an interface if it has the required fields and methods. No implements declaration is needed. This allows composing types across module boundaries without shared ancestry.

## **2.7  Comptime Is The Only Metaprogramming**

There is no preprocessor, no macro system, and no template language. All compile-time code generation is done through the comptime keyword, which marks expressions and blocks to be evaluated at compile time. Generics, reflection, and specialisation all flow through this single mechanism.

# **3\. Formal Grammar (EBNF)**

The following grammar is the normative definition of AXIOM syntax. Terminals are in double quotes or character classes. Nonterminals are in PascalCase.

### **3.1  Lexical Rules**

Letter       \= \[a-zA-Z\_\]  
Digit        \= \[0-9\]  
HexDigit     \= \[0-9a-fA-F\]  
Ident        \= Letter { Letter | Digit }  
IntLit       \= Digit { Digit | "\_" }  
FloatLit     \= Digit { Digit } "." Digit { Digit }  
StrLit       \= '"' { StrChar } '"'  
StrChar      \= any Unicode except '"' and newline | EscSeq  
EscSeq       \= "\\\\" ( "n" | "t" | "r" | "\\\\" | '"' | "u{" HexDigit+ "}" )  
CharLit      \= "'" ( StrChar ) "'"  
Comment      \= "//" { any } newline  
BlockComment \= "/\*" { any } "\*/"

### **3.2  Top-Level**

Program      \= { TopDecl }  
TopDecl      \= ModuleDecl | UseDecl | TypeDecl | EnumDecl  
             | InterfaceDecl | FnDecl | ConstDecl  
ModuleDecl   \= "module" Ident "{" { TopDecl } "}"  
UseDecl      \= "use" ModulePath \[ "as" Ident \] ";"  
ModulePath   \= Ident { "." Ident }  
ConstDecl    \= "const" Ident ":" Type "=" Expr ";"

### **3.3  Type Declarations**

TypeDecl      \= "type" Ident \[ GenericParams \] "=" "{"  
                  { FieldDecl }  
                  { DerivedDecl }  
                  { InvariantDecl }  
              "}"  
FieldDecl     \= Ident ":" Type ";"  
DerivedDecl   \= Ident ":" Type "derived" "(" Expr ")" ";"  
InvariantDecl \= "invariant" ":" Expr ";"  
EnumDecl      \= "enum" Ident \[ GenericParams \] "{"  
                  Ident { "(" FieldDecl { FieldDecl } ")" }  
              "}"  
InterfaceDecl \= "interface" Ident \[ GenericParams \] "{"  
                  { FieldDecl | FnSignature }  
              "}"

### **3.4  Functions**

FnDecl        \= \[ "async" \] "fn" Ident \[ GenericParams \]  
                "(" \[ ParamList \] ")" \[ "-\>" Type \]  
                { ContractClause }  
                Block  
FnSignature   \= \[ "async" \] "fn" Ident \[ GenericParams \]  
                "(" \[ ParamList \] ")" \[ "-\>" Type \]  
                { ContractClause } ";"  
ParamList     \= Param { "," Param }  
Param         \= \[ "&" \[ "mut" \] \] Ident ":" Type  
ContractClause= ( "requires" | "ensures" ) ":" Expr  
GenericParams \= "\[" Ident { "," Ident } "\]"

### **3.5  Statements**

Block         \= "{" { Stmt } \[ Expr \] "}"  
Stmt          \= LetStmt | VarStmt | AssignStmt | ReturnStmt  
             | ExprStmt | IfStmt | MatchStmt | WhileStmt  
             | ForStmt | SpawnStmt  
LetStmt       \= "let" Ident \[ ":" Type \] "=" Expr ";"  
VarStmt       \= "var" Ident \[ ":" Type \] "=" Expr ";"  
AssignStmt    \= Place "=" Expr ";"  
ReturnStmt    \= "return" \[ Expr \] ";"  
ExprStmt      \= Expr ";"  
IfStmt        \= "if" Expr Block { "elif" Expr Block } \[ "else" Block \]  
MatchStmt     \= "match" Expr "{" { MatchArm } "}"  
MatchArm      \= Pattern "=\>" ( Block | Expr "," )  
WhileStmt     \= "while" Expr Block  
ForStmt       \= "for" Ident "in" Expr Block  
SpawnStmt     \= "spawn" Block

### **3.6  Expressions**

Expr          \= OrExpr \[ "?" \]  
OrExpr        \= AndExpr { "||" AndExpr }  
AndExpr       \= CmpExpr { "&&" CmpExpr }  
CmpExpr       \= AddExpr { ( "==" | "\!=" | "\<" | "\>" | "\<=" | "\>=" ) AddExpr }  
AddExpr       \= MulExpr { ( "+" | "-" ) MulExpr }  
MulExpr       \= UnaryExpr { ( "\*" | "/" | "%" ) UnaryExpr }  
UnaryExpr     \= ( "\!" | "-" | "&" \[ "mut" \] ) UnaryExpr | PostfixExpr  
PostfixExpr   \= Primary { "." Ident | "(" ArgList ")" | "\[" Expr "\]" }  
Primary       \= Ident | IntLit | FloatLit | StrLit | CharLit  
             | "true" | "false" | "(" Expr ")"  
             | StructLit | ArrayLit | ClosureExpr  
             | "await" Expr | "comptime" Expr  
             | "Some" "(" Expr ")" | "None"  
             | "Ok" "(" Expr ")" | "Err" "(" Expr ")"  
StructLit     \= Ident \[ GenericArgs \] "{" { Ident ":" Expr "," } "}"  
ArrayLit      \= "\[" \[ Expr { "," Expr } \] "\]"  
ClosureExpr   \= "fn" "(" \[ ParamList \] ")" Block  
ArgList       \= Expr { "," Expr }  
GenericArgs   \= "\[" Type { "," Type } "\]"

# **4\. Type System**

## **4.1  Primitive Types**

| Type | Width | Notes |
| :---- | :---- | :---- |
| **Bool** | 1 bit logical | Only true or false. No integer coercion. |
| **Int** | Platform (64-bit) | Signed. Default integer type. |
| **Int8** | 8 bits | Signed byte. |
| **Int16** | 16 bits | Signed short. |
| **Int32** | 32 bits | Signed word. |
| **Int64** | 64 bits | Signed double word. |
| **UInt** | Platform (64-bit) | Unsigned. Use for sizes and indices. |
| **UInt8** | 8 bits | Byte. Alias: Byte. |
| **UInt16** | 16 bits |  |
| **UInt32** | 32 bits |  |
| **UInt64** | 64 bits |  |
| **Float32** | IEEE 754 single |  |
| **Float64** | IEEE 754 double | Default float type. |
| **Char** | 32 bits | Unicode scalar value. Not a byte. |
| **Str** | Fat pointer | Immutable UTF-8 slice. Not null-terminated. |

## **4.2  Compound Types**

| Syntax | Description |
| :---- | :---- |
| **Option\[T\]** | Either Some(value) or None. Replaces null. |
| **Result\[T, E\]** | Either Ok(value) or Err(error). Replaces exceptions. |
| **Vec\[T\]** | Heap-allocated growable array. Owns its elements. |
| **Slice\[T\]** | Non-owning view into contiguous T values. |
| **Map\[K, V\]** | Hash map. K must satisfy the Hashable interface. |
| **Set\[T\]** | Hash set. T must satisfy Hashable. |
| **(T, U)** | Tuple. Fixed arity, mixed types, accessed by index. |
| **\*T** | Raw pointer. Only usable inside unsafe blocks. |
| **\[N\]T** | Fixed-size array of N elements of type T. N is comptime. |

## **4.3  Type Inference**

The compiler infers types from context in let and var bindings and in closure parameters. Type inference does not cross function boundaries. Function signatures are always fully annotated. This keeps inference local and error messages clear.

let x \= 42          // inferred: Int  
let f \= 3.14        // inferred: Float64  
let s \= "hello"     // inferred: Str  
let v \= \[1, 2, 3\]   // inferred: Vec\[Int\]  
let t \= (1, true)   // inferred: (Int, Bool)

## **4.4  Generics via Comptime**

Generics are implemented through comptime type parameters. The type parameter is resolved at compile time, producing a monomorphised specialisation. No runtime dispatch, no boxing, no virtual calls unless explicitly requested via interface references.

fn max\[T\](a: T, b: T) \-\> T  
  requires: T satisfies Comparable  
{  
  if a \> b { return a }  
  return b  
}  
   
// Call sites — T inferred from arguments  
let m1 \= max(10, 20\)          // T \= Int  
let m2 \= max(1.5, 2.7)        // T \= Float64

## **4.5  Structural Interface Satisfaction**

A type satisfies an interface if it provides all required fields and methods with matching signatures. No implements keyword. Satisfaction is checked at the use site.

interface Comparable {  
  fn compare(other: \&Self) \-\> Int  // \-1, 0, 1  
}  
   
type Score \= { value: Int }  
   
fn Score.compare(other: \&Score) \-\> Int {  
  if self.value \< other.value { return \-1 }  
  if self.value \> other.value { return  1 }  
  return 0  
}  
   
// Score now satisfies Comparable — no declaration needed  
let result \= max(Score{ value: 10 }, Score{ value: 20 })

# **5\. Memory Model**

AXIOM uses ownership semantics for memory management. There is no garbage collector. Memory is freed when the owning binding leaves its scope. The model is intentionally simpler than Rust's lifetime system while providing the same core safety guarantee: use-after-free and double-free are compile errors.

## **5.1  Ownership Rules**

| Rule | Description |
| :---- | :---- |
| **Single Owner** | Every value has exactly one owner at any time. Assignment moves ownership. |
| **Scope Lifetime** | A value is freed when its owning binding leaves scope. No GC, no manual free. |
| **Read Borrow (\&T)** | Multiple simultaneous read borrows allowed. No mutation during active read borrows. |
| **Write Borrow (\&mut T)** | Exactly one write borrow at a time. No other borrows active simultaneously. |
| **Explicit Clone** | Duplicating a value requires .clone(). No implicit deep copy. |
| **Move On Call** | Passing a value to a function moves ownership unless the parameter is a borrow. |

fn consume(data: Vec\[Int\]) {  
  // data owned here — freed at end of this scope  
}  
   
fn read\_only(data: \&Vec\[Int\]) {  
  // read borrow — caller retains ownership  
}  
   
fn mutate(data: \&mut Vec\[Int\]) {  
  data.push(99)   // write borrow — exclusive access  
}  
   
let v \= \[1, 2, 3\]  
read\_only(\&v)        // borrow, v still valid  
mutate(\&mut v)       // write borrow, v still valid  
consume(v)           // move — v no longer usable here  
// read\_only(\&v)     // COMPILE ERROR: v was moved

## **5.2  Unsafe Blocks**

Raw pointer arithmetic and C interop that cannot be verified by the compiler are permitted only inside explicit unsafe { } blocks. The unsafe keyword is a declaration that the programmer takes responsibility for memory safety inside that scope. Unsafe blocks are visible in code review and audits. They cannot be hidden.

unsafe {  
  let raw: \*Int \= some\_c\_function()  
  let value \= \*raw   // dereference — programmer guarantees validity  
}

# **6\. Contract System**

Contracts are the formal specification layer of AXIOM. They transform function signatures from documentation into machine-checkable specifications. The compiler integrates an SMT solver (Z3) to attempt static proof of each contract. Contracts it cannot prove statically are emitted as runtime guards. Contracts that are logically contradictory prevent compilation.

## **6.1  Keywords**

| Keyword | Semantics |
| :---- | :---- |
| **requires** | Pre-condition. Must hold when the function is called. Caller is responsible. |
| **ensures** | Post-condition. Must hold when the function returns. Implementation is responsible. |
| **invariant** | Type-level contract. Must hold after every mutation of a value of this type. |
| **result** | Refers to the return value inside an ensures clause. |
| **self@pre** | Value of self at the moment the function was entered. For use in ensures. |

## **6.2  Function Contracts**

fn divide(a: Float64, b: Float64) \-\> Float64  
  requires: b \!= 0.0  
  ensures:  result \* b \== a  
{  
  return a / b  
}

## **6.3  Type Invariants**

type Health \= {  
  current: Int;  
  maximum: Int;  
  invariant: current \>= 0;  
  invariant: current \<= maximum;  
  invariant: maximum \> 0;  
}  
   
// The compiler rejects any code that could violate these invariants.  
// No runtime crash — compile error.

## **6.4  Quantifiers in Contracts**

Contracts can express properties over collections using forall and exists. These are evaluated by the SMT solver where possible. When they cannot be statically proven, the compiler emits a loop-based runtime check.

fn sort(items: \&mut Vec\[Int\])  
  ensures: forall i in 0..items.len-1 \=\> items\[i\] \<= items\[i+1\]  
{  
  // ... sorting implementation  
}

## **6.5  Contract Verification Modes**

| Mode | Behaviour |
| :---- | :---- |
| **Static (default)** | Compiler attempts SMT proof. Zero runtime cost if proven. |
| **Runtime guard** | Inserted when static proof fails. Panics with a clear message on violation. |
| **Disabled (\#\[no\_contracts\])** | Strips all contracts in release builds when explicitly requested. Opt-in only. |
| **Contradictory** | Compile error. The specification is logically impossible to satisfy. |

# **7\. Module System**

## **7.1  Declaring Modules**

A module is a named namespace. Every source file begins with a module declaration. Modules can be nested. A module hierarchy corresponds to the directory structure.

module math.vector  
   
// Everything declared here is in the math.vector namespace.

## **7.2  Importing**

use math.vector              // imports the module — access as vector.Vec3  
use math.vector.Vec3         // imports one type — access as Vec3  
use math.vector.Vec3 as V3   // alias — access as V3  
use math.vector.\*            // imports all public symbols (discouraged)

## **7.3  Visibility**

All declarations are private to their module by default. The pub keyword makes a declaration visible to other modules. There is no protected or friend visibility.

pub type Vec3 \= {        // visible outside math.vector  
  x: Float32;  
  y: Float32;  
  z: Float32;  
}  
   
fn internal\_helper() {  // private to this module  
  // ...  
}

## **7.4  Method Declarations**

Methods on a type are declared outside the type definition using the TypeName.methodName syntax. This avoids nesting all methods inside the type block and allows methods to be declared in any file within the same module.

// In math/vector.ax  
pub type Vec3 \= { x: Float32; y: Float32; z: Float32; }  
   
pub fn Vec3.dot(other: \&Vec3) \-\> Float32 {  
  return self.x \* other.x \+ self.y \* other.y \+ self.z \* other.z  
}  
   
pub fn Vec3.length() \-\> Float32 {  
  return (self.x\*self.x \+ self.y\*self.y \+ self.z\*self.z).sqrt()  
}

## **7.5  Package Manager**

Packages are collections of modules published to the AXIOM package registry. A package is defined by a package.ax manifest file at the root of the project. Dependencies are resolved at build time. Version pinning uses semantic versioning.

// package.ax  
package {  
  name:    "myproject"  
  version: "1.0.0"  
  deps: {  
    "axiom-std": "0.4.\*"  
    "axiom-net":  "0.2.1"  
  }  
}

# **8\. Concurrency**

Concurrency primitives are part of the language, not a library. The ownership model guarantees data-race freedom at compile time. The same rules that prevent use-after-free prevent concurrent mutation of shared data.

## **8.1  Async / Await**

Async functions return a future. They do not block the calling thread. The runtime drives futures to completion. An async function is called with await inside another async context.

async fn fetch(url: Str) \-\> Result\[Str, NetError\] {  
  let response \= await http.get(url)?  
  return Ok(response.body\_text())  
}  
   
async fn main() {  
  match await fetch("https://example.com") {  
    Ok(body) \=\> io.print(body)  
    Err(e)   \=\> io.print\_err(e.message)  
  }  
}

## **8.2  Spawn**

spawn launches a concurrent task. The spawned block may not capture mutable references from the outer scope — the compiler enforces this. Communication between tasks goes through channels.

spawn {  
  let result \= heavy\_computation()  
  sender.send(result)  
}

## **8.3  Channels**

Channels are typed, bounded or unbounded message queues. Send and receive are the only operations. Ownership of the sent value transfers to the channel.

let (tx, rx) \= Channel\[Int\].bounded(32)   // capacity 32  
   
spawn { tx.send(compute()) }  
   
match rx.recv() {  
  Ok(value) \=\> use(value)  
  Err(\_)    \=\> io.print("channel closed")  
}

## **8.4  Parallel Iterators**

let results \= items.par\_map(fn(item) { expensive(item) })  
// Distributes across available cores.  
// Ownership rules ensure no data races.

# **9\. Error Handling**

## **9.1  Result Type**

fn parse\_int(s: Str) \-\> Result\[Int, ParseError\] {  
  // ...  
}

## **9.2  Propagation With ?**

The ? operator returns the error from the current function if the Result is Err. It is syntactic sugar for an explicit match that returns the error. ? can only appear inside a function that returns Result.

fn load\_config(path: Str) \-\> Result\[Config, AppError\] {  
  let file    \= io.read\_file(path)?     // returns Err on failure  
  let config  \= parse\_config(file)?     // returns Err on failure  
  return Ok(config)  
}

## **9.3  Match Exhaustion**

Every match expression must cover all cases. The compiler rejects non-exhaustive matches. A wildcard arm \_ covers remaining cases.

match parse\_int("42") {  
  Ok(n)  \=\> io.print(n.to\_str())  
  Err(e) \=\> io.print\_err(e.message)  
}  
   
// Matching an enum — all variants required  
match state {  
  AgentState.Idle              \=\> ...  
  AgentState.Patrolling(route) \=\> ...  
  AgentState.Attacking(target) \=\> ...  
  AgentState.Dead(cause)       \=\> ...  
}

## **9.4  Option Handling**

let val: Option\[Int\] \= Some(10)  
   
// Unwrap with default  
let n \= val.unwrap\_or(0)  
   
// Pattern match  
match val {  
  Some(n) \=\> use(n)  
  None    \=\> handle\_absent()  
}  
   
// Propagate None with ?  (inside a function returning Option)  
let n \= val?

# **10\. Compiler Pipeline**

| Stage | Description |
| :---- | :---- |
| **Lexer** | Converts UTF-8 source text into a flat token stream. Whitespace is not significant except for string literals. |
| **Parser** | Converts the token stream into an AST. Grammar is LL(1). Single deterministic parse path. No backtracking. |
| **Name Resolution** | Resolves all identifiers to their declarations. Detects undefined names, shadowing, and circular dependencies. |
| **Type Checker** | Infers and verifies types throughout the AST. Checks interface satisfaction, generic bounds, and ownership constraints. |
| **Contract Verifier** | Feeds contracts and type information to the Z3 SMT solver. Marks unverifiable contracts for runtime guard emission. |
| **AXIOM IR** | Lowers typed AST to a simple, explicit, fully-typed intermediate representation. Human-readable. Platform-independent. |
| **Optimizer** | Performs dead code elimination, inlining, and constant folding at the IR level. Elides statically-proven contract checks. |
| **LLVM Backend** | Lowers AXIOM IR to LLVM IR. LLVM performs backend optimisation and emits machine code or WASM. |

## **10.1  AXIOM IR**

AXIOM IR is an explicit, typed, SSA-form intermediate representation. Every operation has an explicit type. Control flow is explicit. Ownership transfers are annotated. The IR is designed to be readable by both humans and AI systems.

; AXIOM IR — illustrative excerpt  
fn @add(%a: Int, %b: Int) \-\> Int {  
block entry:  
  %result \= add.Int %a, %b  
  ret.Int %result  
}

## **10.2  Bootstrapping Phases**

| Phase | Compiler Written In | What It Compiles |
| :---- | :---- | :---- |
| **0** | Rust | Minimal AXIOM subset (no contracts, limited generics) |
| **1** | AXIOM subset | Full AXIOM language — compiled by Phase 0 |
| **2** | Full AXIOM | Full AXIOM compiler — compiled by Phase 1 |
| **3** | Full AXIOM | Self-hosting. Phase 0 Rust compiler retired. |

# **11\. Target Platforms**

AXIOM produces output via two paths: LLVM for native and WASM for portable bytecode. Both paths are first-class. Platform-specific code is isolated in the standard library platform modules.

## **11.1  Native Targets via LLVM**

| Target Triple | Platform |
| :---- | :---- |
| **x86\_64-unknown-linux-gnu** | Linux 64-bit |
| **x86\_64-pc-windows-msvc** | Windows 64-bit |
| **x86\_64-apple-darwin** | macOS Intel |
| **aarch64-apple-darwin** | macOS Apple Silicon |
| **aarch64-apple-ios** | iOS |
| **aarch64-linux-android** | Android |
| **riscv64gc-unknown-linux-gnu** | RISC-V Linux |

## **11.2  WebAssembly**

The WASM target produces wasm32 binaries via LLVM's WebAssembly backend. WASI is supported for system-interface access outside the browser. The WASM binary contains no AXIOM runtime — it is self-contained.

## **11.3  C Interoperability**

AXIOM has zero-cost C FFI. C functions and types are declared in extern blocks. The compiler generates no wrapper code. C ABI calling conventions are used directly. Unsafe is required because the compiler cannot verify C memory safety.

extern "C" {  
  fn malloc(size: UInt) \-\> \*UInt8  
  fn free(ptr: \*UInt8)  
  fn strlen(s: \*UInt8) \-\> UInt  
}  
   
fn c\_string\_length(ptr: \*UInt8) \-\> UInt {  
  unsafe { return strlen(ptr) }  
}

# **12\. Error Message Philosophy**

Error messages are part of the language design. A compiler that produces cryptic errors is a language that is hard to use. Every error in AXIOM must satisfy four criteria:

| LOCATION | Point to the exact source location causing the error. Not a line range. The exact token. |
| :---: | :---- |

| CAUSE | Explain what the compiler expected and what it found. In plain language, not compiler jargon. |
| :---: | :---- |

| IMPLICATION | Explain why this is an error. Not every programmer knows why you cannot have two mutable borrows. |
| :---: | :---- |

| SUGGESTION | Offer a concrete fix where one can be inferred. The compiler should solve problems, not just report them. |
| :---: | :---- |

### **Example — Ownership Error**

error\[E0101\]: value used after move  
  \--\> src/main.ax:14:5  
   |  
12 |   consume(v)         // v moved here  
   |           ^ ownership of \`v\` moved into \`consume\`  
13 |  
14 |   read\_only(\&v)      // v used here after move  
   |             ^ \`v\` no longer valid here  
   |  
   \= Values can only have one owner. When you passed \`v\` to \`consume\`,  
     ownership transferred. You cannot use \`v\` after that point.  
   \= help: if \`consume\` does not need to own the data, change its  
     parameter to a borrow:  fn consume(data: \&Vec\[Int\])

### **Example — Contract Violation**

error\[E0202\]: contract pre-condition cannot be satisfied  
  \--\> src/main.ax:8:3  
   |  
 6 |   fn divide(a: Float64, b: Float64) \-\> Float64  
 7 |     requires: b \!= 0.0  
 8 |   let result \= divide(x, 0.0)  
   |                ^^^^^^^^^^^^^^  
   |  
   \= The \`requires\` clause of \`divide\` states that \`b\` must not be 0.0.  
     You are passing the literal 0.0 as \`b\`, which always violates this.  
   \= help: check \`b\` before calling, or use a checked division function  
     that returns Option\[Float64\].

# **13\. Complete Example Program**

The following program demonstrates: module declaration, types with invariants, structural interface satisfaction, generics, error handling, and ownership — in a single working program. It implements a bounded stack.

module collections.stack  
   
use axiom.io  
   
// ── Type with invariants ──────────────────────────────────  
   
pub type Stack\[T\] \= {  
  items:    Vec\[T\];  
  capacity: UInt;  
  invariant: items.len() \<= capacity;  
  invariant: capacity \> 0;  
}  
   
// ── Constructor ───────────────────────────────────────────  
   
pub fn Stack.new\[T\](capacity: UInt) \-\> Result\[Stack\[T\], Str\]  
  requires: capacity \> 0  
  ensures:  result is Ok  
{  
  if capacity \== 0 {  
    return Err("capacity must be greater than zero")  
  }  
  return Ok(Stack\[T\] {  
    items:    Vec\[T\].with\_capacity(capacity),  
    capacity: capacity,  
  })  
}  
   
// ── Push ──────────────────────────────────────────────────  
   
pub fn Stack.push\[T\](self: \&mut Stack\[T\], value: T) \-\> Result\[(), Str\]  
  requires: self.items.len() \<= self.capacity  
  ensures:  result is Ok \=\> self.items.len() \== self.items.len()@pre \+ 1  
{  
  if self.items.len() \== self.capacity {  
    return Err("stack is full")  
  }  
  self.items.push(value)  
  return Ok(())  
}  
   
// ── Pop ───────────────────────────────────────────────────  
   
pub fn Stack.pop\[T\](self: \&mut Stack\[T\]) \-\> Option\[T\] {  
  return self.items.pop()  
}  
   
pub fn Stack.peek\[T\](self: \&Stack\[T\]) \-\> Option\[\&T\] {  
  return self.items.last()  
}  
   
pub fn Stack.is\_empty\[T\](self: \&Stack\[T\]) \-\> Bool {  
  return self.items.len() \== 0  
}  
   
// ── Interface: Printable ──────────────────────────────────  
   
interface Printable {  
  fn to\_str(self: \&Self) \-\> Str  
}  
   
// Stack\[Int\] satisfies Printable structurally  
pub fn Stack.to\_str(self: \&Stack\[Int\]) \-\> Str {  
  return "Stack(" \+ self.items.join(", ") \+ ")"  
}  
   
// ── Entry point ───────────────────────────────────────────  
   
fn main() \-\> Result\[(), Str\] {  
  var s \= Stack.new\[Int\](3)?  
   
  s.push(10)?  
  s.push(20)?  
  s.push(30)?  
   
  match s.push(40) {  
    Ok(\_)  \=\> io.print("unexpected success")  
    Err(e) \=\> io.print("correctly rejected: " \+ e)  
  }  
   
  while \!s.is\_empty() {  
    match s.pop() {  
      Some(v) \=\> io.print(v.to\_str())  
      None    \=\> {}  
    }  
  }  
   
  return Ok(())  
}

# **14\. Comparison With Existing Languages**

| Feature | AXIOM | Rust | Go / Zig |
| :---- | :---- | :---- | :---- |
| **Memory model** | Ownership-lite | Full borrow checker | GC / manual |
| **Contracts** | First-class, SMT-backed | None (assertions only) | None |
| **Null safety** | No null — Option\[T\] | No null — Option\<T\> | Null exists (Go) |
| **Error handling** | Result\[T,E\], no throws | Result\<T,E\>, no throws | Multi-return / Result |
| **Generics** | Comptime monomorphised | Monomorphised | Generics (Go) / comptime (Zig) |
| **Interfaces** | Structural | Nominal (trait impls) | Structural (Go) |
| **GC** | None | None | Yes (Go) / None (Zig) |
| **WASM target** | First-class | Supported | Limited (Go) / Yes (Zig) |
| **C FFI** | Zero-cost, first-class | Zero-cost, first-class | Zero-cost (Zig) |
| **Self-hosted** | Planned (Phase 3\) | Yes | Yes / Planned |
| **Grammar ambiguity** | None — canonical form | Some | Minimal |

# **15\. Build Roadmap**

The following estimates assume a team of two to three compiler engineers with prior experience in at least one systems language. All timelines are realistic minimums, not targets. Compiler development consistently takes longer than estimated.

## **Phase 0 — Prototype Compiler  (6–10 months)**

Written in Rust. Compiles a minimal subset of AXIOM: primitives, functions, let/var bindings, if/match, basic structs. No generics, no contracts, no modules. Goal: Hello World compiles to native binary and to WASM.

* Define EBNF grammar fully before writing any code

* Implement Lexer — tokenise all valid AXIOM source

* Implement Parser — produce typed AST from token stream

* Implement basic type checker — primitives and function signatures

* Emit LLVM IR for subset — link and run

* Emit WASM via LLVM WebAssembly backend

* Test suite: 200+ parser tests, 100+ type checker tests

## **Phase 1 — Full Language  (12–18 months)**

Still compiled by Phase 0 Rust compiler. Adds the full language surface: generics, ownership checker, contracts, modules, async, channels, error handling, C FFI, standard library core.

* Ownership model — borrow checker implementation

* Generic type parameters via comptime

* Contract syntax — requires / ensures / invariant

* SMT solver integration (Z3 via C FFI)

* Module system and package manifest

* Async runtime and channel primitives

* Standard library: core, io, collections, string, math, ffi

* Package manager prototype — local resolution only

* Canonical formatter (axiom fmt)

* Language server (LSP) prototype for editor integration

## **Phase 2 — Self-Hosting  (12–18 months)**

Rewrite the AXIOM compiler in AXIOM itself. Compiled by Phase 1\. This is the most difficult phase — the language must be stable enough that the compiler can be its own largest test case.

* Rewrite Lexer in AXIOM — compiled by Phase 1 compiler

* Rewrite Parser in AXIOM

* Rewrite type checker in AXIOM

* Rewrite IR emitter and LLVM bindings in AXIOM

* Compile new compiler with Phase 1 compiler

* New compiler compiles itself — bootstrap complete

* Phase 0 Rust compiler retired

* Full contract static verification — SMT proof coverage target: 60%+

## **Phase 3 — Stability & Ecosystem  (ongoing)**

Language specification locked. Breaking changes require a formal proposal and deprecation period. Ecosystem development — package registry, documentation tooling, IDE integration, additional compiler targets.

* Public package registry

* Documentation generator (axiom doc)

* Additional LLVM targets as needed

* WASI full compliance

* Formal specification document — normative, implementer-facing

* Third-party compiler implementations welcomed

## **Realistic Total Timeline**

Phase 0 through self-hosting: 30 to 46 months with an experienced team. Rust took approximately 8 years from start to 1.0. Go took 3 years with a large Google team. Zig is still pre-1.0 after 8 years. These timelines are normal. A language that cuts corners to ship faster will have the wrong corners cut forever.

**AXIOM Language Reference — Version 0.2**

This specification defines the language only. Standard library, toolchain, and ecosystem are separate documents.

All syntax and semantics subject to revision until Version 1.0.