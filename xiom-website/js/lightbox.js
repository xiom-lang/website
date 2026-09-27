/*
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0

Click-to-enlarge preview with zoom and pan.

Add data-lightbox to a link that points at an image file: without JavaScript
the link opens the image in the current tab. With JavaScript the image opens
in an in-page modal with wheel/trackpad zoom, drag to pan, pinch on touch
screens, a zoom toolbar, and Escape / click-outside / Close to dismiss.
*/
(function () {
  "use strict";

  var MIN_SCALE = 1;
  var MAX_SCALE = 8;
  var ZOOM_STEP = 1.4;

  var overlay = null;
  var stage = null;
  var image = null;
  var levelLabel = null;
  var scale = 1;
  var tx = 0;
  var ty = 0;
  var lastFocus = null;
  var dragging = false;
  var dragStart = null;
  var pointers = {};
  var pinchStart = null;

  function clamp(value, lo, hi) {
    return value < lo ? lo : value > hi ? hi : value;
  }

  function apply() {
    image.style.transform = "translate(" + tx + "px, " + ty + "px) scale(" + scale + ")";
    if (levelLabel) levelLabel.textContent = Math.round(scale * 100) + "%";
    if (stage) {
      if (scale > 1) stage.classList.add("is-zoomed");
      else stage.classList.remove("is-zoomed");
    }
  }

  function maxPan() {
    var sw = stage.clientWidth;
    var sh = stage.clientHeight;
    var w = image.clientWidth * scale;
    var h = image.clientHeight * scale;
    return {
      x: Math.max(0, (w - sw) / 2) + (w <= sw ? 40 : 0),
      y: Math.max(0, (h - sh) / 2) + (h <= sh ? 40 : 0)
    };
  }

  function clampPan() {
    var m = maxPan();
    tx = clamp(tx, -m.x, m.x);
    ty = clamp(ty, -m.y, m.y);
  }

  function zoomTo(next, clientX, clientY) {
    var prev = scale;
    next = clamp(next, MIN_SCALE, MAX_SCALE);
    var rect = stage.getBoundingClientRect();
    var cx = clientX == null ? rect.left + rect.width / 2 : clientX;
    var cy = clientY == null ? rect.top + rect.height / 2 : clientY;
    var ux = cx - (rect.left + rect.width / 2);
    var uy = cy - (rect.top + rect.height / 2);
    tx = ux - (next / prev) * (ux - tx);
    ty = uy - (next / prev) * (uy - ty);
    scale = next;
    clampPan();
    apply();
  }

  function reset() {
    scale = 1;
    tx = 0;
    ty = 0;
    apply();
  }

  function close() {
    if (!overlay) return;
    overlay.parentNode.removeChild(overlay);
    overlay = null;
    stage = null;
    image = null;
    levelLabel = null;
    pointers = {};
    dragging = false;
    pinchStart = null;
    document.documentElement.classList.remove("lightbox-open");
    if (lastFocus && typeof lastFocus.focus === "function") lastFocus.focus();
  }

  function onWheel(event) {
    event.preventDefault();
    zoomTo(scale * Math.exp(-event.deltaY * 0.0022), event.clientX, event.clientY);
  }

  function onPointerDown(event) {
    if (event.pointerType === "mouse" && event.button !== 0) return;
    pointers[event.pointerId] = { x: event.clientX, y: event.clientY };
    var ids = Object.keys(pointers);
    if (ids.length === 1) {
      dragging = true;
      dragStart = { x: event.clientX - tx, y: event.clientY - ty };
      if (image.setPointerCapture) {
        try { image.setPointerCapture(event.pointerId); } catch (e) { /* synthetic or released */ }
      }
      image.classList.add("is-dragging");
    } else if (ids.length === 2) {
      dragging = false;
      var a = pointers[ids[0]];
      var b = pointers[ids[1]];
      pinchStart = {
        dist: Math.hypot(a.x - b.x, a.y - b.y),
        scale: scale,
        tx: tx,
        ty: ty,
        cx: (a.x + b.x) / 2,
        cy: (a.y + b.y) / 2
      };
    }
  }

  function onPointerMove(event) {
    if (!pointers[event.pointerId]) return;
    pointers[event.pointerId] = { x: event.clientX, y: event.clientY };
    var ids = Object.keys(pointers);
    if (ids.length >= 2 && pinchStart) {
      var a = pointers[ids[0]];
      var b = pointers[ids[1]];
      var dist = Math.hypot(a.x - b.x, a.y - b.y);
      if (pinchStart.dist > 0) {
        var next = clamp(pinchStart.scale * (dist / pinchStart.dist), MIN_SCALE, MAX_SCALE);
        var rect = stage.getBoundingClientRect();
        var ux = pinchStart.cx - (rect.left + rect.width / 2);
        var uy = pinchStart.cy - (rect.top + rect.height / 2);
        tx = ux - (next / pinchStart.scale) * (ux - pinchStart.tx);
        ty = uy - (next / pinchStart.scale) * (uy - pinchStart.ty);
        scale = next;
        clampPan();
        apply();
      }
      return;
    }
    if (dragging && dragStart) {
      tx = event.clientX - dragStart.x;
      ty = event.clientY - dragStart.y;
      clampPan();
      apply();
    }
  }

  function onPointerUp(event) {
    delete pointers[event.pointerId];
    var ids = Object.keys(pointers);
    if (ids.length < 2) pinchStart = null;
    if (ids.length === 0) {
      dragging = false;
      image.classList.remove("is-dragging");
    } else if (ids.length === 1) {
      dragging = true;
      dragStart = { x: pointers[ids[0]].x - tx, y: pointers[ids[0]].y - ty };
    }
  }

  function makeTool(label, ariaLabel, onClick) {
    var button = document.createElement("button");
    button.type = "button";
    button.className = "lightbox-tool";
    button.textContent = label;
    button.setAttribute("aria-label", ariaLabel);
    button.addEventListener("click", onClick);
    return button;
  }

  function open(href, label, alt) {
    lastFocus = document.activeElement;

    overlay = document.createElement("div");
    overlay.className = "lightbox";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.setAttribute("aria-label", label || "Image preview");

    stage = document.createElement("div");
    stage.className = "lightbox-stage";
    stage.addEventListener("click", function (event) {
      if (event.target === stage) close();
    });

    image = document.createElement("img");
    image.className = "lightbox-img";
    image.src = href;
    image.alt = alt || "";
    image.draggable = false;
    image.addEventListener("wheel", onWheel, { passive: false });
    image.addEventListener("pointerdown", onPointerDown);
    image.addEventListener("pointermove", onPointerMove);
    image.addEventListener("pointerup", onPointerUp);
    image.addEventListener("pointercancel", onPointerUp);
    image.addEventListener("dblclick", function (event) {
      event.preventDefault();
      zoomTo(scale > 1 ? 1 : 2.5, event.clientX, event.clientY);
    });
    stage.appendChild(image);

    var tools = document.createElement("div");
    tools.className = "lightbox-tools";
    tools.appendChild(makeTool("-", "Zoom out", function () { zoomTo(scale / ZOOM_STEP); }));
    levelLabel = document.createElement("span");
    levelLabel.className = "lightbox-level";
    levelLabel.textContent = "100%";
    tools.appendChild(levelLabel);
    tools.appendChild(makeTool("+", "Zoom in", function () { zoomTo(scale * ZOOM_STEP); }));
    tools.appendChild(makeTool("Reset", "Reset zoom and pan", reset));
    overlay.appendChild(tools);

    var closeButton = document.createElement("button");
    closeButton.type = "button";
    closeButton.className = "lightbox-close";
    closeButton.textContent = "Close";
    closeButton.addEventListener("click", close);
    overlay.appendChild(closeButton);

    overlay.appendChild(stage);
    document.body.appendChild(overlay);
    document.documentElement.classList.add("lightbox-open");
    scale = 1;
    tx = 0;
    ty = 0;
    apply();
    closeButton.focus();
  }

  document.addEventListener("click", function (event) {
    if (event.defaultPrevented) return;
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
    var link = event.target && event.target.closest ? event.target.closest("a[data-lightbox]") : null;
    if (!link || overlay) return;
    var img = link.querySelector("img");
    event.preventDefault();
    open(link.getAttribute("href"), link.getAttribute("aria-label"), img ? img.alt : "");
  });

  document.addEventListener("keydown", function (event) {
    if (!overlay) return;
    if (event.key === "Escape") {
      close();
    } else if (event.key === "+" || event.key === "=") {
      event.preventDefault();
      zoomTo(scale * ZOOM_STEP);
    } else if (event.key === "-" || event.key === "_") {
      event.preventDefault();
      zoomTo(scale / ZOOM_STEP);
    } else if (event.key === "0") {
      event.preventDefault();
      reset();
    }
  });
})();
