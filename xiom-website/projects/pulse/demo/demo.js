/*
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0

The Pulse live-demo page: each button runs one real request against the
service behind this subdomain (same-origin, so no CORS) and prints the
raw response. When the service is not reachable through the proxy yet,
every card reports exactly what it got instead of pretending.
*/
(function () {
  "use strict";

  function out(name, text) {
    var node = document.querySelector('[data-demo-out="' + name + '"]');
    if (node) node.textContent = text;
  }

  function show(name, res, body) {
    var pretty = body;
    try { pretty = JSON.stringify(JSON.parse(body), null, 2); } catch (e) { /* raw text is fine */ }
    out(name, "HTTP " + res.status + " " + res.statusText + "\n" + pretty);
  }

  function request(name, path, options) {
    out(name, "requesting " + path + " ...");
    return fetch(path, options || { cache: "no-store" })
      .then(function (res) {
        return res.text().then(function (body) { show(name, res, body); });
      })
      .catch(function (err) {
        out(name, "request failed: " + err);
      });
  }

  function statusLine() {
    var node = document.querySelector("[data-demo-status]");
    if (!node) return;
    fetch("/health", { cache: "no-store" })
      .then(function (res) {
        return res.text().then(function (body) {
          var ok = false;
          try { ok = JSON.parse(body).status === "ok"; } catch (e) { ok = false; }
          if (ok) {
            node.textContent = "The Pulse service is answering here; the cards below run against it.";
            out("health", "HTTP " + res.status + "\n" + body);
          } else {
            node.textContent = "The service is not proxied on this host yet: /health answered HTTP " + res.status + " with " + res.headers.get("content-type") + ". The cards below show exactly what each call returns.";
          }
        });
      })
      .catch(function () {
        node.textContent = "Could not reach /health from this page.";
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

  var buttons = document.querySelectorAll("[data-demo-action]");
  for (var i = 0; i < buttons.length; i++) {
    buttons[i].addEventListener("click", function (ev) {
      action(ev.currentTarget.getAttribute("data-demo-action"));
    });
  }

  statusLine();
})();
