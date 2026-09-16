<!--
Copyright (c) 2026 Eleftherios Notas and XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Operating System Module

Operating system interface: platform detection, process management, filesystem operations, signals, pipes, and file watching.

```
use xiom.os;
```

## System Information

### `platform()`
Returns a string identifying the OS platform (e.g., `"windows"`, `"linux"`, `"macos"`).

```
pub fn platform() -> Str;
```

### `cpu_count()`
Returns the number of logical CPU cores available.

```
pub fn cpu_count() -> Int;
```

### `total_memory()`
Returns the total physical memory in bytes.

```
pub fn total_memory() -> Int;
```

### `free_memory()`
Returns the amount of free physical memory in bytes.

```
pub fn free_memory() -> Int;
```

### `arch()`
Returns the CPU architecture string (e.g., `"x86_64"`, `"aarch64"`).

```
pub fn arch() -> Str;
```

## Environment

### `env_set(name, value)`
Sets an environment variable for the current process.

```
pub fn env_set(name: Str, value: Str);
```

### `env_unset(name)`
Removes an environment variable from the current process.

```
pub fn env_unset(name: Str);
```

### `env_vars()`
Returns a map of all environment variables.

```
pub fn env_vars() -> Map[Str, Str];
```

### `set_env(name, value)`
Alias for `env_set`.

```
fn set_env(name: Str, value: Str);
```

### `unset_env(name)`
Alias for `env_unset`.

```
fn unset_env(name: Str);
```

## Directory Operations

### `current_dir()`
Returns the current working directory as a string.

```
pub fn current_dir() -> Str;
```

### `set_current_dir(path)`
Sets the current working directory.

```
pub fn set_current_dir(path: Str) -> Result[Unit, Str];
```

### `temp_dir()`
Returns the system's temporary directory path.

```
pub fn temp_dir() -> Str;
```

### `home_dir()`
Returns the current user's home directory, if available.

```
pub fn home_dir() -> Option[Str];
```

## OS Detection

### `is_windows()`
Returns `true` if the current OS is Windows.

```
fn is_windows() -> Bool;
```

### `is_linux()`
Returns `true` if the current OS is Linux.

```
fn is_linux() -> Bool;
```

### `is_macos()`
Returns `true` if the current OS is macOS.

```
fn is_macos() -> Bool;
```

## Permissions

### `set_permissions(path, mode)`
Sets filesystem permissions for the given path using a numeric mode.

```
fn set_permissions(path: Str, mode: Int) -> Result[Unit, Str];
```

### `get_permissions(path)`
Returns the numeric permission mode for the given path.

```
fn get_permissions(path: Str) -> Result[Int, Str];
```

## Symlinks

### `read_link(path)`
Reads the target of a symbolic link.

```
fn read_link(path: Str) -> Result[Str, Str];
```

### `create_symlink(original, link)`
Creates a symbolic link at `link` pointing to `original`.

```
fn create_symlink(original: Str, link: Str) -> Result[Unit, Str];
```

### `is_symlink(path)`
Returns `true` if the path points to a symbolic link.

```
fn is_symlink(path: Str) -> Bool;
```

## Temp Files

### `temp_file()`
Creates a temporary file and returns its path.

```
fn temp_file() -> Result[Str, Str];
```

### `temp_dir_os()`
Creates a temporary directory and returns its path.

```
fn temp_dir_os() -> Result[Str, Str];
```

## Process Management

### `spawn(command, args)`
Spawns a child process with the given command and arguments. Returns the process PID.

```
fn spawn(command: Str, args: Vec[Str]) -> Result[Int, Str];
```

### `spawn_piped(command, args)`
Spawns a child process with piped stdin/stdout/stderr. Returns `(pid, stdin_fd, stdout_fd, stderr_fd)`.

```
fn spawn_piped(command: Str, args: Vec[Str]) -> Result[(Int, Int, Int), Str];
```

### `wait(pid)`
Waits for a child process to exit and returns its exit code.

```
fn wait(pid: Int) -> Result[Int, Str];
```

### `kill(pid)`
Sends a SIGKILL to the given process.

```
fn kill(pid: Int) -> Result[Unit, Str];
```

### `ChildProcess`
A handle to a child process with piped I/O.

