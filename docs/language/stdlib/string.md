<!--
Copyright (c) 2026 Eleftherios Notas and XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# String Library

The `string` module provides functions for inspecting, manipulating, and converting strings. Operations include length queries, concatenation, slicing, searching, splitting, trimming, case conversion, formatting, and extraction of characters, lines, and words.

```
use xiom.string;
```

---

## Length & Inspection

### `str_len(s)`
Returns the length of `s` in bytes.

```xiom
fn str_len(s: Str) -> Int;
```

### `char_count(s)`
Returns the number of Unicode characters (code points) in `s`. This may differ from `str_len` for strings containing multi-byte characters.

```xiom
fn char_count(s: Str) -> Int;
```

### `byte_count(s)`
Returns the number of bytes in `s`. Equivalent to `str_len`.

```xiom
fn byte_count(s: Str) -> Int;
```

### `is_empty(s)`
Returns true if `s` has zero length.

```xiom
fn is_empty(s: Str) -> Bool;
```

---

## Building & Slicing

### `str_concat(a, b)`
Returns a new string formed by concatenating `a` and `b`.

```xiom
fn str_concat(a: Str, b: Str) -> Str;
```

### `str_slice(s, start, end)`
Returns a substring of `s` from byte offset `start` (inclusive) to `end` (exclusive). Offsets must be valid UTF-8 boundaries.

```xiom
fn str_slice(s: Str, start: Int, end: Int) -> Str;
```

### `char_at(s, pos)`
Returns the Unicode character at byte position `pos` in `s`, or `None` if `pos` is out of bounds or not at a valid UTF-8 boundary.

```xiom
fn char_at(s: Str, pos: Int) -> Option[Char];
```

---

## Searching

### `str_contains(s, substr)`
Returns true if `s` contains the substring `substr`.

```xiom
fn str_contains(s: Str, substr: Str) -> Bool;
```

### `str_starts_with(s, prefix)`
Returns true if `s` starts with `prefix`.

```xiom
fn str_starts_with(s: Str, prefix: Str) -> Bool;
```

### `str_ends_with(s, suffix)`
Returns true if `s` ends with `suffix`.

```xiom
fn str_ends_with(s: Str, suffix: Str) -> Bool;
```

### `index_of(s, substr)`
Returns the byte offset of the first occurrence of `substr` in `s`, or `None` if not found.

```xiom
fn index_of(s: Str, substr: Str) -> Option[Int];
```

### `last_index_of(s, substr)`
Returns the byte offset of the last occurrence of `substr` in `s`, or `None` if not found.

```xiom
fn last_index_of(s: Str, substr: Str) -> Option[Int];
```

---

## Transformation

### `str_split(s, delimiter)`
Splits `s` by `delimiter` and returns the parts as a `Vec[Str]`. The delimiter is not included in the output.

```xiom
fn str_split(s: Str, delimiter: Str) -> Vec[Str];
```

### `str_trim(s)`
Returns a new string with leading and trailing whitespace removed.

```xiom
fn str_trim(s: Str) -> Str;
```

### `str_upper(s)`
Returns a new string with all characters converted to uppercase.

```xiom
fn str_upper(s: Str) -> Str;
```

### `str_lower(s)`
Returns a new string with all characters converted to lowercase.

```xiom
fn str_lower(s: Str) -> Str;
```

### `replace(s, from, to)`
Returns a new string with all non-overlapping occurrences of `from` replaced with `to`.

```xiom
fn replace(s: Str, from: Str, to: Str) -> Str;
```

---

## Parsing

### `str_to_int(s)`
Parses the string `s` as a signed integer. Returns `Ok(Int)` on success or `Err(Str)` if the string is not a valid integer.

```xiom
fn str_to_int(s: Str) -> Result[Int, Str];
```

### `str_to_float(s)`
Parses the string `s` as a 64-bit floating-point number. Returns `Ok(Float64)` on success or `Err(Str)` if parsing fails.

```xiom
fn str_to_float(s: Str) -> Result[Float64, Str];
```

---

## Lines & Words

### `lines(s)`
Splits `s` on newline boundaries and returns each line as a `Str` in a `Vec[Str]`. Newline characters are not included in the output lines.

```xiom
fn lines(s: Str) -> Vec[Str];
```

### `words(s)`
Splits `s` on whitespace boundaries and returns each word as a `Str` in a `Vec[Str]`.

```xiom
fn words(s: Str) -> Vec[Str];
```

---

## Formatting

### `format(fmt, args...)`
Formats a string using `fmt` as a template with variadic arguments. The syntax of the format string follows XIOM's standard format specifiers (e.g., `{}` for positional argument insertion).

```xiom
fn format(fmt: Str, args: ...) -> Str;
```
