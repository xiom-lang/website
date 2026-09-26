<!--
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Getting Started

## Prerequisites

Release installs need one external tool; everything else is optional:

- **LLVM/Clang 18 or newer (required).** The compiler uses `clang` to assemble
  and link every program.
  - Windows: `winget install LLVM.LLVM`
  - macOS: `xcode-select --install` (Xcode command line tools)
  - Debian/Ubuntu: `sudo apt install clang`
  - Fedora: `sudo dnf install clang`
- **NASM 2.15 or newer (recommended).** Source builds with the `nasm` feature
  use it to assemble the hardware-accelerated runtime (crypto, memory, context
  switching). Without NASM the toolchain compiles the runtime without those
  assembly paths; `xiom doctor` reports whether it was found. The contracts
  guide documents how this affects the verification boundary.
  - Windows: `winget install NASM.NASM`
  - macOS: `brew install nasm`
  - Debian/Ubuntu: `sudo apt install nasm`
  - Fedora: `sudo dnf install nasm`
- **Z3** is not installed separately. The contract verifier uses the copy that
  ships with the toolchain (`xiom-verify`), or a system `z3` when present.
- **Rust 1.86+** is only needed to build the compiler from source.

## Install the Toolchain

The installer downloads the latest release from `dl.xiom-lang.org`, verifies
its SHA256 checksum, installs it for your user (no administrator or root
needed), and makes the tools available on your `PATH`. It also checks for
LLVM/Clang and prints install instructions when it is missing.

Linux:

```bash
curl -fsSL https://xiom-lang.org/install.sh | sh

# pin a specific release
curl -fsSL https://xiom-lang.org/install.sh | sh -s -- --version <tag>
```

macOS: the same script detects macOS and arm64 or Intel, and macOS archives
are published with each release. Install the Xcode command line tools first.

```bash
curl -fsSL https://xiom-lang.org/install.sh | sh
```

Windows (PowerShell):

```powershell
irm https://xiom-lang.org/install.ps1 | iex

# pinned release
irm https://xiom-lang.org/install.ps1 -OutFile install.ps1
.\install.ps1 -Version v0.60.1
```

What the installer does, so you know what you are agreeing to:

- Installs into `%LOCALAPPDATA%\xiom` on Windows and
  `~/.local/share/xiom` (or `$XIOM_HOME`) on Linux/macOS. An existing install
  in that directory is replaced.
- Windows adds `bin` to your user `PATH` (use `-NoPath` to skip it; reopen the
  terminal afterwards). Linux/macOS links every tool into `~/.local/bin`
  (use `XIOM_ADD_PATH=1` to also append the export to `~/.profile`).
- Verifies the archive against `SHA256SUMS` and refuses to install on
  mismatch.
- `-InstallDir <path>` on Windows overrides the install directory.

Activate the current shell and verify:

```bash
export PATH="$HOME/.local/bin:$PATH"; hash -r     # Linux/macOS if needed
xiom --version
xiom doctor
# -> clang [OK]  opt [OK]  nasm [OK]
```

`xiom doctor` is the fastest way to see what is present, including the
companion tools (`xiom-lsp`, `xiom-dbg`, `xiom-pkg`, `xiom-fmt`, `xiom-mcp`,
`xiom-verify`) that recent releases ship in the same `bin/` directory.

To uninstall, delete the install directory and, on Windows, remove that `bin`
entry from your user `PATH`; on Linux/macOS remove the `xiom*` links from
`~/.local/bin`.

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
xiom --emit-ir hello.xi            # print LLVM IR
xiom -o hello hello.xi             # compile to a native binary
xiom --run hello.xi                # compile and run
# -> exit code: 30
xiom --target wasm -o hello.wasm hello.xi
```

## CLI Reference

| Flag | Description |
|------|-------------|
| `<source.xi>` | Print LLVM IR to stdout |
| `--emit-ir <source.xi>` | Print LLVM IR to stdout |
| `-o <output> <source.xi>` | Compile to native binary |
| `--run <source.xi>` | Compile and run, print exit code |
| `--target wasm -o <out.wasm> <source.xi>` | Compile to WASM |
| `--no-contracts` | Disable contract runtime checks |
| `--diagnostics=json` | Structured compiler output |
| `--dump-contracts` | Queryable contract index |
| `--ai` | Explain errors with a model (see below) |

## AI-Assisted Compilation (`--ai`)

`--ai` sends compilation errors to a model and writes actionable hints to
`.xiom_ai.json`. Source files are never modified. There are two ways to set a
provider.

Local, free, nothing leaves the machine (Ollama):

```bash
ollama pull codellama
xiom --ai --ai-local source.xi
```

A cloud key, configured in a file. Create `.xiom_ai_config.json`; the compiler
searches these locations in order and uses the first one it finds:

1. `<project>/.xiom_ai_config.json` (per project)
2. `%LOCALAPPDATA%\xiom\.xiom_ai_config.json` on Windows,
   `~/.local/share/xiom/.xiom_ai_config.json` on Linux/macOS (the install
   directory; the installer writes it here)
3. `~/.xiom_ai_config.json` (home)

```json
{
  "provider": "deepseek",
  "endpoint": "https://api.deepseek.com",
  "api_key": "sk-your-key-here",
  "model": "deepseek-chat"
}
```

Environment variables override the file, and command-line flags override the
environment. This is also how you change the key later: edit the same JSON
file, or export a new value.

| Variable | Purpose |
|----------|---------|
| `XIOM_AI_KEY` | API key (not needed for Ollama; HTTPS endpoints only) |
| `XIOM_AI_ENDPOINT` | Endpoint URL |
| `XIOM_AI_MODEL` | Model name |
| `XIOM_AI_PROVIDER` | Force `ollama`, `deepseek`, `openai`, `openrouter` or `groq` |
| `XIOM_AI_TIMEOUT` | Per-request timeout in seconds (default 10) |
| `XIOM_AI_MAX_TOKENS` | Response token cap (default 150) |
| `XIOM_AI_ALLOW_HTTP` | `1` allows a key over `http://` to a trusted local proxy |

