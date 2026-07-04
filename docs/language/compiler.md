# Compiler

## Pipeline

```
.xi source
  → Lexer           (tokenize — 40+ token kinds)
  → Parser          (AST — LL(1), no backtracking)
  → Type Checker    (primitives, structs, functions, interface satisfaction)
  → Borrow Checker  (lexical scope — &T, &mut T, move semantics)
  → LLVM IR         (text emission, human-readable)
     ├─ Contracts   (runtime guards — @llvm.trap on violation)
     ├─ Derive      (Eq, Clone, Display, Hash, Ord)
     └─ Generics    (monomorphisation — register + specialize)
  → clang           (native .exe or .wasm)
```

## CLI Reference

```bash
xiomc [flags] <source.xi>
```

| Flag | Description |
|------|-------------|
| *(no flag)* | Print LLVM IR to stdout |
| `--emit-ir` | Print LLVM IR to stdout |
| `-o <output>` | Compile to native binary |
| `--run` | Compile and run, print exit code |
| `--target wasm` | Compile to `wasm32-unknown-unknown` |
| `--no-contracts` | Disable contract runtime checks |
| `--diagnostics=json` | Structured compiler output (Phase 2) |
| `--dump-contracts` | Queryable contract index (Phase 2) |

### Via Cargo

```bash
cargo run -p xiomc -- [flags] <source.xi>
```

## Targets

| Target | Status |
|--------|--------|
| `x86_64-pc-windows-msvc` | Verified |
| `wasm32-unknown-unknown` | Verified |
| `x86_64-unknown-linux-gnu` | Planned |
| `aarch64-apple-darwin` | Planned |

## Crate Structure

| Crate | Purpose | LOC |
|-------|---------|-----|
| `xiom-ast` | AST node definitions (full EBNF coverage) | ~480 |
| `xiom-lexer` | Tokenizer (40+ token kinds) | ~500 |
| `xiom-parser` | Recursive descent LL(1) parser | ~1,450 |
| `xiom-check` | Type checker + Borrow checker + Module resolver | ~1,415 |
| `xiom-codegen` | LLVM IR emitter + Contracts + Derive + Generics | ~1,405 |
| `xiomc` | CLI binary | ~220 |

## Self-Hosted Compiler

The XIOM compiler itself is written in XIOM (`selfhost/` directory). It is compiled by the Rust bootstrap compiler. Once Phase 2C bootstrapping is complete, the XIOM compiler compiles itself.

| File | Purpose |
|------|---------|
| `selfhost/xiom-lexer.xi` | Tokenizer in XIOM |
| `selfhost/xiom-parser.xi` | Recursive descent parser in XIOM |
| `selfhost/xiom-check.xi` | Type checker in XIOM |
| `selfhost/xiom-codegen.xi` | LLVM IR emitter in XIOM |
| `selfhost/xiomc.xi` | CLI driver in XIOM |

## Version History

| Version | Codename | Phase | Tests | LOC |
|---------|----------|-------|-------|-----|
| **v0.11.0** | Self-Hosted | Eco | 213 | ~10,000 |
| v0.10.0 | Sovereign | 3 | 208 | ~9,600 |
| v0.4.0 | Mirror | 2B | 124 | ~7,020 |
| v0.2.5 | Hardened | 1.5 | 109 | ~6,924 |
| v0.2.0 | Guardian | 1 | 87 | ~5,200 |
| v0.1.0 | Pipeline | 0 | 36 | ~3,800 |

See the [full version history](https://xiom-lang.org/versions) for all releases.

## Architecture Decisions

| Decision | Status |
|----------|--------|
| Phase 0 compiler language | **Rust** |
| LLVM backend | **Text IR emission** (no library dependency) |
| WASM target | via clang |
| Ownership model | **Lexical scope borrowing** |
| Contracts | **Runtime guards** (Phase 1), Z3 (Phase 3) |
| Type constraints | **Inline** `[T: Ord]` |
| Method receiver | **Implicit** `self`, inferred |
| Rust bootstrap | **Permanent** — never deleted |

## Build from Source

```bash
git clone https://gitea.example.com/xiom-lang/xiom.git
cd xiom
cargo build
cargo test     # 213 tests
```

## Download

Pre-built binaries for Windows, macOS, and Linux are available on the [download page](https://xiom-lang.org/download).
