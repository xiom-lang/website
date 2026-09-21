<!--
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Debugging

> **Quick look:** compile with `-g`, then attach any Debug Adapter Protocol (DAP) client. `xiom-dbg` ships with the toolchain; raw GDB works too.

XIOM ships a source-level debugger, `xiom-dbg`, in the same `bin/` directory as the compiler (recent releases; `xiom dbg` dispatches to it). It is a DAP server: VS Code, Neovim, Emacs and any other DAP client talk to it, and it drives GDB/MI underneath (CDB on Windows). Breakpoints, stepping, variable inspection and expression evaluation work on XIOM source, not on generated machine code.

## Compile with Debug Symbols

```bash
xiom -g -o app app.xi      # DWARF/PDB debug metadata
```

Without `-g` there are no symbols: breakpoints and variable names are unavailable. The debugger backend (`gdb`, or `cdb` on Windows) must be on your `PATH`.

Two helpers in the language work with the debugger:

```xiom
fn check(value: Int) {
  debugger;              // break into the attached debugger, a no-op when none
  assert(value > 0, "value must be positive");
  let seen = dbg!(value);
}
```

Release builds strip `assert`, `dbg!` and `debugger;` unless you pass `--keep-debug-checks`; debug builds always keep them.

## Attach a Client

`xiom-dbg` speaks DAP over stdio: point the client at the executable with no arguments.

VS Code (`launch.json`), with the XIOM extension installed:

```json
{
  "type": "xiom",
  "request": "launch",
  "program": "${workspaceFolder}/app",
  "stopOnEntry": true,
  "contractTraps": true,
  "cwd": "${workspaceFolder}"
}
```

The VS Code extension is being published to the Marketplace and Open VSX; until the listing is live, the client sources are in the toolchain repository. Neovim (`nvim-dap`) and Emacs (`dape`) are wired in the support matrix at [editors/README.md](https://github.com/xiom-lang/xiom/blob/main/editors/README.md).

`contractTraps: true` makes a failing `requires`, `ensures` or `invariant` stop the debugger like an exception, with the clause and location.

## Script It: JSON Mode

For scripts and custom tooling, `xiom-dbg --json` exposes a line-oriented JSON API:

```bash
xiom-dbg --json
```

```
launch
set-breakpoint <file> <line>
delete-breakpoint <id>
step          # step over
step-in
continue
stack
variables
registers
memory <addr> <size>
evaluate <expr>
threads
terminate
help
```

## Raw GDB

Debug symbols are standard DWARF, so any GDB-compatible debugger works directly:

```bash
gdb ./app
(gdb) break main.xi:43
(gdb) run
(gdb) info locals
(gdb) print value * 2
```

## Breakpoints, Stepping, Inspection

- Source-level breakpoints are set by file and line: click the gutter in your editor, `set-breakpoint main.xi 43` in JSON mode, or `break main.xi:43` in GDB.
- Function entry breakpoints: `breakpoint set fn_name`.
- Continue resumes to the next breakpoint; step over (`next` / `step`) executes the current line; step into (`stepIn` / `step-in`) enters a call.
- Locals: `variables` in JSON mode, `info locals` in GDB. Expressions: `evaluate "items.len() + count"` or `print ...` in GDB. Memory: `memory 0x7fff1234 256` or `x/256xb ...`.

Contract violations trap with the clause and source location:

```
Contract violation: requires: b != 0.0
  at main.xi:15 in fn divide(a: Float64, b: Float64) -> Float64
```

## Current Limits

- Conditional breakpoints, hit-count breakpoints and logpoints are not implemented yet.
- The JSON API does not expose pause; interrupt from the client or GDB instead.
- On Windows the CDB backend supports basic breakpoints and stepping; GDB/MI on Linux and macOS is the full path.

## See Also

- [Compiler](compiler.md) -- `-g`, `--keep-debug-checks` and the tool dispatchers
- [Getting Started](getting-started.md) -- installing the toolchain and the companion tools
- [Unsafe](unsafe.md) -- fault trapping in confined `unsafe` blocks
