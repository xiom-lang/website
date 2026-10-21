/*
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0

"Served by Pulse" footer note.

The site is served through the Pulse runtime; this note only renders
after the runtime answers on this origin, and it prints the running
version read from /api/version. While the static fallback serves the
site -- or before the origin switch -- nothing is added and no claim is
made. One request per page view, hidden entirely on any failure.
*/
(function () {
  "use strict";

  function append(version) {
    var row = document.querySelector(".footer-bottom");
    if (!row) return;
    var note = document.createElement("p");
    note.setAttribute("data-served-by", "");
    note.appendChild(document.createTextNode("Served by "));
    var link = document.createElement("a");
    link.href = "https://xiom-pulse.com";
    link.style.color = "var(--signal)";
    link.textContent = "Pulse";
    note.appendChild(link);
    var ver = document.createElement("span");
    ver.className = "footer-version";
    ver.textContent = " " + version;
    note.appendChild(ver);
    row.appendChild(note);
  }

  fetch("/api/version", { cache: "no-store" })
    .then(function (res) {
      if (!res.ok) throw new Error("version " + res.status);
      return res.json();
    })
    .then(function (data) {
      if (data && typeof data.version === "string" && data.version) {
        append(data.version);
      }
    })
    .catch(function () {
      /* Static fallback or pre-switch: no note. */
    });
})();
