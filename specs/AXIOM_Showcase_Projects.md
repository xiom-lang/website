# AXIOM Showcase Projects — AxiomDB & AxiomVDB

> Two flagship projects to fully exercise the language post-Phase 3:
> a general-purpose embedded database and a vector database.
> Both are chosen because they stress exactly what AXIOM was built for —
> no-GC determinism, contracts as correctness, and FFI for everything
> that isn't core to the language (networking included — "will be a wrap").

---

## Why These Two, Together

They deliberately overlap in infrastructure but diverge in the interesting part:

| Shared foundation | Diverges in |
|---|---|
| Storage engine, page/buffer management, WAL, FFI-wrapped networking | AxiomDB: B-tree/LSM + query semantics. AxiomVDB: float arrays + ANN index + distance math |

Building them side by side means the boring 40% (storage, durability, wire
protocol) is written once and shared. The contract system gets exercised
against two genuinely different correctness domains — relational/transactional
invariants vs. numerical/geometric invariants — which is a better language
stress test than either project alone.

---

## Project 1 — AxiomDB

### Scope (MVP)

- Embedded, single-node, single-process key-value store as the core
- Simple typed query layer on top (not full SQL — a query builder API is enough for v1)
- B-tree storage engine (LSM-tree is a v2 option, not MVP)
- Write-ahead log (WAL) for durability
- Page-based buffer pool with explicit eviction (no GC — this is the showcase point)
- Transactions: single-writer, MVCC-lite (snapshot read, serialized write) — full
  serializability is a stretch goal, not MVP

### Where Contracts Do Real Work

This is the part that makes it a *language* showcase, not just a DB clone:

```axiom
fn BTreeNode.insert(key: Key, value: Value)
  requires: self.num_keys < MAX_KEYS_PER_NODE
  ensures:  self.is_sorted()
  invariant: self.num_keys <= MAX_KEYS_PER_NODE

fn Transaction.commit()
  requires: self.state == TxState.Active
  ensures:  self.state == TxState.Committed || self.state == TxState.Aborted
```

- B-tree node invariants (`is_sorted`, key count bounds) — uses the
  `is_sorted()` contract collection method already in your Phase 1 spec
- WAL ordering invariant: "log record never written after the data page it
  describes is flushed" — a real, historically common DB bug class
- Transaction state machine: `requires`/`ensures` on every state transition
  prevents the classic "commit after abort" bug class at compile-checked
  runtime-guard level

### Networking

Wire protocol (client/server mode, if you add it post-MVP) is FFI-wrapped —
bind to an existing C socket/HTTP library rather than writing AXIOM's own
networking stack. Embedded mode (in-process, like SQLite) needs no networking
at all and should be the actual MVP target — it's the simpler, more honest
showcase and matches how you'd consume it from Tauri/Rust anyway.

### Suggested Build Order

1. Page/buffer pool + on-disk format
2. WAL + crash recovery
3. B-tree (insert/lookup/delete) with contracts on node invariants
4. Single-writer transactions with state-machine contracts
5. Typed query API on top
6. (Stretch) client/server mode over FFI-wrapped sockets

---

## Project 2 — AxiomVDB

### Scope (MVP)

- Embedded vector store: insert, delete, k-NN query
- Flat float32 array storage (no quantization in v1 — that's a real
  optimization rabbit hole, defer it)
- One ANN index structure for v1 — **HNSW** is the right pick (better
  recall/speed tradeoff than IVF for an MVP, and the graph-construction
  invariants are a better contract showcase, see below)
- Cosine similarity + dot product as the two distance functions for v1
- Metadata filtering is a stretch goal, not MVP (it's a real feature people
  want, but it adds query-planning complexity that isn't the point of v1)

### Where Contracts Do Real Work

This is the strongest contract showcase of the two projects, because the bugs
it prevents are extremely common in real vector DB clients today:

```axiom
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
  vector DB client (Pinecone, Chroma, FAISS wrappers — all of them). Catching
  it at the contract layer instead of a confusing native crash deep in a
  distance computation is a genuinely compelling, concrete demo.
- HNSW's `max_connections` per layer is a real structural invariant in the
  algorithm itself — this isn't a contrived example, it's the actual
  correctness property the algorithm depends on.
- `result.is_sorted_by_descending_score()` reuses your existing `is_sorted`
  contract collection pattern, just with a custom comparator — good test of
  whether that mechanism generalizes past the trivial case.

### Networking / Integration with Kyberon OS

Same principle as AxiomDB: embedded mode first (called in-process or via a
thin FFI boundary from Rust/Tauri), no networking needed for v1. If you want
it as a standalone service later, wrap an existing C HTTP lib for the wire
layer — don't write AXIOM's own.

### Suggested Build Order

1. Flat float32 storage + brute-force k-NN (correctness baseline before
   building the index — also gives you a ground truth to test HNSW recall
   against)
2. Distance functions (dot product, cosine) with dimension contracts
3. HNSW index construction with neighbor-count invariants
4. Query path with result-ordering contracts
5. (Stretch) metadata filtering, quantization

---

## Integration Path with Kyberon OS (Tauri/Rust/React/SQLite)

Both projects are embedded libraries, not services, for v1. That means:

- Compile AxiomDB/AxiomVDB to a native library (AXIOM → LLVM → `.so`/`.dll`)
- Expose a thin C-ABI surface (this is a natural fit — you already need C FFI
  for AXIOM's own ecosystem story)
- Call from Rust via a `bindgen`-style FFI wrapper, same pattern as any other
  native Rust dependency
- SQLite stays as-is for whatever it's already doing (app state, settings) —
  AxiomVDB specifically replaces/supplements whatever you'd otherwise reach
  for (a Python-based vector store, or bolting vectors onto SQLite) for
  Kyberon's memory subsystem (MNEME)

This also means the C-ABI export work for these two projects doubles as your
first real test of AXIOM's FFI story in the *outbound* direction (AXIOM
exposing itself to other languages), which you haven't stress-tested yet —
so far the FFI discussion has been about AXIOM calling *into* C libraries,
not the reverse.

---

## Summary Comparison

| | AxiomDB | AxiomVDB |
|---|---|---|
| Core data structure | B-tree | HNSW graph |
| Contract showcase | Transaction state machine, node invariants | Dimension safety, neighbor-count invariants |
| Most common bug it prevents | Commit-after-abort, corrupted node ordering | Dimension mismatch crashes (very common in real tools) |
| MVP scope risk | Medium — transactions are easy to over-scope | Lower — k-NN/HNSW is well-bounded |
| Networking | None for v1 (embedded) | None for v1 (embedded) |
| Kyberon integration | Optional (general storage) | Direct (MNEME memory subsystem) |

**Recommendation on sequencing:** Build AxiomVDB first. It has a tighter,
better-bounded MVP, a more compelling and concrete contract demo (dimension
mismatch is something every ML/AI developer has hit), and direct, immediate
utility for Kyberon's MNEME subsystem rather than being a showcase that sits
unused. AxiomDB is the better long-term flagship but has more scope-creep
risk (transactions are a classic over-engineering trap).

---

*Companion to AXIOM_Build_Strategy.md and AXIOM_Phase3_Recommendations.md.*
