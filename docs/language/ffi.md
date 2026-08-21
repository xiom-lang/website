# C FFI (Foreign Function Interface)

XIOM has zero-cost C interoperability. C functions and types are declared in `extern` blocks. The compiler generates no wrapper code. C ABI calling conventions are used directly.

`unsafe` is required because the compiler cannot verify C memory safety.

## Extern Blocks

```xiom
extern "C" {
  fn malloc(size: UInt) -> *UInt8
  fn free(ptr: *UInt8)
  fn strlen(s: *UInt8) -> UInt
  fn printf(format: *UInt8, ...) -> Int32
}
```

## Calling C Functions

```xiom
fn c_string_length(ptr: *UInt8) -> UInt {
  unsafe { return strlen(ptr); }
}

fn allocate_buffer(size: UInt) -> *UInt8 {
  unsafe { return malloc(size); }
}
```

## Raw Pointers

Raw pointers (`*T`) are only usable inside `unsafe` blocks. They cannot be dereferenced in safe code.

```xiom
unsafe {
  let raw: *Int = some_c_function();
  let value = *raw;   // dereference -- programmer guarantees validity
  *raw = 42;          // write through pointer
}
```

## Safe Wrappers

The recommended pattern is to wrap C libraries with safe XIOM interfaces that add contracts:

```xiom
fn safe_alloc(size: UInt) -> Option[*UInt8]
  requires: size > 0
{
  unsafe {
    let ptr = malloc(size);
    if ptr == null_ptr() {
      return None;
    }
    return Some(ptr);
  }
}

fn safe_free(ptr: *UInt8) {
  unsafe { free(ptr) }
}
```

## Type Mapping

| C Type | XIOM Type |
|--------|-----------|
| `int` | `Int32` |
| `unsigned int` | `UInt32` |
| `long` | `Int64` |
| `size_t` | `UInt` |
| `char` | `Int8` |
| `char*` | `*UInt8` |
| `void*` | `*UInt8` |
| `float` | `Float32` |
| `double` | `Float64` |

## C-ABI Export

XIOM functions can be exported with C ABI for consumption from other languages:

```xiom
extern "C" fn xiom_add(a: Int32, b: Int32) -> Int32 {
  return a + b;
}
```

This compiles to a standard C-callable symbol that can be linked from Rust, Python, or any language with C FFI.

## Strategy

XIOM does not rewrite C libraries. It wraps them with safe interfaces and contract-verified preconditions:

| Library | C LOC | XIOM Wrapper LOC |
|---------|-------|-------------------|
| SQLite | 150,000 | ~200 |
| OpenSSL | 500,000 | ~300 |
| BLAS | 100,000+ | ~150 |

The C library provides battle-tested implementation. The XIOM wrapper adds contracts and type safety.

## FFI Best Practices

1. **Always use `unsafe` blocks** -- never call C functions outside `unsafe { }`.
2. **Wrap with safe functions** -- expose a safe XIOM interface with contracts.
3. **Validate at the boundary** -- check pointer validity, buffer sizes, and nullability.
4. **Auto-infer contracts from C headers** -- planned Phase 3 feature for mechanical binding generation.
