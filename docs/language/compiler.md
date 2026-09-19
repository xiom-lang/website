<!--
Copyright (c) 2026 Eleftherios Notas and XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Compiler

## Pipeline

```
.xi source
  -> Lexer           (tokenize -- 55+ token kinds)
  -> Parser          (AST -- LL(1), no backtracking)
  -> Type Checker    (primitives, structs, functions, interface satisfaction, Send/Sync)
  -> Borrow Checker  (lexical scope -- &T, &mut T, move semantics, E001 warnings)
  -> CTFE            (compile-time function evaluation -- const exprs, builtins, pure fn VM)
  -> LLVM IR         (text emission, human-readable)
     |- Contracts   (runtime guards -- @llvm.trap on violation)
     |- DWARF DI    (function-level debug metadata -- per-function !DISubprogram)
     |- Derive      (Eq, Clone, Display, Hash, Ord, Debug -- struct + enum)
     |- Generics    (monomorphisation -- register + specialize, worklist)
     `- Parallel    (rayon per-function IR emission -- --parallel-codegen)
  -> clang           (native .exe, .out, .wasm)
```

## Architecture

XIOM is a Rust toolchain of 20 crates. It emits LLVM IR as text and hands
it to clang for the final binary, so there is no LLVM library dependency
and the generated IR is readable by humans. The bootstrap compiler is Rust
by design and permanent; self-hosting gates are cleared, but no
self-hosted release has shipped yet.

Design decisions that shape everything else:

- **Lexical scope borrowing** instead of lifetime annotations: a borrow
  expires where it is visible in the source, so checking needs no lifetime
  calculus.
- **Contracts compile to runtime guards**, with an SMT-LIB path for Z3
  verification. Static proof is an additional mode, not a prerequisite for
  running code.
- **Text IR emission** keeps the backend debuggable and portable; clang is
  the only external tool used for codegen.
- **Implicit `self`** and inline type constraints (`[T: Ord]`) keep
  signatures short; `derive` generates the repetitive interfaces.

## Modes

The compiler behaves differently depending on how it is invoked and which
flags are set. This section explains the modes; the reference tables below
list every flag.

### Build modes

- Default (`xiom file.xi`): native binary with debug-friendly codegen.
- `--release`: clang `-O3`. Contract guards and debug checks are stripped
  unless `--runtime-contracts` / `--keep-debug-checks` are passed.
- `--lto`: ThinLTO whole-program optimization.
- `--target wasm|arm`, `--shared`: cross-compilation and library output.

### Execution modes

- `xiom build`: compile a package (directory containing `package.xi`).
- `xiom run <file>`: scripting mode. Shebang scripts, inline `-e`, stdin
  `-`, and `--watch` are supported, and top-level code is wrapped
  automatically, so `fn main()` is optional.
- `xiom repl`: interactive shell.
- `--jit` and `--jit --lazy`: in-process JIT with an optional incremental
  cache; `--cache` caches binaries by source hash.
- `--standalone script.xi -o app`: turn a script into a binary.

### Contract modes

Contracts (`requires:` / `ensures:` / `invariant:`) are part of the
language, not annotations. By default they compile to runtime guards that
trap on violation. `--no-contracts` removes the guards. `--release` strips
them unless `--runtime-contracts` forces them. Static proof is a separate
path: `--dump-contracts` emits SMT-LIB and `--verify` runs Z3 over that
output.

### Debug and diagnostics

- `--debug` / `-g`: DWARF/PDB metadata for debuggers.
- Debug intrinsics: `assert(cond[, msg])`, `dbg!()`, `todo!()`,
  `unimplemented!()`, and `debugger;`. These are stripped in release builds
  unless `--keep-debug-checks` is passed.
- `--diagnostics=json`: structured output for tooling.
- `--explain T001`: explain an error code.
- `--emit-tokens`, `--emit-ir`, `--check`: inspect a single compilation
  stage.

### AI-assisted diagnostics (`--ai`)

The compiler can send compilation errors to an LLM and get actionable hints
back. Results are written to `.xiom_ai.json`; source files are **never
modified**. Providers: Ollama (local, free), DeepSeek, OpenAI, OpenRouter,
Groq, and any OpenAI-compatible endpoint.

```bash
# local: nothing leaves the machine
ollama pull codellama
xiom --ai --ai-local source.xi

