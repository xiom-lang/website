# Getting Started

## Prerequisites

- **Rust** 1.85+ ([rustup](https://rustup.rs))
- **LLVM/Clang** 18+ for native compilation
  - Windows: `winget install LLVM.LLVM`
  - macOS: `brew install llvm`
  - Linux: `apt install clang` or `dnf install clang`

## Build from Source

```bash
git clone https://gitea.example.com/axiom-lang/axiom.git
cd axiom
cargo build
cargo test          # 213 tests should pass
```

## Your First Program

Create a file `hello.ax`:

```axiom
fn add(a: Int, b: Int) -> Int {
  return a + b
}

fn main() -> Int {
  return add(10, 20)
}
```

Compile and run:

```bash
# View LLVM IR
cargo run -p axiomc -- --emit-ir hello.ax

# Compile to native binary
cargo run -p axiomc -- -o hello.exe hello.ax

# Compile and run (prints exit code)
cargo run -p axiomc -- --run hello.ax
# → exit code: 30

# Compile to WASM
cargo run -p axiomc -- --target wasm -o hello.wasm hello.ax
# → wasm size: 618 bytes
```

## Try in Browser

Open the [AXIOM Playground](https://axiom-lang.org/playground) to write and compile AXIOM directly in your browser. No install required.

## CLI Reference

| Flag | Description |
|------|-------------|
| `<source.ax>` | Print LLVM IR to stdout |
| `--emit-ir <source.ax>` | Print LLVM IR to stdout |
| `-o <output> <source.ax>` | Compile to native binary |
| `--run <source.ax>` | Compile and run, print exit code |
| `--target wasm -o <out.wasm> <source.ax>` | Compile to WASM |
| `--no-contracts` | Disable contract runtime checks |
| `--diagnostics=json` | Structured compiler output (Phase 2 tooling) |
| `--dump-contracts` | Queryable contract index (Phase 2 tooling) |

## Project Structure

```
AXIOM/
├── crates/             # Rust bootstrap compiler (permanent)
│   ├── axiom-ast/      # AST node definitions
│   ├── axiom-lexer/    # Tokenizer
│   ├── axiom-parser/   # Recursive descent parser
│   ├── axiom-check/    # Type checker + borrow checker + module resolver
│   ├── axiom-codegen/  # LLVM IR emitter + contracts + derive + generics
│   └── axiomc/         # CLI binary
├── selfhost/           # AXIOM self-hosted compiler
│   ├── axiom-lexer.ax
│   ├── axiom-parser.ax
│   ├── axiom-check.ax
│   ├── axiom-codegen.ax
│   └── axiomc.ax
├── stdlib/             # Standard library (AXIOM source)
├── examples/           # Example programs
├── specs/              # Language specification
├── docs/               # Documentation
├── website/            # Official website
└── playground/         # WASM playground
```

## Editor Support

- **VS Code** — Install `vscode-axiom` extension for syntax highlighting
- **Any editor** — AXIOM uses `.ax` file extension. Set up `.ax` → plain text with 4-space indentation for now. Full LSP support planned for Phase 3.

## Next Steps

1. Read the [Syntax Guide](syntax.md)
2. Explore the [Type System](types.md)
3. Understand the [Memory Model](memory-model.md)
4. Learn about [Contracts](contracts.md)
