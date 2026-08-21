# SIMD Module

Hardware-accelerated SIMD (Single Instruction Multiple Data) vector types and operations. Provides 128-bit, 256-bit, and 512-bit vector types with arithmetic, geometric, and conversion operations. Falls back to scalar implementations when SIMD ISA extensions are unavailable.

```
use xiom.simd;
```

| Property | Value |
|----------|-------|
| C Runtime | `stdlib/runtime/simd_runtime.c` (402 lines) |
| x86_64 | SSE / SSE2 / AVX / AVX2 / AVX-512 |
| ARM64 | NEON |
| Fallback | Portable scalar C |

---

## ISA Detection

### `simd_supported()`
Returns `true` if at least one SIMD ISA extension is available.

```
fn simd_supported() -> Bool;
```

### `has_sse()`
Returns `true` if SSE (128-bit float) is available on x86_64.

```
fn has_sse() -> Bool;
```

### `has_avx()`
Returns `true` if AVX (256-bit float) is available on x86_64.

```
fn has_avx() -> Bool;
```

### `has_avx2()`
Returns `true` if AVX2 (256-bit integer) is available on x86_64.

```
fn has_avx2() -> Bool;
```

### `has_avx512()`
Returns `true` if AVX-512F (512-bit) is available on x86_64.

```
fn has_avx512() -> Bool;
```

### `has_neon()`
Returns `true` if NEON (128-bit) is available on ARM64.

```
fn has_neon() -> Bool;
```

---

## 128-bit Vector Types (SSE / NEON)

### Vec4f -- 4 x Float32

#### Constructors

##### `Vec4f.new(x, y, z, w)`
Creates a new `Vec4f` from four scalar values.

```
fn Vec4f.new(x: Float32, y: Float32, z: Float32, w: Float32) -> Vec4f;
```

##### `Vec4f.splat(value)`
Creates a new `Vec4f` with all lanes set to the given scalar value.

```
fn Vec4f.splat(value: Float32) -> Vec4f;
```

##### `Vec4f.zero()`
Creates a new `Vec4f` with all lanes set to 0.0.

```
fn Vec4f.zero() -> Vec4f;
```

#### Operations

##### `Vec4f.add(self, other)`
Element-wise addition. SIMD-accelerated when available.

```
fn Vec4f.add(self, other: Vec4f) -> Vec4f;
```

##### `Vec4f.sub(self, other)`
Element-wise subtraction. SIMD-accelerated when available.

```
fn Vec4f.sub(self, other: Vec4f) -> Vec4f;
```

##### `Vec4f.mul(self, other)`
Element-wise multiplication. SIMD-accelerated when available.

```
fn Vec4f.mul(self, other: Vec4f) -> Vec4f;
```

##### `Vec4f.div(self, other)`
Element-wise division. SIMD-accelerated when available.

```
fn Vec4f.div(self, other: Vec4f) -> Vec4f;
```

##### `Vec4f.sqrt(self)`
Element-wise square root. SIMD-accelerated when available.

```
fn Vec4f.sqrt(self) -> Vec4f;
```

##### `Vec4f.dot(self, other)`
Computes the dot product of `self` and `other` across all 4 lanes. SIMD-accelerated when available.

```
fn Vec4f.dot(self, other: Vec4f) -> Float32;
```

##### `Vec4f.min(self, other)`
Element-wise minimum. SIMD-accelerated when available.

```
fn Vec4f.min(self, other: Vec4f) -> Float32;
```

##### `Vec4f.max(self, other)`
Element-wise maximum. SIMD-accelerated when available.

```
fn Vec4f.max(self, other: Vec4f) -> Float32;
```

##### `Vec4f.get(self, index)`
Extracts the value at lane `index` (0-3).

```
fn Vec4f.get(self, index: Int) -> Float32;
```

##### `Vec4f.set(self, index, value)`
Sets the value at lane `index` (0-3) to `value`. Returns a new `Vec4f`.

```
fn Vec4f.set(self, index: Int, value: Float32) -> Vec4f;
```

##### `Vec4f.len(self)`
Returns the vector magnitude (Euclidean norm).

```
fn Vec4f.len(self) -> Float32;
```

##### `Vec4f.normalize(self)`
Returns the unit vector in the same direction.

```
fn Vec4f.normalize(self) -> Vec4f;
```

##### `Vec4f.cross3(self, other)`
Computes the 3D cross product using lanes x, y, z (w is set to 0).

