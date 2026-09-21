<!--
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# XIOM Showcase Projects -- XiomDB & XiomVDB

> Two flagship projects to fully exercise the language post-Phase 3:
> a general-purpose embedded database and a vector database.
> Both stress what XIOM was built for -- no-GC determinism, contracts as
> correctness, and FFI for everything outside the core language.
> **Status: DECIDED.** Build order and scope fixed. Promoted to the Build
> Strategy decision log.

---

## Decision: Build Order

**XiomDB first. XiomVDB second.** A key-value store with B-tree forces
implementation of every systems primitive XIOM needs: heap allocation, file
I/O, byte-level memory management, crash recovery. XiomVDB skips half of
these because it can lean on brute-force k-NN for correctness. Building
XiomDB first gives XiomVDB a battle-tested storage engine to build on.

The two projects deliberately overlap in infrastructure but diverge in the
interesting part:

| Shared foundation | Diverges in |
|---|---|
| Storage engine, page/buffer management, WAL, FFI-wrapped networking | XiomDB: B-tree/LSM + query semantics. XiomVDB: float arrays + ANN index + distance math |

Building XiomDB first means the storage engine is written once and reused.
The contract system gets exercised against two genuinely different correctness
domains -- relational/transactional invariants vs. numerical/geometric
invariants -- which is a better language stress test than either project alone.

---

## Project 1 -- XiomDB

### Phase A: Key-Value Store (MVP)

- Embedded, single-node, single-process key-value store
- B-tree storage engine (LSM-tree is a v2 option, not MVP)
- Write-ahead log (WAL) for durability
- Page-based buffer pool with explicit eviction (no GC)
- No networking -- embedded mode only (like SQLite, called in-process)
- No transactions -- single operations only
- Target: ~2,000 lines of XIOM

### Phase B: Transactions (post-XiomVDB)

Only after XiomVDB exercises the storage engine from a different domain:
- Single-writer, MVCC-lite (snapshot read, serialized write)
- Full serializability is a stretch goal, not MVP
- Target: verify the storage engine is correct under write pressure

### Where Contracts Do Real Work

```xiom
fn BTreeNode.insert(key: Key, value: Value)
  requires: self.num_keys < MAX_KEYS_PER_NODE
  ensures:  self.is_sorted()
  invariant: self.num_keys <= MAX_KEYS_PER_NODE

fn Transaction.commit()
  requires: self.state == TxState.Active
  ensures:  self.state == TxState.Committed || self.state == TxState.Aborted
```

- B-tree node invariants (`is_sorted`, key count bounds) -- uses the
  `is_sorted()` contract collection method already in the Phase 1 spec
- WAL ordering invariant: "log record never written after the data page it
  describes is flushed" -- a real, historically common DB bug class
- Transaction state machine: `requires`/`ensures` on every state transition
  prevents the classic "commit after abort" bug class at compile-checked
  runtime-guard level

### Build Order

1. Page/buffer pool + on-disk format
2. WAL + crash recovery
3. B-tree (insert/lookup/delete) with contracts on node invariants
4. **STOP.** Verify. Build XiomVDB on this foundation.
5. Single-writer transactions with state-machine contracts
6. Typed query API
7. (Stretch) client/server mode over FFI-wrapped sockets

---

## Project 2 -- XiomVDB

### Scope (MVP)

- Embedded vector store: insert, delete, k-NN query
- Built on XiomDB's storage engine (page pool, WAL)
- Flat float32 array storage (no quantization in v1)
- HNSW as the ANN index (better recall/speed tradeoff than IVF for an MVP)
- Cosine similarity + dot product as the two distance functions
- Metadata filtering is a stretch goal, not MVP

### Where Contracts Do Real Work

This is the strongest contract showcase of the two projects, because the bugs
it prevents are extremely common in real vector DB clients today:

```xiom
fn VectorIndex.insert(vector: Vec[Float32], id: Id)
  requires: vector.len() == self.dimension
  ensures:  self.count == old(self.count) + 1

fn VectorIndex.query(vector: Vec[Float32], k: Int) -> Vec[(Id, Float32)]
  requires: vector.len() == self.dimension
  requires: k > 0
  ensures:  result.len() <= k
  ensures:  result.is_sorted_by_descending_score()

fn HNSWNode.add_neighbor(neighbor: NodeId)
  requires: self.neighbors.len() < self.max_connections
  invariant: self.neighbors.len() <= self.max_connections
```

- **Dimension mismatch** is the single most common runtime crash in every
  vector DB client (Pinecone, Chroma, FAISS wrappers -- all of them). Catching
  it at the contract layer instead of a confusing native crash is a genuinely
  compelling, concrete demo.
- HNSW's `max_connections` per layer is a real structural invariant in the
  algorithm -- not a contrived example. It's the correctness property the
  algorithm depends on.
- `result.is_sorted_by_descending_score()` reuses the existing `is_sorted`
  contract collection pattern with a custom comparator -- a good test of
  whether that mechanism generalizes past the trivial case.

### Networking

Embedded mode only for v1 -- called in-process or via a thin C-ABI boundary
from Rust/Tauri. Standalone service mode wraps an existing C HTTP library
for the wire layer later; don't write XIOM's own networking stack.

### Build Order

1. Flat float32 storage + brute-force k-NN (correctness baseline)
2. Distance functions (dot product, cosine) with dimension contracts
3. HNSW index construction with neighbor-count invariants
4. Query path with result-ordering contracts
5. (Stretch) metadata filtering, quantization

---

## C-ABI Export

Both projects expose a thin C-ABI surface for consumption from Rust (Tauri),
Python, and other languages via FFI. This doubles as XIOM's first real test
of the *outbound* FFI story -- XIOM exposing itself to other languages, not
just calling into C libraries.

---

## Comparison

| | XiomDB | XiomVDB |
|---|---|---|
| Core data structure | B-tree | HNSW graph |
| Builds on | (self) | XiomDB storage engine |
| Contract showcase | Transaction state machine, node invariants, WAL ordering | Dimension safety, neighbor-count invariants, result ordering |
| Most common bug it prevents | Commit-after-abort, corrupted node ordering, WAL/page write ordering | Dimension mismatch crashes (very common in real tools) |
| MVP scope risk | Medium -- if transactions scope-creep. Mitigated by Phase A/B split. | Lower -- k-NN/HNSW is well-bounded |
| Networking | None for v1 (embedded) | None for v1 (embedded) |

---

## Integration with External Systems (Kyberon OS, Tauri)

Both projects are embedded libraries, not services, for v1:

- Compile XiomDB/XiomVDB to a native library (XIOM -> LLVM -> `.so`/`.dll`)
- Expose a thin C-ABI surface
- Call from Rust via `bindgen`-style FFI wrapper
- XiomVDB directly integrates with Kyberon's MNEME memory subsystem

---

*XIOM Showcase Projects -- Version 1.0. Decisions made 2026-06-30.*
*Recorded in XIOM_Build_Strategy.md decision log.*
