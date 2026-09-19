<!--
Copyright (c) 2026 XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# XIOM Standard Library API

> **44 modules.** Types (`Option`, `Result`, `Vec`, `Int`, `Str`...) are built-in -- no import needed.
> Functions live in modules -- import with `use xiom.<module>`.
> Beta: the library is still being completed; see the
> [known limitations](https://github.com/xiom-lang/stdlib/blob/main/docs/STDLIB_BETA_LIMITATIONS.md)
> for current gaps.

---

## Foundation

Core types, interfaces, and utilities used by every XIOM program.

| Module | Import | Description |
|--------|--------|-------------|
| **[core](stdlib/core.md)** | `use xiom.core;` | `Option[T]`, `Result[T, E]`, `Box[T]`, `BinaryHeap[T]`. 13 interfaces (Clone, Eq, Ord, Display, Hash, Add, Sub, Mul, Div, Iterator, IntoIterator, Default, Drop). Numeric conversions, contract methods (`is_sorted`, `all`, `none`, `contains`), numeric limits. |
| **[error](stdlib/error.md)** | `use xiom.error;` | `Error` interface, `From<T>` for error conversion, `IOError`, `NetError`, `ParseError` types. |
| **[char](stdlib/char.md)** | `use xiom.char;` | Unicode character classification (`is_digit`, `is_alpha`, `is_whitespace`) and transformation (`to_upper`, `to_lower`). |

---

## I/O & Filesystem

Console input/output, file operations, and path manipulation.

| Module | Import | Description |
|--------|--------|-------------|
| **[io](stdlib/io.md)** | `use xiom.io;` | Console: `print`, `println`, `read_line`, `read_int`, `read_float`. Files: `read_file`, `write_file`, `append_file`, `copy_file`, `remove_file`, `rename`. Directories: `create_dir`, `list_dir`, `is_dir`, `file_exists`. Process: `exit`, `args`, `env_var`. Timing: `time_now`, `sleep`. |
| **[path](stdlib/path.md)** | `use xiom.path;` | Path operations: `join`, `basename`, `dirname`, `extension`, `is_absolute`, `normalize`, `home_dir`, `current_dir`, `temp_dir`. |

---

## Data Structures

Collections and container types.

| Module | Import | Description |
|--------|--------|-------------|
| **[collections](stdlib/collections.md)** | `use xiom.collections;` | `Vec[T]` (push, pop, get, insert, remove, first, last, set), `Map[K,V]` (insert, get, remove, contains, keys, values), `Set[T]` (insert, contains, remove, union, intersection, difference), `VecDeque`, `BTreeMap`, `BTreeSet`, `LinkedList`, `Queue`, `Stack`. |
| **[array](stdlib/array.md)** | `use xiom.array;` | Fixed-size array operations: `len`, `get`, `set`, `fill`, `slice`. |

---

## Text & Encoding

String manipulation and character encoding.

| Module | Import | Description |
|--------|--------|-------------|
| **[string](stdlib/string.md)** | `use xiom.string;` | UTF-8 operations: `str_len`, `str_concat`, `str_slice`, `str_contains`, `str_split`, `str_trim`, `str_upper`, `str_lower`, `replace`, `format`, `char_at`, `index_of`, `last_index_of`. Parsing: `str_to_int`, `str_to_float`. |
| **[encoding](stdlib/encoding.md)** | `use xiom.encoding;` | Text encoding: `utf8_encode`, `utf8_decode`, `base64_encode`, `base64_decode`, `hex_encode`, `hex_decode`. |

---

## Mathematics

Numeric operations, trigonometry, and random numbers.

| Module | Import | Description |
|--------|--------|-------------|
| **[math](stdlib/math.md)** | `use xiom.math;` | Constants: `PI`, `E`, `TAU`. Fast libm-backed: `sqrt`, `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2`, `exp`, `ln`, `log10`, `log2`, `pow`, `floor`, `ceil`, `abs_float`. Pure XIOM fallbacks as `*_pure` variants. |
| **[num](stdlib/num.md)** | `use xiom.num;` | Numeric traits: `abs`, `signum`, `is_positive`, `is_negative`, `pow`, `sqrt`, `cbrt`, `gcd`, `lcm`, byte conversion, `saturating_add`, `wrapping_add`. |
| **[cmp](stdlib/cmp.md)** | `use xiom.cmp;` | Comparison traits: `Compare[T]`, `PartialOrd[T]`, `Ord[T]`, `Eq[T]`, `min`, `max`, `clamp`. |

---

## Concurrency

Async runtime, threads, and synchronization primitives.

| Module | Import | Description |
|--------|--------|-------------|
| **[async](stdlib/async.md)** | `use xiom.async;` | Async runtime: `spawn` for concurrent tasks. `Channel[T]` with `bounded`/`unbounded`, `send`, `recv`, `try_recv`, `close`. |
| **[thread](stdlib/thread.md)** | `use xiom.thread;` | Real OS threads via pthreads/Win32: `spawn`, `join`, `Thread` handle, `sleep`, `current`, `available_parallelism`, `yield_now`. |
| **[sync](stdlib/sync.md)** | `use xiom.sync;` | Real platform concurrency: `Mutex[T]` (pthreads/Win32 CS), `RwLock[T]`, `Condvar`, `Once`, `Arc[T]` (atomic ref count), `AtomicBool`, `AtomicInt` (real atomics via GCC __atomic / MSVC Interlocked), `Barrier`, `Semaphore`. |

---

## Networking

TCP, UDP, and HTTP.

| Module | Import | Description |
|--------|--------|-------------|
| **[net](stdlib/net.md)** | `use xiom.net;` | Real BSD/Winsock sockets: `tcp_connect`, `tcp_listen`, `TcpStream` (read, write, close), `TcpListener` (accept). HTTP: `http_get`, `http_post`. UDP: `udp_bind`, `UdpSocket`. DNS: `resolve_host`. Cross-platform `#ifdef _WIN32` / POSIX. |

---

## Memory & Pointers

Low-level memory management, allocation, and pointer operations.

| Module | Import | Description |
|--------|--------|-------------|
| **[mem](stdlib/mem.md)** | `use xiom.mem;` | Memory utilities: `size_of`, `align_of`, `swap`, `replace`, `zeroed`, `copy`, `drop`. |
| **[ptr](stdlib/ptr.md)** | `use xiom.ptr;` | Raw pointer ops (unsafe): `null`, `is_null`, `read`, `write`, `add`, `sub`, `offset`. |
| **[alloc](stdlib/alloc.md)** | `use xiom.alloc;` | Heap allocation: `alloc`, `alloc_zeroed`, `realloc`, `free`. |
| **[rc](stdlib/rc.md)** | `use xiom.rc;` | Reference counting: `Rc[T]` (single-threaded), `Arc[T]` (atomic). Clone to increment, automatic drop. |

---

## SIMD & Hardware Acceleration

Vectorized operations and hardware-accelerated crypto.

| Module | Import | Description |
|--------|--------|-------------|
| **[simd](stdlib/simd.md)** | `use xiom.simd;` | SIMD vector types: `Vec4f`, `Vec2d`, `Vec4i`, `Vec8f`, `Vec4d`, `Vec8i`, `Vec16f`, `Vec8d`. SSE/SSE2/AVX/AVX2/AVX-512 on x86_64, NEON on ARM64. Operations: add, sub, mul, div, sqrt, dot, min, max, normalize, cross3. ISA detection: `has_sse()`, `has_avx()`, `has_neon()`. Scalar fallbacks when SIMD unavailable. |

---

## System & Environment

Operating system interface, environment variables, and time.

| Module | Import | Description |
|--------|--------|-------------|
| **[os](stdlib/os.md)** | `use xiom.os;` | OS detection: `platform`, `arch`, `cpu_count`, `total_memory`, `process_id`. Process: `spawn`, `set_env`. |
| **[env](stdlib/env.md)** | `use xiom.env;` | Environment: `var`, `set_var`, `remove_var`, `vars`, `home_dir`, `temp_dir`, `current_dir`, `set_current_dir`. |
| **[time](stdlib/time.md)** | `use xiom.time;` | Time types: `Duration`, `Instant`, `SystemTime`, `DateTime`, `sleep`, `now`. |

---

## Utilities

Iterators, type conversion, interior mutability, formatting, and hashing.

| Module | Import | Description |
|--------|--------|-------------|
| **[iter](stdlib/iter.md)** | `use xiom.iter;` | `Range`, `RangeInclusive`. 7 adapters: `map`, `filter`, `enumerate`, `take`, `skip`, `chain`, `zip`. 12 collectors: `collect`, `fold`, `count`, `sum`, `product`, `max`, `min`, `find`, `all`, `any`, `nth`, `last`. |
| **[convert](stdlib/convert.md)** | `use xiom.convert;` | Type conversion: `From<T>`, `Into<T>`, `TryFrom<T>`, `TryInto<T>`, `AsRef<T>`, `AsMut<T>`. |
| **[cell](stdlib/cell.md)** | `use xiom.cell;` | Interior mutability: `Cell[T]` (copy-based), `RefCell[T]` (borrow-based). |
| **[fmt](stdlib/fmt.md)** | `use xiom.fmt;` | String formatting: `Display` trait, `format`, `format_args`. |
| **[hash](stdlib/hash.md)** | `use xiom.hash;` | Hashing: `Hash` trait, `Hasher`, `hash`. |

---

## Security

Cryptography, compression, random numbers, and regular expressions.

| Module | Import | Description |
|--------|--------|-------------|
| **[crypto](stdlib/crypto.md)** | `use xiom.crypto;` | Hashing: `sha256`, `sha512`, `sha256_hex`, `md5`, `blake3`, `hmac_sha256`. AES: `aes_encrypt`, `aes_decrypt` with hardware acceleration (AES-NI on x86_64, ARM crypto extensions). RSA: `generate_rsa_keypair`, `rsa_encrypt`, `rsa_decrypt`. Key derivation: `pbkdf2`, `argon2`. Safety: `constant_time_compare`. |
| **[compress](stdlib/compress.md)** | `use xiom.compress;` | Compression: `gzip`, `gunzip`, `zlib`, `unzlib`, `deflate`, `inflate`. |
| **[rand](stdlib/rand.md)** | `use xiom.rand;` | Random numbers: `Rng` type, `random` [0,1), `random_range(min, max)`, `shuffle[T]`, `choose[T]`. |
| **[regex](stdlib/regex.md)** | `use xiom.regex;` | Regular expressions: `Regex` type, `compile`, `is_match`, `find`, `find_all`, `replace`, `split`. |

---

## Tooling

Testing, benchmarking, logging, contracts, serialization, and reflection.

| Module | Import | Description |
|--------|--------|-------------|
| **[test](stdlib/test.md)** | `use xiom.test;` | Contract-aware test framework. 10 assertions: `assert`, `assert_eq`, `assert_ne`, `assert_lt`, `assert_gt`, `assert_contains`, `assert_ok`, `assert_err`, `assert_some`, `assert_none`, `assert_contract`. Runners: `run`, `run_all`, `run_filtered`. `TestResult` and `ContractFailure` types. |
| **[bench](stdlib/bench.md)** | `use xiom.bench;` | Benchmarking: `bench`, `run_benches`, `black_box` to prevent optimization. |
| **[log](stdlib/log.md)** | `use xiom.log;` | Structured logging: `debug`, `info`, `warn`, `error`, `set_level`. |
| **[contracts](stdlib/contracts.md)** | `use xiom.contracts;` | Contract verification helpers: `verify_requires`, `verify_ensures`, `verify_invariant`. |
| **[serialize](stdlib/serialize.md)** | `use xiom.serialize;` | Serialization: `Serialize`/`Deserialize` interfaces with contract-preserving invariant checks on deserialization. JSON, bytes, format detection. `SerializeError` with path/line/col. |
| **[reflect](stdlib/reflect.md)** | `use xiom.reflect;` | Comptime introspection: `type_name[T]`, `type_size[T]`, `field_names[T]`, `variant_names[T]`. |

---

## Interop

C foreign function interface.

| Module | Import | Description |
|--------|--------|-------------|
| **[ffi](stdlib/ffi.md)** | `use xiom.ffi;` | Zero-cost C FFI: `extern "C"` blocks, `*T` raw pointers, `unsafe` blocks, `CStr`, `CString`. Standard C bindings in `stdlib/libc.xiom-bind` (malloc, free, strlen, printf, sqrt, pow). |

---

## Quick Reference

```xiom
// Types -- built-in, no import
Option[T]   Result[T, E]   Vec[T]   Map[K,V]   Set[T]
Int         Float64        Bool     Str        Char

// Most commonly imported
use xiom.io;           // io.println("Hello")
use xiom.math;         // math.sqrt(2.0)
use xiom.string;       // string.str_split("a,b", ",")
use xiom.collections;  // Vec.new[Int]()
use xiom.sync;         // sync.Mutex.new(data)
use xiom.net;          // net.http_get("https://...")
use xiom.test;         // test.assert_eq(a, b, "name")
use xiom.crypto;       // crypto.sha256(&data)
```

## Status

**Beta.** The standard library ships with the toolchain and is actively being completed. Contract coverage and test counts vary by module; the [known limitations](https://github.com/xiom-lang/stdlib/blob/main/docs/STDLIB_BETA_LIMITATIONS.md) list the current gaps.
