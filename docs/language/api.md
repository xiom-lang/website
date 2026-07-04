# XIOM Standard Library API

> **39 modules.** Types (`Option`, `Result`, `Vec`, `Int`, `Str`...) are built-in — no import needed.
> Functions live in modules — import with `use xiom.<module>`.
> Every module documented with signatures and descriptions.

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
| **[math](stdlib/math.md)** | `use xiom.math;` | Constants: `PI`, `E`, `TAU`. Basic: `sqrt`, `pow`, `abs_int`, `abs_float`, `min_int`, `max_int`, `min_float`, `max_float`, `floor`, `ceil`, `round`. Trig: `sin`, `cos`, `tan`, `asin`, `acos`, `atan`. Exponential: `exp`, `log`, `log2`, `log10`. Interpolation: `clamp`, `lerp`. Random: `random`, `random_int`. |
| **[num](stdlib/num.md)** | `use xiom.num;` | Numeric traits: `abs`, `signum`, `is_positive`, `is_negative`, `pow`, `sqrt`, `cbrt`, `gcd`, `lcm`, byte conversion, `saturating_add`, `wrapping_add`. |
| **[cmp](stdlib/cmp.md)** | `use xiom.cmp;` | Comparison traits: `Compare[T]`, `PartialOrd[T]`, `Ord[T]`, `Eq[T]`, `min`, `max`, `clamp`. |

---

## Concurrency

Async runtime, threads, and synchronization primitives.

| Module | Import | Description |
|--------|--------|-------------|
| **[async](stdlib/async.md)** | `use xiom.async;` | Async runtime: `spawn` for concurrent tasks. `Channel[T]` with `bounded`/`unbounded`, `send`, `recv`, `try_recv`, `close`. |
| **[thread](stdlib/thread.md)** | `use xiom.thread;` | OS threads: `spawn`, `join`, `Thread` handle, `sleep`, `current`, `available_parallelism`. |
| **[sync](stdlib/sync.md)** | `use xiom.sync;` | `Mutex[T]` with `MutexGuard` (lock, try_lock), `RwLock[T]` with `ReadGuard`/`WriteGuard` (read, write, try_read, try_write), `Condvar` (wait, notify_one, notify_all), `Once`, `Arc[T]`, `AtomicBool`, `AtomicInt`, `Barrier`, `Semaphore`. |

---

## Networking

TCP, UDP, and HTTP.

| Module | Import | Description |
|--------|--------|-------------|
| **[net](stdlib/net.md)** | `use xiom.net;` | TCP: `tcp_connect`, `tcp_listen`, `TcpStream` (read, write, close), `TcpListener` (accept). HTTP: `http_get`, `http_post`, `HttpResponse` (status, body). UDP: `udp_bind`, `UdpSocket` (send_to, recv_from). `NetError` type. |

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
| **[crypto](stdlib/crypto.md)** | `use xiom.crypto;` | Hashing: `sha256`, `sha512`, `sha256_hex`, `md5`, `blake3`, `hmac_sha256`. AES: `aes_encrypt`, `aes_decrypt`, `aes_encrypt_gcm`, `aes_decrypt_gcm`. RSA: `generate_rsa_keypair`, `rsa_encrypt`, `rsa_decrypt`, `rsa_sign`, `rsa_verify`. Key derivation: `pbkdf2`, `argon2`. Random: `secure_random_bytes`. Safety: `constant_time_compare`. |
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
// Types — built-in, no import
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
