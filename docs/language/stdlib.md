# Standard Library Reference

> 39 modules. All ship with the compiler in `stdlib/axiom/`. Every module is imported via `use axiom.<module>`.

## Core Types & Operations

### `axiom.core`

Foundation types and utilities used by every AXIOM program.

| Type/Function | Signature | Description |
|---------------|-----------|-------------|
| `Option[T]` | `{ is_some: Bool; value: T; }` | Optional value. `Some(value)` or `None`. |
| `Result[T, E]` | `{ is_ok: Bool; value: T; error: E; }` | Success or typed error. `Ok(value)` or `Err(error)`. |
| `panic(msg)` | `fn panic(msg: Str)` | Immediate trap with error message. |
| `assert(condition, msg)` | `fn assert(condition: Bool, msg: Str)` | Runtime assertion. |
| `to_int(x)` | `fn to_int(x: Float64) -> Int` | Float → Int conversion. |
| `to_float(x)` | `fn to_float(x: Int) -> Float64` | Int → Float conversion. |
| `to_string(x)` | `fn to_string(x: Int) -> Str` | Int → Str conversion. |
| `is_sorted[T]` | `fn is_sorted[T: Ord](items: &Slice[T]) -> Bool` | Contract method. |
| `all[T]` | `fn all[T](items: &Slice[T], predicate: fn(T) -> Bool) -> Bool` | Contract method. |
| `none[T]` | `fn none[T](items: &Slice[T], predicate: fn(T) -> Bool) -> Bool` | Contract method. |
| `contains[T]` | `fn contains[T: Eq](items: &Slice[T], value: T) -> Bool` | Contract method. |

Also: `Copy`, `Default`, `Drop`, `Box`, `BinaryHeap`, `Iterator`, numeric limits (`MAX_INT`, `MIN_INT`, `MAX_FLOAT64`), and core interfaces (`Clone`, `Eq`, `Ord`, `Display`, `Hash`, `Add`, `Sub`, `Mul`, `Div`).

### `axiom.error`

Error handling types and helpers.

| Item | Description |
|------|-------------|
| `Error` interface | StdError trait |
| `From<T>` interface | Error conversion for `?` operator |
| `IOError` | I/O error type |
| `NetError` | Network error type |
| `ParseError` | Parsing error type |

### `axiom.char`

Unicode character operations.

| Function | Description |
|----------|-------------|
| `char_at(s, pos)` | Get character at position |
| `char_len(c)` | UTF-8 byte length of character |
| `is_digit(c)` | Check if digit |
| `is_alpha(c)` | Check if alphabetic |
| `is_whitespace(c)` | Check if whitespace |
| `to_upper(c)` | Convert to uppercase |
| `to_lower(c)` | Convert to lowercase |

---

## I/O & Filesystem

### `axiom.io`

Console I/O and file system operations.

| Function | Signature | Description |
|----------|-----------|-------------|
| `print(msg)` | `fn print(msg: Str)` | Print to stdout. |
| `println(msg)` | `fn println(msg: Str)` | Print with newline. |
| `read_line()` | `fn read_line() -> Str` | Read line from stdin. |
| `read_int()` | `fn read_int() -> Result[Int, Str]` | Read and parse integer. |
| `read_float()` | `fn read_float() -> Result[Float64, Str]` | Read and parse float. |
| `read_file(path)` | `fn read_file(path: Str) -> Result[Str, IOError]` | Read entire file. |
| `write_file(path, content)` | `fn write_file(path: Str, content: Str) -> Result[Unit, IOError]` | Write file. |
| `file_exists(path)` | `fn file_exists(path: Str) -> Bool` | Check file existence. |
| `create_dir(path)` | `fn create_dir(path: Str) -> Result[Unit, IOError]` | Create directory. |
| `list_dir(path)` | `fn list_dir(path: Str) -> Result[Vec[Str], IOError]` | List directory contents. |
| `remove_file(path)` | `fn remove_file(path: Str) -> Result[Unit, IOError]` | Delete file. |
| `copy_file(src, dst)` | `fn copy_file(src: Str, dst: Str) -> Result[Unit, IOError]` | Copy file. |
| `exit(code)` | `fn exit(code: Int)` | Exit process. |
| `args()` | `fn args() -> Vec[Str]` | Command-line arguments. |
| `env_var(name)` | `fn env_var(name: Str) -> Option[Str]` | Environment variable. |
| `time_now()` | `fn time_now() -> Int` | Current timestamp. |
| `sleep(ms)` | `fn sleep(ms: Int)` | Sleep milliseconds. |

