# I/O Library

The `io` module provides console input/output, file system manipulation, process interaction, timing, buffered I/O wrappers, standard streams, in-memory I/O cursors, and path utilities.

```
use axiom.io;
```

---

## Error Type

The `IOError` type represents an I/O operation failure with a human-readable message and a platform-specific error code.

```axiom
type IOError = {
  message: Str;
  code: Int;
}
```

---

## SeekFrom Enum

Specifies the reference point for a seek operation.

```axiom
type SeekFrom = enum { Start(Int), End(Int), Current(Int) }
```

| Variant      | Description                                        |
|-------------|----------------------------------------------------|
| `Start(n)`  | Seek `n` bytes from the beginning of the stream.   |
| `End(n)`    | Seek `n` bytes from the end of the stream (usually negative). |
| `Current(n)`| Seek `n` bytes from the current stream position.   |

---

## Console

### `print(msg)`
Writes `msg` to standard output without a trailing newline.

```axiom
fn print(msg: Str);
```

### `println(msg)`
Writes `msg` to standard output followed by a newline character.

```axiom
fn println(msg: Str);
```

### `read_line()`
Reads a single line from standard input. The trailing newline is stripped.

```axiom
fn read_line() -> Str;
```

### `read_int()`
Reads a line from standard input and attempts to parse it as an `Int`. Returns `Ok(Int)` on success or `Err(Str)` if the input is not a valid integer.

```axiom
fn read_int() -> Result[Int, Str];
```

### `read_float()`
Reads a line from standard input and attempts to parse it as a `Float64`. Returns `Ok(Float64)` on success or `Err(Str)` if the input is not a valid floating-point number.

```axiom
fn read_float() -> Result[Float64, Str];
```

---

## File System

### `read_file(path)`
Reads the entire contents of the file at `path` into a `Str`. Returns `Ok(content)` on success or `Err(IOError)` if the file cannot be read.

```axiom
fn read_file(path: Str) -> Result[Str, IOError];
```

### `write_file(path, content)`
Writes `content` to the file at `path`, replacing the file if it already exists. Returns `Ok(())` on success or `Err(IOError)`.

```axiom
fn write_file(path: Str, content: Str) -> Result[Unit, IOError];
```

### `append_file(path, content)`
Appends `content` to the end of the file at `path`, creating the file if it does not exist. Returns `Ok(())` on success or `Err(IOError)`.

```axiom
fn append_file(path: Str, content: Str) -> Result[Unit, IOError];
```

### `file_exists(path)`
Returns true if a file or directory exists at `path`.

```axiom
fn file_exists(path: Str) -> Bool;
```

### `is_dir(path)`
Returns true if the path points to an existing directory.

```axiom
fn is_dir(path: Str) -> Bool;
```

### `create_dir(path)`
Creates a new directory at `path`. Returns `Ok(())` on success or `Err(IOError)`.

```axiom
fn create_dir(path: Str) -> Result[Unit, IOError];
```

### `list_dir(path)`
Lists the entries in the directory at `path`. Returns `Ok(entries)` where entries is a `Vec[Str]` of file/directory names, or `Err(IOError)`.

```axiom
fn list_dir(path: Str) -> Result[Vec[Str], IOError];
```

### `remove_file(path)`
Deletes the file at `path`. Returns `Ok(())` on success or `Err(IOError)`.

```axiom
fn remove_file(path: Str) -> Result[Unit, IOError];
```

### `copy_file(src, dst)`
Copies the file from `src` to `dst`. Returns `Ok(())` on success or `Err(IOError)`.

```axiom
fn copy_file(src: Str, dst: Str) -> Result[Unit, IOError];
```

### `rename(src, dst)`
Renames (moves) a file or directory from `src` to `dst`. Returns `Ok(())` on success or `Err(IOError)`.

```axiom
fn rename(src: Str, dst: Str) -> Result[Unit, IOError];
```

---

## Process

### `exit(code)`
Terminates the program immediately with the given exit code.

```axiom
fn exit(code: Int);
```

### `args()`
Returns the command-line arguments passed to the program as a `Vec[Str]`. The first element is the program name.

```axiom
fn args() -> Vec[Str];
```

### `env_var(name)`
Retrieves the value of the environment variable `name`. Returns `Some(value)` if set or `None` if undefined.

```axiom
fn env_var(name: Str) -> Option[Str];
```

---

## Time

### `time_now()`
Returns the current time as a Unix timestamp (seconds since January 1, 1970 UTC).

```axiom
fn time_now() -> Int;
```

### `sleep(ms)`
Suspends execution for at least `ms` milliseconds.

```axiom
fn sleep(ms: Int);
```

---

## Standard Streams

### `stdin()`
Returns the file descriptor for standard input (typically 0).

```axiom
fn stdin() -> Int;
```

### `stdout()`
Returns the file descriptor for standard output (typically 1).

```axiom
fn stdout() -> Int;
```

### `stderr()`
Returns the file descriptor for standard error (typically 2).

```axiom
fn stderr() -> Int;
```

### `print_line(s)`
Writes `s` followed by a newline to standard output. Equivalent to `println` but may use a lower-level path.

```axiom
fn print_line(s: Str);
```

---

## Read / Write / Seek Traits

### `Read`
Provides byte-level reading from a source. The source is typically a file descriptor or a `Cursor`.

```axiom
interface Read {
  fn read(self, buf: &mut Vec[UInt8]) -> Result[Int, IOError];
  fn read_to_end(self, buf: &mut Vec[UInt8]) -> Result[Int, IOError];
  fn read_to_string(self) -> Result[Str, IOError];
  fn read_exact(self, buf: &mut Vec[UInt8]) -> Result[Unit, IOError];
}
```

