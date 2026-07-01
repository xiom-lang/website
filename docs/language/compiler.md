# Compiler

## Pipeline

```
.ax source
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
axiomc [flags] <source.ax>
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
cargo run -p axiomc -- [flags] <source.ax>
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
| `axiom-ast` | AST node definitions (full EBNF coverage) | ~480 |
| `axiom-lexer` | Tokenizer (40+ token kinds) | ~500 |
| `axiom-parser` | Recursive descent LL(1) parser | ~1,450 |
| `axiom-check` | Type checker + Borrow checker + Module resolver | ~1,415 |
| `axiom-codegen` | LLVM IR emitter + Contracts + Derive + Generics | ~1,405 |
| `axiomc` | CLI binary | ~220 |

## Self-Hosted Compiler

The AXIOM compiler itself is written in AXIOM (`selfhost/` directory). It is compiled by the Rust bootstrap compiler. Once Phase 2C bootstrapping is complete, the AXIOM compiler compiles itself.

| File | Purpose |
|------|---------|
| `selfhost/axiom-lexer.ax` | Tokenizer in AXIOM |
| `selfhost/axiom-parser.ax` | Recursive descent parser in AXIOM |
| `selfhost/axiom-check.ax` | Type checker in AXIOM |
| `selfhost/axiom-codegen.ax` | LLVM IR emitter in AXIOM |
| `selfhost/axiomc.ax` | CLI driver in AXIOM |

## Version History

| Version | Codename | Phase | Tests | LOC |
|---------|----------|-------|-------|-----|
| **v0.11.0** | Self-Hosted | Eco | 213 | ~10,000 |
| v0.10.0 | Sovereign | 3 | 208 | ~9,600 |
| v0.4.0 | Mirror | 2B | 124 | ~7,020 |
| v0.2.5 | Hardened | 1.5 | 109 | ~6,924 |
| v0.2.0 | Guardian | 1 | 87 | ~5,200 |
| v0.1.0 | Pipeline | 0 | 36 | ~3,800 |

See the [full version history](https://axiom-lang.org/versions) for all releases.

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
git clone https://gitea.example.com/axiom-lang/axiom.git
cd axiom
cargo build
cargo test     # 213 tests
```

## Download

Pre-built binaries for Windows, macOS, and Linux are available on the [download page](https://axiom-lang.org/download).