### `axiom.path`

File path manipulation.

| Function | Description |
|----------|-------------|
| `join(a, b)` | Join path components |
| `basename(path)` | Extract filename |
| `dirname(path)` | Extract directory |
| `extension(path)` | Extract file extension |
| `is_absolute(path)` | Check if absolute path |
| `normalize(path)` | Normalize path separators |
| `home_dir()` | User home directory |
| `current_dir()` | Current working directory |
| `temp_dir()` | System temp directory |

---

## Collections

### `axiom.collections`

Data structures for storing and organizing values.

| Type | Description |
|------|-------------|
| `Vec[T]` | Heap-allocated growable array. `push`, `pop`, `get`, `len`, `clear`, `insert`, `remove`, `first`, `last`, `set`. |
| `Map[K, V]` | Hash map. `insert`, `get`, `remove`, `contains`, `len`, `keys`, `values`, `clear`. |
| `Set[T]` | Hash set. `insert`, `contains`, `remove`, `len`, `clear`, `union`, `intersection`, `difference`. |
| `VecDeque[T]` | Double-ended queue. `push_front`, `push_back`, `pop_front`, `pop_back`. |
| `BTreeMap[K, V]` | Ordered map. Same API as Map with key ordering. |
| `BTreeSet[T]` | Ordered set. Same API as Set with ordering. |
| `LinkedList[T]` | Doubly-linked list. |
| `Queue[T]` | FIFO queue. |
| `Stack[T]` | LIFO stack. |

### `axiom.array`

Fixed-size array operations.

| Function | Description |
|----------|-------------|
| `len(arr)` | Array length |
| `get(arr, index)` | Element at index |
| `set(arr, index, value)` | Set element at index |
| `fill(arr, value)` | Fill array with value |
| `slice(arr, start, end)` | Create array slice |

---

## String & Text

### `axiom.string`

UTF-8 string operations.

| Function | Signature | Description |
|----------|-----------|-------------|
| `str_len(s)` | `fn str_len(s: Str) -> Int` | String length. |
| `str_concat(a, b)` | `fn str_concat(a: Str, b: Str) -> Str` | Concatenate. |
| `str_slice(s, start, end)` | `fn str_slice(s: Str, start: Int, end: Int) -> Str` | Substring. |
| `str_contains(s, substr)` | `fn str_contains(s: Str, substr: Str) -> Bool` | Contains check. |
| `str_split(s, delimiter)` | `fn str_split(s: Str, delimiter: Str) -> Vec[Str]` | Split string. |
| `str_trim(s)` | `fn str_trim(s: Str) -> Str` | Trim whitespace. |
| `str_upper(s)` | `fn str_upper(s: Str) -> Str` | Uppercase. |
| `str_lower(s)` | `fn str_lower(s: Str) -> Str` | Lowercase. |
| `format(fmt, args...)` | `fn format(fmt: Str, args: ...) -> Str` | Format string. |
| `replace(s, from, to)` | `fn replace(s: Str, from: Str, to: Str) -> Str` | Replace substrings. |
| `index_of(s, substr)` | `fn index_of(s: Str, substr: Str) -> Option[Int]` | Find position. |
| `char_at(s, pos)` | `fn char_at(s: Str, pos: Int) -> Option[Char]` | Character at position. |
| `str_to_int(s)` | `fn str_to_int(s: Str) -> Result[Int, Str]` | Parse integer. |
| `str_to_float(s)` | `fn str_to_float(s: Str) -> Result[Float64, Str]` | Parse float. |

