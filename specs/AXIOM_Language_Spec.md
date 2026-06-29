  
**AXIOM**

Language Specification & Build Guide

Version 0.1 — Conceptual Foundation

| A compiled, contract-first, AI-native systems language targeting WASM \+ Vulkan \+ LLVM |
| :---: |

# **1\. Vision & Philosophy**

AXIOM is a systems programming language designed around three core beliefs that no existing language fully satisfies simultaneously:

| SAFE | Memory safety without a garbage collector. Ownership is explicit and verified at compile time. |
| :---: | :---- |

| VERIFIED | Contracts are first-class language constructs, not documentation. The compiler enforces them. |
| :---: | :---- |

| AI-NATIVE | Unambiguous grammar, dense semantics, and self-describing contracts minimize token cost for AI-generated code. |
| :---: | :---- |

AXIOM compiles via LLVM to native code, WASM, and GPU-adjacent targets via Vulkan bindings. It is self-hostable — the compiler is written in AXIOM once the language is stable enough to bootstrap.

# **2\. Design Principles**

## **2.1 Unambiguous Grammar**

Every construct in AXIOM has exactly one canonical form. No style debates, no semicolons vs no semicolons, no multiple ways to declare the same thing. The grammar is deterministic and parseable without context. This directly reduces token cost when AI generates AXIOM code.

## **2.2 Explicit Over Implicit**

No hidden constructors, no operator overloading surprises, no implicit type coercions. If memory is allocated, you see it. If a function can fail, the type says so. What you read is exactly what runs.

## **2.3 Contracts As First-Class Citizens**

Pre-conditions, post-conditions, and invariants are part of the function signature — not comments, not asserts, not separate test files. The compiler verifies them statically where possible and inserts runtime checks where not.

fn attack(attacker: Player, target: Player) \-\> (Player, Player)

  requires: attacker.alive

  requires: target.health \> 0

  ensures:  result.1.health \< target.health

  ensures:  result.0.alive

## **2.4 No Nulls**

There is no null or nil. Absence is expressed via the Option\[T\] type. The compiler enforces handling of the absent case everywhere. Null pointer exceptions are a compile error category, not a runtime surprise.

## **2.5 Errors Are Values**

No exceptions. Functions that can fail return Result\[T, E\]. Error handling is explicit in the call site. Propagation is syntactic sugar, not magic.

## **2.6 Structural Typing**

Types are compatible by shape, not by declared hierarchy. If a type has the required fields and methods, it satisfies the interface. This allows AI to compose types freely without navigating deep inheritance trees.

## **2.7 Comptime Metaprogramming**

Code that runs at compile time is marked with the comptime keyword. Generics, reflection, and code generation all flow through this single mechanism. No preprocessor, no macros, no templates — one clean system.

# **3\. Syntax Overview**

## **3.1 Primitives & Types**

| Type | Description | Example |
| :---- | :---- | :---- |
| **Int** | Platform-width signed integer | let x: Int \= 42 |
| **Int32 / Int64** | Explicit width integers | let y: Int64 \= 100\_000 |
| **Float32 / Float64** | IEEE 754 floats | let f: Float64 \= 3.14 |
| **Bool** | True or false only | let alive: Bool \= true |
| **Str** | Immutable UTF-8 string | let name: Str \= "AXIOM" |
| **Char** | Single Unicode codepoint | let c: Char \= 'A' |
| **Option\[T\]** | Present or absent value | let val: Option\[Int\] \= Some(5) |
| **Result\[T,E\]** | Success or typed error | fn load() \-\> Result\[Data, IOError\] |
| **Vec\[T\]** | Growable typed array | let items: Vec\[Int\] \= \[1,2,3\] |
| **Map\[K,V\]** | Hash map | let m: Map\[Str, Int\] \= {} |

## **3.2 Variable Declaration**

let x: Int \= 10           // immutable binding

var y: Int \= 10           // mutable binding

let name \= "AXIOM"        // type inferred

let items: Vec\[Int\] \= \[\]  // explicit generic

## **3.3 Functions**

fn add(a: Int, b: Int) \-\> Int {

  return a \+ b

}

// With contracts

fn divide(a: Float64, b: Float64) \-\> Float64

  requires: b \!= 0.0

  ensures:  result \* b \== a

