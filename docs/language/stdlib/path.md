<!--
Copyright (c) 2026 XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Path Module

File path manipulation with `Path` (borrowed) and `PathBuf` (owned) types. Provides platform-aware path parsing, joining, and filesystem queries.

```
use xiom.path;
```

## Types

### `Path`
A borrowed path string.

```
pub type Path = { inner: Str; } derive[Eq, Clone, Hash, Ord]
```

### `PathBuf`
An owned, mutable path string.

```
pub type PathBuf = { inner: Str; } derive[Eq, Clone]
```

## Constructors

### `Path.new(s)`
Creates a `Path` from a string.

```
pub fn Path.new(s: Str) -> Path;
```

### `PathBuf.new()`
Creates an empty `PathBuf`.

```
pub fn PathBuf.new() -> PathBuf;
```

### `PathBuf.from(s)`
Creates a `PathBuf` from a string.

```
pub fn PathBuf.from(s: Str) -> PathBuf;
```

## Path Operations

### `Path.parent(self)`
Returns the parent directory of the path, or `None` if there is no parent.

```
pub fn Path.parent(self) -> Option<Path>;
```

### `Path.file_name(self)`
Returns the file name component of the path.

```
pub fn Path.file_name(self) -> Option<Str>;
```

### `Path.extension(self)`
Returns the file extension (the part after the last `.`).

```
pub fn Path.extension(self) -> Option<Str>;
```

### `Path.file_stem(self)`
Returns the file name without the extension.

```
pub fn Path.file_stem(self) -> Option<Str>;
```

### `Path.is_absolute(self)`
Returns `true` if the path is absolute.

```
pub fn Path.is_absolute(self) -> Bool;
```

### `Path.is_relative(self)`
Returns `true` if the path is relative.

```
pub fn Path.is_relative(self) -> Bool;
```

### `Path.has_root(self)`
Returns `true` if the path has a root component.

```
pub fn Path.has_root(self) -> Bool;
```

### `Path.components(self)`
Splits the path into its individual components.

```
pub fn Path.components(self) -> Vec<Str>;
```

### `Path.to_str(self)`
Returns the path as a string.

```
pub fn Path.to_str(self) -> Str;
```

### `Path.join(self, child)`
Joins the path with a child path component, producing a `PathBuf`.

```
pub fn Path.join(self, child: Str) -> PathBuf;
```

### `Path.with_extension(self, ext)`
Replaces the file extension with a new one, returning a `PathBuf`.

```
pub fn Path.with_extension(self, ext: Str) -> PathBuf;
```

### `Path.with_file_name(self, name)`
Replaces the file name with a new one, returning a `PathBuf`.

```
pub fn Path.with_file_name(self, name: Str) -> PathBuf;
```

### `Path.exists(self)`
Returns `true` if the path points to an existing filesystem entry.

```
pub fn Path.exists(self) -> Bool;
```

### `Path.is_file(self)`
Returns `true` if the path points to a regular file.

```
pub fn Path.is_file(self) -> Bool;
```

### `Path.is_dir(self)`
Returns `true` if the path points to a directory.

```
pub fn Path.is_dir(self) -> Bool;
```

### `Path.metadata(self)`
Returns the filesystem metadata for the path.

```
pub fn Path.metadata(self) -> Result<Metadata, Str>;
```

### `Path.canonicalize(self)`
Resolves the path to its canonical, absolute form.

```
pub fn Path.canonicalize(self) -> Result<PathBuf, Str>;
```

### `Path.starts_with(self, base)`
Returns `true` if the path starts with the given base path.

```
pub fn Path.starts_with(self, base: &Path) -> Bool;
```

### `Path.ends_with(self, child)`
Returns `true` if the path ends with the given child path.

```
pub fn Path.ends_with(self, child: &Path) -> Bool;
```

## PathBuf Operations

### `PathBuf.push(self, component)`
Appends a path component to the buffer.

```
pub fn PathBuf.push(self, component: Str);
```

### `PathBuf.pop(self)`
Removes the last path component. Returns `false` if the buffer was empty.

```
pub fn PathBuf.pop(self) -> Bool;
```

### `PathBuf.as_path(self)`
Returns a borrowed `Path` from the buffer.

```
pub fn PathBuf.as_path(self) -> Path;
```

### `PathBuf.clear(self)`
Clears the path buffer to an empty string.

```
pub fn PathBuf.clear(self);
```

## Utility

### `path_separator()`
Returns the platform-specific path separator (`/` or `\`).

```
pub fn path_separator() -> Str;
```