# any OpenAI-compatible provider
export XIOM_AI_ENDPOINT=https://api.deepseek.com
export XIOM_AI_KEY=sk-...
export XIOM_AI_MODEL=deepseek-chat
xiom --ai source.xi
```

| Flag | Description |
|------|-------------|
| `--ai` | Enable AI diagnostics (Ollama or an API key required) |
| `--ai-local` | Local-only: never sends code to the cloud |
| `--ai-dry-run` | Print the prompt without calling the model |
| `--ai-silent` | Suppress stdout; write only `.xiom_ai.json` |
| `--ai-strict` | Refuse binary output on contract violations |
| `--ai-model=<name>` | Override the model |
| `--ai-timeout=<sec>` | Model timeout in seconds (default: 30) |

Configuration can also live in `.xiom_ai_config.json`, or in the
`XIOM_AI_KEY`, `XIOM_AI_ENDPOINT`, `XIOM_AI_MODEL` and `XIOM_AI_PROVIDER`
environment variables. `xiom --help-ai` prints the full guide.

### MCP server and companion tools

`xiom-mcp` is a Model Context Protocol server (stdio, JSON-RPC 2.0) that
lets AI agents compile-check XIOM code, read the language and workflow
guides, and query the standard library reference as tools. Register it in
any MCP-capable client:

```json
{
  "mcpServers": {
    "xiom": { "command": "C:\\path\\to\\xiom-mcp.exe" }
  }
}
```

Build it from source with `cargo build --release -p xiom-mcp`.

The toolchain also includes `xiom-fmt`, `xiom-doc`, `xiom-ffigen`,
`xiom-pkg`, `xiom-lsp`, `xiom-mcp`, `xiom-dbg` and `xiom-verify`. Release
archives ship `bin/xiom` today and will add `bin/xiom-pkg`; the remaining
tools are built from source with `cargo build --release -p <crate>`.

### Safety modes

- Integer overflow checks are ON by default; `--no-overflow-checks`
  disables them.
- `--strict-mode` turns borrow-checker warnings (E001) into hard errors;
  `--strict-exhaustive` makes non-exhaustive matches a hard error.
- `--sanitize=address|undefined|thread`: sanitizer instrumentation.
- Unsafe confinement: every `unsafe` block is a confined transaction.
  `#[unsafe_no_retry]` and `#[unsafe_direct]` (with
  `--enable-unsafe-direct`) are the explicit escape hatches.

### Concurrency, caching, and limits

- `--parallel`: parallel parsing; `--parallel-codegen`: per-function IR
  emission.
- `--max-depth <N>`: recursion limit (default: 500).

## CLI Reference

```
xiom [flags] <source.xi>
```

### Compilation Flags

| Flag | Description | Default |
|------|-------------|---------|
| `-o <output>` | Output binary path | `a.exe` (Win) / `a.out` (Linux) |
| `--run` | Compile and run, print exit code | -- |
| `--check` | Type-check only, no binary | -- |
| `--emit-ir` | Print LLVM IR to stdout | -- |
| `--release` | clang -O3 optimization | -- |
| `--debug` / `-g` | DWARF/PDB debug info (DIFile, DICompileUnit, DISubprogram) | off |
| `--lto` | ThinLTO link-time optimization (`-flto=thin`) | off |
| `--jit` | In-process DLL JIT compilation (xiom-jit) | off |
| `--jit --lazy` | JIT with SHA-256 incremental cache | off |
| `--cache` | Binary cache by source hash | off |
| `--no-cache` | Disable caching | -- |
| `--parallel` | Rayon-based parallel parse | off |
| `--parallel-codegen` | Rayon-based per-function IR emission | off |
| `--target wasm` | Compile to `wasm32-unknown-unknown` | native |
| `--target arm` | Compile to `aarch64-unknown-linux-gnu` | native |
| `--shared` | Compile to shared library (.dll/.so) | off |
| `--standalone <file> -o <exe>` | Script-to-binary | -- |