{

  return a / b

}

## **3.4 Types & Structs**

type Vector3 \= {

  x: Float32

  y: Float32

  z: Float32

  magnitude: Float32  derived (sqrt(x\*x \+ y\*y \+ z\*z))

}

The derived keyword creates a computed field. It is recalculated automatically when dependencies change and cannot be set manually. This pattern replaces property getters with a declarative intent.

## **3.5 Enums**

enum AgentState {

  Idle

  Patrolling(route: Vec\[Vector3\])

  Attacking(target: EntityId)

  Dead(cause: DamageCause)

}

## **3.6 Interfaces (Structural)**

interface Damageable {

  health: Int

  fn takeDamage(amount: Int) \-\> Self

    requires: amount \>= 0

    ensures:  result.health \<= self.health

}

Any type with a health: Int field and a matching takeDamage function satisfies Damageable automatically. No implements keyword needed.

## **3.7 Error Handling**

fn loadFile(path: Str) \-\> Result\[File, IOError\] {

  let f \= open(path)?   // ? propagates error up

  return Ok(f)

}

// Call site must handle both cases

match loadFile("data.bin") {

  Ok(file)  \=\> process(file)

  Err(e)    \=\> log.error(e.message)

}

# **4\. Memory Model**

AXIOM uses a ownership-lite model. Simpler than Rust's borrow checker, safer than C/C++. The compiler tracks ownership through three rules:

| Rule | Description |
| :---- | :---- |
| **Single Owner** | Every value has exactly one owner at any time. Assignment transfers ownership. |
| **Borrow Read** | Multiple simultaneous read references allowed. No writes during active reads. |
| **Borrow Write** | Exactly one write reference at a time. No reads or other writes simultaneously. |
| **Clone Explicit** | Copying a value is always explicit via .clone(). No silent deep copies. |
| **No GC** | Memory is freed when the owner goes out of scope. Deterministic. No pauses. |

fn process(data: Vec\[Int\]) {          // takes ownership

  // data freed here automatically

}

fn inspect(data: \&Vec\[Int\]) {          // read borrow

  // caller still owns data

}

fn mutate(data: \&mut Vec\[Int\]) {       // write borrow

  data.push(99)

}

# **5\. Contract System — The Core Innovation**

Contracts in AXIOM are not assertions that crash at runtime. They are formal specifications that the compiler reasons about. This is the feature that makes AXIOM uniquely suited to AI-generated code.

## **5.1 Contract Keywords**

| Keyword | Meaning |
| :---- | :---- |
| **requires** | Pre-condition — must be true when function is called |
| **ensures** | Post-condition — must be true when function returns |
| **invariant** | Must be true at all times for this type |
| **result** | Special variable referring to the return value inside ensures |
| **self@pre** | Value of self at the time the function was called (for ensures) |

## **5.2 Type Invariants**

type Health {

  value: Int

  max:   Int

  invariant: value \>= 0

  invariant: value \<= max

  invariant: max \> 0

}

The compiler guarantees these invariants hold after every mutation. Any code path that could violate them is a compile error, not a runtime crash.

## **5.3 AI Code Verification Flow**

When AI generates an AXIOM function, the contract layer acts as an automatic reviewer:

* AI writes function with contracts

* Compiler attempts static verification of contracts

* Verified statically — no runtime cost, zero overhead

* Cannot verify statically — compiler inserts minimal runtime checks

* Contract logically impossible — compile error, AI must regenerate

* Human reviews contracts, not implementation — massively reduced review surface

# **6\. Concurrency Model**

AXIOM treats concurrency as a first-class concern, not a library bolt-on. Three primitives cover all cases:

## **6.1 Async / Await**

async fn fetchData(url: Str) \-\> Result\[Bytes, NetError\] {

  let response \= await http.get(url)?

  return Ok(response.body)

}

## **6.2 Channels — Message Passing**

let (sender, receiver) \= Channel\[Message\].new()

spawn {

  sender.send(Message.Ping)

}

match receiver.recv() {

  Message.Ping \=\> sender.send(Message.Pong)

  \_            \=\> {}

}

## **6.3 Parallel Iterators**

let results \= items.par\_map(fn(item) {

  heavyCompute(item)

})

