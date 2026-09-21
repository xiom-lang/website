<!--
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Encoding Module

Text encoding and decoding utilities: Base64, Hex, URL, Percent, and UTF-8 encoding.

```
use xiom.encoding;
```

## Base64

### `base64_encode(data)`
Encodes bytes as a standard Base64 string.

```
pub fn base64_encode(data: &Vec[UInt8]) -> Str;
```

### `base64_decode(encoded)`
Decodes a standard Base64 string to bytes.

```
pub fn base64_decode(encoded: Str) -> Result<Vec[UInt8], Str>;
```

### `base64url_encode(data)`
Encodes bytes as a URL-safe Base64 string (no padding, `-` and `_` instead of `+` and `/`).

```
pub fn base64url_encode(data: &Vec[UInt8]) -> Str;
```

### `base64url_decode(encoded)`
Decodes a URL-safe Base64 string to bytes.

```
pub fn base64url_decode(encoded: Str) -> Result<Vec[UInt8], Str>;
```

## Hex

### `hex_encode(data)`
Encodes bytes as a lowercase hexadecimal string.

```
pub fn hex_encode(data: &Vec[UInt8]) -> Str;
```

### `hex_decode(encoded)`
Decodes a hexadecimal string to bytes.

```
pub fn hex_decode(encoded: Str) -> Result<Vec[UInt8], Str>;
```

### `hex_encode_upper(data)`
Encodes bytes as an uppercase hexadecimal string.

```
pub fn hex_encode_upper(data: &Vec[UInt8]) -> Str;
```

## URL Encoding

### `url_encode(data)`
Encodes a string for use in a URL (form-encoded).

```
pub fn url_encode(data: Str) -> Str;
```

### `url_decode(encoded)`
Decodes a URL-encoded string.

```
pub fn url_decode(encoded: Str) -> Result<Str, Str>;
```

## Percent Encoding

### `percent_encode(data)`
Percent-encodes a string (RFC 3986).

```
pub fn percent_encode(data: Str) -> Str;
```

### `percent_decode(encoded)`
Decodes a percent-encoded string.

```
pub fn percent_decode(encoded: Str) -> Result<Str, Str>;
```

## UTF-8

### `utf8_encode(s)`
Encodes a string as UTF-8 bytes.

```
pub fn utf8_encode(s: Str) -> Vec[UInt8];
```

### `utf8_decode(data)`
Decodes UTF-8 bytes into a string. Returns an error if the data is invalid UTF-8.

```
pub fn utf8_decode(data: &Vec[UInt8]) -> Result<Str, Str>;
```

### `utf8_valid(data)`
Returns `true` if the byte sequence is valid UTF-8.

```
pub fn utf8_valid(data: &Vec[UInt8]) -> Bool;
```

### `utf8_char_len(first_byte)`
Returns the number of bytes (1-4) of a UTF-8 character given its leading byte.

```
pub fn utf8_char_len(first_byte: UInt8) -> Int;
```

## Binary to Text

### `binary_to_text(data, format)`
Encodes bytes as text using the specified format: `0` = Base64, `1` = hex, `2` = Base64 URL-safe.

```
pub fn binary_to_text(data: &Vec[UInt8], format: Int) -> Str;
```

### `text_to_binary(text, format)`
Decodes text to bytes using the specified format: `0` = Base64, `1` = hex, `2` = Base64 URL-safe.

```
pub fn text_to_binary(text: Str, format: Int) -> Result<Vec[UInt8], Str>;
```