### Safety Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--overflow-checks` | Integer overflow traps (`@llvm.trap`) | **ON** (v0.56) |
| `--no-overflow-checks` | Disable overflow checks | -- |
| `--no-contracts` | Disable all contract runtime guards | off |
| `--strict-exhaustive` | Non-exhaustive match -> hard error | off |
| `--sanitize=address` | Enable ASan | off |
| `--sanitize=undefined` | Enable UBSan | off |
| `--sanitize=thread` | Enable TSan | off |
| `--strict-mode` | Borrow errors (E001) become hard errors | off |
| `--runtime-contracts` | Force contract guards in release builds | off |
| `--keep-debug-checks` | Keep debug intrinsics in release builds | off |
| `--enable-unsafe-direct` | Allow `#[unsafe_direct]` trusted escapes | off |

### Utility Flags

| Flag | Description |
|------|-------------|
| `--version` | Print version + test stats |
| `--help` | Print usage |
| `--explain T001` | Error code reference |
| `--emit-tokens` | Print token stream |
| `--verify` | Z3 formal verification (requires `--dump-contracts`) |
| `--dump-contracts` | SMT-LIB contract generation |
| `--diagnostics=json` | Structured compiler output |
| `--max-depth <N>` | Max recursion depth (default: 500) |

### Scripting Mode

```
xiom run <file.xi>          Execute script
xiom run -e "code"           Inline expression
xiom run -                   stdin script
xiom run --watch <file>      Watch + re-run
xiom run --jit <file>        In-process DLL JIT
xiom run --jit --lazy <file> JIT with incremental cache
xiom run --cache <file>      Binary cache for instant re-run
xiom run --no-cache          Disable caching
```

### Other Commands

```
xiom build-runtime            Build libxiom_runtime.dll/.so
xiom repl                     Interactive shell
xiom doctor                   Check toolchain
xiom clean                    Remove build artifacts
xiom clean --cache            Clear JIT cache
```

## Targets

| Target | Status |
|--------|--------|
| `x86_64-pc-windows-msvc` | [OK] Verified |
| `x86_64-unknown-linux-gnu` | [OK] Verified (WSL build + compile + run) |
| `wasm32-unknown-unknown` | [OK] Verified |
| `aarch64-apple-darwin` | Planned |

## Language Features

| Feature | Status | Since |
|---------|--------|-------|
| `move` keyword (spawn captures) | `spawn move { ... }` | v0.56 |
| Overflow checks ON by default | `--overflow-checks` default true | v0.56 |
| Parallel codegen | `--parallel-codegen` | v0.56 |
| DWARF debug info | `--debug` / `-g` | v0.56 |
| Thread-local recursion counter | `@xiom_recursion_counter thread_local` | v0.56 |
| Send/Sync enforcement | Auto-derived, spawn capture check | v0.56 |
| Spawn move semantics | Capture analysis + env forwarding | v0.56 |
| Unsafe confinement | Confined `unsafe` transactions, guard heap, fault trapping | v0.57 |
| Debug intrinsics | `assert`, `dbg!`, `todo!`, `unimplemented!`, `debugger;` | v0.58 |
| Secure numeric policy | `Int` / `Float64` mixing requires explicit `as` | v0.58 |
| Labeled loops | `@label: while` / `break @label;` | v0.58 |
| Release-stripped contracts | `--runtime-contracts` retains them | v0.58 |

## Selfhost Gate Status

All self-hosting gates are cleared, but no self-hosted release has shipped
yet; the released compiler remains the bootstrap toolchain. Remaining work
is tracked in the compiler repository (`docs/PRE_SELFHOST_GAPS.md`).

## Architecture Decisions

| Decision | Status |
|----------|--------|
| Bootstrap compiler | **Rust** (permanent) |
| LLVM backend | **Text IR emission** (no library dependency) |
| WASM target | via clang |
| Ownership model | **Lexical scope borrowing** |
| Contracts | **Runtime guards** + Z3 (SMT-LIB) |
| Type constraints | **Inline** `[T: Ord]` |
| Method receiver | **Implicit** `self`, inferred |
| Crate structure | 20 crates (xiom, xiom-ast, xiom-lowering, xiom-check, xiom-lexer, xiom-parser, xiom-codegen, xiom-ctfe, xiom-jit, xiom-verify, xiom-fmt, xiom-lsp, xiom-pkg, xiom-mcp, xiom-doc, xiom-ffigen, xiom-dbg, xiom-display, xiom-graph, xiom-wasm) |

## Build from Source

```bash
git clone https://github.com/xiom-lang/xiom.git
cd xiom
cargo build -p xiom
cargo test -p xiom-codegen --test e2e_tests
```