par\_map distributes work across available cores automatically. The ownership model guarantees no data races at compile time — parallel code has the same safety guarantees as single-threaded code.

# **7\. Compiler Architecture**

## **7.1 Pipeline**

| Stage | Description |
| :---- | :---- |
| **Lexer** | Converts source text to tokens. Whitespace significant for blocks, no semicolons. |
| **Parser** | Builds AST from token stream. Grammar is LL(1) — no ambiguity, single parse path. |
| **Semantic Analysis** | Type checking, name resolution, interface satisfaction, scope analysis. |
| **Contract Verifier** | Attempts static proof of contracts using SMT solver (Z3). Marks unverifiable ones for runtime. |
| **IR Generation** | Lowers typed AST to AXIOM IR — a simple, explicit intermediate representation. |
| **Optimizer** | Dead code elimination, inlining, contract elision for statically proven contracts. |
| **LLVM Backend** | AXIOM IR → LLVM IR → native machine code / WASM / GPU targets. |

## **7.2 AXIOM IR**

AXIOM IR is the internal representation between the language frontend and LLVM. It is explicitly typed, has no implicit control flow, and is human-readable for debugging. AI can target AXIOM IR directly for performance-critical code generation without going through the full language frontend.

## **7.3 Bootstrapping Plan**

| Phase | Compiler Implementation |
| :---- | :---- |
| **Phase 0 — Prototype** | Compiler written in Rust. Targets a minimal AXIOM subset only. |
| **Phase 1 — Core** | Minimal AXIOM compiler written in AXIOM subset. Compiled by Phase 0\. |
| **Phase 2 — Full** | Full AXIOM compiler written in AXIOM. Compiled by Phase 1\. |
| **Phase 3 — Self-hosted** | Full compiler compiles itself. Phase 0 Rust compiler retired. |

# **8\. Target Platforms**

## **8.1 Native via LLVM**

LLVM handles all native code generation targets. AXIOM gets these for free once LLVM IR output is working:

* x86-64 — Windows, Linux, macOS

* ARM64 — macOS Apple Silicon, iOS, Android

* RISC-V — Embedded and future hardware

* PS5 / Xbox Series — Via PlayStation SDK and GDK (same LLVM backend, different libs)

## **8.2 WebAssembly**

WASM is a primary target from day one, not an afterthought. AXIOM → LLVM → WASM32 produces binaries that run in:

* All modern browsers via the standard WASM runtime

* Node.js and Deno on the server

* Edge compute platforms (Cloudflare Workers, Fastly)

* WASI-compatible runtimes for server-side execution without a browser

* Embedded WASM runtimes on IoT and future hardware

WASM as a target means AXIOM code is deployable to virtually any compute environment that will exist in the next decade without recompilation.

## **8.3 GPU via Vulkan**

Vulkan is the lowest common GPU denominator. AXIOM provides Vulkan bindings via C FFI. Translation layers handle platform-specific GPU APIs:

| Platform | GPU Path |
| :---- | :---- |
| **Windows / Linux** | AXIOM → Vulkan (native) |
| **macOS / iOS** | AXIOM → Vulkan → MoltenVK → Metal |
| **Android** | AXIOM → Vulkan (native Android support) |
| **Xbox Series** | AXIOM → Vulkan → VKD3D → DirectX 12 |
| **PS5** | AXIOM → GNM SDK (Vulkan-adjacent architecture) |
| **WebGPU** | AXIOM → WebGPU API → browser translates to Vulkan/Metal/DX12 |

## **8.4 C Interoperability**

AXIOM has first-class C FFI. Any C library is callable with zero overhead. This is critical for the ecosystem bootstrap — AXIOM does not need to rewrite OpenGL, SDL, Bullet Physics, or any existing C library. It wraps them with safe AXIOM interfaces.

extern "C" {

  fn SDL\_Init(flags: Uint32) \-\> Int32

  fn SDL\_CreateWindow(title: \*Char, x: Int, y: Int,

                      w: Int, h: Int, flags: Uint32) \-\> \*SDL\_Window

}

# **9\. Standard Library — Minimum Viable Scope**

The stdlib ships with the compiler. It covers the essentials and no more. Domain-specific functionality lives in the package ecosystem.

