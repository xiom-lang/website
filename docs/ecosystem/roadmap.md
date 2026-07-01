# AXIOM Ecosystem — Expansion Roadmap

> v0.14.1 — 38 stdlib modules, 75 conformance tests, 244 Rust tests.
> This document defines the ecosystem expansion strategy.

## Philosophy

| Tier | Who Builds | Who Maintains | Examples |
|------|-----------|---------------|----------|
| **First-party** | AXIOM team | AXIOM team | stdlib, axiom:net, axiom:sql |
| **First-party FFI** | AXIOM team provides bindings | Community extends | libcurl, SQLite, OpenSSL wrappers |
| **Community** | Anyone | Community | HTTP frameworks, ORM, GUI apps |

### What We Don't Bless

Axiom explicitly does NOT bless a single solution for:
- **HTTP server frameworks** — let the ecosystem compete (Axum/Actix equivalents)
- **ORM / query builders** — too tied to database choice
- **GUI framework** — platform-fragmented, use Dear ImGui via FFI
- **Parser combinators** — let libraries emerge organically
- **Crypto implementations** — never write native crypto; always FFI-wrap (libsodium, OpenSSL)

## Package Categories

### Database & Storage

| Package | Status | Strategy |
|---------|--------|----------|
| `axiom:sql` (SQLite) | ✅ First-party FFI | SQLite C bindings |
| `axiom:postgres` | 🚧 Community | libpq FFI bindings |
| `axiom:mysql` | 🚧 Community | MySQL C connector FFI |
| `axiom:redis` | 🚧 Community | hiredis FFI bindings |
| `axiom:rocksdb` | 📋 Planned | RocksDB C FFI |
| `axiom:sled` | 📋 Community | Pure AXIOM embedded DB |
| AxiomDB (KV store) | 📋 Gated | Requires full self-hosting |
| AxiomVDB (vector DB) | 📋 Gated | Requires AxiomDB |

### Networking & HTTP

| Package | Status | Strategy |
|---------|--------|----------|
| `axiom:net` (HTTP client) | ✅ First-party FFI | libcurl C bindings |
| `axiom:websocket` | 🚧 Community | libwebsockets FFI |
| `axiom:grpc` | 📋 Community | gRPC C core FFI |
| HTTP server (Axum-like) | 📋 Community | Not first-party blessed |
| HTTP server (Actix-like) | 📋 Community | Not first-party blessed |
| TLS/SSL | ✅ First-party FFI | OpenSSL/libressl bindings |

### Cryptography & Security

| Package | Status | Strategy |
|---------|--------|----------|
| `axiom:crypto` (hashing) | ✅ First-party FFI | OpenSSL SHA/ AES bindings |
| `axiom:libsodium` | 🚧 First-party FFI | libsodium C bindings |
| `axiom:jwt` | 🚧 Community | Pure AXIOM JWT |
| `axiom:bcrypt` | 🚧 Community | FFI-wrap bcrypt |
| **⚠ Never write native crypto** — always FFI-wrap battle-tested C libraries |

### GPU & Graphics

| Package | Status | Strategy |
|---------|--------|----------|
| `axiom:vulkan` | 🚧 First-party FFI | Vulkan C bindings |
| `axiom:opengl` | 🚧 Community | OpenGL C bindings |
| `axiom:wgpu` | 📋 Community | WebGPU native FFI |
| `axiom:cuda` | 📋 Community | CUDA C FFI |
| `axiom:opencl` | 📋 Community | OpenCL C FFI |

### GUI

| Approach | Status | Strategy |
|----------|--------|----------|
| Dear ImGui (C FFI) | 🚧 Community | MIT license, C API, cross-platform |
| SDL2 windowing | 🚧 Community | SDL2 C FFI for window creation |
| GLFW windowing | 🚧 Community | GLFW C FFI |
| Native AXIOM GUI | 📋 Future | Do NOT build now — platform fragmentation is a full-time job |

### Machine Learning & Math

| Package | Status | Strategy |
|---------|--------|----------|
| `axiom:blas` | 🚧 Community | BLAS/LAPACK C FFI |
| `axiom:tensorflow` | 📋 Community | TensorFlow C API FFI |
| `axiom:onnx` | 📋 Community | ONNX Runtime C FFI |
| `axiom:torch` | 📋 Community | LibTorch C FFI |

### File Formats & Serialization

| Package | Status | Strategy |
|---------|--------|----------|
| `axiom:serialize` | ✅ First-party | JSON, binary |
| `axiom:toml` | 🚧 Community | Pure AXIOM or tomlc99 FFI |
| `axiom:yaml` | 🚧 Community | libyaml FFI |
| `axiom:csv` | 🚧 Community | Pure AXIOM |
| `axiom:protobuf` | 📋 Community | protobuf C FFI |
| `axiom:msgpack` | 🚧 Community | msgpack-c FFI |

### Game Development (AXIOM's Sweet Spot)

| Package | Status | Strategy |
|---------|--------|----------|
| `axiom:vulkan` | 🚧 | Vulkan C FFI (graphics + compute) |
| `axiom:glfw` | 🚧 | GLFW C FFI (windowing + input) |
| `axiom:openal` | 🚧 | OpenAL C FFI (audio) |
| `axiom:bullet` | 📋 | Bullet Physics C FFI |
| `axiom:imgui` | 🚧 | Dear ImGui C FFI (debug UI) |
| `axiom:stb` | 🚧 | stb_image C FFI (image loading) |

## Build Order

### Wave 1: Core FFI Bindings (First-party)
1. `axiom:vulkan` — Vulkan C bindings via axiom ffigen
2. `axiom:glfw` — GLFW windowing bindings
3. `axiom:libsodium` — Secure crypto primitives

### Wave 2: Game Dev Stack
4. `axiom:imgui` — Dear ImGui debug UI
5. `axiom:openal` — Audio
6. `axiom:stb` — Image loading

### Wave 3: Database Ecosystem
7. `axiom:postgres` — PostgreSQL
8. `axiom:redis` — Redis

### Wave 4: Community Growth
9. HTTP server frameworks emerge
10. ORM libraries appear
11. Pure AXIOM packages without FFI

## How to Create an FFI Package

```powershell
# 1. Create the binding spec
# ecosystem/axiom-vulkan/vulkan.axiom-bind

# 2. Generate AXIOM extern blocks
axiom ffigen ecosystem/axiom-vulkan/vulkan.axiom-bind

# 3. Create the AXIOM wrapper
# ecosystem/axiom-vulkan/vulkan.ax

# 4. Publish to registry
axiom pkg publish
```

## Concurrency Notes

AXIOM's ownership model makes GPU/Vulkan bindings SAFER than C++:
- No use-after-free of GPU resources (ownership tracking)
- No data races on buffer updates (borrow checker)
- Contracts can verify buffer sizes and alignment

This is genuinely AXIOM's competitive advantage for game dev.