```
pub type ChildProcess = {
    pid: Int;
    stdin: Int;
    stdout: Int;
    stderr: Int;
}
```

### `ChildProcess.wait(self)`
Waits for the child process to exit and returns its exit code.

```
pub fn ChildProcess.wait(self) -> Result[Int, Str];
```

### `ChildProcess.kill(self)`
Kills the child process.

```
pub fn ChildProcess.kill(self) -> Result[Unit, Str];
```

### `ChildProcess.id(self)`
Returns the process ID of the child.

```
pub fn ChildProcess.id(self) -> Int;
```

## Filesystem Walk

### `walk_dir(path, callback)`
Recursively walks a directory, calling `callback` with the path and metadata for each entry.

```
pub fn walk_dir(path: Str, callback: fn(Str, Metadata) -> Unit) -> Result[Unit, Str];
```

### `walk_dir_filtered(path, pattern, callback)`
Recursively walks a directory, calling `callback` only for entries whose name matches the glob `pattern`.

```
pub fn walk_dir_filtered(path: Str, pattern: Str, callback: fn(Str, Metadata) -> Unit) -> Result[Unit, Str];
```

## File Watching

### `FileWatcher`
A handle for watching filesystem changes.

```
pub type FileWatcher = { path: Str; recursive: Bool; }
```

### `watch_file(path)`
Starts watching a specific file for changes.

```
pub fn watch_file(path: Str) -> Result[FileWatcher, Str];
```

### `watch_dir(path, recursive)`
Starts watching a directory for changes. If `recursive` is true, watches subdirectories as well.

```
pub fn watch_dir(path: Str, recursive: Bool) -> Result[FileWatcher, Str];
```

### `FileWatcher.poll(self)`
Polls for file events since the last poll. Returns the list of events.

```
pub fn FileWatcher.poll(self) -> Result[Vec[FileEvent], Str];
```

### `FileWatcher.close(self)`
Stops watching and releases resources.

```
pub fn FileWatcher.close(self);
```

### `FileEvent`
An enum representing filesystem events.

```
pub type FileEvent = enum {
    Created(path: Str),
    Modified(path: Str),
    Deleted(path: Str),
    Renamed(from: Str, to: Str),
}
```

## Signal Handling

### `on_signal(signal, handler)`
Registers a handler function for the given OS signal.

```
pub fn on_signal(signal: Int, handler: fn(Int) -> Unit);
```

### `raise_signal(signal)`
Sends the given signal to the current process.

```
pub fn raise_signal(signal: Int);
```

### Signal Constants

```
pub const SIGINT: Int;
pub const SIGTERM: Int;
pub const SIGKILL: Int;
pub const SIGUSR1: Int;
pub const SIGUSR2: Int;
```

## Pipe

### `Pipe`
A unidirectional inter-process communication channel.

```
pub type Pipe = { read_fd: Int; write_fd: Int; }
```

### `create_pipe()`
Creates a new pipe and returns the read/write file descriptors.

```
pub fn create_pipe() -> Result[Pipe, Str];
```

### `Pipe.read(self, buf)`
Reads data from the pipe into the buffer. Returns the number of bytes read.

```
pub fn Pipe.read(self, buf: &mut Vec[UInt8]) -> Result[Int, Str];
```

### `Pipe.write(self, data)`
Writes data to the pipe. Returns the number of bytes written.

```
pub fn Pipe.write(self, data: &Vec[UInt8]) -> Result[Int, Str];
```

### `Pipe.close_read(self)`
Closes the read end of the pipe.

```
pub fn Pipe.close_read(self);
```

### `Pipe.close_write(self)`
Closes the write end of the pipe.

```
pub fn Pipe.close_write(self);
```

## Disk Usage

### `disk_free(path)`
Returns the amount of free disk space at the given path in bytes.

```
pub fn disk_free(path: Str) -> Result[Int, Str];
```

### `disk_total(path)`
Returns the total disk space at the given path in bytes.

```
pub fn disk_total(path: Str) -> Result[Int, Str];
```

### `file_size_bytes(path)`
Returns the size of the file at the given path in bytes.

```
pub fn file_size_bytes(path: Str) -> Result[Int, Str];
```