| Module | Contents | Status |
| :---- | :---- | :---- |
| **axiom.core** | Primitives, Option, Result, panic, assert | Required |
| **axiom.io** | File system, stdin/stdout, paths | Required |
| **axiom.net** | TCP/UDP/HTTP, async sockets | Required |
| **axiom.collections** | Vec, Map, Set, Queue, Ring | Required |
| **axiom.string** | UTF-8 ops, formatting, parsing | Required |
| **axiom.math** | Numerics, vectors, matrices, SIMD | Required |
| **axiom.async** | Async runtime, channels, spawn | Required |
| **axiom.ffi** | C interop helpers, unsafe block | Required |
| **axiom.wasm** | WASM-specific runtime APIs | Platform |
| **axiom.gpu** | Vulkan bindings, shader types | Platform |
| **axiom.reflect** | Comptime type introspection | Optional |

# **10\. Build Roadmap**

## **Phase 0 — Foundation (Months 1-6)**

Goal: A working compiler for a minimal AXIOM subset. Written in Rust.

* Define complete formal grammar (EBNF)

* Implement Lexer in Rust

* Implement Parser → AST in Rust

* Basic type checker — primitives, structs, functions

* No contracts yet — defer to Phase 1

* LLVM IR output for simple functions

* Compile and run Hello World natively

* Compile and run Hello World in WASM

## **Phase 1 — Core Language (Months 6-14)**

Goal: The full language minus advanced contracts. Still compiled by Phase 0 Rust compiler.

* Full type system — generics, enums, interfaces

* Ownership model — borrow checker lite

* Basic contracts — requires / ensures, runtime checks

* Error handling — Result, ? operator

* Async/await and channels

* C FFI layer

* Basic stdlib: core, io, collections, string

* Package manager prototype

## **Phase 2 — Self-Hosting (Months 14-24)**

Goal: Rewrite the AXIOM compiler in AXIOM. Bootstrap.

* Rewrite Lexer in AXIOM

* Rewrite Parser in AXIOM

* Rewrite type checker in AXIOM

* Compile new AXIOM compiler with Phase 0 Rust compiler

* New AXIOM compiler compiles itself — bootstrapped

* Retire Phase 0 Rust compiler

* Static contract verification via SMT solver integration (Z3)

## **Phase 3 — Ecosystem (Months 24-48)**

Goal: Production ready. Vulkan GPU layer. Package ecosystem.

* Vulkan bindings via axiom.gpu

* Full WASM \+ WASI target support

* WebGPU bindings for browser GPU access

* Platform SDKs: iOS, Android, console targets

* Language server protocol (LSP) for editor support

* Formatter and linter (single canonical style)

* Package registry — public and private

* First-party game framework library

# **11\. Team & Tooling Requirements**

## **Minimum Team to Execute Phase 0-1**

| Role | Responsibility |
| :---- | :---- |
| **Compiler Engineer x2** | Lexer, parser, type checker, LLVM IR generation |
| **Language Designer x1** | Grammar spec, contract semantics, stdlib API design |
| **Runtime Engineer x1** | Async runtime, memory model, WASM target |
| **Developer Advocate x1** | Documentation, examples, community building |

## **Core Tools**

* LLVM — compiler backend, maintained at llvm.org, Apache 2.0 license

* Z3 — SMT solver for static contract verification, MIT license

* Cranelift — alternative lightweight backend for fast debug builds

* WASI SDK — WebAssembly System Interface target support

* MoltenVK — Vulkan to Metal translation for Apple platforms

* tree-sitter — syntax highlighting and editor integration

# **12\. What You Can Build With AXIOM**

| Domain | What AXIOM Enables | Why It Fits |
| :---- | :---- | :---- |
| **Game Engines** | Full engine written in AXIOM, GPU via Vulkan, no GC pauses | Deterministic memory, frame-perfect control |
| **Game Logic** | Scripting layer compiled to WASM, sandboxed mod support | Safe plugin architecture, contracts catch bugs |
| **Web Apps** | Full stack in AXIOM, frontend via WASM, backend native | One language, one mental model, all targets |
| **Mobile Apps** | iOS via ARM64+UIKit FFI, Android via NDK FFI | C FFI covers all platform APIs |
| **AI Agent Systems** | Self-modifying agents with contract-verified rewrites | Homoiconic \+ contracts \= safe self-evolution |
| **OS / Embedded** | Kernel-level code, no runtime dependency, WASM firmware | No GC, no hidden allocations, bare metal ready |
| **Distributed Systems** | Type-safe message passing, identity in type system | First-class async, Result propagation |
| **Compilers** | Write new language compilers in AXIOM itself | Clean IR, comptime metaprogramming |

