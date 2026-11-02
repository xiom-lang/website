/*
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0

Benchmark of Chaos -- published results renderer.

Reads bench/latest.json (the current report) and bench/manifest.json
(evidence links) at page load, so replacing those files updates the page
without a code change. Nothing is rendered when the report cannot be read.
*/
(function () {
  "use strict";

  var LANGS = {
    c: ["C", "c.svg"],
    cpp: ["C++", "cplusplus.svg"],
    rust: ["Rust", "rust.svg"],
    zig: ["Zig", "zig.svg"],
    go: ["Go", "go.svg"],
    ada: ["Ada", "ada.svg"],
    xiom: ["XIOM", "xiom.png"]
  };

  var TASKS = [
    ["t1-allocator", "t1 -- Allocator"],
    ["t2-queue", "t2 -- Queue"],
    ["t3-hot-reload", "t3 -- Hot reload"],
    ["t4-packet", "t4 -- Packet"],
    ["t5-btree", "t5 -- B-tree"]
  ];

  function e(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined && text !== null) n.textContent = text;
    return n;
  }

  function icon(key) {
    var img = e("img");
    img.src = "img/lang/" + LANGS[key][1];
    img.alt = "";
    img.width = 18;
    img.height = 18;
    img.loading = "lazy";
    return img;
  }

  function langCell(key) {
    var box = e("div", "bench-lang");
    box.appendChild(icon(key));
    box.appendChild(e("span", null, LANGS[key][0]));
    return box;
  }

  function row(key, label, pct) {
    var r = e("div", "bench-row");
    r.appendChild(langCell(key));
    var bar = e("div", "bench-bar");
    var fill = e("span");
    fill.style.width = Math.max(0, Math.min(100, pct)) + "%";
    bar.appendChild(fill);
    r.appendChild(bar);
    r.appendChild(e("div", "bench-val", label));
    return r;
  }

  function humanMs(v) {
    if (typeof v !== "number" || !isFinite(v)) return "n/a";
    return Math.round(v) + " ms";
  }

  function humanMb(v) {
    if (typeof v !== "number" || !isFinite(v)) return "n/a";
    return (Math.round(v * 10) / 10) + " MB";
  }

  function humanKb(v) {
    if (typeof v !== "number" || !isFinite(v)) return "n/a";
    return Math.round(v) + " KB";
  }

  function cards(report) {
    var host = document.getElementById("bench-summary");
    if (!host) return;
    var session = (report.sessions && report.sessions[0]) || {};
    var count = (report.samples && report.samples.languages) ? report.samples.languages.length : 0;
    var toolchain = (report.provenance && report.provenance.toolchain) ? report.provenance.toolchain.xiom : "";
    var date = (report.generatedAt || "").slice(0, 10);
    var items = [
      ["Run date", date || "n/a"],
      ["Arena", session.arena || "n/a"],
      ["Languages", String(count)],
      ["Trials", String(session.trials || "n/a")],
      ["Toolchain", toolchain || "n/a"]
    ];
    items.forEach(function (it) {
      var card = e("div", "bench-card");
      card.appendChild(e("span", null, it[0]));
      card.appendChild(e("b", null, it[1]));
      host.appendChild(card);
    });
  }

  function tasks(report) {
    var host = document.getElementById("bench-tasks");
    if (!host || !report.samples || !report.samples.byTask) return;
    var byTask = report.samples.byTask;
    var langs = report.samples.languages || [];
    TASKS.forEach(function (task) {
      var key = task[0];
      var values = [];
      langs.forEach(function (lang) {
        var cell = byTask[lang + "|" + key];
        if (!cell || !cell.metrics || !cell.metrics.duration_ms) return;
        var v = cell.metrics.duration_ms.median;
        if (typeof v === "number" && isFinite(v)) values.push([lang, v]);
      });
      if (!values.length) return;
      values.sort(function (a, b) { return a[1] - b[1]; });
      var max = values[values.length - 1][1] || 1;
      var box = e("div", "bench-task");
      box.appendChild(e("h4", null, task[1]));
      box.appendChild(e("p", "cap", "Run time per language; bar length is time, so shorter is faster."));
      values.forEach(function (v) {
        box.appendChild(row(v[0], humanMs(v[1]), (v[1] / max) * 100));
      });
      host.appendChild(box);
    });
  }

  function safety(report) {
    var host = document.getElementById("bench-safety");
    if (!host || !report.safety || !report.safety[0] || !report.safety[0].languages) return;
    var values = [];
    report.safety[0].languages.forEach(function (entry) {
      var raw = entry.raw || {};
      if (typeof raw.safety_index === "number") values.push([entry.language, raw.safety_index]);
    });
    if (!values.length) return;
    values.sort(function (a, b) { return b[1] - a[1]; });
    values.forEach(function (v) {
      host.appendChild(row(v[0], String(v[1]), v[1]));
    });
  }

  function table(report) {
    var host = document.getElementById("bench-table");
    if (!host || !report.samples || !report.samples.byLanguage) return;
    var indices = {};
    if (report.safety && report.safety[0] && report.safety[0].languages) {
      report.safety[0].languages.forEach(function (entry) {
        if (entry.raw && typeof entry.raw.safety_index === "number") indices[entry.language] = entry.raw.safety_index;
      });
    }
    var table = e("table", "bench-table");
    var thead = e("thead");
    var hr = e("tr");
    ["Language", "Pass rate", "Memory", "Binary", "t8 index"].forEach(function (h) {
      hr.appendChild(e("th", null, h));
    });
    thead.appendChild(hr);
    table.appendChild(thead);
    var tbody = e("tbody");
    (report.samples.languages || []).forEach(function (lang) {
      var b = report.samples.byLanguage[lang];
      if (!b || !b.metrics) return;
      var m = b.metrics;
      var tr = e("tr");
      var td0 = e("td");
      td0.appendChild(langCell(lang));
      tr.appendChild(td0);
      tr.appendChild(e("td", "num", (typeof m.passRate.mean === "number" ? Math.round(m.passRate.mean * 100) + "%" : "n/a")));
      tr.appendChild(e("td", "num", humanMb(m.memory_mb ? m.memory_mb.mean : null)));
      tr.appendChild(e("td", "num", humanKb(m.binary_size_kb ? m.binary_size_kb.mean : null)));
      tr.appendChild(e("td", "num", typeof indices[lang] === "number" ? String(indices[lang]) : "n/a"));
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    host.appendChild(table);
  }

  function evidence(manifest) {
    var reportLink = document.getElementById("bench-report");
    if (reportLink) reportLink.href = "bench/latest.json";
    if (!manifest) return;
    var proof = document.getElementById("bench-proof");
    if (proof && manifest.proof) {
      proof.href = "bench/" + manifest.proof;
      proof.textContent = "proof bundle";
    }
    var session = document.getElementById("bench-session");
    if (session && manifest.session) {
      session.href = "bench/" + manifest.session;
      session.textContent = "raw session";
    }
  }

  function fail() {
    var err = document.getElementById("bench-error");
    if (err) err.hidden = false;
  }

  fetch("bench/latest.json", { cache: "no-store" })
    .then(function (res) {
      if (!res.ok) throw new Error("report " + res.status);
      return res.json();
    })
    .then(function (report) {
      cards(report);
      tasks(report);
      safety(report);
      table(report);
      return fetch("bench/manifest.json", { cache: "no-store" })
        .then(function (res) { return res.ok ? res.json() : null; })
        .then(function (manifest) { evidence(manifest); })
        .catch(function () { evidence(null); });
    })
    .catch(fail);
})();
