/*
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0

Click-to-enlarge preview for diagrams and other dense images.

Add data-lightbox to a link that points at an image file: without JavaScript
the link opens the image in the current tab, and with JavaScript the image
opens in an in-page modal that closes on Escape, on the Close button, or on
a click outside the image.
*/
(function () {
  "use strict";

  var overlay = null;
  var lastFocus = null;

  function close() {
    if (!overlay) return;
    overlay.parentNode.removeChild(overlay);
    overlay = null;
    document.documentElement.classList.remove("lightbox-open");
    if (lastFocus && typeof lastFocus.focus === "function") lastFocus.focus();
  }

  function open(href, label, alt) {
    lastFocus = document.activeElement;

    overlay = document.createElement("div");
    overlay.className = "lightbox";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.setAttribute("aria-label", label || "Image preview");

    var image = document.createElement("img");
    image.className = "lightbox-img";
    image.src = href;
    image.alt = alt || "";
    overlay.appendChild(image);

    var button = document.createElement("button");
    button.type = "button";
    button.className = "lightbox-close";
    button.textContent = "Close";
    button.addEventListener("click", close);
    overlay.appendChild(button);

    overlay.addEventListener("click", function (event) {
      if (event.target === overlay) close();
    });

    document.body.appendChild(overlay);
    document.documentElement.classList.add("lightbox-open");
    button.focus();
  }

  document.addEventListener("click", function (event) {
    if (event.defaultPrevented) return;
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
    var link = event.target && event.target.closest ? event.target.closest("a[data-lightbox]") : null;
    if (!link) return;
    var image = link.querySelector("img");
    event.preventDefault();
    open(link.getAttribute("href"), link.getAttribute("aria-label"), image ? image.alt : "");
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") close();
  });
})();
