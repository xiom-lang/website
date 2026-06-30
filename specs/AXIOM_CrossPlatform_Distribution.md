# AXIOM — Cross-Platform Build & Distribution Recommendations

> Companion to AXIOM_Build_Strategy.md. Covers two related but separate
> questions: how the compiler gets built and verified across OS/architecture
> targets, and how end users actually get AXIOM onto their machine.
> Recommendations only — promote to the Build Strategy decision log if and
> when actually decided.

---

## Part 1 — Cross-Platform Build Strategy

### The wrong approach: per-OS branches

**Recommendation: do not do this.** Branching `main` into `macos`, `windows`,
`linux-x86_64`, `linux-aarch64` etc. and merging back creates permanent
maintenance debt — every fix has to be cherry-picked or merged across every
branch, and platform-specific stdlib implementations will drift apart over
time until merging becomes genuinely painful. This contradicts the Build
Strategy's own "single source of truth, nothing built on speculation"
philosophy.

The source is the same across platforms. Only two things actually differ:

1. The LLVM target triple (codegen detail, not a source fork)
2. A thin layer of OS-specific stdlib code (filesystem, process spawning, syscalls)

Neither requires a branch.

### The recommended approach: one branch, conditional compilation, CI matrix

**Single source tree (`main`).** All platform differences live in the same
codebase, gated by conditional compilation at the point where they're
actually needed — the same pattern Rust uses with `#[cfg(target_os = "...")]`.
AXIOM's stdlib should define an equivalent `cfg`-style mechanism for this
once Phase 1.5/2 stdlib work reaches OS-facing code (filesystem paths,
process spawning, etc.).

```axiom
// illustrative — exact syntax TBD when AXIOM defines its cfg mechanism
fn Path.separator() -> Char
  cfg(target_os: "windows") { return '\\' }
  cfg(target_os: "linux", "macos") { return '/' }
```

**CI build matrix, not manual per-OS branching.** Every commit to `main`
builds on every target in parallel via CI (e.g. GitHub Actions):

| Target | How |
|---|---|
| `x86_64-unknown-linux-gnu` | Native CI runner |
| `aarch64-unknown-linux-gnu` | Cross-compile from x86_64 (LLVM handles this natively) or QEMU |
| `x86_64-pc-windows-msvc` | Native CI runner |
| `aarch64-pc-windows-msvc` | Cross-compile |
| `x86_64-apple-darwin` | Apple-hosted CI runner (see note below) |
| `aarch64-apple-darwin` | Apple-hosted CI runner |
| `wasm32-unknown-unknown` | Already proven in Phase 0 — same pipeline |

Cross-compilation covers most of the matrix without needing separate
physical machines — LLVM can target `aarch64-unknown-linux-gnu` from an
x86_64 host directly. Real machines/VMs are only needed when you need to
**run and test** the output binary, not just build it.

### macOS-specific constraint

Apple's EULA restricts virtualizing macOS to genuine Apple hardware — a
generic VirtualBox/QEMU macOS VM is a legal gray area most CI providers
won't support. Recommended paths:

- Use GitHub Actions' macOS runners (Apple-hosted, properly licensed), or
- Test on real Mac hardware if available

Linux has no such restriction — VirtualBox/QEMU VMs are fine there for
runtime testing.

### Sequencing recommendation

Don't try to prove self-hosting and full cross-platform support
simultaneously. Recommended order:

1. Get Phase 2 self-hosting working end-to-end on one host platform first
   (whichever is the daily development machine)
2. Add the CI build matrix and additional target support as Phase 3
   ecosystem work, alongside the package registry and LSP — not bolted
   onto Phase 2
3. Reserve actual VMs/physical machines for final runtime verification per
   target, not as a build/branch mechanism

This follows the existing Build Strategy principle directly: "the next
phase only starts when the previous one is provably working." Stacking
cross-platform proof on top of self-hosting proof at the same time
violates that.

---

## Part 2 — Distribution Model

### Recommendation: support both pre-built binaries and build-from-source — binaries are the headline path

This is the standard model across mature languages (Rust, Go, Node) and
isn't really an either/or choice.

#### Pre-built binaries (primary, what most users expect)

- Built once per target triple in CI (the same matrix from Part 1) — no
  extra build work, it's the same pipeline that already proves the source
  compiles everywhere
- Distributed via:
  - An installer script (`curl | sh` style, e.g. rustup's model)
  - Platform-native packages: `.msi` (Windows), `.pkg` (macOS), `.deb`/
    `.rpm` or a static binary (Linux)
- User experience: install, get `axiom` on PATH, never see a build step.
  This is what makes the language feel usable to the large majority of
  users who want to write AXIOM, not bootstrap a toolchain.

#### Build from source (secondary, but always available)

- Necessary for: security-conscious organizations, package maintainers,
  Linux distros that build everything from source by policy
- Effectively free once self-hosting works — the CI matrix in Part 1
  already proves the source builds on every target, so "build from
  source" docs are just "here's the repo, here's the command CI already
  runs"

#### What not to do

- Don't make build-from-source the only path — most users will bounce off
  a language that requires bootstrapping a toolchain just to try it
- Don't let the CI/testing workflow (VMs, build matrix) leak into what end
  users have to do to install the language — those are separate concerns

### Stretch recommendation: version manager

Once there are versioned releases across multiple OSes, "which AXIOM
version is installed, how do I switch between them" becomes a real
question — the same problem Rust solved with `rustup` and Node with `nvm`.
Easier to design this in from the start of the distribution work than
retrofit it after users already have ad hoc install habits.

### Website implication

The install page's primary CTA should be the one-line installer command
(binary path), with "build from source" linked below it as the secondary,
not equal-weight, option.

---

## Summary

| Question | Recommendation |
|---|---|
| Branch per OS? | No — one `main`, conditional compilation for OS-specific code |
| How to verify cross-platform builds? | CI build matrix (e.g. GitHub Actions), cross-compilation where possible |
| When to physically test on a target? | Only for runtime verification, not build verification |
| macOS CI/testing | Apple-hosted CI runners or real hardware — not generic VMs (EULA) |
| When to build out full cross-platform support | Phase 3, after Phase 2 self-hosting is proven on one platform first |
| Should end users build from source? | Optional, not required — pre-built binaries are the primary distribution path |
| Distribution model | Installer script + platform packages, same pattern as rustup/Go/Node |

---

*Companion to AXIOM_Build_Strategy.md, AXIOM_Phase3_Recommendations.md, and
AXIOM_Showcase_Projects.md.*