```
fn Vec4f.cross3(self, other: Vec4f) -> Vec4f;
```

##### `Vec4f.add_scalar(self, value)`
Scalar fallback: adds a scalar to each lane. No SIMD acceleration.

```
fn Vec4f.add_scalar(self, value: Float32) -> Vec4f;
```

##### `Vec4f.mul_scalar(self, value)`
Scalar fallback: multiplies each lane by a scalar. No SIMD acceleration.

```
fn Vec4f.mul_scalar(self, value: Float32) -> Vec4f;
```

#### Usage Example

```
use xiom.simd;
use xiom.io;

fn main() {
  if !simd_supported() {
    io.println("SIMD not available -- using scalar fallback");
  }

  let a = Vec4f.new(1.0, 2.0, 3.0, 4.0);
  let b = Vec4f.new(5.0, 6.0, 7.0, 8.0);

  let sum = a.add(b);        // [6.0, 8.0, 10.0, 12.0]
  let product = a.mul(b);    // [5.0, 12.0, 21.0, 32.0]
  let dp = a.dot(b);         // 70.0 (1*5 + 2*6 + 3*7 + 4*8)
  let mag = a.len();         // sqrt(1+4+9+16) ~= 5.477
}
```

---

### Vec2d -- 2 x Float64

128-bit double-precision vector.

#### Constructor

##### `Vec2d.new(x, y)`
Creates a new `Vec2d` from two scalar values.

```
fn Vec2d.new(x: Float64, y: Float64) -> Vec2d;
```

#### Operations

##### `Vec2d.add(self, other)`
Element-wise addition. SIMD-accelerated when available.

```
fn Vec2d.add(self, other: Vec2d) -> Vec2d;
```

##### `Vec2d.sub(self, other)`
Element-wise subtraction. SIMD-accelerated when available.

```
fn Vec2d.sub(self, other: Vec2d) -> Vec2d;
```

##### `Vec2d.mul(self, other)`
Element-wise multiplication. SIMD-accelerated when available.

```
fn Vec2d.mul(self, other: Vec2d) -> Vec2d;
```

##### `Vec2d.div(self, other)`
Element-wise division. SIMD-accelerated when available.

```
fn Vec2d.div(self, other: Vec2d) -> Vec2d;
```

##### `Vec2d.sqrt(self)`
Element-wise square root. SIMD-accelerated when available.

```
fn Vec2d.sqrt(self) -> Vec2d;
```

##### `Vec2d.dot(self, other)`
Computes the dot product of `self` and `other` across both lanes.

```
fn Vec2d.dot(self, other: Vec2d) -> Float64;
```

##### `Vec2d.get(self, index)`
Extracts the value at lane `index` (0-1).

```
fn Vec2d.get(self, index: Int) -> Float64;
```

##### `Vec2d.set(self, index, value)`
Sets the value at lane `index` (0-1) to `value`. Returns a new `Vec2d`.

```
fn Vec2d.set(self, index: Int, value: Float64) -> Vec2d;
```

---

### Vec4i -- 4 x Int32

128-bit integer vector.

#### Constructor

##### `Vec4i.new(v0, v1, v2, v3)`
Creates a new `Vec4i` from four integer values.

```
fn Vec4i.new(v0: Int, v1: Int, v2: Int, v3: Int) -> Vec4i;
```

#### Operations

##### `Vec4i.add(self, other)`
Element-wise addition.

```
fn Vec4i.add(self, other: Vec4i) -> Vec4i;
```

##### `Vec4i.sub(self, other)`
Element-wise subtraction.

```
fn Vec4i.sub(self, other: Vec4i) -> Vec4i;
```

##### `Vec4i.mul(self, other)`
Element-wise multiplication.

```
fn Vec4i.mul(self, other: Vec4i) -> Vec4i;
```

##### `Vec4i.get(self, index)`
Extracts the value at lane `index` (0-3).

```
fn Vec4i.get(self, index: Int) -> Int;
```

##### `Vec4i.set(self, index, value)`
Sets the value at lane `index` (0-3) to `value`. Returns a new `Vec4i`.

```
fn Vec4i.set(self, index: Int, value: Int) -> Vec4i;
```

---

### Vec8s -- 8 x Int16

128-bit short integer vector.

#### Constructor

##### `Vec8s.new(v0..v7)`
Creates a new `Vec8s` from eight integer values.

