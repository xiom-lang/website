<!--
Copyright (c) 2026 XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Character Module

Unicode character classification, case conversion, digit conversion, and UTF-8 encoding utilities.

```
use xiom.char;
```

## Classification

### `is_alphabetic(c)`
Returns `true` if the character is an alphabetic Unicode letter.

```
pub fn is_alphabetic(c: Char) -> Bool;
```

### `is_alphanumeric(c)`
Returns `true` if the character is alphabetic or a decimal digit.

```
pub fn is_alphanumeric(c: Char) -> Bool;
```

### `is_ascii(c)`
Returns `true` if the character is in the ASCII range (U+0000-U+007F).

```
pub fn is_ascii(c: Char) -> Bool;
```

### `is_control(c)`
Returns `true` if the character is a control character (U+0000-U+001F, U+007F-U+009F).

```
pub fn is_control(c: Char) -> Bool;
```

### `is_digit(c)`
Returns `true` if the character is an ASCII decimal digit (0-9).

```
pub fn is_digit(c: Char) -> Bool;
```

### `is_lowercase(c)`
Returns `true` if the character has the Unicode Lowercase property.

```
pub fn is_lowercase(c: Char) -> Bool;
```

### `is_uppercase(c)`
Returns `true` if the character has the Unicode Uppercase property.

```
pub fn is_uppercase(c: Char) -> Bool;
```

### `is_numeric(c)`
Returns `true` if the character is a Unicode numeric character (digits, fractions, Roman numerals, etc.).

```
pub fn is_numeric(c: Char) -> Bool;
```

### `is_punctuation(c)`
Returns `true` if the character is a Unicode punctuation character.

```
pub fn is_punctuation(c: Char) -> Bool;
```

### `is_whitespace(c)`
Returns `true` if the character is a Unicode whitespace character.

```
pub fn is_whitespace(c: Char) -> Bool;
```

## Case Conversion

### `to_lowercase(c)`
Converts the character to its lowercase equivalent.

```
pub fn to_lowercase(c: Char) -> Char;
```

### `to_uppercase(c)`
Converts the character to its uppercase equivalent.

```
pub fn to_uppercase(c: Char) -> Char;
```

## Digit Conversion

### `to_digit(c, radix)`
Converts a character to its numeric digit value in the given radix (2-36). Returns `None` if the character is not a valid digit.

```
pub fn to_digit(c: Char, radix: Int) -> Option[Int];
```

### `from_digit(n, radix)`
Converts a numeric digit value (0-35) to its character representation in the given radix (2-36). Returns `None` if the value is out of range.

```
pub fn from_digit(n: Int, radix: Int) -> Option[Char];
```

## UTF-8 Encoding

### `len_utf8(c)`
Returns the number of UTF-8 bytes required to encode the character (1-4).

```
pub fn len_utf8(c: Char) -> Int;
```

### `encode_utf8(c, buf)`
Encodes the character as UTF-8 and appends the bytes to the provided buffer.

```
pub fn encode_utf8(c: Char, buf: &mut Vec[UInt8]);
```
