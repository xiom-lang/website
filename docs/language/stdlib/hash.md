<!--
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Hash Module

Hashing infrastructure: the `Hasher` trait, the `Hash` interface, and the default hasher implementation.

```
use xiom.hash;
```

## Hasher

### `Hasher`
The trait for types that compute hash values. Data is fed incrementally via `write`, `write_int`, and `write_str`.

```
pub interface Hasher {
    fn write(self, bytes: &Vec[UInt8]);
    fn write_int(self, n: Int);
    fn write_str(self, s: Str);
    fn finish(self) -> Int;
}
```

### `Hasher.write(self, bytes)`
Feeds a byte slice into the hasher.

### `Hasher.write_int(self, n)`
Feeds an integer into the hasher.

### `Hasher.write_str(self, s)`
Feeds a string into the hasher.

### `Hasher.finish(self)`
Finalizes the hash and returns the computed hash value as an integer.

## Functions

### `hash_value(value)`
Computes the hash of a value that implements the `Hash` trait.

```
pub fn hash_value[T: Hash](value: &T) -> Int;
```

### `hash_combine(seed, hash)`
Combines two hash values using a mixing function (useful for composite types).

```
pub fn hash_combine(seed: Int, hash: Int) -> Int;
```

## DefaultHasher

### `DefaultHasher`
The default hash algorithm (SipHash-like). Suitable for use in hash maps.

```
pub type DefaultHasher = { state: Int; } derive[Clone]
```

### `DefaultHasher.new()`
Creates a new `DefaultHasher` with an initial state.

```
pub fn DefaultHasher.new() -> DefaultHasher;
```