```
fn Vec8s.new(v0: Int, v1: Int, v2: Int, v3: Int, v4: Int, v5: Int, v6: Int, v7: Int) -> Vec8s;
```

#### Operations

##### `Vec8s.add(self, other)`
Element-wise addition.

```
fn Vec8s.add(self, other: Vec8s) -> Vec8s;
```

##### `Vec8s.sub(self, other)`
Element-wise subtraction.

```
fn Vec8s.sub(self, other: Vec8s) -> Vec8s;
```

##### `Vec8s.get(self, index)`
Extracts the value at lane `index` (0-7).

```
fn Vec8s.get(self, index: Int) -> Int;
```

##### `Vec8s.set(self, index, value)`
Sets the value at lane `index` (0-7) to `value`. Returns a new `Vec8s`.

```
fn Vec8s.set(self, index: Int, value: Int) -> Vec8s;
```

---

### Vec16b -- 16 x Int8

128-bit byte vector.

#### Constructor

##### `Vec16b.new(v0..v15)`
Creates a new `Vec16b` from sixteen integer values.

```
fn Vec16b.new(v0: Int, v1: Int, v2: Int, v3: Int, v4: Int, v5: Int, v6: Int, v7: Int, v8: Int, v9: Int, v10: Int, v11: Int, v12: Int, v13: Int, v14: Int, v15: Int) -> Vec16b;
```

#### Operations

##### `Vec16b.add(self, other)`
Element-wise addition.

```
fn Vec16b.add(self, other: Vec16b) -> Vec16b;
```

##### `Vec16b.sub(self, other)`
Element-wise subtraction.

```
fn Vec16b.sub(self, other: Vec16b) -> Vec16b;
```

##### `Vec16b.get(self, index)`
Extracts the value at lane `index` (0-15).

```
fn Vec16b.get(self, index: Int) -> Int;
```

##### `Vec16b.set(self, index, value)`
Sets the value at lane `index` (0-15) to `value`. Returns a new `Vec16b`.

```
fn Vec16b.set(self, index: Int, value: Int) -> Vec16b;
```

---

## 256-bit Vector Types (AVX / AVX2)

### Vec8f -- 8 x Float32

#### Constructor

##### `Vec8f.new(v0..v7)`
Creates a new `Vec8f` from eight scalar values.

```
fn Vec8f.new(v0: Float32, v1: Float32, v2: Float32, v3: Float32, v4: Float32, v5: Float32, v6: Float32, v7: Float32) -> Vec8f;
```

#### Operations

##### `Vec8f.add(self, other)`
Element-wise addition. AVX-accelerated when available.

```
fn Vec8f.add(self, other: Vec8f) -> Vec8f;
```

##### `Vec8f.mul(self, other)`
Element-wise multiplication. AVX-accelerated when available.

```
fn Vec8f.mul(self, other: Vec8f) -> Vec8f;
```

##### `Vec8f.get(self, index)`
Extracts the value at lane `index` (0-7).

```
fn Vec8f.get(self, index: Int) -> Float32;
```

##### `Vec8f.set(self, index, value)`
Sets the value at lane `index` (0-7) to `value`. Returns a new `Vec8f`.

```
fn Vec8f.set(self, index: Int, value: Float32) -> Vec8f;
```

---

### Vec4d -- 4 x Float64

256-bit double-precision vector.

#### Constructor

##### `Vec4d.new(v0, v1, v2, v3)`
Creates a new `Vec4d` from four scalar values.

```
fn Vec4d.new(v0: Float64, v1: Float64, v2: Float64, v3: Float64) -> Vec4d;
```

#### Operations

##### `Vec4d.add(self, other)`
Element-wise addition.

```
fn Vec4d.add(self, other: Vec4d) -> Vec4d;
```

##### `Vec4d.mul(self, other)`
Element-wise multiplication.

```
fn Vec4d.mul(self, other: Vec4d) -> Vec4d;
```

##### `Vec4d.get(self, index)`
Extracts the value at lane `index` (0-3).

```
fn Vec4d.get(self, index: Int) -> Float64;
```

##### `Vec4d.set(self, index, value)`
Sets the value at lane `index` (0-3) to `value`. Returns a new `Vec4d`.

```
fn Vec4d.set(self, index: Int, value: Float64) -> Vec4d;
```

---

### Vec8i -- 8 x Int32

256-bit integer vector.

#### Constructor

##### `Vec8i.new(v0..v7)`
Creates a new `Vec8i` from eight integer values.

