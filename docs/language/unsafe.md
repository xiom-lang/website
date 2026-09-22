<!--
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Unsafe

> **Quick look:** `unsafe { ... }` is a confined transaction. Raw pointers, extern calls and inline assembly live inside it; everything that could escape is checked at the block boundary.

XIOM is memory-safe by default. `unsafe` exists for the three things a compiler cannot verify on its own: raw pointer operations, calls into C, and inline assembly. Writing `unsafe` does not switch safety off -- it marks a region where the compiler applies a confinement model instead of ordinary rules.

## The Block Rule

`unsafe` applies strictly to a block expression. It cannot prefix a declaration:

```xiom
fn abi_like() -> Int
  requires: true
{
  unsafe {
    asm("nop");
    return 0;
  }
}
```

`unsafe fn`, `unsafe module`, `unsafe struct` and `unsafe impl` are hard errors, not warnings. The compiler reports: "`unsafe` applies only to block expressions `unsafe { ... }`; it cannot prefix declarations".

Inline assembly is only available inside an `unsafe` block. A function whose entire body is a single `unsafe` block must declare a `requires:` clause (the pre-entry contract), because callers need to know what they are buying into:

```xiom
fn read_value() -> Int
  requires: true
{
  unsafe {
    let raw: *Int = get_ptr();
    return *raw;
  }
}
```

## The Confinement Model

Every `unsafe` block runs as a transaction. The requirements below are enforced by the compiler or by the runtime fault path:

| Rule | What it enforces |
|------|------------------|
| Lexical | `unsafe` is a block expression only. Whole-body unsafe functions declare `requires:`. |
| Extern gate | Calling an `extern "C"` function from safe code is an error. Functions that declare contracts are sanctioned wrappers; otherwise call inside `unsafe`. |
| Signature gate | A safe function cannot cast or return a raw pointer outside `unsafe`. The integer-to-pointer cast is itself gated. |
| Pre-entry contracts | A function whose entire body is one `unsafe` block must declare `requires:`. |
| Heap isolation | Allocations inside the block route to a per-thread guard arena, discarded wholesale at block exit. |
| Stack guard | A per-thread guard page is armed at block entry; a stack overflow faults in the red zone instead of writing into adjacent memory. |
| Fault trap | A hardware fault inside the block is caught by the platform trampoline (SEH on Windows, sigsetjmp elsewhere); the process survives. |
| Transient retry | A transient fault is retried once on a fresh memory slot. `#[unsafe_no_retry]` disables this for deterministic behavior. |
| Zero escape | A raw pointer, `&T` / `&mut T`, function type, or struct containing them cannot be the block's tail value. String tails are copied out to the main heap before the arena resets. |
| FFI ownership | An extern call returning `*T` must be converted to an owned XIOM type before the block tail (`ffi.safe_ptr_from_raw`, `box_from_ptr`, `vec_from_ptr_with_free`, `str_from_ptr_owned`). |

## Attributes

```xiom
#[unsafe_no_retry]   // disable the once-only transient retry (deterministic faults)
#[unsafe_direct]     // trusted escape hatch: plain unsafe, no trampoline, arena or
                     // guard page. Stdlib/selfhost only; user code requires
                     // --enable-unsafe-direct and every use is warned and audited.
```

## Fault Handling

A fault inside a confined block does not abort the process. The block yields a recoverable zero for the enclosing function's return type, and the fault is classified:

| Code | Cause |
|------|-------|
| 1 | Access violation (SIGSEGV) |
| 2 | Illegal instruction (SIGILL) |
| 3 | Floating-point error (SIGFPE) |
| 4 | Stack overflow |
| 5 | Guard page hit |
| 6 | Other |

Runtime types for callers that want the details:

```xiom
pub type HardwareFault     = { signal: Str; pc: UInt64; retried: Bool; }
pub type ContractViolation = { contract: Str; }
```

## A Safe Wrapper for C

The pattern the compiler expects: a function with a contract that owns the unsafe block, and converts any raw result into an owned XIOM value before returning.

```xiom
extern "C" {
  fn get_ptr() -> *Int;
}

fn read_value() -> Int
  requires: true
{
  unsafe {
    let raw: *Int = get_ptr();
    let value = *raw;
    return value;
  }
}
```

Callers see a normal safe function. The unsafe region is at the boundary, in one place, visible in review.

## Auditing Unsafe Code

The compiler can report what each `unsafe` block does:

```
xiom --sandbox file.xi              # text safety report
xiom --sandbox=strict file.xi       # fail the build on HIGH severity findings
xiom --sandbox-report=json file.xi  # machine-readable report
```

`#[unsafe_direct]` is the only escape from confinement, and using it is deliberately loud: the compiler prints a warning on every invocation so release logs cannot silently contain unguarded code.

## What Unsafe Does Not Change

- Memory safety in safe code: ownership, borrowing and `Send`/`Sync` rules are unchanged.
- Contracts: they still run (unless stripped) inside and outside unsafe blocks.
- Review expectations: an unsafe block is the place to document the invariant the compiler cannot see.

## Runtime Assembly Is Not User Unsafe

The toolchain ships hand-written x86_64 assembly for some runtime hot paths
(crypto primitives, bulk memory operations, context switching). That code
belongs to the trusted runtime, not to the `unsafe` blocks described here: the
confinement model on this page does not apply to it, and the contract verifier
treats it as an implementation of a contract rather than something it proves.
The [contracts guide](contracts.md) states the boundary in full.

## See Also

- [Memory Model](memory-model.md) -- ownership, borrowing, and where unsafe fits
- [C FFI](ffi.md) -- extern declarations and wrapper patterns
- [Compiler](compiler.md) -- flags, targets, and the confinement model summary
