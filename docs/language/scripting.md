# Scripting

XIOM is compiled, but the toolchain has a script mode: a file with top-level
code is wrapped in `fn main()` automatically, compiled, and run in one step.
Scripts suit small tools, one-off data work and shell-style automation.

## Running scripts

| Command | What it does |
|---------|--------------|
| `xiom run script.xi` | Compile the script and run it (top-level code allowed) |
| `xiom run -e "<code>"` | Compile and run an inline snippet |
| `xiom run -` | Compile and run a script read from stdin |
| `xiom --run program.xi` | Compile and run a program (requires `fn main()`) |
| `xiom run --watch script.xi` | Re-run the script when the file changes |
| `xiom script.xi -o tool.exe` | Compile to a binary you can ship |
| `xiom repl` | Interactive REPL |

Scripts are compiled on every run; the built binary is written under the
system temp directory (reused while the script is unchanged). For anything
you run often, build a binary once and ship it.

`xiom --check script.xi` type-checks without compiling or running, and it
accepts the same top-level style as a script.

## Hello, script

```xiom
// hello.xi -- top-level code runs as-is, no fn main required
use xiom.io;

io.println("hello, xiom");
```

```bash
xiom run hello.xi
```

## Working with values

`io.println` takes a `Str`; use `xiom.convert.itos` for numbers.

```xiom
use xiom.io;
use xiom.convert.itos;

let a = 21;
let b = 2;
io.println("a * b = " + itos(a * b));
```

Top-level bindings are immutable by default; use `var` for values you
reassign inside loops.

```xiom
use xiom.io;
use xiom.convert.itos;

var total = 0;
var i = 1;
while i <= 4 {
  total = total + i;
  i = i + 1;
}
io.println("sum: " + itos(total));
```

## Files

```xiom
use xiom.io;
use xiom.convert.itos;

match io.read_file("input.txt") {
  Ok(text) => io.println("input.txt: " + itos(text.len()) + " bytes"),
  Err(e) => io.println("cannot read input.txt: " + e.message),
}
```

`io.write_file`, `io.append_file`, `io.file_exists`, `io.list_dir` and
`io.read_file_lines` cover the common file tasks; `xiom.io.fs` adds
byte-level and range helpers.

## Environment and exit codes

```xiom
use xiom.io;
use xiom.convert.itos;
use xiom.process;

io.println("pid: " + itos(process.get_pid()));

match process.env_var("HOME") {
  Some(home) => io.println("HOME=" + home),
  None => io.println("HOME is not set"),
}

process.exit(0);
```

## Running other programs

```xiom
use xiom.io;
use xiom.convert.itos;
use xiom.process;

match process.spawn_blocking("git --version") {
  Ok(code) => io.println("git exited with " + itos(code)),
  Err(e) => io.println("could not run git: " + e),
}
```

`process.spawn_command(cmd, args)` starts a program with an argument vector
and returns its pid; `process.wait(pid)` collects the exit code, and
`process.command_exists(name)` checks availability first.

## Shebang scripts (Linux and macOS)

A plain `#!/usr/bin/env xiom` starts the compiler in program mode, which
rejects top-level code; route the shebang through `xiom run` with the `-S`
form:

```xiom
#!/usr/bin/env -S xiom run
use xiom.io;

io.println("hello from a shebang script");
```

```bash
chmod +x greet.xi
./greet.xi
```

Windows runs scripts through `xiom run`; shebangs are POSIX-only.

## Known limitations (v0.61.3)

Verified against the shipped toolchain; each item is tracked upstream.

- `xiom run` does not pass script arguments yet: `args.args_raw()` returns
  only the temporary binary path, with or without a `--` separator, so
  `xiom.os.args` sees no user arguments.
- Reading piped standard input crashes on Linux (`Fatal error: glibc
  detected an invalid stdio handle`) through both `io.read_all_stdin()` and
  `io.read_line_trim()`.
- `for x in [ ... ]` over an array literal fails at LLVM codegen
  (`invalid getelementptr indices`); use `while` or the `xiom.iter`
  functions until the fix ships.

## Determinism and limits

- Scripts are compiled, not interpreted: type errors surface before anything
  runs, and contract checks are active by default.
- Anything a program can do, a script can do -- the only difference is the
  automatic `fn main()` wrapper.
- `xiom run` reads the script from the path you give it; for a project with a
  `xiom.toml`, `xiom build` builds the project instead.
