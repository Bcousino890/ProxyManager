"use strict";
// Gráficas SVG sin librerías. Los colores vienen de clases CSS (sin estilos en línea). solo nodos DOM.
window.PM = window.PM || {};
(function () {
  const NS = "http://www.w3.org/2000/svg";
  const live = new Set();

  function s(tag, attrs, text) {
    const n = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs || {})) n.setAttribute(k, String(v));
    if (text !== undefined) n.textContent = text;
    return n;
  }
  function niceMax(v) {
    if (v <= 0) return 1;
    const p = Math.pow(10, Math.floor(Math.log10(v))), f = v / p;
    return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 5 ? 5 : 10) * p;
  }
  function frame(container, height, label) {
    const width = Math.max(container.clientWidth || 320, 260);
    const svg = s("svg", { viewBox: "0 0 " + width + " " + height, width, height, role: "img", "aria-label": label, class: "chart" });
    return { svg, width };
  }
  function legend(items) {
    const box = document.createElement("div"); box.className = "legend";
    for (const it of items) {
      const span = document.createElement("span"); span.className = "legend-item";
      const sw = document.createElement("i"); sw.className = "swatch " + it.cls; sw.setAttribute("aria-hidden", "true");
      span.append(sw, document.createTextNode(it.name)); box.append(span);
    }
    return box;
  }
  function render(container, draw) {
    const run = () => { container.replaceChildren(); draw(); };
    run(); live.add({ container, run });
  }
  function empty(container, text) {
    const p = document.createElement("p"); p.className = "empty"; p.textContent = text; container.replaceChildren(p);
  }

  // Barras apiladas por día: series = [{name, cls, values}]
  PM.stackedBars = function (container, labels, series, opts) {
    const o = Object.assign({ height: 220, unit: "", label: "Gráfica" }, opts);
    const totals = labels.map((_, i) => series.reduce((a, sr) => a + (sr.values[i] || 0), 0));
    if (!totals.some((t) => t > 0)) { empty(container, o.empty || "Sin datos todavía."); return; }
    render(container, () => {
      const { svg, width } = frame(container, o.height, o.label + ": " + labels.map((l, i) => l + " " + totals[i]).join(", "));
      const left = 38, bottom = 24, top = 8, plotH = o.height - bottom - top, plotW = width - left - 6;
      const max = Math.ceil(niceMax(Math.max(...totals)) / 4) * 4;  // marcas enteras
      for (let g = 0; g <= 4; g++) {
        const y = top + plotH - (plotH * g) / 4;
        svg.append(s("line", { x1: left, x2: width - 4, y1: y, y2: y, class: "grid" }), s("text", { x: left - 6, y: y + 4, class: "axis-text", "text-anchor": "end" }, String(Math.round((max * g) / 4))));
      }
      const step = plotW / labels.length, bar = Math.max(Math.min(step * 0.64, 36), 3);
      labels.forEach((label, i) => {
        let y = top + plotH;
        const x = left + step * i + (step - bar) / 2;
        const group = s("g", {});
        group.append(s("title", {}, label + ": " + totals[i] + " solicitudes" + series.map((sr) => (sr.values[i] ? " · " + sr.name + " " + sr.values[i] : "")).join("")));
        for (const sr of series) {
          const v = sr.values[i] || 0; if (!v) continue;
          const h = (v / max) * plotH; y -= h;
          group.append(s("rect", { x, y, width: bar, height: Math.max(h, 1), class: sr.cls, rx: 1.5 }));
        }
        svg.append(group);
        if (labels.length <= 10 || i % Math.ceil(labels.length / 8) === 0) svg.append(s("text", { x: x + bar / 2, y: o.height - 6, class: "axis-text", "text-anchor": "middle" }, label.slice(5)));
      });
      container.append(svg, legend(series));
    });
  };

  // Líneas por día con huecos donde no hay dato: lines = [{name, cls, values}]
  PM.lines = function (container, labels, lines, opts) {
    const o = Object.assign({ height: 220, unit: " ms", label: "Gráfica" }, opts);
    const all = lines.flatMap((l) => l.values.filter((v) => v !== null && v !== undefined));
    if (!all.length) { empty(container, o.empty || "Sin datos todavía."); return; }
    render(container, () => {
      const { svg, width } = frame(container, o.height, o.label + ": " + lines.map((l) => l.name + " " + l.values.map((v, i) => (v === null || v === undefined ? "" : labels[i] + " " + Math.round(v) + o.unit)).filter(Boolean).join(", ")).join(". "));
      const left = 44, bottom = 24, top = 8, plotH = o.height - bottom - top, plotW = width - left - 10;
      const max = niceMax(Math.max(...all));
      for (let g = 0; g <= 4; g++) {
        const y = top + plotH - (plotH * g) / 4;
        svg.append(s("line", { x1: left, x2: width - 4, y1: y, y2: y, class: "grid" }), s("text", { x: left - 6, y: y + 4, class: "axis-text", "text-anchor": "end" }, String(Math.round((max * g) / 4))));
      }
      const xAt = (i) => left + (labels.length === 1 ? plotW / 2 : (plotW * i) / (labels.length - 1));
      const yAt = (v) => top + plotH - (v / max) * plotH;
      for (const ln of lines) {
        let d = "", pen = false;
        ln.values.forEach((v, i) => { if (v === null || v === undefined) { pen = false; return; } d += (pen ? "L" : "M") + xAt(i).toFixed(1) + " " + yAt(v).toFixed(1) + " "; pen = true; });
        if (d) svg.append(s("path", { d, class: "line " + ln.cls, fill: "none" }));
        ln.values.forEach((v, i) => { if (v === null || v === undefined) return; const c = s("circle", { cx: xAt(i), cy: yAt(v), r: 3, class: "dot " + ln.cls }); c.append(s("title", {}, labels[i] + " · " + ln.name + ": " + Math.round(v) + o.unit)); svg.append(c); });
      }
      labels.forEach((label, i) => { if (labels.length <= 10 || i % Math.ceil(labels.length / 8) === 0) svg.append(s("text", { x: xAt(i), y: o.height - 6, class: "axis-text", "text-anchor": "middle" }, label.slice(5))); });
      container.append(svg, legend(lines));
    });
  };

  // Barras horizontales: items = [{label, value, text}]
  PM.hbars = function (container, items, opts) {
    const o = Object.assign({ cls: "bar-ok" }, opts);
    if (!items.length) { empty(container, o.empty || "Sin datos todavía."); return; }
    const max = Math.max(...items.map((i) => i.value), 1);
    container.replaceChildren();
    for (const it of items) {
      const row = document.createElement("div"); row.className = "hrow";
      const name = document.createElement("span"); name.className = "hname"; name.textContent = it.label;
      const track = document.createElement("span"); track.className = "htrack";
      const bar = document.createElement("progress"); bar.className = "hbar"; bar.max = max; bar.value = it.value; bar.setAttribute("aria-label", it.label + ": " + it.text);
      track.append(bar);
      const val = document.createElement("span"); val.className = "hval"; val.textContent = it.text;
      row.append(name, track, val); container.append(row);
    }
  };

  let timer = 0;
  window.addEventListener("resize", () => {
    clearTimeout(timer);
    timer = setTimeout(() => { for (const c of [...live]) { if (!c.container.isConnected) live.delete(c); else c.run(); } }, 150);
  });
})();
