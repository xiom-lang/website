<!--
Copyright (c) 2026 XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Standard Library

> 40 modules. All ship with the compiler in `stdlib/xiom/`.
> Types (Option, Result, Vec, Int, Str...) are built-in -- no import needed.
> Functions live in modules -- import with `use xiom.<module>`.

## Foundation

| Module | Description |
|--------|-------------|
| [core](core.md) | Option, Result, Box, BinaryHeap, interfaces (Clone, Eq, Ord, Display, Hash, Add, Sub, Mul, Div, Iterator, Default, Drop), conversions, contract methods, numeric limits |
| [error](error.md) | Error interface, From/Into error conversion, IOError, NetError, ParseError |
| [char](char.md) | Unicode character operations: is_digit, is_alpha, is_whitespace, to_upper, to_lower |

## I/O & Filesystem

| Module | Description |
|--------|-------------|
| [io](io.md) | Console I/O (print, println, read_line), file operations (read, write, append, copy, remove), directories (create, list), process (exit, args, env_var), timing (time_now, sleep) |
| [path](path.md) | File path manipulation: join, basename, dirname, extension, is_absolute, normalize, home_dir, current_dir, temp_dir |

## Data Structures

| Module | Description |
|--------|-------------|
| [collections](collections.md) | Vec, Map, Set, VecDeque, BTreeMap, BTreeSet, LinkedList, Queue, Stack |
| [array](array.md) | Fixed-size array operations: len, get, set, fill, slice |

## Text & Encoding

| Module | Description |
|--------|-------------|
| [string](string.md) | UTF-8 string operations: length, concat, slice, contains, split, trim, upper/lower, format, replace, index_of, char_at, parse int/float |
| [encoding](encoding.md) | Text encoding: UTF-8 encode/decode, Base64, Hex |

## Mathematics

| Module | Description |
|--------|-------------|
| [math](math.md) | Constants (PI, E, TAU), basic math (sqrt, pow, abs, min, max, floor, ceil, round), trigonometry (sin, cos, tan, asin, acos, atan), exponential/log (exp, log, log2, log10), interpolation (clamp, lerp), random numbers |
| [num](num.md) | Numeric traits: abs, signum, is_positive, is_negative, pow, sqrt, cbrt, gcd, lcm, byte conversion, saturating/wrapping operations |
| [cmp](cmp.md) | Comparison traits: Compare, PartialOrd, Ord, Eq, min, max, clamp |
| [simd](simd.md) | Hardware-accelerated SIMD vectors: Vec4f/Vec8f/Vec16f (Float32), Vec2d/Vec4d/Vec8d (Float64), Vec4i/Vec8i (Int32), Vec8s (Int16), Vec16b (Int8). SSE/AVX/AVX2/AVX-512/NEON with scalar fallback |

## Concurrency

| Module | Description |
|--------|-------------|
| [async](async.md) | Async runtime: spawn, Channel (bounded/unbounded, send, recv, try_recv, close) |
| [thread](thread.md) | OS thread management: spawn, join, Thread handle, sleep, current, available_parallelism |
| [sync](sync.md) | Synchronization primitives: Mutex with MutexGuard, RwLock with ReadGuard/WriteGuard, Condvar, Once, Arc, AtomicBool, AtomicInt, Barrier, Semaphore |

## Networking

| Module | Description |
|--------|-------------|
| [net](net.md) | TCP (connect, listen, read/write, close), UDP (bind, send_to, recv_from), HTTP (GET, POST with HttpResponse), NetError |

## Memory & Pointers

| Module | Description |
|--------|-------------|
| [mem](mem.md) | Memory management: size_of, align_of, swap, replace, zeroed, copy, drop |
| [ptr](ptr.md) | Pointer utilities: null, is_null, read, write, pointer arithmetic (add, sub, offset) |
| [alloc](alloc.md) | Memory allocation: alloc, alloc_zeroed, realloc, free |
| [rc](rc.md) | Reference counting: Rc (single-threaded), Arc (atomic) |

## System & Environment

| Module | Description |
|--------|-------------|
| [os](os.md) | Operating system interface: platform, arch, cpu_count, total_memory, process_id, spawn, set_env |
| [env](env.md) | Environment variables: var, set_var, remove_var, vars, home_dir, temp_dir, current_dir |
| [time](time.md) | Time types: Duration, Instant, SystemTime, DateTime, sleep, now |

## Utilities

| Module | Description |
|--------|-------------|
| [iter](iter.md) | Iterator combinators: Range, RangeInclusive, map, filter, enumerate, take, skip, chain, zip, collect, fold, count, sum, product, max, min, find, all, any, nth |
| [convert](convert.md) | Type conversion traits: From, Into, TryFrom, TryInto, AsRef, AsMut |
| [cell](cell.md) | Interior mutability: Cell (copy-based), RefCell (borrow-based) |
| [fmt](fmt.md) | String formatting: Display trait, format, format_args |
| [hash](hash.md) | Hashing infrastructure: Hash trait, Hasher, hash function |

## Security

| Module | Description |
|--------|-------------|
| [crypto](crypto.md) | Cryptography: SHA-256/512, MD5, BLAKE3, HMAC, AES encryption/decryption (GCM), RSA keypair/sign/verify, PBKDF2, Argon2, secure random bytes, constant-time comparison |
| [compress](compress.md) | Compression: gzip/gunzip, zlib/unzlib, deflate/inflate |
| [rand](rand.md) | Random number generation: Rng type, random, random_range, shuffle, choose |
| [regex](regex.md) | Regular expressions: compile, match, find, find_all, replace, split |

## Tooling

| Module | Description |
|--------|-------------|
| [test](test.md) | Contract-aware test framework: assert, assert_eq, assert_ne, assert_ok, assert_err, assert_some, assert_none, assert_contract, TestResult, run, run_all, run_filtered |
| [bench](bench.md) | Benchmarking: bench, run_benches, black_box |
| [log](log.md) | Structured logging: debug, info, warn, error, set_level |
| [contracts](contracts.md) | Contract helpers: verify_requires, verify_ensures, verify_invariant |
| [serialize](serialize.md) | Serialization: Serialize/Deserialize interfaces (JSON, bytes) with contract-preserving invariant checks on deserialization, SerializeError with format detection |
| [reflect](reflect.md) | Comptime type introspection: type_name, type_size, field_names, variant_names |

## Interop

| Module | Description |
|--------|-------------|
| [ffi](ffi.md) | Zero-cost C FFI: extern "C" blocks, *T raw pointers, unsafe blocks, CStr, CString, libc bindings (malloc, free, strlen, printf, sqrt, pow) |
