# Project icon briefs (for the designer)

Internal briefing document -- not part of the website build.

Common spec: 24x24 SVG, single color (XIOM signal blue #69B8FF), line
style matching the existing Simple Icons row (roughly 2px strokes, round
joins, filled or line consistent within a set), readable at 16px. Each
icon illustrates one capability on a project page. Deliver SVG plus a 48px
PNG preview; name files after the capability.

## Pulse -- the XIOM web backend

1. Single binary -- one hexagon holding the service.
2. HTTP/1.1 request -- arrow in and out of a bracket.
3. Sessions and JWT -- keycard with a token glyph.
4. CSRF and smuggling guard -- shield with a check over a wire.
5. Crash-safe append store -- cylinder with an appended line and a check.
6. Rate limiting -- speedometer with a stop tick.
7. Access log and audit trail -- document with numbered lines.
8. Prometheus metrics -- gauge with a small graph.
9. TLS through the proxy -- padlock behind a gateway.
10. Load soak -- waveform held flat under a clock.
11. Docker image -- container box.
12. Loopback behind the proxy -- loop arrow into a port.

## OrbitDB -- the embedded database

1. B-tree -- branching node tree.
2. Write-ahead log -- reel with appended segments.
3. Crash recovery -- restart arrow into a disk.
4. Query filter -- funnel over rows.
5. Schema and validation -- document with a check badge.
6. Pages and buffer pool -- stacked pages with a cache ring.
7. Tuple codec and CRC32C -- binary brackets with a check digit.
8. Transactions -- two arrows merging into one commit.
9. fsync durability -- disk with a pin.
10. Conformance suite -- checklist with a flask.
11. Range queries -- bracket over a number line.

## XVector -- the vector database

1. Dense vectors -- grid of arrows.
2. Distance metrics -- angle plus ruler (cosine, dot, euclidean in one mark).
3. Exact search -- magnifier over points.
4. HNSW graph -- layered network of nodes.
5. Payload filtering -- tag plus funnel.
6. WAL-backed upsert -- log line into a shield.
7. Collections and segments -- grouped boxes along a timeline.
8. Top-K results -- ranked stack with a K badge.
9. Multimodal vectors -- image, text, audio, 3D and video glyphs in a row.
10. Recall -- target with a check (the oracle the indexes are measured against).

## Benchmark of Chaos

1. Language matrix -- grid of language marks under one robot.
2. Same LLM for all -- robot writing lines of code.
3. Arenas -- four columns: systems, contracts, scripting, LLM.
4. Digest binding -- fingerprint over a container.
5. Methodology contract -- document with a seal.
6. Fairness -- balance scale over a chart.
7. Offline run -- container with an offline-cloud slash.
8. Dashboard -- console with gauges.
9. Reproducibility -- rewind arrow into a check.
10. Results -- bar chart with confidence ticks.
11. Safety focus -- shield over a bug.

Notes: avoid literal brand logos and emoji; keep metaphors abstract and
technical. One accent mark per icon; no gradients (the site is flat,
token-based). Route any icon whose meaning is unclear back through the
website lane.
