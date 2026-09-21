<!--
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# `xiom.serialize` -- Serialization

Provides interfaces and utilities for serializing and deserializing data in JSON and binary formats. Deserialization preserves and validates contracts (invariants).

```xiom
use xiom.serialize;
```

---

## Traits

### `Serialize`

The `Serialize` interface must be implemented by types that can be serialized. Provides three serialization methods covering text (default), JSON, and binary formats.

```xiom
pub interface Serialize {
  fn serialize(self) -> Result[Str, SerializeError];
  fn serialize_json(self) -> Result[Str, SerializeError];
  fn serialize_bytes(self) -> Result[Vec[UInt8], SerializeError];
}
```

### `Deserialize`

The `Deserialize` interface must be implemented by types that can be deserialized. Each method has a postcondition `ensures` that validates the result's invariants (contract preservation), guaranteeing that deserialized values satisfy their type contracts.

```xiom
pub interface Deserialize {
  fn deserialize(data: Str) -> Result[Self, SerializeError]
    ensures: result is Ok => self.invariant_check()
  fn deserialize_json(data: Str) -> Result[Self, SerializeError]
    ensures: result is Ok => self.invariant_check()
  fn deserialize_bytes(data: Vec[UInt8]) -> Result[Self, SerializeError]
    ensures: result is Ok => self.invariant_check()
}
```

---

## Types

### `SerializeError`

Represents a serialization or deserialization failure with detailed location information. Error kind codes: `0=Unknown`, `1=InvalidFormat`, `2=MissingField`, `3=TypeMismatch`, `4=ContractViolation`, `5=UnsupportedType`.

```xiom
pub type SerializeError = {
  kind: Int;
  message: Str;
  path: Str;
  line: Int;
  col: Int;
} derive[Eq, Clone, Display]
```

### `SerializeError.format_error()`

Formats the `SerializeError` into a human-readable error string.

```xiom
pub fn SerializeError.format_error() -> Str
```

### `JsonValue`

A recursive enum representing parsed JSON values. Supports `Null`, `Bool`, `Number`, `String`, `Array`, and `Object` variants.

```xiom
pub type JsonValue = enum {
  Null,
  Bool(value: Bool),
  Number(value: Float64),
  String(value: Str),
  Array(items: Vec[JsonValue]),
  Object(entries: Map[Str, JsonValue]),
}
```

---

## Format Detection

### `detect_format(data)`

Detects the serialization format of a byte buffer by inspecting its magic bytes or structure. Returns a string identifying the format (e.g., `"json"`, `"binary"`).

```xiom
pub fn detect_format(data: &Vec[UInt8]) -> Str
```

### `is_valid_json(data)`

Checks whether a string is syntactically valid JSON.

```xiom
pub fn is_valid_json(data: Str) -> Bool
```

### `is_valid_bytes(data)`

Checks whether a byte buffer contains valid binary serialization data.

```xiom
pub fn is_valid_bytes(data: &Vec[UInt8]) -> Bool
```

---

## JSON Helpers

### `json_string(s)`

Produces a JSON-encoded string literal from a plain string, including proper escaping.

```xiom
pub fn json_string(s: Str) -> Str
```

### `json_number(n)`

Produces a JSON number literal from a `Float64` value.

```xiom
pub fn json_number(n: Float64) -> Str
```

### `json_bool(b)`

Produces a JSON boolean literal (`true` or `false`).

```xiom
pub fn json_bool(b: Bool) -> Str
```

### `json_null()`

Produces the JSON null literal.

```xiom
pub fn json_null() -> Str
```

### `json_array(items)`

Produces a JSON array string from a vector of pre-serialized item strings.

```xiom
pub fn json_array(items: Vec[Str]) -> Str
```

### `json_object(pairs)`

Produces a JSON object string from a vector of key-value pairs, where each key and value is a pre-serialized JSON string.

```xiom
pub fn json_object(pairs: Vec[(Str, Str)]) -> Str
```

### `json_parse(data)`

Parses a JSON string into a `JsonValue` enum. Returns the parsed value on success.

```xiom
pub fn json_parse(data: Str) -> Result[JsonValue, SerializeError]
```

---

## Binary Helpers

### `little_endian()`

Returns `true` if the current system uses little-endian byte ordering.

```xiom
pub fn little_endian() -> Bool
```

### `big_endian()`

Returns `true` if the current system uses big-endian byte ordering.

```xiom
pub fn big_endian() -> Bool
```
