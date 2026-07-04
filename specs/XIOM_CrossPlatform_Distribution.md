# XIOM — Cross-Platform Build & Distribution Recommendations

> Companion to XIOM_Build_Strategy.md. Covers how the compiler gets built and
> verified across targets, and how users install XIOM.
> **Status: DECIDED.** Promoted to the Build Strategy decision log.

---

## Part 1 — Cross-Platform Build Strategy

### Decision: One Branch, Conditional Compilation, CI Matrix

**Status: DECIDED.** Single `main` branch. Platform differences gated by
conditional compilation. CI matrix per commit. No per-OS branches. No
exceptions.

The source is identical across platforms. Two things differ:

1. The LLVM target triple (a codegen flag, not a source fork)
2. OS-specific stdlib code (filesystem paths, process spawning, syscalls)

Neither justifies a branch. XIOM's stdlib defines a `cfg`-style mechanism for
OS-specific code once Phase 1.5 stdlib work reaches OS-facing APIs:

```xiom
// illustrative — exact syntax TBD when XIOM defines its cfg mechanism
fn Path.separator() -> Char
  cfg(target_os: "windows") { return '\\' }
  cfg(target_os: "linux", "macos") { return '/' }
```

### Decision: CI Build Matrix

**Status: DECIDED.** Every commit to `main` builds on every target in parallel:

| Target | How |
|---|---|
| `x86_64-unknown-linux-gnu` | Native CI runner |
| `aarch64-unknown-linux-gnu` | Cross-compile from x86_64 (LLVM handles this natively) or QEMU |
| `x86_64-pc-windows-msvc` | Native CI runner |
| `aarch64-pc-windows-msvc` | Cross-compile |
| `x86_64-apple-darwin` | Apple-hosted CI runner |
| `aarch64-apple-darwin` | Apple-hosted CI runner |
| `wasm32-unknown-unknown` | Already proven in Phase 0 — same pipeline, runs in CI |

LLVM cross-compilation covers most of the matrix without separate physical
machines — LLVM can target `aarch64-unknown-linux-gnu` from an x86_64 host
directly. Real machines/VMs are only needed to **run and test** the output
binary, not just build it.

### Decision: Sequencing

**Status: DECIDED.** Self-host on one platform first. Add CI matrix in Phase 3.

1. Get Phase 2 self-hosting working end-to-end on one host platform (daily
   development machine)
2. Add the CI build matrix and additional target support as Phase 3 ecosystem
   work, alongside the package registry and LSP
3. Reserve actual VMs/physical machines for final runtime verification per
   target — not as a build/branch mechanism

This follows the Build Strategy principle: "the next phase only starts when
the previous one is provably working."

### Note: macOS CI

Apple's EULA restricts virtualizing macOS to genuine Apple hardware. Use
GitHub Actions' macOS runners (Apple-hosted, properly licensed), or test on
real Mac hardware if available.

---

## Part 2 — Distribution Model

### Decision: Three Distribution Paths

**Status: DECIDED.** Pre-built binaries, build-from-source, and WASM compiler
playground.

#### Path 1: Pre-built Binaries (Primary)

- Built once per target triple in CI (the same matrix from Part 1)
- Distributed via:
  - An installer script (`curl | sh` style, e.g. rustup's model)
  - Platform-native packages: `.msi` (Windows), `.pkg` (macOS), `.deb`/`.rpm`
    or a static binary (Linux)
- User experience: install, get `xiom` on PATH, never see a build step.

#### Path 2: Build from Source (Secondary)

- For security-conscious organizations, package maintainers, distros
- Effectively free once self-hosting works — the CI matrix already proves the
  source builds on every target

#### Path 3: WASM Compiler Playground (Tertiary — Unique to XIOM)

**This is the genuinely differentiated distribution path.** The XIOM compiler
itself compiles to WASM (proven in Phase 0 — it's the same pipeline flag).
This means:

- A web-based XIOM playground where the compiler runs **client-side** in the
  browser via WASM — no install, no backend server, no account
- Instant-on for new users: open a URL, write XIOM, see compiled output or
  run the WASM binary directly in the browser
- The compiler WASM is a distribution artifact built by the same CI matrix

No other systems language (Rust, Go, Zig) ships its compiler as WASM for
in-browser use. This is a competitive differentiator worth investing in.

The website's primary CTA should be the playground ("Try XIOM in your
browser"), with the installer command as the second CTA ("Install locally"),
and "build from source" linked below both as the tertiary option.

### Decision: Version Manager

**Status: DEFERRED to Phase 3.** Once there are versioned releases across
multiple OSes, "which XIOM version is installed" becomes a real question.
Model: `xiomup` (equivalent to `rustup`, `nvm`). Design the distribution
infrastructure to support this from the start, even if the tool itself ships
later.

---

## Part 3 — What We Reject

| Approach | Why |
|---|---|
| Per-OS branches (`macos`, `windows`, `linux-x86_64`) | Maintenance suicide. Every fix must be cherry-picked across every branch. Single source of truth is non-negotiable. |
| Build-from-source as the only path | Most users will bounce off a language that requires bootstrapping a toolchain just to try it. |
| Leaking CI/testing workflow into user install experience | The CI build matrix is for verifying correctness. Users never see it. |

---

## Summary

| Question | Decision |
|---|---|
| Branch per OS? | **No** — one `main`, conditional compilation |
| How to verify cross-platform builds? | CI build matrix, cross-compilation where possible |
| When to physically test on a target? | Only for runtime verification, not build verification |
| macOS CI/testing | Apple-hosted CI runners or real hardware |
| When to build full cross-platform support? | Phase 3, after Phase 2 self-hosting proven on one platform |
| Distribution model | Three paths: pre-built binaries (primary), build-from-source (secondary), WASM compiler playground (tertiary — differentiated) |
| Version manager? | DEFERRED to Phase 3 (`xiomup`) |

---

*XIOM Cross-Platform Build & Distribution — Version 1.0. Decisions made 2026-06-30.*
*Recorded in XIOM_Build_Strategy.md decision log.*