| Method            | Description |
|-------------------|-------------|
| `read(buf)`       | Reads up to `buf.len()` bytes into `buf`. Returns the number of bytes read. |
| `read_to_end(buf)`| Reads all remaining bytes from the source into `buf`. Returns the total number of bytes read. |
| `read_to_string()` | Reads all remaining bytes and returns them as a `Str`. |
| `read_exact(buf)` | Reads exactly `buf.len()` bytes, blocking until all bytes are read. Returns `Err` on unexpected EOF. |

### `Write`
Provides byte-level writing to a sink.

```axiom
interface Write {
  fn write(self, buf: &Vec[UInt8]) -> Result[Int, IOError];
  fn write_all(self, buf: &Vec[UInt8]) -> Result[Unit, IOError];
  fn flush(self) -> Result[Unit, IOError];
}
```

| Method         | Description |
|----------------|-------------|
| `write(buf)`   | Writes up to `buf.len()` bytes. Returns the number of bytes written. |
| `write_all(buf)`| Writes all bytes in `buf`, retrying until complete. |
| `flush()`      | Flushes any buffered data to the underlying sink. |

### `Seek`
Provides the ability to reposition a byte-oriented stream.

```axiom
interface Seek {
  fn seek(self, pos: SeekFrom) -> Result[Int, IOError];
  fn stream_position(self) -> Result[Int, IOError];
}
```

| Method               | Description |
|----------------------|-------------|
| `seek(pos)`          | Seeks to `pos` relative to `SeekFrom`. Returns the new position from the start of the stream. |
| `stream_position()`  | Returns the current position from the start of the stream. |

---

## Buffered I/O

### `BufReader`

A buffered reader that wraps a raw file descriptor, reducing system calls by reading larger chunks into an internal buffer.

```axiom
type BufReader = { inner: Int; buf: Vec[UInt8]; }
```

#### `BufReader.new(reader)`
Creates a new `BufReader` wrapping the given file descriptor.

```axiom
fn BufReader.new(reader: Int) -> BufReader;
```

#### `BufReader.read_line(buf)`
Reads a line (up to and including the newline) into `buf`. Returns the number of bytes read, or `Err(IOError)`.

```axiom
fn BufReader.read_line(self, buf: &mut Str) -> Result[Int, IOError];
```

#### `BufReader.lines()`
Reads all remaining lines from the buffered reader and returns them as a `Vec[Str]`. Each string has the trailing newline stripped.

```axiom
fn BufReader.lines(self) -> Vec[Str];
```

### `BufWriter`

A buffered writer that wraps a raw file descriptor, accumulating writes in an internal buffer and flushing on overflow or explicit `flush()`.

```axiom
type BufWriter = { inner: Int; buf: Vec[UInt8]; }
```

#### `BufWriter.new(writer)`
Creates a new `BufWriter` wrapping the given file descriptor.

```axiom
fn BufWriter.new(writer: Int) -> BufWriter;
```

---

## File Metadata

The `Metadata` type holds information about a file or directory on disk.

```axiom
type Metadata = {
  size: Int;
  is_file: Bool;
  is_dir: Bool;
  modified: Int;
  created: Int;
  permissions: Int;
}
```

| Field         | Description |
|---------------|-------------|
| `size`        | File size in bytes. |
| `is_file`     | True if this entry is a regular file. |
| `is_dir`      | True if this entry is a directory. |
| `modified`    | Last modification timestamp (Unix timestamp). |
| `created`     | Creation timestamp (Unix timestamp). |
| `permissions` | Platform-specific permission bits. |

### `metadata(path)`
Retrieves metadata for the file or directory at `path`. Returns `Ok(Metadata)` or `Err(IOError)`.

```axiom
fn metadata(path: Str) -> Result[Metadata, IOError>;
```

### `set_permissions(path, perm)`
Sets the permission bits of the file or directory at `path`. Returns `Ok(())` on success or `Err(IOError)`.

```axiom
fn set_permissions(path: Str, perm: Int) -> Result[Unit, IOError];
```

---

## Memory I/O

### `Cursor`

An in-memory buffer that implements `Read`, `Write`, and `Seek`. Useful for testing I/O logic without the file system.

```axiom
type Cursor = { data: Vec[UInt8]; pos: Int; }
```

#### `Cursor.new(data)`
Creates a new `Cursor` initialized with the given byte data, positioned at the start.

```axiom
fn Cursor.new(data: Vec[UInt8]) -> Cursor;
```

#### `Cursor.into_inner()`
Consumes the `Cursor` and returns the underlying byte buffer.

```axiom
fn Cursor.into_inner(self) -> Vec[UInt8];
```

---

## Path Operations

### `join_paths(base, child)`
Joins two path components using the platform-specific separator. Returns a single combined path string.

```axiom
fn join_paths(base: Str, child: Str) -> Str;
```

### `parent_path(path)`
Returns the parent directory of `path`, or `None` if there is no parent (e.g., the root).

```axiom
fn parent_path(path: Str) -> Option[Str];
```

### `file_name(path)`
Returns the file or directory name component of `path` (the last segment), or `None` if the path ends with `..` or is the root.

```axiom
fn file_name(path: Str) -> Option[Str];
```

### `extension(path)`
Returns the file extension (the part after the last `.`), or `None` if the path has no extension.

```axiom
fn extension(path: Str) -> Option[Str];
```

### `is_absolute(path)`
Returns true if `path` is an absolute path (platform-specific: starts with `/` on Unix, or a drive letter on Windows).

```axiom
fn is_absolute(path: Str) -> Bool;
```