# **13\. AXIOM vs Today's Languages**

| Feature | AXIOM | Closest Alternative |
| :---- | :---- | :---- |
| **Memory Safety** | Ownership-lite, no GC | Rust (borrow checker, more complex) |
| **Contracts** | First-class, compiler-verified | Eiffel (1986, not mainstream) |
| **WASM Target** | Primary target | Rust (secondary), Go (limited) |
| **GPU Bindings** | Vulkan stdlib | Rust via ash crate (manual) |
| **AI Code Gen** | Unambiguous grammar, dense semantics | No language designed for this yet |
| **C Interop** | Zero cost FFI, first-class | Zig (closest), C (obviously) |
| **Async** | Built-in, unified model | Rust (complex), Go (goroutines, simpler) |
| **Bootstrapped** | Yes, in AXIOM itself | Rust, Go, Zig (all self-hosted) |
| **Learning Curve** | Moderate — simpler than Rust, stricter than Go | Go (easiest), Rust (hardest) |

# **14\. AXIOM As AGI Infrastructure**

The design decisions in AXIOM were made with one eye on conventional software and one eye on what an autonomous AI system would need from a language substrate. Every feature serves both use cases.

| AXIOM Feature | AGI Relevance |
| :---- | :---- |
| **Homoiconic core** | AI reads and rewrites its own AXIOM source at runtime |
| **Contract verification** | Each self-rewrite is automatically verified before deployment |
| **WASM deployment** | AI compiles itself to WASM and deploys to any available compute node |
| **Vulkan GPU access** | AI runs its own inference on any GPU without cloud dependency |
| **Distributed types** | AI identity persists across node failures via the type system |
| **C FFI** | AI accesses all OS capabilities via existing C interfaces |
| **Comptime** | AI generates specialized code at compile time for specific hardware |
| **Unambiguous grammar** | AI-to-AI communication in AXIOM is lossless and token-efficient |

The contract system is the critical safety layer. If core alignment constraints are expressed as type invariants and function contracts, the compiler enforces them on every self-rewrite. This does not solve alignment — but it makes alignment constraints enforceable at the language level rather than relying solely on training.

# **15\. Where To Start — Concrete First Steps**

If you want to actually build AXIOM, here is the most direct path from zero to a working prototype compiler:

## **Week 1-2 — Study These**

* Read the Crafting Interpreters book by Robert Nystrom — free online, best practical compiler intro

* Study the Zig compiler source — closest to what AXIOM targets philosophically

* Read LLVM Kaleidoscope tutorial — official LLVM intro using a toy language

* Study Z3 theorem prover docs — needed for contract verification

## **Week 3-4 — Specify the Grammar**

* Write the complete AXIOM grammar in EBNF notation

* Verify grammar is unambiguous — no shift-reduce conflicts

* Define the contract syntax formally

* Get the grammar reviewed by a PL theory person if possible

## **Month 2-3 — Build the Lexer and Parser**

* Implement Lexer in Rust — tokenize AXIOM source

* Implement Parser in Rust — build AST from tokens

* Write extensive test suite for both

* Target: can parse any valid AXIOM program into AST

## **Month 3-4 — Type Checker**

* Implement basic type inference

* Add struct and enum type checking

* Add interface structural satisfaction checking

* Target: reject all type-invalid programs with clear errors

## **Month 4-6 — LLVM IR Output**

* Integrate LLVM via inkwell (safe Rust LLVM bindings)

* Lower typed AST to LLVM IR for simple programs

* Generate working native binary from AXIOM source

* Generate working WASM binary from AXIOM source

* Target: Hello World compiles and runs on native and WASM

**AXIOM — Language Specification v0.1**

This document is a living specification. All syntax and APIs subject to revision.