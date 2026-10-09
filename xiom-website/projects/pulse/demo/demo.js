/*
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0

The Pulse live-demo page: each button runs one real request against the
service behind this subdomain (same-origin, so no CORS) and prints the
raw response with its status and timing. Health and version run once on
load so the page never starts empty. When the service is not reachable
through the proxy, every console says exactly what it got instead of
pretending; buttons disable while their request is in flight.
*/
(function () {
  "use strict";

  function out(name, text) {
    var node = document.querySelector('[data-demo-out="' + name + '"]');
    if (node) node.textContent = text;
  }

  function show(name, res, body, ms) {
    var pretty = body;
    try { pretty = JSON.stringify(JSON.parse(body), null, 2); } catch (e) { /* raw text is fine */ }
    var statusText = res.statusText ? " " + res.statusText : "";
    out(name, "HTTP " + res.status + statusText + " (" + ms + " ms)\n" + pretty);
  }

  function request(name, path, options) {
    var started = Date.now();
    out(name, "requesting " + path + " ...");
    return fetch(path, options || { cache: "no-store" })
      .then(function (res) {
        return res.text().then(function (body) {
          show(name, res, body, Date.now() - started);
        });
      })
      .catch(function (err) {
        out(name, "request failed: " + err);
      });
  }

  function action(name) {
    if (name === "health") return request("health", "/health");
    if (name === "version") return request("version", "/api/version");
    if (name === "echo") {
      var input = document.querySelector('[data-demo-input="echo"]');
      return request("echo", "/api/echo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input ? input.value : "" }),
        cache: "no-store"
      });
    }
    if (name === "append") {
      var note = document.querySelector('[data-demo-input="events"]');
      return request("events", "/api/events", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ kind: "note", msg: note ? note.value : "" }),
        cache: "no-store"
      });
    }
    if (name === "list") return request("events", "/api/events?limit=10");
    if (name === "count") return request("events", "/api/events/count");
  }

  function statusLine() {
    var status = document.querySelector("[data-demo-status]");
    var text = document.querySelector("[data-demo-status-text]");
    if (!status || !text) return;
    fetch("/health", { cache: "no-store" })
      .then(function (res) {
        return res.text().then(function (body) {
          var ok = false;
          try { ok = JSON.parse(body).status === "ok"; } catch (e) { ok = false; }
          if (!ok) {
            text.textContent = "The service is not proxied on this host yet: /health answered HTTP " +
              res.status + " (" + (res.headers.get("content-type") || "unknown type") +
              "). The consoles below show exactly what each call returns.";
            return;
          }
          status.className = "demo-status is-live";
          fetch("/api/version", { cache: "no-store" })
            .then(function (r) { return r.ok ? r.json() : null; })
            .then(function (info) {
              var v = info && info.version ? " -- v" + info.version : "";
              var b = info && info.build ? ", build " + info.build : "";
              text.textContent = "The service is answering" + v + b + ".";
            })
            .catch(function () {
              text.textContent = "The service is answering.";
            });
        });
      })
      .catch(function () {
        text.textContent = "Could not reach /health from this page.";
      });
  }

  var buttons = document.querySelectorAll("[data-demo-action]");
  for (var i = 0; i < buttons.length; i++) {
    buttons[i].addEventListener("click", function (ev) {
      var btn = ev.currentTarget;
      btn.disabled = true;
      action(btn.getAttribute("data-demo-action")).then(function () {
        btn.disabled = false;
      });
    });
  }

  statusLine();
  action("health");
  action("version");
})();
