<!--
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
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
- `--target wasm|arm|riscv`, `--shared`: cross-compilation and library
  output.

### Execution modes

- `xiom build`: build the project from `xiom.toml`; `xiom build --watch`
  keeps rebuilding on change.
- `xiom run <file>`: scripting mode. Shebang scripts, inline `-e`, stdin
  `-`, and `--watch` are supported, and top-level code is wrapped
  automatically, so `fn main()` is optional.
- `xiom repl`: interactive shell.
- `--jit` and `--jit --lazy`: in-process JIT with an optional incremental
  cache; `--cache` caches binaries by source hash.
- `--watch` / `--hot-reload`: recompile on change, optionally hot-swapping
  a shared library (`--hot-reload-contracts` verifies contracts first).
- `--standalone script.xi -o app`: turn a script into a binary.

### Contract modes

Contracts (`requires:` / `ensures:` / `invariant:`) are part of the
language, not annotations. By default they compile to runtime guards that
trap on violation. `--no-contracts` removes the guards. `--release` strips
them unless `--runtime-contracts` forces them.

Verification is a separate path with three distinct stages:

- **exported** -- `--dump-contracts` exports contract metadata (JSON) and
  `--verify` exports SMT-LIB proof obligations; no proof claim is made.
- **checked** -- `xiom-verify --check` runs the bundled `z3` over that
  output; the verdict is Proven, Violated or UNKNOWN.
- **proved** -- only a verdict of `unsat` (Proven) counts as a proof.
  Obligations the encoder cannot express faithfully are reported UNKNOWN
  and never count as proofs.

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
| `--ai-batch` (alias `--batch`) | Batch mode: analyze all sources into one `.xiom_ai.json` |
| `--ai-model=<name>` | Override the model |
| `--ai-timeout=<sec>` | Model timeout in seconds (default: 10) |

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

Build it from source with `cargo build --release -p xiom-mcp` if you
prefer; the release archives already ship it as `bin/xiom-mcp`.

Release archives ship the full toolchain in `bin/`: `xiom`, `xiom-pkg`,
`xiom-fmt`, `xiom-doc`, `xiom-ffigen`, `xiom-lsp`, `xiom-mcp`, `xiom-dbg`
and `xiom-verify`, plus a pinned `z3` for the verifier. The installer links
every `xiom*` tool into your PATH and leaves `z3` beside the tools.

### Safety modes

- Integer overflow checks are ON by default; `--no-overflow-checks`
  disables them.
- `--sanitize=address|undefined|leak|thread`: sanitizer instrumentation;
  `--stack-protector` adds stack canaries.
- `--strict` (alias `--strict-mode`) turns borrow-checker warnings (E001)
  into hard errors; `--strict-exhaustive` makes non-exhaustive matches a
  hard error.
- Unsafe confinement: every `unsafe` block is a confined transaction.
  `#[unsafe_no_retry]` and `#[unsafe_direct]` (with
  `--enable-unsafe-direct`) are the explicit escape hatches.
- `--sandbox` runs a safety audit over `unsafe` blocks; `--sandbox=strict`
  blocks compilation on HIGH severity findings, and
  `--sandbox-report=json` emits the report as JSON.

### Iteration, caching, and limits

- `--watch` recompiles on change; `--hot-reload` pairs it with shared
  library reloads, and `--hot-reload-contracts` verifies contracts before
  swapping function pointers.
- `--incremental` caches IR and skips unchanged sources; `--force`
  ignores every cache.
- `--parallel` / `--sequential` / `--jobs <N>` control parallelism;
  `--parallel-codegen` emits IR per function.
- `--timeout <seconds>` (default 300; 0 disables) and
  `--max-memory-mb <N>` bound a compilation; `--max-depth <N>` bounds
  recursion (default 500).

## CLI Reference

```
xiom [flags] <source.xi>
```

### Invocation and subcommands

| Command | Description |
|---------|-------------|
| `xiom <file.xi>` | Compile a single file |
| `xiom --run <file.xi>` | Compile and run (requires `fn main()`) |
| `xiom run <file.xi>` | Execute as a script (auto-wraps in `fn main()`) |
| `xiom run -` | Read the script from stdin |
| `xiom run -e "<code>"` | Execute inline code |
| `xiom build` | Build the project from `xiom.toml` |
| `xiom build --watch` | Build daemon: watch and rebuild |
| `xiom repl` | Interactive shell |
| `xiom doc <file.xi>` | Generate documentation (Markdown/HTML) |
| `xiom build-runtime` | Pre-compile the C runtime shared library (OrcJIT) |
| `xiom doctor` | Check toolchain dependencies |
| `xiom fmt` / `lsp` / `mcp` / `pkg` / `dbg` / `verify` / `ffigen` / `ai` / `graph` / `test` | Tool dispatchers for the companion binaries |

### Output, targets and debug builds

