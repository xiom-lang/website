/*
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0

Pulse page wiring: the live demo badge and the release downloads.

The badge is same-origin (the demo serves this page), so /health and
/api/version need no CORS; it stays hidden until the demo answers, and it
never shows a version the service does not report. The downloads prefer
the dl mirror (https://dl.xiom-lang.org/pulse/latest.json) and fall back
to the GitHub release API, which is the documented source of the mirror;
when the fallback runs, the asset URLs are rewritten onto the dl mirror
paths so the buttons still point at dl even before the mirror learns to
send CORS headers. No version is ever hardcoded here. On any failure the
authored "soon" markers stay and nothing is claimed.
*/
(function () {
  "use strict";

  var DL_BASE = "https://dl.xiom-lang.org/pulse";
  var DL_URL = DL_BASE + "/latest.json";
  var GH_URL = "https://api.github.com/repos/xiom-projects/xiom-pulse/releases/latest";
  var LABELS = { "windows-x64": "Windows x64", "linux-x64": "Linux x64", "macos": "macOS" };

  function el(tag, text) {
    var node = document.createElement(tag);
    if (text) node.textContent = text;
    return node;
  }

  function loadBadge() {
    var node = document.querySelector("[data-pulse-badge]");
    if (!node) return;
    fetch("/health", { cache: "no-store" })
      .then(function (res) {
        if (!res.ok) throw new Error("health HTTP " + res.status);
        return res.json();
      })
      .then(function (data) {
        if (!data || data.status !== "ok") throw new Error("not ok");
        return fetch("/api/version", { cache: "no-store" })
          .then(function (res) { return res.ok ? res.json() : null; })
          .then(function (info) {
            var v = info && info.version ? " v" + info.version : "";
            node.textContent = "live demo" + v;
            node.hidden = false;
          });
      })
      .catch(function () {
        // Stays hidden until the demo is live.
      });
  }

  function pickAsset(assets, os) {
    var suffix = "-" + os + ".zip";
    for (var i = 0; i < assets.length; i++) {
      var name = assets[i].name || "";
      if (name.slice(-suffix.length) === suffix) return assets[i];
    }
    return null;
  }

  function pickSums(assets) {
    for (var i = 0; i < assets.length; i++) {
      if (assets[i].name === "SHA256SUMS") return assets[i];
    }
    return null;
  }

  function assetUrl(asset) {
    return asset.browser_download_url || asset.url;
  }

  function fill(version, assets, source) {
    var slots = document.querySelectorAll("[data-pulse-slot]");
    for (var i = 0; i < slots.length; i++) {
      var os = slots[i].getAttribute("data-pulse-slot");
      var match = os === "macos"
        ? (pickAsset(assets, "macos-arm64") || pickAsset(assets, "macos-x64") || pickAsset(assets, "macos"))
        : pickAsset(assets, os);
      if (!match) continue;
      slots[i].innerHTML = "";
      var a = el("a", LABELS[os] || os);
      a.className = "btn-primary";
      a.href = assetUrl(match);
      slots[i].appendChild(a);
    }

    var line = document.querySelector("[data-pulse-release]");
    if (line && version) {
      line.innerHTML = "";
      line.appendChild(document.createTextNode("Release v" + version + " -- " + source + ". "));
      var sums = pickSums(assets);
      if (sums) {
        var link = el("a", "SHA256SUMS");
        link.href = assetUrl(sums);
        link.setAttribute("style", "color:var(--signal);");
        line.appendChild(link);
      }
      line.hidden = false;
    }
  }

  function loadDownloads() {
    if (!document.querySelector("[data-pulse-downloads]")) return;
    fetch(DL_URL, { cache: "no-store" })
      .then(function (res) {
        if (!res.ok) throw new Error("dl HTTP " + res.status);
        return res.json();
      })
      .then(function (data) {
        var tag = data.tag || data.version || "";
        fill(String(tag).replace(/^pulse-v/, ""), data.assets || [], "from the mirror");
      })
      .catch(function () {
        fetch(GH_URL, {
          headers: { "Accept": "application/vnd.github+json" },
          cache: "no-store"
        })
          .then(function (res) {
            if (!res.ok) throw new Error("gh HTTP " + res.status);
            return res.json();
          })
          .then(function (data) {
            var tag = data.tag_name || "";
            var assets = (data.assets || []).map(function (a) {
              return {
                name: a.name || "",
                browser_download_url: DL_BASE + "/releases/" + tag + "/" + (a.name || "")
              };
            });
            fill(String(tag).replace(/^pulse-v/, ""), assets, "from the dl mirror (release metadata via GitHub)");
          })
          .catch(function () {
            // The authored "soon" markers stay.
          });
      });
  }

  function loadDemoState() {
    var node = document.querySelector("[data-pulse-demo-state]");
    if (!node) return;
    fetch("/health", { cache: "no-store" })
      .then(function (res) {
        if (!res.ok) throw new Error("health HTTP " + res.status);
        return res.json();
      })
      .then(function (data) {
        if (!data || data.status !== "ok") throw new Error("not ok");
        return fetch("/api/version", { cache: "no-store" })
          .then(function (res) { return res.ok ? res.json() : null; })
          .then(function (info) {
            var v = info && info.version ? " -- v" + info.version : "";
            node.textContent = "The demo service is answering" + v + "; open the page to try the endpoints.";
            node.hidden = false;
          });
      })
      .catch(function () {
        // Stays hidden until the demo answers.
      });
  }

  function load() {
    loadBadge();
    loadDemoState();
    loadDownloads();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", load);
  } else {
    load();
  }
})();