### `axiom.encoding`

Text encoding support.

| Item | Description |
|------|-------------|
| `utf8_encode(cp)` | Codepoint → UTF-8 bytes |
| `utf8_decode(bytes)` | UTF-8 bytes → codepoint |
| `base64_encode(data)` | Base64 encoding |
| `base64_decode(s)` | Base64 decoding |
| `hex_encode(data)` | Hex encoding |
| `hex_decode(s)` | Hex decoding |

---

## Math & Numbers

### `axiom.math`

Mathematical functions.

| Function | Description |
|----------|-------------|
| `abs(x)` | Absolute value |
| `sqrt(x)` | Square root |
| `sin(x)`, `cos(x)`, `tan(x)` | Trigonometry |
| `asin(x)`, `acos(x)`, `atan(x)` | Inverse trig |
| `pow(base, exp)` | Power |
| `exp(x)` | e^x |
| `log(x)`, `log2(x)`, `log10(x)` | Logarithms |
| `floor(x)`, `ceil(x)`, `round(x)` | Rounding |
| `min(a, b)`, `max(a, b)` | Min/max |
| `clamp(x, min, max)` | Clamp value |
| `lerp(a, b, t)` | Linear interpolation |
| `random()` | Random Float64 [0, 1) |
| `random_int(min, max)` | Random Int [min, max] |
| `PI`, `E`, `TAU` | Constants |

### `axiom.num`

Numeric traits and operations.

| Item | Description |
|------|-------------|
| `abs`, `signum` | Sign operations |
| `is_positive`, `is_negative` | Sign checks |
| `pow`, `sqrt`, `cbrt` | Power/root |
| `gcd`, `lcm` | Number theory |
| `to_be_bytes`, `to_le_bytes` | Byte conversion |
| `saturating_add`, `wrapping_add` | Overflow handling |

### `axiom.cmp`

Comparison and ordering traits.

| Item | Description |
|------|-------------|
| `Compare[T]` | 3-way comparison (-1, 0, 1) |
| `PartialOrd[T]` | Partial ordering |
| `Ord[T]` | Total ordering |
| `Eq[T]` | Equality |
| `min`, `max` | Extremum functions |
| `clamp` | Value clamping |

---

## Concurrency & Async

### `axiom.async`

Async runtime primitives.

| Type/Function | Description |
|---------------|-------------|
| `spawn(task)` | Launch async task |
| `Channel[T]` | Typed message channel |
| `Channel.bounded(n)` | Bounded channel (capacity n) |
| `Channel.unbounded()` | Unbounded channel |
| `.send(value)` | Send on channel |
| `.recv()` | Blocking receive |
| `.try_recv()` | Non-blocking receive |
| `.close()` | Close channel |

### `axiom.thread`

Thread management.

| Item | Description |
|------|-------------|
| `spawn(fn)` | Spawn OS thread |
| `join(handle)` | Wait for thread |
| `Thread` type | Thread handle |
| `sleep(duration)` | Thread sleep |
| `current()` | Current thread ID |
| `available_parallelism()` | CPU core count |

### `axiom.sync`

Synchronization primitives.

| Type | Description |
|------|-------------|
| `Mutex[T]` | Mutual exclusion lock |
| `RwLock[T]` | Read-write lock |
| `Condvar` | Condition variable |
| `Once` | One-time initialization |
| `Arc[T]` | Atomic reference counting |
| `AtomicBool` | Atomic boolean |
| `AtomicInt` | Atomic integer |
| `Barrier` | Thread barrier |
| `Semaphore` | Counting semaphore |

---

