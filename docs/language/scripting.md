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
for n in [1, 2, 3, 4] {
  total = total + n;
}
io.println("sum: " + itos(total));
```

## Arguments, flags and options

`xiom.os.args` reads the arguments passed after the script name.

```xiom
use xiom.io;
use xiom.convert.itos;
use xiom.os.args;

let raw = args.args_raw();
let positional = args.positionals(&raw);

if args.args_has_flag("--shout") {
  io.println("shouting with " + itos(positional.len()) + " argument(s)");
} else {
  io.println(itos(positional.len()) + " argument(s)");
}

match args.args_option("--name") {
  Some(name) => io.println("hello, " + name),
  None => io.println("hello, world"),
}
```

`args.flag_lookup(raw, flag)` and `args.option_value(raw, key)` are the
lower-level forms when you manage the argument vector yourself.

## Standard input

```xiom
use xiom.io;
use xiom.convert.itos;

let text = io.read_all_stdin();
io.println("read " + itos(text.len()) + " bytes from stdin");
```

`io.read_line()` and `io.read_line_trim()` read one line at a time, and
`io.read_int()` parses a line into a `Result[Int, Str]`.

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

Make the script executable and the shebang runs it directly:

```xiom
#!/usr/bin/env xiom
use xiom.io;

io.println("hello from a shebang script");
```

```bash
chmod +x greet.xi
./greet.xi
```

Windows runs scripts through `xiom run`; shebangs are POSIX-only.

## Determinism and limits

- Scripts are compiled, not interpreted: type errors surface before anything
  runs, and contract checks are active by default.
- Anything a program can do, a script can do -- the only difference is the
  automatic `fn main()` wrapper.
- `xiom run` reads the script from the path you give it; for a project with a
  `xiom.toml`, `xiom build` builds the project instead.
