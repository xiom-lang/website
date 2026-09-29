/*
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0

Live self-hosting progress for the roadmap page.

Reads the compiler repository's tracker (docs/SELFHOST_PROGRESS.md on main,
served by raw.githubusercontent.com with Access-Control-Allow-Origin: *) and
fills every element carrying a data-selfhost-meter attribute from its meter
line, for example "9% -- 1 of 11 tracked gates complete." The authored text
stays as the fallback when the fetch or the parse fails, so the page never
shows a guessed number.
*/
(function () {
  "use strict";

  var TRACKER = "https://raw.githubusercontent.com/xiom-lang/xiom/main/docs/SELFHOST_PROGRESS.md";

  function fill(text) {
    var nodes = document.querySelectorAll("[data-selfhost-meter]");
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
      fill(m[1] + "% (" + m[2] + " of " + m[3] + " gates)");
    })
    .catch(function () {
      /* the authored fallback text stands */
    });
})();
