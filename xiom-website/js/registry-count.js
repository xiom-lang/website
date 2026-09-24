/*
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0

Live official-package count for the roadmap and ecosystem pages.

Reads the public registry index (registry.xiom-lang.org/index.json, served
with Access-Control-Allow-Origin: *) and fills every element that carries a
data-registry-count attribute. The text authored inside those elements stays
as the fallback when the request fails, so the pages never show a guessed
number. The count is installable packages: entries whose latest version is
not yanked.
*/
(function () {
  "use strict";

  var INDEX = "https://registry.xiom-lang.org/index.json";

  function fill(count) {
    var nodes = document.querySelectorAll("[data-registry-count]");
    for (var i = 0; i < nodes.length; i++) {
      nodes[i].textContent = String(count);
    }
  }

  fetch(INDEX, { cache: "no-store" })
    .then(function (res) {
      if (!res.ok) throw new Error("registry index " + res.status);
      return res.json();
    })
    .then(function (data) {
      var packages = data.packages || {};
      var names = Object.keys(packages);
      var installable = 0;
      for (var i = 0; i < names.length; i++) {
        var entry = packages[names[i]];
        if (entry && entry.latest) installable += 1;
      }
      fill(installable);
    })
    .catch(function () {
      /* The authored fallback text stands. */
    });
})();