| Flag | Description |
|------|-------------|
| `-o <output>` | Output binary path (default `a.exe` / `a.out`) |
| `--emit-ir` | Print LLVM IR to stdout (no compilation) |
| `--emit-tokens` | Print the token stream |
| `--check` | Type-check only, no binary |
| `--release` | clang `-O3`; strips contract guards and debug checks unless re-enabled |
| `--debug` / `-g` | DWARF/PDB debug metadata |
| `--lto` | ThinLTO link-time optimization |
| `--shared` | Compile as a shared library (.dll/.so) |
| `--static` | Compile as a static library |
| `--opt-level <0..3>` | Explicit optimization level |
| `--standalone <file> -o <exe>` | Turn a script into a binary |
| `--target <target>` | `native` (default), `wasm`, `arm`, `riscv` |
| `--jit` / `--jit --lazy` | In-process JIT; `--lazy` adds the incremental cache |
| `--cache` / `--no-cache` | Binary cache by source hash / disable it |

### Contracts and verification

| Flag | Description |
|------|-------------|
| `--no-contracts` | Disable all contract runtime checks |
| `--runtime-contracts` | Force runtime contract checks, even in release |
| `--dump-contracts` | Export contract metadata (JSON) |
| `--verify` | Export SMT-LIB proof obligations (no proof claim) |
| `--verify-output <file>` | Write the SMT-LIB output to a file |
| `--keep-debug-checks` | Keep debug intrinsics in release builds |

### Safety and hardening

| Flag | Description |
|------|-------------|
| `--sandbox` | Safety audit over `unsafe` blocks (text report) |
| `--sandbox=strict` | Block compilation on HIGH severity findings |
| `--sandbox-report=json` | Emit the sandbox report as JSON |
| `--sanitize=address` | AddressSanitizer |
| `--sanitize=undefined` | UndefinedBehaviorSanitizer |
| `--sanitize=leak` | LeakSanitizer |
| `--sanitize=thread` | ThreadSanitizer |
| `--stack-protector` | Stack canaries (`-fstack-protector`) |
| `--overflow-checks` / `--no-overflow-checks` | Integer overflow traps (ON by default) |
| `--enable-unsafe-direct` | Allow `#[unsafe_direct]` in user code |
| `--strict` (alias `--strict-mode`) | Borrow-checker warnings (E001) become hard errors |
| `--strict-exhaustive` | Non-exhaustive matches become hard errors |

### Iteration and performance

| Flag | Description |
|------|-------------|
| `--watch` | Watch source files and recompile on change |
| `--hot-reload` | Watch plus shared-library hot reload |
| `--hot-reload-contracts` | Verify contracts before hot-swapping function pointers |
| `--incremental` | Cache compiled IR, skip unchanged sources |
| `--force` | Force recompile, ignore all caches |
| `--parallel` / `--sequential` | Parallel lex+parse (rayon) or force sequential |
| `--jobs <N>` | Number of parallel compile jobs (default: CPUs) |
| `--parallel-codegen` | Per-function IR emission |

### Diagnostics, graphs and limits

| Flag | Description |
|------|-------------|
| `--diagnostics=json` | Structured compiler output |
| `--explain <CODE>` | Explain an error code (e.g. `--explain T001`) |
| `--graph` / `--graph=mermaid` | Dependency graph as DOT or Mermaid |
| `--timeout <seconds>` | Compilation timeout (default 300; 0 disables) |
| `--max-memory-mb <N>` | Memory budget in MB (0 = disabled) |
| `--max-depth <N>` | Maximum recursion depth (default 500) |

### Linking

| Flag | Description |
|------|-------------|
| `--link <name>` | Link a native library (repeatable, e.g. `vulkan-1`) |
| `--link-path <dir>` | Add a library search path (repeatable) |
| `--c-source <file>` | Link an extra C/object file (repeatable) |

### Testing and benchmarks

| Flag | Description |
|------|-------------|
| `--test` | Run the example test suite |
| `--test-dir <dir>` | Test directory for `--test` (default: examples) |
| `--bench-file <file>` | Benchmark a single file |
| `--count <N>` | Benchmark iteration count |

### Project and packages

| Flag | Description |
|------|-------------|
| `--scaffold` | Scaffold a project in the current directory |
| `--clean` | Remove build artifacts |
| `--registry <url>` | Package registry URL (`xiom pkg`) |
| `--locked` | Use the lockfile exactly (`xiom pkg`) |
| `--frozen` | Offline lockfile-only mode (`xiom pkg`) |

### Utility

| Flag | Description |
|------|-------------|
| `--version` | Print version and test stats |
| `--help` | Print usage |
| `--help-ai` | AI mode setup and configuration guide |

## Targets

| Target | Status |
|--------|--------|
| `x86_64-pc-windows-msvc` | [OK] Verified |
| `x86_64-unknown-linux-gnu` | [OK] Verified (WSL build + compile + run) |
| `wasm32-unknown-unknown` | [OK] Verified |
| `aarch64-unknown-linux-gnu` (`--target arm`) | Accepted by the CLI |
| `riscv` | Accepted by the CLI; status tracked in the compiler repository |
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
| Contracts | Runtime guards; SMT-LIB export checked with the bundled `z3` (`xiom-verify --check`) |
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
