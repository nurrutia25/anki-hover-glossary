// Hover Glossary: marks known terms in the rendered card and shows a plain-English
// definition on hover (tap/click pins it). Works on any note type because it only
// reads the drawn DOM; note fields are never touched.
//
// Onigiri safety:
//  - Marks are removed the moment Onigiri's inline edit starts (body.ba-editing),
//    so edited field HTML never contains glossary spans; re-marked after.
//  - Clicks on a term stop propagation, so Onigiri's click-to-reveal doesn't fire.
//  - The tooltip lives on <body>, outside #qa and outside every [data-ba-field].
(function () {
  if (window.HG) return;
  var DATA = window.HG_DATA || { e: [], k: {}, a: {}, n: 1 };
  var OPTS = window.HG_OPTS || {};
  var overrides = OPTS.overrides || {};
  var SKIP_TAGS = { SCRIPT: 1, STYLE: 1, A: 1, BUTTON: 1, TEXTAREA: 1, INPUT: 1, SELECT: 1,
                    CODE: 1, PRE: 1, SVG: 1, CANVAS: 1, AUDIO: 1, VIDEO: 1, RUBY: 1 };
  var WORD = /[A-Za-z0-9]+(?:['’\-][A-Za-z0-9]+)*/g;
  var tip, tipFor, showTimer, hideTimer, pinned = false, marking = false;

  function lookupPhrase(p) {
    var i = DATA.k[p];
    if (i === undefined && p.length > 4) {
      if (p.slice(-1) === "s") i = DATA.k[p.slice(0, -1)];
      if (i === undefined && p.slice(-2) === "es") i = DATA.k[p.slice(0, -2)];
    }
    return i;
  }

  function lookupAbbr(w) {
    var i = DATA.a[w];
    if (i === undefined && /[A-Z0-9]s$/.test(w)) i = DATA.a[w.slice(0, -1)];
    return i;
  }

  function skipped(el, root) {
    for (; el && el !== root; el = el.parentNode) {
      if (el.nodeType !== 1) continue;
      if (SKIP_TAGS[el.tagName.toUpperCase()]) return true;
      if (el.isContentEditable || el.classList.contains("hg-term") || el.id === "hg-tip") return true;
      if (el.getAttribute("data-hg-skip") !== null) return true;
    }
    return false;
  }

  function matchesIn(text) {
    var toks = [], m;
    WORD.lastIndex = 0;
    while ((m = WORD.exec(text))) toks.push({ w: m[0], lw: m[0].toLowerCase().replace(/’/g, "'"), s: m.index, e: m.index + m[0].length });
    var out = [];
    for (var j = 0; j < toks.length; ) {
      var hit = null;
      for (var n = Math.min(DATA.n, toks.length - j); n >= 1 && !hit; n--) {
        var phrase = toks[j].lw;
        for (var q = 1; q < n; q++) phrase += " " + toks[j + q].lw;
        var i = lookupPhrase(phrase);
        if (i !== undefined) hit = { i: i, s: toks[j].s, e: toks[j + n - 1].e, n: n };
      }
      if (!hit) {
        var ai = lookupAbbr(toks[j].w);
        if (ai !== undefined) hit = { i: ai, s: toks[j].s, e: toks[j].e, n: 1, abbr: 1 };
      }
      if (hit) { out.push(hit); j += hit.n; } else j++;
    }
    return out;
  }

  function markAll() {
    if (marking || document.body.classList.contains("ba-editing")) return;
    var root = document.getElementById("qa");
    if (!root || !DATA.e.length) return;
    var isQuestion = !root.querySelector("#answer") && !document.body.classList.contains("hg-answer");
    if (isQuestion && OPTS.question === false) return;
    marking = true;
    try {
      var seen = {};
      root.querySelectorAll(".hg-term").forEach(function (el) { seen[el.getAttribute("data-hg")] = 1; });
      var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
      var nodes = [], t;
      while ((t = walker.nextNode())) {
        if (t.nodeValue.length > 2 && /[A-Za-z]/.test(t.nodeValue) && !skipped(t.parentNode, root)) nodes.push(t);
      }
      nodes.forEach(function (node) {
        var text = node.nodeValue;
        var hits = matchesIn(text).filter(function (h) {
          if (!OPTS.everyOccurrence && seen[h.i]) return false;
          seen[h.i] = 1;
          return true;
        });
        if (!hits.length) return;
        var frag = document.createDocumentFragment(), pos = 0;
        hits.forEach(function (h) {
          if (h.s > pos) frag.appendChild(document.createTextNode(text.slice(pos, h.s)));
          var sp = document.createElement("span");
          sp.className = "hg-term";
          sp.setAttribute("data-hg", h.i);
          sp.textContent = text.slice(h.s, h.e);
          frag.appendChild(sp);
          pos = h.e;
        });
        if (pos < text.length) frag.appendChild(document.createTextNode(text.slice(pos)));
        node.parentNode.replaceChild(frag, node);
      });
    } finally {
      marking = false;
    }
  }

  function unmarkAll() {
    marking = true;
    try {
      hide(true);
      document.querySelectorAll(".hg-term").forEach(function (sp) {
        var p = sp.parentNode;
        p.replaceChild(document.createTextNode(sp.textContent), sp);
        p.normalize();
      });
    } finally {
      marking = false;
    }
  }

  function entry(i) {
    var e = DATA.e[i];
    var key = e[0];
    return { key: key, title: e[0], def: overrides[key] || e[1], abbr: e[2] || [], edited: !!overrides[key] };
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
  }

  function ensureTip() {
    if (tip) return tip;
    tip = document.createElement("div");
    tip.id = "hg-tip";
    tip.setAttribute("role", "tooltip");
    tip.addEventListener("mouseenter", function () { clearTimeout(hideTimer); });
    tip.addEventListener("mouseleave", function () { if (!pinned) hide(); });
    tip.addEventListener("click", function (ev) {
      ev.stopPropagation();
      var a = ev.target.closest("[data-hg-edit]");
      if (!a || !tipFor) return;
      var e = entry(+tipFor.getAttribute("data-hg"));
      try { pycmd("hg:edit:" + JSON.stringify({ key: e.key, title: e.title, def: e.def })); } catch (_) {}
    });
    document.body.appendChild(tip);
    return tip;
  }

  function show(el) {
    var e = entry(+el.getAttribute("data-hg"));
    var t = ensureTip();
    tipFor = el;
    var shown = el.textContent.trim();
    var head = esc(e.title);
    if (shown.toLowerCase() !== e.title.toLowerCase() && e.abbr.indexOf(shown) !== -1) head = esc(shown) + " · " + head;
    var abbr = e.abbr.filter(function (a) { return a !== shown; });
    t.innerHTML =
      '<div class="hg-title">' + head + "</div>" +
      '<div class="hg-def">' + esc(e.def) + "</div>" +
      '<div class="hg-foot">' +
      (abbr.length ? '<span class="hg-abbr">' + esc(abbr.join(", ")) + "</span>" : "<span></span>") +
      '<span class="hg-edit" data-hg-edit>' + (e.edited ? "edited · " : "") + "edit</span></div>";
    t.style.display = "block";
    var r = el.getBoundingClientRect(), tw = t.offsetWidth, th = t.offsetHeight;
    var left = Math.max(8, Math.min(r.left + r.width / 2 - tw / 2, window.innerWidth - tw - 8));
    var top = r.bottom + 6;
    if (top + th > window.innerHeight - 8 && r.top - th - 6 > 8) top = r.top - th - 6;
    // Viewport coordinates. Onigiri offsets/transforms the page, so measure where the
    // tip actually landed and correct by the difference.
    t.style.left = left + "px";
    t.style.top = top + "px";
    var got = t.getBoundingClientRect();
    if (Math.abs(got.left - left) > 1 || Math.abs(got.top - top) > 1) {
      t.style.left = left + (left - got.left) + "px";
      t.style.top = top + (top - got.top) + "px";
    }
    t.classList.add("hg-open");
  }

  function hide(now) {
    clearTimeout(showTimer);
    clearTimeout(hideTimer);
    var go = function () { if (tip) { tip.classList.remove("hg-open"); tip.style.display = "none"; } pinned = false; tipFor = null; };
    if (now === true) go(); else hideTimer = setTimeout(go, 160);
  }

  document.addEventListener("mouseover", function (ev) {
    var el = ev.target.closest && ev.target.closest(".hg-term");
    if (!el || pinned) return;
    clearTimeout(hideTimer);
    clearTimeout(showTimer);
    showTimer = setTimeout(function () { show(el); }, OPTS.hoverDelayMs || 120);
  });
  document.addEventListener("mouseout", function (ev) {
    var el = ev.target.closest && ev.target.closest(".hg-term");
    if (el && !pinned) hide();
  });
  // Capture phase so a term click never reaches #qa's click-to-reveal handler.
  document.addEventListener("click", function (ev) {
    var el = ev.target.closest && ev.target.closest(".hg-term");
    if (el) {
      ev.stopPropagation();
      if (pinned && tipFor === el) { hide(true); return; }
      show(el);
      pinned = true;
    } else if (pinned && !(tip && tip.contains(ev.target))) {
      hide(true);
    }
  }, true);
  document.addEventListener("keydown", function (ev) { if (ev.key === "Escape") hide(true); });
  window.addEventListener("scroll", function () { hide(true); }, { capture: true, passive: true });

  // Re-mark whenever #qa is redrawn (new card, answer shown, Onigiri re-render).
  var pending;
  function schedule() {
    clearTimeout(pending);
    pending = setTimeout(markAll, 30);
  }
  // Onigiri keeps touching the card DOM (progress, FX, wrappers). Only a change to the
  // card's text counts as a new card/side; anything else must not close an open tip.
  var lastText = null;
  function watch() {
  new MutationObserver(function (recs) {
    if (marking) return;
    var qa = document.getElementById("qa");
    var relevant = recs.some(function (r) {
      if (qa && qa.contains(r.target)) return true;
      return Array.prototype.some.call(r.addedNodes, function (n) { return n.nodeType === 1 && (n.id === "qa" || (n.querySelector && n.querySelector("#qa"))); });
    });
    if (!relevant || !qa) return;
    var text = qa.textContent;
    if (text === lastText && qa.querySelector(".hg-term")) return;
    lastText = text;
    hide(true);
    schedule();
  }).observe(document.body, { childList: true, subtree: true });
  new MutationObserver(function () {
    if (document.body.classList.contains("ba-editing")) unmarkAll(); else schedule();
  }).observe(document.body, { attributes: true, attributeFilter: ["class"] });
  schedule();
  }
  if (typeof onShownHook !== "undefined" && onShownHook.push) onShownHook.push(schedule);
  // Anki puts add-on scripts in <head>, before <body> exists.
  if (document.body) watch(); else document.addEventListener("DOMContentLoaded", watch);

  window.HG = {
    mark: markAll,
    unmark: unmarkAll,
    setOverride: function (key, text) {
      if (text) overrides[key] = text; else delete overrides[key];
      if (tipFor) show(tipFor);
    },
    _match: matchesIn,
  };
})();
