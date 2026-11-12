"use strict";
// Iconos propios (trazo simple, 24x24). Se construyen con createElementNS: solo textContent y nodos DOM.
window.PM = window.PM || {};
(function () {
  const NS = "http://www.w3.org/2000/svg";
  const SHAPES = {
    overview: [["rect", { x: 3, y: 3, width: 7, height: 8, rx: 1.5 }], ["rect", { x: 14, y: 3, width: 7, height: 5, rx: 1.5 }], ["rect", { x: 14, y: 12, width: 7, height: 9, rx: 1.5 }], ["rect", { x: 3, y: 15, width: 7, height: 6, rx: 1.5 }]],
    proxies: [["rect", { x: 3, y: 4, width: 18, height: 7, rx: 2 }], ["rect", { x: 3, y: 13, width: 18, height: 7, rx: 2 }], ["path", { d: "M7 7.5h.01M7 16.5h.01" }]],
    destinations: [["circle", { cx: 12, cy: 12, r: 9 }], ["circle", { cx: 12, cy: 12, r: 5 }], ["circle", { cx: 12, cy: 12, r: 1 }]],
    sessions: [["circle", { cx: 12, cy: 12, r: 9 }], ["path", { d: "M12 7v5l3 2" }]],
    bench: [["path", { d: "M4 18a8 8 0 1 1 16 0" }], ["path", { d: "M12 18l4-6" }], ["path", { d: "M12 4v2M4.9 7.9l1.4 1.4M19.1 7.9l-1.4 1.4" }]],
    keys: [["circle", { cx: 8, cy: 15, r: 4 }], ["path", { d: "M11 12l9-9M16 7l3 3M14 9l2 2" }]],
    playground: [["rect", { x: 3, y: 4, width: 18, height: 16, rx: 2 }], ["path", { d: "M7 9l3 3-3 3M13 15h4" }]],
    usage: [["path", { d: "M4 20V10M10 20V4M16 20v-7M22 20H2" }]],
    expenses: [["circle", { cx: 12, cy: 12, r: 9 }], ["path", { d: "M14.5 9.2c-.5-.8-1.4-1.2-2.5-1.2-1.5 0-2.5.8-2.5 2s1 1.7 2.5 2 2.5.8 2.5 2-1 2-2.5 2c-1.1 0-2-.4-2.5-1.2M12 6v2M12 16v2" }]],
    audit: [["path", { d: "M12 3l8 3v6c0 4.5-3.2 8-8 9-4.8-1-8-4.5-8-9V6z" }], ["path", { d: "M9 12l2 2 4-4" }]],
    refresh: [["path", { d: "M20 11a8 8 0 0 0-14-4L4 9M4 4v5h5M4 13a8 8 0 0 0 14 4l2-2M20 20v-5h-5" }]],
    copy: [["rect", { x: 9, y: 9, width: 11, height: 11, rx: 2 }], ["path", { d: "M5 15V6a2 2 0 0 1 2-2h9" }]],
    eye: [["path", { d: "M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z" }], ["circle", { cx: 12, cy: 12, r: 3 }]],
    eyeOff: [["path", { d: "M3 3l18 18M10.6 6.1A9.7 9.7 0 0 1 12 6c6.5 0 10 6 10 6a17 17 0 0 1-3.2 4M6.5 7.6C3.7 9.4 2 12 2 12s3.5 6 10 6c1.4 0 2.7-.3 3.8-.7" }]],
    play: [["path", { d: "M7 5l12 7-12 7z" }]],
    plus: [["path", { d: "M12 5v14M5 12h14" }]],
    globe: [["circle", { cx: 12, cy: 12, r: 9 }], ["path", { d: "M3 12h18M12 3c2.5 2.7 3.8 5.7 3.8 9s-1.3 6.3-3.8 9c-2.5-2.7-3.8-5.7-3.8-9S9.500 5.700 12 3z" }]],
    check: [["path", { d: "M5 13l4 4L19 7" }]],
    trash: [["path", { d: "M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3" }]],
  };
  window.PM.icon = function (name) {
    const svg = document.createElementNS(NS, "svg");
    svg.setAttribute("viewBox", "0 0 24 24"); svg.setAttribute("aria-hidden", "true"); svg.setAttribute("focusable", "false");
    svg.setAttribute("class", "icon");
    for (const [tag, attrs] of SHAPES[name] || []) {
      const node = document.createElementNS(NS, tag);
      for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, String(v));
      svg.append(node);
    }
    return svg;
  };
})();