## Networking

### `axiom.net`

TCP, UDP, and HTTP networking.

| Type/Function | Description |
|---------------|-------------|
| `tcp_connect(host, port)` | TCP client connection |
| `tcp_listen(host, port)` | TCP server listener |
| `TcpStream` | TCP stream (read/write/close) |
| `TcpListener` | TCP listener (accept connections) |
| `http_get(url)` | HTTP GET request |
| `http_post(url, body)` | HTTP POST request |
| `HttpResponse` | HTTP response (status + body) |
| `udp_bind(host, port)` | UDP socket |
| `UdpSocket` | UDP socket (send_to/recv_from) |
| `NetError` | Network error type |

---

## Memory & Pointers

### `axiom.mem`

Memory management.

| Function | Description |
|----------|-------------|
| `size_of[T]()` | Size of type in bytes |
| `align_of[T]()` | Alignment of type |
| `swap(a, b)` | Swap two values |
| `replace(dst, src)` | Move and replace |
| `zeroed[T]()` | Zero-initialized value |
| `copy(src, dst, count)` | Copy memory |
| `drop(value)` | Explicit drop |

### `axiom.ptr`

Pointer utilities.

| Function | Description |
|----------|-------------|
| `null[T]()` | Null pointer |
| `is_null(ptr)` | Null check |
| `read(ptr)` | Read from pointer (unsafe) |
| `write(ptr, value)` | Write to pointer (unsafe) |
| `add(ptr, offset)` | Pointer arithmetic |
| `sub(ptr, offset)` | Pointer arithmetic |
| `offset(ptr, count)` | Byte offset |

### `axiom.alloc`

Memory allocation.

| Function | Description |
|----------|-------------|
| `alloc(size)` | Allocate memory |
| `alloc_zeroed(size)` | Zero-initialized allocation |
| `realloc(ptr, size)` | Resize allocation |
| `free(ptr)` | Free memory |

### `axiom.rc`

Reference counting.

| Type | Description |
|------|-------------|
| `Rc[T]` | Single-threaded reference count |
| `Arc[T]` | Atomic reference count |
| `.clone()` | Increment reference |
| `.strong_count()` | Reference count |

---

## System & Environment

### `axiom.os`

Operating system interface.

| Function | Description |
|----------|-------------|
| `platform()` | OS name ("windows", "linux", "macos") |
| `arch()` | CPU architecture ("x86_64", "aarch64") |
| `cpu_count()` | Logical CPU count |
| `total_memory()` | Total system memory |
| `process_id()` | Current process ID |
| `spawn(cmd, args)` | Spawn child process |
| `set_env(key, value)` | Set env variable |

### `axiom.env`

Environment variables and configuration.

| Item | Description |
|------|-------------|
| `var(name)` | Get env variable |
| `set_var(name, value)` | Set env variable |
| `remove_var(name)` | Remove env variable |
| `vars()` | All env variables |
| `home_dir()` | Home directory |
| `temp_dir()` | Temp directory |
| `current_dir()` | CWD |
| `set_current_dir(path)` | Change CWD |

### `axiom.time`

Time and date.

| Type/Function | Description |
|---------------|-------------|
| `Duration` | Time duration type |
| `Instant` | Monotonic timestamp |
| `SystemTime` | System clock time |
| `DateTime` | Calendar date/time |
| `sleep(duration)` | Thread sleep |
| `now()` | Current instant |

---

## Patterns & Utilities

### `axiom.iter`

Iterator combinators.

| Item | Description |
|------|-------------|
| `Range` | Integer range `0..10` |
| `RangeInclusive` | Inclusive range `0..=10` |
| `.map(fn)` | Transform elements |
| `.filter(fn)` | Filter elements |
| `.take(n)` | Take first n |
| `.skip(n)` | Skip first n |
| `.chain(other)` | Concatenate iterators |
| `.zip(other)` | Pair elements |
| `.enumerate()` | Index + element |
| `.fold(init, fn)` | Reduce |
| `.sum()` | Sum elements |
| `.product()` | Multiply elements |
| `.max()`, `.min()` | Extremum |
| `.find(fn)` | Find first match |
| `.all(fn)`, `.any(fn)` | Predicate tests |

