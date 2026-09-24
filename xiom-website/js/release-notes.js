/*
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0

XIOM release notes ("What's new").

Fetches release.json per tag from the mirror first and from the tag-pinned
raw file second, validates it against the schema in
docs/release-notes-schema.md, and renders it with textContent only. If no
valid document exists the caller shows nothing and links the changelog.
*/
window.XIOMReleaseNotes = (function () {
  "use strict";

  var MIRROR_BASE = "https://dl.xiom-lang.org";
  var RAW_BASE = "https://raw.githubusercontent.com/xiom-lang/xiom";
  var CACHE_MS = 10 * 60 * 1000;
  var MISS_MS = 60 * 1000;
  var MAX_SUMMARY = 240;
  var MAX_TITLE = 60;
  var MAX_TEXT = 320;
  var MAX_ITEM = 240;
  var MAX_HIGHLIGHTS = 6;
  var MAX_DOCS = 6;
  var KIND_LABELS = {
    language: "Language",
    compiler: "Compiler",
    stdlib: "Standard library",
    tooling: "Tooling",
    fix: "Fix",
    security: "Security"
  };

  function text(value) {
    return typeof value === "string" ? value.trim() : "";
  }

  function isTag(tag) {
    return /^v?\d+\.\d+\.\d+(?:-[0-9A-Za-z.]+)?$/.test(text(tag));
  }

  function isHttps(url) {
    return /^https:\/\/\S+$/.test(text(url));
  }

  function within(value, max) {
    var value_text = text(value);
    return value_text.length > 0 && value_text.length <= max;
  }

  function validNotes(data, tag) {
    if (!data || typeof data !== "object") return false;
    if (data.schema !== 1) return false;
    if (text(data.tag) !== text(tag)) return false;
    if (!within(data.summary, MAX_SUMMARY)) return false;
    if (!Array.isArray(data.highlights) ||
        data.highlights.length < 1 ||
        data.highlights.length > MAX_HIGHLIGHTS) return false;
    for (var i = 0; i < data.highlights.length; i++) {
      var h = data.highlights[i];
      if (!h || !within(h.title, MAX_TITLE) || !within(h.text, MAX_TEXT)) return false;
      if (!KIND_LABELS[h.kind]) return false;
    }
    if (!Array.isArray(data.breaking)) return false;
    for (var j = 0; j < data.breaking.length; j++) {
      if (!within(data.breaking[j], MAX_ITEM)) return false;
    }
    if (data.known_issues !== undefined) {
      if (!Array.isArray(data.known_issues)) return false;
      for (var k = 0; k < data.known_issues.length; k++) {
        if (!within(data.known_issues[k], MAX_ITEM)) return false;
      }
    }
    if (data.docs !== undefined) {
      if (!Array.isArray(data.docs) || data.docs.length > MAX_DOCS) return false;
      for (var d = 0; d < data.docs.length; d++) {
        var doc = data.docs[d];
        if (!doc || !within(doc.title, MAX_TITLE) || !isHttps(doc.url)) return false;
      }
    }
    if (!isHttps(data.full_changelog)) return false;
    return true;
  }

  function cacheGet(key) {
    try {
      var raw = sessionStorage.getItem(key);
      if (!raw) return null;
      var parsed = JSON.parse(raw);
      var ttl = parsed.ttl || CACHE_MS;
      if (Date.now() - parsed.at > ttl) return null;
      return { hit: true, value: parsed.value };
    } catch (e) {
      return null;
    }
  }

  function cacheSet(key, value, ttl) {
    try {
      sessionStorage.setItem(key, JSON.stringify({
        at: Date.now(),
        ttl: ttl || CACHE_MS,
        value: value
      }));
    } catch (e) { /* storage unavailable */ }
  }

  function fetchJson(url) {
    return fetch(url, { cache: "no-store" }).then(function (res) {
      if (!res.ok) throw new Error("http " + res.status);
      return res.json();
    });
  }

  function notesUrl(tag) {
    return MIRROR_BASE + "/releases/" + encodeURIComponent(tag) + "/release.json";
  }

  function rawUrl(tag) {
    return RAW_BASE + "/" + encodeURIComponent(tag) +
      "/release-notes/" + encodeURIComponent(tag) + ".json";
  }

  function fetchNotes(tag) {
    tag = text(tag);
    if (!isTag(tag)) return Promise.resolve(null);
    var key = "xiom-release-notes:" + tag;
    var cached = cacheGet(key);
    if (cached) return Promise.resolve(cached.value);
    return fetchJson(notesUrl(tag))
      .then(function (data) {
        if (!validNotes(data, tag)) throw new Error("invalid notes on mirror");
        return data;
      })
      .catch(function () {
        return fetchJson(rawUrl(tag)).then(function (data) {
          if (!validNotes(data, tag)) throw new Error("invalid notes at tag");
          return data;
        });
      })
      .then(function (data) {
        cacheSet(key, data);
        return data;
      })
      .catch(function () {
        // A missed lookup is cached briefly so a release published moments
        // later appears without a hard reload.
        cacheSet(key, null, MISS_MS);
        return null;
      });
  }

  function el(tagName, className, content) {
    var node = document.createElement(tagName);
    if (className) node.className = className;
    if (content !== undefined && content !== null) node.textContent = content;
    return node;
  }

  function externalLink(label, url) {
    var anchor = el("a", null, label);
    anchor.href = url;
    anchor.target = "_blank";
    anchor.rel = "noopener";
    return anchor;
  }

  function render(container, notes, options) {
    if (!container) return;
    options = options || {};
    container.textContent = "";
    if (!notes) return;

    container.appendChild(el("p", "rn-summary", notes.summary));

    var limit = options.limit && options.limit > 0
      ? Math.min(options.limit, notes.highlights.length)
      : notes.highlights.length;
    var list = el("ul", "rn-list");
    for (var i = 0; i < limit; i++) {
      var h = notes.highlights[i];
      var item = el("li", "rn-item");
      var head = el("div", "rn-item-head");
      head.appendChild(el("span", "rn-chip rn-chip--" + h.kind, KIND_LABELS[h.kind]));
      head.appendChild(el("strong", "rn-item-title", h.title));
      item.appendChild(head);
      item.appendChild(el("p", "rn-item-text", h.text));
      list.appendChild(item);
    }
    container.appendChild(list);

    if (notes.breaking.length) {
      var breaking = el("div", "rn-breaking");
      breaking.appendChild(el("h3", null, "Upgrade notes"));
      var breakingList = el("ul");
      for (var b = 0; b < notes.breaking.length; b++) {
        breakingList.appendChild(el("li", null, notes.breaking[b]));
      }
      breaking.appendChild(breakingList);
      container.appendChild(breaking);
    } else {
      container.appendChild(el("p", "rn-none", "No breaking changes in this release."));
    }

    if (notes.known_issues && notes.known_issues.length) {
      var issues = el("div", "rn-issues");
      issues.appendChild(el("h3", "rn-section-title", "Known issues"));
      var issuesList = el("ul");
      for (var n = 0; n < notes.known_issues.length; n++) {
        issuesList.appendChild(el("li", null, notes.known_issues[n]));
      }
      issues.appendChild(issuesList);
      container.appendChild(issues);
    }

    var links = el("p", "rn-links");
    if (notes.docs) {
      for (var d = 0; d < notes.docs.length; d++) {
        links.appendChild(externalLink(notes.docs[d].title, notes.docs[d].url));
      }
    }
    links.appendChild(externalLink("full changelog on GitHub", notes.full_changelog));
    container.appendChild(links);

    if (options.limit && notes.highlights.length > limit) {
      container.appendChild(el(
        "p",
        "rn-none",
        (notes.highlights.length - limit) + " more change" +
          (notes.highlights.length - limit === 1 ? "" : "s") +
          " in this release."
      ));
    }
  }

  return {
    fetchNotes: fetchNotes,
    render: render,
    validate: validNotes,
    isTag: isTag,
    kindLabel: function (kind) { return KIND_LABELS[kind] || ""; }
  };
})();
