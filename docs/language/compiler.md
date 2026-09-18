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
| Crate structure | 19 crates (xiom-ast, lexer, parser, check, codegen, ctfe, jit, verify, fmt, lsp, pkg, mcp, doc, ffigen, dbg, display, graph, wasm, cli) |

## Build from Source

```bash
git clone https://github.com/XIOM-lang/XIOM.git
cd xiom
cargo build -p xiom
cargo test -p xiom-codegen --test e2e_tests

# Linux build (WSL)
wsl -d Ubuntu -- bash -c 'export PATH=$HOME/.cargo/bin:$PATH; cd /mnt/e/Projects/AXIOM && cargo build -p xiom'
```
