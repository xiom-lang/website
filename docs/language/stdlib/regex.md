<!--
Copyright (c) 2026 Eleftherios Notas and XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Regex Module

Regular expression matching, searching, replacing, splitting, and capture groups.

```
use xiom.regex;
```

## Types

### `Regex`
A compiled regular expression pattern.

```
pub type Regex = { pattern: Str; compiled: Int; } derive[Clone]
```

### `Match`
A single match result with start/end positions and the matched text.

```
pub type Match = { start: Int; end: Int; text: Str; } derive[Eq, Clone]
```

### `Captures`
The capture groups from a regex match.

```
pub type Captures = { groups: Vec[Option[Match]]; } derive[Clone]
```

## Compilation

### `Regex.new(pattern)`
Compiles a regular expression pattern. Returns an error if the pattern is invalid.

```
pub fn Regex.new(pattern: Str) -> Result<Regex, Str>;
```

## Matching

### `Regex.is_match(self, text)`
Returns `true` if the regex matches anywhere in the text.

```
pub fn Regex.is_match(self, text: Str) -> Bool;
```

### `Regex.find(self, text)`
Returns the first match of the regex in the text, or `None`.

```
pub fn Regex.find(self, text: Str) -> Option<Match>;
```

### `Regex.find_all(self, text)`
Returns all non-overlapping matches of the regex in the text.

```
pub fn Regex.find_all(self, text: Str) -> Vec<Match>;
```

### `Regex.match_count(self, text)`
Returns the number of non-overlapping matches in the text.

```
pub fn Regex.match_count(self, text: Str) -> Int;
```

## Capture Groups

### `Regex.captures(self, text)`
Returns the capture groups for the first match in the text.

```
pub fn Regex.captures(self, text: Str) -> Option<Captures>;
```

### `Captures.get(self, index)|
Returns the match for the capture group at the given index (0 = the full match).

```
pub fn Captures.get(self, index: Int) -> Option<Match>;
```

### `Captures.get_named(self, name)`
Returns the match for the named capture group, or `None` if the group does not exist.

```
pub fn Captures.get_named(self, name: Str) -> Option<Match>;
```

### `Captures.len(self)`
Returns the number of capture groups (including the implicit group 0).

```
pub fn Captures.len(self) -> Int;
```

## Replacement

### `Regex.replace(self, text, replacement)`
Replaces the first match with the replacement string. Supports backreferences (e.g., `$1`, `$name`).

```
pub fn Regex.replace(self, text: Str, replacement: Str) -> Str;
```

### `Regex.replace_all(self, text, replacement)`
Replaces all non-overlapping matches with the replacement string.

```
pub fn Regex.replace_all(self, text: Str, replacement: Str) -> Str;
```

## Splitting

### `Regex.split(self, text)`
Splits the text at each match of the regex.

```
pub fn Regex.split(self, text: Str) -> Vec<Str>;
```

## Escaping & Validation

### `regex_escape(pattern)|
Escapes special characters in a string so it can be used as a literal pattern in a regex.

```
pub fn regex_escape(pattern: Str) -> Str;
```

### `is_valid_regex(pattern)`
Returns `true` if the pattern string is a valid regular expression.

```
pub fn is_valid_regex(pattern: Str) -> Bool;
```
