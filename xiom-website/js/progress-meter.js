/*
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0

Live progress meters for the roadmap page.

Each element carrying a data-progress-block attribute names a tracker in
SOURCES; the script fetches that markdown from raw.githubusercontent.com
(Access-Control-Allow-Origin: *), parses its single meter line, for example

    **18% -- 2 of 11 tracked gates complete.**
    **40% -- 4 of 10 readiness gates complete.**

and drives that meter's fill width, percentage label, detail text and ARIA
value. A tracker may also carry an optional gates line, for example

    **Gates: e2e 2338/2338, checker 195/195, lsp 45/45.**
    **Gates: corpus 951/951, modules 509/509.**

Each `label x/y` pair fills the matching `data-gate` cell on the roadmap's
Verification gates table; labels without a cell are ignored. The authored
text stays as the fallback and the meter stays hidden until its fetch
succeeds, so the page never shows a guessed number.
*/
(function () {
  "use strict";

  var SOURCES = {
    selfhost: "https://raw.githubusercontent.com/xiom-lang/xiom/main/docs/SELFHOST_PROGRESS.md",
    stdlib: "https://raw.githubusercontent.com/xiom-lang/stdlib/main/docs/PRODUCTION_READINESS_QUEUE.md"
  };
  var METER = /\*\*(\d+)%[^*]*?(\d+) of (\d+) [a-z- ]*gates complete\.\*\*/;
  var GATES = /\*\*Gates:\s*([^.\n]+)\.\*\*/;

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

  function fillGates(text) {
    var pairs = text.split(",");
    for (var i = 0; i < pairs.length; i++) {
      // Tolerate annotations such as "e2e 2395/2395 (+4 ignored)".
      var pair = pairs[i].replace(/\([^)]*\)/g, "").trim();
      var m = pair.match(/^([a-z0-9-]+)\s+(\d+)\s*\/\s*(\d+)$/);
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
