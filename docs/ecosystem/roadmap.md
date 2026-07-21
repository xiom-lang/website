# XIOM Ecosystem — Expansion Roadmap

> v0.14.1 — 38 stdlib modules, 75 conformance tests, 244 Rust tests.
> This document defines the ecosystem expansion strategy.

## Philosophy

| Tier | Who Builds | Who Maintains | Examples |
|------|-----------|---------------|----------|
| **First-party** | XIOM team | XIOM team | stdlib, xiom:net, xiom:sql |
| **First-party FFI** | XIOM team provides bindings | Community extends | libcurl, SQLite, OpenSSL wrappers |
| **Community** | Anyone | Community | HTTP frameworks, ORM, GUI apps |

### What We Don't Bless

xiom explicitly does NOT bless a single solution for:
- **HTTP server frameworks** — let the ecosystem compete (Axum/Actix equivalents)
- **ORM / query builders** — too tied to database choice
- **GUI framework** — platform-fragmented, use Dear ImGui via FFI
- **Parser combinators** — let libraries emerge organically
- **Crypto implementations** — never write native crypto; always FFI-wrap (libsodium, OpenSSL)

## Package Categories

### Database & Storage

| Package | Status | Strategy |
|---------|--------|----------|
| `xiom:sql` (SQLite) | ✅ First-party FFI | SQLite C bindings |
| `xiom:postgres` | 🚧 Community | libpq FFI bindings |
| `xiom:mysql` | 🚧 Community | MySQL C connector FFI |
| `xiom:redis` | 🚧 Community | hiredis FFI bindings |
| `xiom:rocksdb` | 📋 Planned | RocksDB C FFI |
| `xiom:sled` | 📋 Community | Pure XIOM embedded DB |
| xiomDB (KV store) | 📋 Gated | Requires full self-hosting |
| xiomVDB (vector DB) | 📋 Gated | Requires xiomDB |

### Networking & HTTP

| Package | Status | Strategy |
|---------|--------|----------|
| `xiom:net` (HTTP client) | ✅ First-party FFI | libcurl C bindings |
| `xiom:websocket` | 🚧 Community | libwebsockets FFI |
| `xiom:grpc` | 📋 Community | gRPC C core FFI |
| HTTP server (Axum-like) | 📋 Community | Not first-party blessed |
| HTTP server (Actix-like) | 📋 Community | Not first-party blessed |
| TLS/SSL | ✅ First-party FFI | OpenSSL/libressl bindings |

### Cryptography & Security

| Package | Status | Strategy |
|---------|--------|----------|
| `xiom:crypto` (hashing) | ✅ First-party FFI | OpenSSL SHA/ AES bindings |
| `xiom:libsodium` | 🚧 First-party FFI | libsodium C bindings |
| `xiom:jwt` | 🚧 Community | Pure XIOM JWT |
| `xiom:bcrypt` | 🚧 Community | FFI-wrap bcrypt |
| **⚠ Never write native crypto** — always FFI-wrap battle-tested C libraries |

### GPU & Graphics

| Package | Status | Strategy |
|---------|--------|----------|
| `xiom:vulkan` | 🚧 First-party FFI | Vulkan C bindings |
| `xiom:opengl` | 🚧 Community | OpenGL C bindings |
| `xiom:wgpu` | 📋 Community | WebGPU native FFI |
| `xiom:cuda` | 📋 Community | CUDA C FFI |
| `xiom:opencl` | 📋 Community | OpenCL C FFI |

### GUI

| Approach | Status | Strategy |
|----------|--------|----------|
| Dear ImGui (C FFI) | 🚧 Community | MIT license, C API, cross-platform |
| SDL2 windowing | 🚧 Community | SDL2 C FFI for window creation |
| GLFW windowing | 🚧 Community | GLFW C FFI |
| Native XIOM GUI | 📋 Future | Do NOT build now — platform fragmentation is a full-time job |

### Machine Learning & Math

| Package | Status | Strategy |
|---------|--------|----------|
| `xiom:blas` | 🚧 Community | BLAS/LAPACK C FFI |
| `xiom:tensorflow` | 📋 Community | TensorFlow C API FFI |
| `xiom:onnx` | 📋 Community | ONNX Runtime C FFI |
| `xiom:torch` | 📋 Community | LibTorch C FFI |

### File Formats & Serialization

| Package | Status | Strategy |
|---------|--------|----------|
| `xiom:serialize` | ✅ First-party | JSON, binary |
| `xiom:toml` | 🚧 Community | Pure XIOM or tomlc99 FFI |
| `xiom:yaml` | 🚧 Community | libyaml FFI |
| `xiom:csv` | 🚧 Community | Pure XIOM |
| `xiom:protobuf` | 📋 Community | protobuf C FFI |
| `xiom:msgpack` | 🚧 Community | msgpack-c FFI |

### Game Development (XIOM's Sweet Spot)

| Package | Status | Strategy |
|---------|--------|----------|
| `xiom:vulkan` | 🚧 | Vulkan C FFI (graphics + compute) |
| `xiom:glfw` | 🚧 | GLFW C FFI (windowing + input) |
| `xiom:openal` | 🚧 | OpenAL C FFI (audio) |
| `xiom:bullet` | 📋 | Bullet Physics C FFI |
| `xiom:imgui` | 🚧 | Dear ImGui C FFI (debug UI) |
| `xiom:stb` | 🚧 | stb_image C FFI (image loading) |

## Build Order

### Wave 1: Core FFI Bindings (First-party)
1. `xiom:vulkan` — Vulkan C bindings via xiom ffigen
2. `xiom:glfw` — GLFW windowing bindings
3. `xiom:libsodium` — Secure crypto primitives

### Wave 2: Game Dev Stack
4. `xiom:imgui` — Dear ImGui debug UI
5. `xiom:openal` — Audio
6. `xiom:stb` — Image loading

### Wave 3: Database Ecosystem
7. `xiom:postgres` — PostgreSQL
8. `xiom:redis` — Redis

### Wave 4: Community Growth
9. HTTP server frameworks emerge
10. ORM libraries appear
11. Pure XIOM packages without FFI

## How to Create an FFI Package

```powershell
# 1. Create the binding spec
# packages/xiom-vulkan/vulkan.xiom-bind

# 2. Generate XIOM extern blocks
xiom ffigen packages/xiom-vulkan/vulkan.xiom-bind

# 3. Create the XIOM wrapper
# packages/xiom-vulkan/vulkan.xi

# 4. Publish to registry
xiom pkg publish
```

## Concurrency Notes

XIOM's ownership model makes GPU/Vulkan bindings SAFER than C++:
- No use-after-free of GPU resources (ownership tracking)
- No data races on buffer updates (borrow checker)
- Contracts can verify buffer sizes and alignment

This is genuinely XIOM's competitive advantage for game dev.