Useful flags: `--ai-local` forces Ollama on loopback and drops any cloud key,
`--ai-dry-run` prints the prompt without calling a model, `--ai-silent` writes
only `.xiom_ai.json`, `--ai-model=<name>` overrides the model, and
`--ai-timeout=<sec>` the timeout. Keys are refused over plaintext `http://` to
non-local hosts, and `xiom --help-ai` prints this guide from the compiler
itself. The installer's config file is gitignored; prefer `XIOM_AI_KEY` over a
key on disk.

## Use XIOM from AI agents (MCP)

`xiom-mcp` is a Model Context Protocol server: it gives agents the compiler,
the language guides, the standard library, contract verification and registry
search as tools (the full list is on the [Compiler page](compiler.md)). It
ships in every release archive and the installers put `xiom-mcp` on your
`PATH`; it speaks stdio JSON-RPC, so any MCP-capable client can run it.

Claude Code:

```bash
claude mcp add --transport stdio xiom -- xiom-mcp              # this project
claude mcp add --scope user --transport stdio xiom -- xiom-mcp # all projects
```

Portable project file (`.mcp.json`), read by Claude Code, VS Code and other
compatible clients:

```json
{
  "mcpServers": {
    "xiom": { "command": "xiom-mcp" }
  }
}
```

Cursor: put the same `mcpServers` block in `.cursor/mcp.json` (project) or
`~/.cursor/mcp.json` (global).

VS Code (Copilot) uses `.vscode/mcp.json` with a `servers` key:

```json
{
  "servers": {
    "xiom": { "command": "xiom-mcp" }
  }
}
```

Codex CLI: add to `~/.codex/config.toml`:

```toml
[mcp_servers.xiom]
command = "xiom-mcp"
```

Kilo: add to `kilo.json`/`kilo.jsonc` in the project, or
`~/.config/kilo/kilo.jsonc` globally:

```json
{
  "mcp": {
    "xiom": { "type": "local", "command": ["xiom-mcp"], "enabled": true }
  }
}
```

Any other MCP-capable client: use the portable `mcpServers` block above, or
run `xiom-mcp` as a stdio server directly.

On Windows the installer places the tools in `%LOCALAPPDATA%\xiom\bin`; if a
client does not inherit your `PATH`, use the absolute path
`%LOCALAPPDATA%\xiom\bin\xiom-mcp.exe` in `command`. `xiom-mcp --version`
prints the server version. Once connected, ask the agent for the
`xiom_cheatsheet`, or have it compile your file with `compile_and_analyze`.

## Build from Source

Requires Rust 1.86+ and LLVM/Clang 18+.

```bash
git clone https://github.com/xiom-lang/xiom.git
cd xiom
./scripts/fetch-stdlib.ps1        # PowerShell; scripts/fetch-stdlib.sh on Linux/macOS
cargo build --release -p xiom     # driver at target/release/xiom
cargo test --workspace --lib
```

The compiler test suites expect the pinned standard library checkout; without
it the stdlib-dependent suites skip loudly.

## Repository Layout

XIOM is split across repositories, not one monorepo:

| Repository | Contents |
|------------|----------|
| `xiom-lang/xiom` | Compiler, tooling crates (`pkg`, `lsp`, `dbg`, `mcp`, `fmt`, `doc`, `verify`, `ffigen`), end-to-end tests |
| `xiom-lang/stdlib` | Standard library sources, runtime, smoke corpus and known-answer vectors |
| `xiom-lang/registry` | Package registry service |
| `xiom-lang/website` | This site and the documentation sources |
| `xiom-lang/playground` | Browser playground |
| `xiom-lang/.github` | Organization profile, process documents and default templates |

Inside `xiom-lang/xiom`, the compiler lives under `crates/`: `xiom-lexer`,
`xiom-parser`, `xiom-ast`, `xiom-check` (types, borrows, modules), `xiom-codegen`
(LLVM IR, contracts, derive, generics), `xiom-graph` (semantic graph) and the
`xiom` driver, with the self-hosted sources under `selfhost/`. Release archives
pack the standard library and runtime under `lib/`; the compiler discovers them
next to the executable, through `XIOM_STDLIB`, from the working directory, or
from `XIOM_HOME`.

## Editor Support

- **VS Code** -- install the **XIOM Toolchain** extension (0.12.0) from the
  [Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=xiom-lang.xiom)
  or [Open VSX](https://open-vsx.org/extension/xiom-lang/xiom); it requires
  toolchain v0.61.0 or newer and resolves `xiom-lsp` and `xiom-dbg` from the
  installed toolchain.
- **Language server (`xiom-lsp`)** and **debugger (`xiom-dbg`)** ship in recent
  releases and work with any LSP/DAP client; the [Debugging guide](debugger.md)
  covers compiling with `-g`, editor launch configs and the JSON API.
- **Other editors** -- the support matrix for Neovim, JetBrains, Helix,
  Sublime, Emacs and Zed is maintained in
  [editors/README.md](https://github.com/xiom-lang/xiom/blob/main/editors/README.md).

## Try in Browser

Open the [XIOM Playground](https://playground.xiom-lang.org) to write and
compile XIOM directly in your browser. No install required.

## Next Steps

1. Read the [Syntax Guide](syntax.md)
2. Explore the [Type System](types.md)
3. Understand the [Memory Model](memory-model.md)
4. Learn about [Contracts](contracts.md)
5. Read the [Unsafe guide](unsafe.md)
