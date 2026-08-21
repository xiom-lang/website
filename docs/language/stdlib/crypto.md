# `xiom.crypto` -- Cryptography

Provides cryptographic primitives including hashing, symmetric and asymmetric encryption, key derivation, and secure random number generation.

```xiom
use xiom.crypto;
```

---

## Hashing

### `sha256(data)`

Computes the SHA-256 hash of the input data and returns the 32-byte digest.

```xiom
pub fn sha256(data: &Vec[UInt8]) -> Vec[UInt8]
```

### `sha512(data)`

Computes the SHA-512 hash of the input data and returns the 64-byte digest.

```xiom
pub fn sha512(data: &Vec[UInt8]) -> Vec[UInt8]
```

### `sha256_hex(data)`

Computes the SHA-256 hash of the input data and returns the result as a hexadecimal string.

```xiom
pub fn sha256_hex(data: &Vec[UInt8]) -> Str
```

### `md5(data)`

Computes the MD5 hash of the input data and returns the 16-byte digest. Note: MD5 is considered cryptographically broken and should not be used for security-sensitive applications.

```xiom
pub fn md5(data: &Vec[UInt8]) -> Vec[UInt8]
```

### `blake3(data)`

Computes the BLAKE3 hash of the input data. BLAKE3 is a high-performance, parallelizable cryptographic hash function.

```xiom
pub fn blake3(data: &Vec[UInt8]) -> Vec[UInt8]
```

### `hmac_sha256(key, data)`

Computes an HMAC using SHA-256 as the underlying hash function. The HMAC provides authentication of `data` using the given `key`.

```xiom
pub fn hmac_sha256(key: &Vec[UInt8], data: &Vec[UInt8]) -> Vec[UInt8]
```

---

## Symmetric Encryption (AES)

### `aes_encrypt(key, plaintext)`

Encrypts `plaintext` using AES in CBC mode with the given `key`. An initialization vector (IV) is generated internally and prepended to the ciphertext.

```xiom
pub fn aes_encrypt(key: &Vec[UInt8], plaintext: &Vec[UInt8]) -> Result<Vec[UInt8], Str>
```

### `aes_decrypt(key, ciphertext)`

Decrypts `ciphertext` that was produced by `aes_encrypt`, extracting the embedded IV.

```xiom
pub fn aes_decrypt(key: &Vec[UInt8], ciphertext: &Vec[UInt8]) -> Result<Vec[UInt8], Str>
```

### `aes_encrypt_gcm(key, nonce, plaintext, aad)`

Encrypts `plaintext` using AES in GCM mode, providing both confidentiality and authentication. Takes a `nonce`, optional additional authenticated data (`aad`), and returns a tuple of `(ciphertext, tag)` where `tag` is the authentication tag.

```xiom
pub fn aes_encrypt_gcm(key: &Vec[UInt8], nonce: &Vec[UInt8], plaintext: &Vec[UInt8], aad: &Vec[UInt8]) -> Result<(Vec[UInt8], Vec[UInt8]), Str>
```

### `aes_decrypt_gcm(key, nonce, ciphertext, tag, aad)`

Decrypts and authenticates AES-GCM ciphertext. Returns the plaintext only if the authentication `tag` validates against the provided `key`, `nonce`, `ciphertext`, and `aad`.

```xiom
pub fn aes_decrypt_gcm(key: &Vec[UInt8], nonce: &Vec[UInt8], ciphertext: &Vec[UInt8], tag: &Vec[UInt8], aad: &Vec[UInt8]) -> Result<Vec[UInt8], Str>
```

---

## Asymmetric (RSA)

### `KeyPair`

A pair of RSA public and private keys, each stored as DER-encoded byte vectors.

```xiom
pub type KeyPair = { public: Vec[UInt8]; private: Vec[UInt8]; }
```

### `generate_rsa_keypair(bits)`

Generates a new RSA key pair with the given key size in bits (e.g., 2048 or 4096).

```xiom
pub fn generate_rsa_keypair(bits: Int) -> Result<KeyPair, Str>
```

### `rsa_encrypt(public_key, data)`

Encrypts `data` using the RSA public key. The data size is limited by the key size.

```xiom
pub fn rsa_encrypt(public_key: &Vec[UInt8], data: &Vec[UInt8]) -> Result<Vec[UInt8], Str>
```

### `rsa_decrypt(private_key, data)`

Decrypts `data` using the RSA private key.

```xiom
pub fn rsa_decrypt(private_key: &Vec[UInt8], data: &Vec[UInt8]) -> Result<Vec[UInt8], Str>
```

### `rsa_sign(private_key, data)`

Creates a digital signature of `data` using the RSA private key.

```xiom
pub fn rsa_sign(private_key: &Vec[UInt8], data: &Vec[UInt8]) -> Result<Vec[UInt8], Str>
```

### `rsa_verify(public_key, data, signature)`

Verifies a digital `signature` of `data` against the RSA public key. Returns `true` if the signature is valid.

```xiom
pub fn rsa_verify(public_key: &Vec[UInt8], data: &Vec[UInt8], signature: &Vec[UInt8]) -> Result<Bool, Str>
```

---

## Key Derivation

### `pbkdf2(password, salt, iterations, key_len)`

Derives a cryptographic key from a password using the PBKDF2 algorithm with the specified number of `iterations` and output `key_len` in bytes. Uses HMAC-SHA256 as the pseudorandom function.

```xiom
pub fn pbkdf2(password: &Str, salt: &Vec[UInt8], iterations: Int, key_len: Int) -> Vec[UInt8]
```

### `argon2(password, salt, memory, iterations, parallelism)`

Derives a key from a password using the Argon2 algorithm, with configurable `memory` cost (in KB), `iterations`, and `parallelism` (thread count). Argon2 is the recommended password hashing function for new applications.

```xiom
pub fn argon2(password: &Str, salt: &Vec[UInt8], memory: Int, iterations: Int, parallelism: Int) -> Vec[UInt8]
```

---

## Random & Comparison

### `secure_random_bytes(count)`

Generates `count` cryptographically secure random bytes using the operating system's CSPRNG.

```xiom
pub fn secure_random_bytes(count: Int) -> Vec[UInt8]
```

### `constant_time_compare(a, b)```

Compares two byte vectors in constant time, preventing timing side-channel attacks. Returns `true` if the contents are equal.

```xiom
pub fn constant_time_compare(a: &Vec[UInt8], b: &Vec[UInt8]) -> Bool
```