### `axiom.convert`

Type conversion traits.

| Trait | Description |
|-------|-------------|
| `From<T>` | Conversion from T |
| `Into<T>` | Conversion into T |
| `TryFrom<T>` | Fallible conversion from T |
| `TryInto<T>` | Fallible conversion into T |
| `AsRef<T>` | Reference conversion |
| `AsMut<T>` | Mutable reference conversion |

### `axiom.cell`

Interior mutability.

| Type | Description |
|------|-------------|
| `Cell[T]` | Copy-based interior mutability |
| `RefCell[T]` | Borrow-based interior mutability |

### `axiom.fmt`

String formatting infrastructure.

| Trait | Description |
|-------|-------------|
| `Display` | User-facing format |
| `format(fmt, args)` | Format string |
| `format_args(...)` | Format arguments |

### `axiom.hash`

Hashing infrastructure.

| Trait | Description |
|-------|-------------|
| `Hash` | Hashable type |
| `Hasher` | Hash state |
| `hash(value)` | Compute hash |

---

## Security & Compression

### `axiom.crypto`

Cryptographic primitives.

| Item | Description |
|------|-------------|
| `sha256(data)` | SHA-256 hash |
| `sha512(data)` | SHA-512 hash |
| `md5(data)` | MD5 hash (legacy) |
| `hmac(key, data)` | HMAC |
| `random_bytes(n)` | Cryptographic random bytes |
| `encrypt_aes(key, data)` | AES encryption |
| `decrypt_aes(key, data)` | AES decryption |
| `base64_encode(data)` | Base64 encode |
| `base64_decode(s)` | Base64 decode |

### `axiom.compress`

Compression algorithms.

| Item | Description |
|------|-------------|
| `gzip(data)` | Gzip compress |
| `gunzip(data)` | Gzip decompress |
| `zlib(data)` | Zlib compress |
| `unzlib(data)` | Zlib decompress |
| `deflate(data)` | Deflate compress |
| `inflate(data)` | Inflate decompress |

### `axiom.rand`

Random number generation.

| Item | Description |
|------|-------------|
| `Rng` | Random number generator type |
| `random()` | Uniform float [0, 1) |
| `random_range(min, max)` | Uniform integer |
| `shuffle[T](vec)` | Shuffle Vec in place |
| `choose[T](vec)` | Random element |

### `axiom.regex`

Regular expressions.

| Item | Description |
|------|-------------|
| `Regex` | Compiled regex type |
| `compile(pattern)` | Compile regex |
| `is_match(text)` | Match test |
| `find(text)` | Find first match |
| `find_all(text)` | Find all matches |
| `replace(text, replacement)` | Replace matches |
| `split(text)` | Split by regex |

---

## Testing & Tooling

### `axiom.test`

Contract-aware test runner.

| Item | Description |
|------|-------------|
| `test(name, fn)` | Register test |
| `assert_eq(a, b)` | Equality assertion |
| `assert_ne(a, b)` | Inequality assertion |
| `assert_true(cond)` | Truth assertion |
| `assert_false(cond)` | Falsity assertion |
| `assert_ok(result)` | Assert Result is Ok |
| `assert_err(result)` | Assert Result is Err |
| `assert_some(option)` | Assert Option is Some |
| `assert_none(option)` | Assert Option is None |
| `run_tests()` | Execute all registered tests |
| `run_test(name)` | Execute single test |

### `axiom.bench`

Benchmarking.

| Item | Description |
|------|-------------|
| `bench(name, fn)` | Register benchmark |
| `run_benches()` | Execute benchmarks |
| `black_box(value)` | Prevent optimization |

