/*
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0

Live self-hosting progress for the roadmap page.

Reads the compiler repository's tracker (docs/SELFHOST_PROGRESS.md on main,
served by raw.githubusercontent.com with Access-Control-Allow-Origin: *) and
fills the roadmap's progress bar: the percentage inside the bar, its fill
width, the ARIA value and the "x of y gates" detail, for example
"9% -- 1 of 11 tracked gates complete." The authored text stays as the
fallback when the fetch or the parse fails, so the page never shows a
guessed number.
*/
(function () {
  "use strict";

  var TRACKER = "https://raw.githubusercontent.com/xiom-lang/xiom/main/docs/SELFHOST_PROGRESS.md";

  function fill(selector, text) {
    var nodes = document.querySelectorAll(selector);
    for (var i = 0; i < nodes.length; i++) {
      nodes[i].textContent = text;
    }
  }

  fetch(TRACKER, { cache: "no-store" })
    .then(function (res) {
      if (!res.ok) throw new Error("tracker " + res.status);
      return res.text();
    })
    .then(function (md) {
      var m = md.match(/\*\*(\d+)%[^*]*?(\d+) of (\d+) tracked gates complete\.\*\*/);
      if (!m) throw new Error("meter line not found");
      var pct = m[1];
      fill("[data-selfhost-pct]", pct + "%");
      fill("[data-selfhost-meter]", m[2] + " of " + m[3] + " gates");
      var fills = document.querySelectorAll("[data-selfhost-fill]");
      for (var i = 0; i < fills.length; i++) {
        fills[i].style.width = pct + "%";
      }
      var bars = document.querySelectorAll("[data-selfhost-bar]");
      for (var j = 0; j < bars.length; j++) {
        bars[j].setAttribute("aria-valuenow", pct);
      }
      var wraps = document.querySelectorAll("[data-selfhost-progress]");
      for (var k = 0; k < wraps.length; k++) {
        wraps[k].hidden = false;
      }
    })
    .catch(function () {
      /* the authored fallback text stands */
    });
})();
