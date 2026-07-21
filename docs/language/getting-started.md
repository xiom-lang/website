# Getting Started

## Prerequisites

- **Rust** 1.85+ ([rustup](https://rustup.rs))
- **LLVM/Clang** 18+ for native compilation
  - Windows: `winget install LLVM.LLVM`
  - macOS: `brew install llvm`
  - Linux: `apt install clang` or `dnf install clang`

## Build from Source

```bash
git clone https://gitea.example.com/xiom-lang/xiom.git
cd xiom
cargo build
cargo test          # 234 tests should pass
```

## Your First Program

Create a file `hello.xi`:

```xiom
fn add(a: Int, b: Int) -> Int {
  return a + b;
}

fn main() -> Int {
  return add(10, 20);
}
```

Compile and run:

```bash
# View LLVM IR
cargo run -p xiom -- --emit-ir hello.xi

# Compile to native binary
cargo run -p xiom -- -o hello.exe hello.xi

# Compile and run (prints exit code)
cargo run -p xiom -- --run hello.xi
# → exit code: 30

# Compile to WASM
cargo run -p xiom -- --target wasm -o hello.wasm hello.xi
# → wasm size: 618 bytes
```

## Try in Browser

Open the [XIOM Playground](https://xiom-lang.org/playground) to write and compile XIOM directly in your browser. No install required.

## CLI Reference

| Flag | Description |
|------|-------------|
| `<source.xi>` | Print LLVM IR to stdout |
| `--emit-ir <source.xi>` | Print LLVM IR to stdout |
| `-o <output> <source.xi>` | Compile to native binary |
| `--run <source.xi>` | Compile and run, print exit code |
| `--target wasm -o <out.wasm> <source.xi>` | Compile to WASM |
| `--no-contracts` | Disable contract runtime checks |
| `--diagnostics=json` | Structured compiler output (Phase 2 tooling) |
| `--dump-contracts` | Queryable contract index (Phase 2 tooling) |

## Project Structure

```
XIOM/
├── crates/             # Rust bootstrap compiler (permanent)
│   ├── xiom-ast/      # AST node definitions
│   ├── xiom-lexer/    # Tokenizer
│   ├── xiom-parser/   # Recursive descent parser
│   ├── xiom-check/    # Type checker + borrow checker + module resolver
│   ├── xiom-codegen/  # LLVM IR emitter + contracts + derive + generics
│   └── xiom/         # CLI binary
├── selfhost/           # XIOM self-hosted compiler
│   ├── xiom-lexer.xi
│   ├── xiom-parser.xi
│   ├── xiom-check.xi
│   ├── xiom-codegen.xi
│   └── xiom.xi
├── stdlib/             # Standard library (XIOM source)
├── examples/           # Example programs
├── specs/              # Language specification
├── docs/               # Documentation
├── website/            # Official website
└── playground/         # WASM playground
```

## Editor Support

- **VS Code** — Install `vscode-xiom` extension for syntax highlighting
- **Any editor** — XIOM uses `.xi` file extension. Set up `.xi` → plain text with 4-space indentation for now. Full LSP support planned for Phase 3.

## Next Steps

1. Read the [Syntax Guide](syntax.md)
2. Explore the [Type System](types.md)
3. Understand the [Memory Model](memory-model.md)
4. Learn about [Contracts](contracts.md)
