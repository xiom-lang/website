/*
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0

Live progress meters for the roadmap page.

Each element carrying a data-progress-block attribute names a tracker in
SOURCES; the script fetches that markdown from raw.githubusercontent.com
(Access-Control-Allow-Origin: *), parses its meter line, for example

    **18% -- 2 of 11 tracked gates complete.**
    **74.9% -- 7 of 10 gates complete; gate 8 at 49.3% (partial credit).**

and drives that meter's fill width, percentage label, detail text and ARIA
value. The percentage may be fractional and the sentence may carry extra
clauses after "gates complete"; tracker lines may also wrap in the source.
A tracker may carry an optional gates line, for example

    **Gates: e2e 2338/2338, checker 195/195, lsp 45/45.**
    **Gates: corpus 950/950 release (952 full; 2 carve-outs), modules
    509/509, probes 233/233, barename 0/509.**

Each pair is matched on its leading `label x/y`, so parenthesised
annotations and trailing words are ignored, and it fills the matching
`data-gate` cell on the roadmap's Verification gates table; labels without
a cell are ignored. The authored text stays as the fallback and the meter
stays hidden until its fetch succeeds, so the page never shows a guessed
number.
*/
(function () {
  "use strict";

  var SOURCES = {
    selfhost: "https://raw.githubusercontent.com/xiom-lang/xiom/main/docs/SELFHOST_PROGRESS.md",
    stdlib: "https://raw.githubusercontent.com/xiom-lang/stdlib/main/docs/PRODUCTION_READINESS_QUEUE.md"
  };
  var METER = /\*\*(\d+(?:\.\d+)?)%[^*]*?(\d+) of (\d+) [a-z- ]*gates complete/;
  var GATES = /\*\*Gates:\s*([\s\S]*?)\*\*/;

  function setAll(selector, value) {
    var nodes = document.querySelectorAll(selector);
    for (var i = 0; i < nodes.length; i++) {
      nodes[i].textContent = value;
    }
  }

  function fill(block, pct, done, total) {
    var key = block.getAttribute("data-progress-block");
    setAll('[data-progress-pct="' + key + '"]', pct + "%");
    setAll('[data-progress-detail="' + key + '"]', done + " of " + total + " gates");
    var fills = document.querySelectorAll('[data-progress-fill="' + key + '"]');
    for (var i = 0; i < fills.length; i++) {
      fills[i].style.width = pct + "%";
    }
    var bars = document.querySelectorAll('[data-progress-bar="' + key + '"]');
    for (var j = 0; j < bars.length; j++) {
      bars[j].setAttribute("aria-valuenow", pct);
    }
    block.hidden = false;
  }

  function fillGates(raw) {
    // The block may wrap in the source; strip annotations first so a comma
    // inside them cannot split a pair, then match each pair's leading
    // "label x/y" (trailing words such as "release" are ignored).
    var pairs = raw.replace(/\([^)]*\)/g, " ").split(",");
    for (var i = 0; i < pairs.length; i++) {
      var m = pairs[i].trim().match(/^([a-z0-9-]+)\s+(\d+)\s*\/\s*(\d+)/);
      if (m) setAll('[data-gate="' + m[1] + '"]', m[2] + " / " + m[3]);
    }
  }

  function load(block) {
    var key = block.getAttribute("data-progress-block");
    var url = SOURCES[key];
    if (!url) return;
    fetch(url, { cache: "no-store" })
      .then(function (res) {
        if (!res.ok) throw new Error(key + " tracker " + res.status);
        return res.text();
      })
      .then(function (md) {
        var meter = md.match(METER);
        var gates = md.match(GATES);
        if (!meter && !gates) throw new Error(key + " no meter line");
        if (meter) fill(block, meter[1], meter[2], meter[3]);
        if (gates) fillGates(gates[1]);
      })
      .catch(function () {
        /* the authored fallback stands; the blocks stay hidden */
      });
  }

  var blocks = document.querySelectorAll("[data-progress-block]");
  for (var i = 0; i < blocks.length; i++) {
    load(blocks[i]);
  }
})();
