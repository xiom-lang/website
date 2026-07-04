# Environment Module

Environment variable access, process argument querying, directory helpers, and platform constants.

```
use xiom.env;
```

## Environment Variables

### `var(name)`
Returns the value of the environment variable `name`, or an error if it is not set.

```
pub fn var(name: Str) -> Result[Str, Str];
```

### `var_opt(name)`
Returns the value of the environment variable `name`, or `None` if it is not set.

```
pub fn var_opt(name: Str) -> Option[Str];
```

### `set_var(name, value)`
Sets the environment variable `name` to `value` for the current process.

```
pub fn set_var(name: Str, value: Str);
```

### `remove_var(name)`
Removes the environment variable `name` from the current process.

```
pub fn remove_var(name: Str);
```

### `vars()`
Returns a list of all environment variable key-value pairs.

```
pub fn vars() -> Vec<(Str, Str)>;
```

## Process Arguments

### `args()`
Returns the command-line arguments passed to the current process.

```
pub fn args() -> Vec<Str>;
```

### `args_os()`
Returns the raw OS-level command-line arguments.

```
pub fn args_os() -> Vec<Str>;
```

### `current_exe()`
Returns the full filesystem path of the current executable.

```
pub fn current_exe() -> Result<Str, Str>;
```

## Directories

### `current_dir()`
Returns the current working directory.

```
pub fn current_dir() -> Result<Str, Str>;
```

### `set_current_dir(path)`
Sets the current working directory to `path`.

```
pub fn set_current_dir(path: Str) -> Result[Unit, Str>;
```

### `temp_dir()`
Returns the system temporary directory path.

```
pub fn temp_dir() -> Str;
```

### `home_dir()`
Returns the current user's home directory, if available.

```
pub fn home_dir() -> Option<Str>;
```

### `data_dir()`
Returns the platform-specific application data directory, if available.

```
pub fn data_dir() -> Option<Str>;
```

### `cache_dir()`
Returns the platform-specific application cache directory, if available.

```
pub fn cache_dir() -> Option<Str>;
```

### `config_dir()`
Returns the platform-specific application config directory, if available.

```
pub fn config_dir() -> Option<Str>;
```

### `executable_dir()`
Returns the directory containing the current executable, if available.

```
pub fn executable_dir() -> Option<Str>;
```

## Path Utilities

### `join_paths(a, b)`
Joins two path components using the platform-specific separator.

```
pub fn join_paths(a: Str, b: Str) -> Str;
```

### `path_separator()`
Returns the platform-specific path separator character.

```
pub fn path_separator() -> Str;
```

## Platform Constants

### `OS`
A string constant identifying the operating system (e.g., `"windows"`, `"linux"`, `"macos"`).

```
pub const OS: Str;
```

### `ARCH`
A string constant identifying the CPU architecture (e.g., `"x86_64"`, `"aarch64"`).

```
pub const ARCH: Str;
```

### `FAMILY`
A string constant identifying the OS family (e.g., `"windows"`, `"unix"`).

```
pub const FAMILY: Str;
```