### `axiom.log`

Structured logging.

| Function | Description |
|----------|-------------|
| `debug(msg, data)` | Debug-level log |
| `info(msg, data)` | Info-level log |
| `warn(msg, data)` | Warning-level log |
| `error(msg, data)` | Error-level log |
| `set_level(level)` | Set minimum log level |

### `axiom.contracts`

Contract helpers for runtime verification.

| Item | Description |
|------|-------------|
| `verify_requires(cond, msg)` | Check precondition |
| `verify_ensures(cond, msg)` | Check postcondition |
| `verify_invariant(cond, msg)` | Check invariant |

### `axiom.serialize`

Serialization framework.

| Trait | Description |
|-------|-------------|
| `Serialize` | Serialize to bytes |
| `Deserialize` | Deserialize from bytes |
| `json_encode(value)` | Encode to JSON string |
| `json_decode[T](s)` | Decode from JSON string |

### `axiom.reflect`

Comptime type introspection.

| Item | Description |
|------|-------------|
| `type_name[T]()` | Get type name as string |
| `type_size[T]()` | Get type size in bytes |
| `field_names[T]()` | Get struct field names |
| `variant_names[T]()` | Get enum variant names |

---

## C FFI

### `axiom.ffi`

Zero-cost C interoperability.

| Item | Description |
|------|-------------|
| `extern "C"` block | Declare C functions |
| `*T` | Raw pointer type |
| `unsafe { }` block | Unsafe code scope |
| `CStr` | Null-terminated C string |
| `CString` | Owned C string |

See [`libc.axiom-bind`](../stdlib/libc.axiom-bind) for standard C library bindings (malloc, free, strlen, printf, sqrt, pow).

---

## Module Quick Index

| Module | Category | Key Types |
|--------|----------|-----------|
| `core` | Foundation | Option, Result, panic, assert |
| `error` | Foundation | Error, From, IOError |
| `char` | Foundation | Unicode ops |
| `io` | I/O | print, read_file, write_file |
| `path` | I/O | Path manipulation |
| `collections` | Data | Vec, Map, Set, VecDeque, BTree |
| `array` | Data | Fixed-size array ops |
| `string` | Text | str_len, split, format, replace |
| `encoding` | Text | UTF-8, Base64, Hex |
| `math` | Numeric | sqrt, sin, cos, rand, PI |
| `num` | Numeric | Traits, bit ops, overflow |
| `cmp` | Numeric | Ord, Eq, min, max |
| `async` | Concurrency | spawn, Channel |
| `thread` | Concurrency | OS threads |
| `sync` | Concurrency | Mutex, RwLock, Arc, Barrier |
| `net` | Network | TCP, UDP, HTTP |
| `mem` | Memory | size_of, swap, copy |
| `ptr` | Memory | Pointer ops (unsafe) |
| `alloc` | Memory | alloc, free |
| `rc` | Memory | Rc, Arc |
| `os` | System | platform, spawn, env |
| `env` | System | Environment variables |
| `time` | System | Duration, Instant, DateTime |
| `iter` | Util | Range, map, filter, fold |
| `convert` | Util | From, Into, TryFrom |
| `cell` | Util | Cell, RefCell |
| `fmt` | Util | Display, format |
| `hash` | Util | Hash, Hasher |
| `crypto` | Security | SHA-256, AES, HMAC |
| `compress` | Security | gzip, zlib |
| `rand` | Security | RNG, shuffle |
| `regex` | Security | Pattern matching |
| `test` | Tooling | Test runner, assertions |
| `bench` | Tooling | Benchmarking |
| `log` | Tooling | Structured logging |
| `contracts` | Tooling | Contract verification |
| `serialize` | Tooling | JSON, binary |
| `reflect` | Tooling | Type introspection |
| `ffi` | Interop | C FFI, unsafe, raw pointers |