```
fn Vec8i.new(v0: Int, v1: Int, v2: Int, v3: Int, v4: Int, v5: Int, v6: Int, v7: Int) -> Vec8i;
```

#### Operations

##### `Vec8i.add(self, other)`
Element-wise addition.

```
fn Vec8i.add(self, other: Vec8i) -> Vec8i;
```

##### `Vec8i.sub(self, other)`
Element-wise subtraction.

```
fn Vec8i.sub(self, other: Vec8i) -> Vec8i;
```

##### `Vec8i.get(self, index)`
Extracts the value at lane `index` (0-7).

```
fn Vec8i.get(self, index: Int) -> Int;
```

##### `Vec8i.set(self, index, value)`
Sets the value at lane `index` (0-7) to `value`. Returns a new `Vec8i`.

```
fn Vec8i.set(self, index: Int, value: Int) -> Vec8i;
```

---

## 512-bit Vector Types (AVX-512)

### Vec16f -- 16 x Float32

512-bit float vector.

#### Constructor

##### `Vec16f.new(v0..v15)`
Creates a new `Vec16f` from sixteen scalar values.

```
fn Vec16f.new(v0: Float32, v1: Float32, v2: Float32, v3: Float32, v4: Float32, v5: Float32, v6: Float32, v7: Float32, v8: Float32, v9: Float32, v10: Float32, v11: Float32, v12: Float32, v13: Float32, v14: Float32, v15: Float32) -> Vec16f;
```

#### Operations

##### `Vec16f.add(self, other)`
Element-wise addition. AVX-512-accelerated when available.

```
fn Vec16f.add(self, other: Vec16f) -> Vec16f;
```

##### `Vec16f.mul(self, other)`
Element-wise multiplication. AVX-512-accelerated when available.

```
fn Vec16f.mul(self, other: Vec16f) -> Vec16f;
```

##### `Vec16f.get(self, index)`
Extracts the value at lane `index` (0-15).

```
fn Vec16f.get(self, index: Int) -> Float32;
```

##### `Vec16f.set(self, index, value)`
Sets the value at lane `index` (0-15) to `value`. Returns a new `Vec16f`.

```
fn Vec16f.set(self, index: Int, value: Float32) -> Vec16f;
```

---

### Vec8d -- 8 x Float64

512-bit double-precision vector.

#### Constructor

##### `Vec8d.new(v0..v7)`
Creates a new `Vec8d` from eight scalar values.

```
fn Vec8d.new(v0: Float64, v1: Float64, v2: Float64, v3: Float64, v4: Float64, v5: Float64, v6: Float64, v7: Float64) -> Vec8d;
```

#### Operations

##### `Vec8d.add(self, other)`
Element-wise addition. AVX-512-accelerated when available.

```
fn Vec8d.add(self, other: Vec8d) -> Vec8d;
```

##### `Vec8d.mul(self, other)`
Element-wise multiplication. AVX-512-accelerated when available.

```
fn Vec8d.mul(self, other: Vec8d) -> Vec8d;
```

##### `Vec8d.get(self, index)`
Extracts the value at lane `index` (0-7).

```
fn Vec8d.get(self, index: Int) -> Float64;
```

##### `Vec8d.set(self, index, value)`
Sets the value at lane `index` (0-7) to `value`. Returns a new `Vec8d`.

```
fn Vec8d.set(self, index: Int, value: Float64) -> Vec8d;
```

---

## Contracts

All SIMD operations that call C FFI are guarded by contracts requiring that SIMD is supported on the target hardware:

```
pub fn Vec4f.add(self, other: Vec4f) -> Vec4f
  requires: simd_supported()
{
  // Hardware-accelerated via SSE/NEON
}
```

Scalar fallback operations have no FFI dependencies and require no contracts.

---

## Architecture

```
+----------------------------------+
|  xiom.simd (Safe XIOM API)       |
|  Vec4f, Vec8f, Vec16f types      |
|  add, mul, dot, sqrt, normalize  |
|  Contracts: requires simd_       |
|  supported                       |
|----------------------------------|
|  C FFI (extern "C")              |
|  xiom_simd_f32x4_add, etc.       |
|----------------------------------|
|  simd_runtime.c (402 lines)      |
|  x86_64: <x86intrin.h> SSE/AVX   |
|  ARM64:  <arm_neon.h> NEON       |
|  Scalar: portable C fallback     |
|  CPUID feature detection         |
`----------------------------------+
```
