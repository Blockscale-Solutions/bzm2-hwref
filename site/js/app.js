/* bzm2-hwref site: catalog, search, markdown/CSV viewer */
(function () {
  var CATALOG_URL = "data/catalog.json";
  var REFS_BASE = "references/";
  var catalog = null;
  var searchIndex = null; // [{id,title,file,text,href}]
  var searchPromise = null;

  function $(sel, root) { return (root || document).querySelector(sel); }
  function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

  function slugify(text) {
    return String(text || "")
      .toLowerCase()
      .replace(/[^\w\s-]/g, "")
      .trim()
      .replace(/\s+/g, "-");
  }

  function docHref(doc, hash) {
    var h = "doc.html?doc=" + encodeURIComponent(doc.id);
    if (hash) h += "#" + hash;
    else if (doc.hash) h += "#" + doc.hash;
    return h;
  }

  function loadCatalog() {
    if (catalog) return Promise.resolve(catalog);
    return fetch(CATALOG_URL).then(function (r) {
      if (!r.ok) throw new Error("catalog " + r.status);
      return r.json();
    }).then(function (data) {
      catalog = data;
      return catalog;
    });
  }

  function findDoc(id) {
    return (catalog.docs || []).find(function (d) { return d.id === id; });
  }

  function uniqueDocs() {
    var seen = {};
    var out = [];
    (catalog.docs || []).forEach(function (d) {
      if (seen[d.file]) return;
      seen[d.file] = true;
      out.push(d);
    });
    return out;
  }

  function buildHub() {
    var grid = $("#task-grid");
    var list = $("#doc-list");
    if (!grid || !list) return;
    (catalog.tasks || []).forEach(function (t) {
      var a = document.createElement("a");
      a.className = "task-card" + (t.tone === "warm" ? " warm" : "");
      a.href = t.href;
      a.innerHTML =
        '<div class="task-id">' + t.id + "</div>" +
        "<h2>" + t.label + "</h2>" +
        "<p>" + t.blurb + "</p>";
      grid.appendChild(a);
    });
    uniqueDocs().forEach(function (d) {
      var a = document.createElement("a");
      a.className = "doc-row";
      a.href = docHref(d);
      a.innerHTML =
        '<span class="doc-title">' + d.title + "</span>" +
        '<span class="doc-file">' + d.file + "</span>";
      list.appendChild(a);
    });
  }

  function setActiveNav(taskId) {
    $$(".nav-links a[data-task]").forEach(function (a) {
      var on = a.getAttribute("data-task") === taskId;
      a.classList.toggle("active", on);
      if (on) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
  }

  function parseCsv(text) {
    var rows = [];
    var row = [];
    var cell = "";
    var i = 0;
    var inQ = false;
    while (i < text.length) {
      var c = text[i];
      if (inQ) {
        if (c === '"') {
          if (text[i + 1] === '"') { cell += '"'; i += 2; continue; }
          inQ = false; i++; continue;
        }
        cell += c; i++; continue;
      }
      if (c === '"') { inQ = true; i++; continue; }
      if (c === ",") { row.push(cell); cell = ""; i++; continue; }
      if (c === "\n" || c === "\r") {
        if (c === "\r" && text[i + 1] === "\n") i++;
        row.push(cell); rows.push(row); row = []; cell = ""; i++; continue;
      }
      cell += c; i++;
    }
    if (cell.length || row.length) { row.push(cell); rows.push(row); }
    return rows;
  }

  function csvToHtml(text) {
    var rows = parseCsv(text.trim());
    if (!rows.length) return "<p>(empty)</p>";
    var html = '<div class="csv-wrap"><table><thead><tr>';
    rows[0].forEach(function (h) {
      html += "<th>" + escapeHtml(h) + "</th>";
    });
    html += "</tr></thead><tbody>";
    for (var r = 1; r < rows.length; r++) {
      html += "<tr>";
      rows[r].forEach(function (cell) {
        html += "<td><code>" + escapeHtml(cell) + "</code></td>";
      });
      html += "</tr>";
    }
    html += "</tbody></table></div>";
    return html;
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function enhanceMarkdownHtml(root) {
    $$("h1, h2, h3", root).forEach(function (h) {
      if (!h.id) h.id = slugify(h.textContent);
    });
    // Fix relative .md links to viewer
    $$("a[href]", root).forEach(function (a) {
      var href = a.getAttribute("href") || "";
      if (/^https?:\/\//i.test(href) || href.startsWith("#") || href.startsWith("mailto:")) return;
      var m = href.match(/^([^#?]+\.(?:md|csv))(#.*)?$/i);
      if (!m) return;
      var file = m[1].split("/").pop();
      var doc = (catalog.docs || []).find(function (d) { return d.file === file; });
      if (doc) {
        a.setAttribute("href", docHref(doc) + (m[2] || ""));
      } else {
        a.setAttribute("href", REFS_BASE + file);
      }
    });
  }

  function buildToc(root, tocEl) {
    if (!tocEl) return;
    var heads = $$("h2, h3", root);
    if (!heads.length) {
      tocEl.innerHTML = '<div class="toc-label">On this page</div><p class="t-muted" style="margin:0;font-size:0.8rem">No sections</p>';
      return;
    }
    var html = '<div class="toc-label">On this page</div>';
    heads.forEach(function (h) {
      var depth = h.tagName === "H3" ? " depth-3" : "";
      html += '<a class="' + depth.trim() + '" href="#' + h.id + '">' + escapeHtml(h.textContent) + "</a>";
    });
    tocEl.innerHTML = html;
  }

  function loadDocPage() {
    var params = new URLSearchParams(location.search);
    var id = params.get("doc") || "integration";
    var doc = findDoc(id);
    var body = $("#doc-body");
    var meta = $("#doc-meta");
    var toc = $("#doc-toc");
    var titleEl = $("#doc-title");
    if (!body) return;

    if (!doc) {
      body.innerHTML = '<div class="doc-error">Unknown document id: <code>' + escapeHtml(id) + "</code></div>";
      return;
    }

    var task = (doc.tasks && doc.tasks[0]) || null;
    if (task) setActiveNav(task);

    if (titleEl) titleEl.textContent = doc.title + " · BZM2 hardware reference";
    document.title = doc.title + " · BZM2 hwref";

    if (meta) {
      meta.innerHTML =
        '<span class="chip">' + escapeHtml(doc.file) + "</span>" +
        '<a class="raw" href="' + REFS_BASE + encodeURIComponent(doc.file) + '" rel="noopener">Raw source</a>' +
        '<a class="raw" href="https://github.com/Blockscale-Solutions/bzm2-hwref/blob/main/references/' +
          encodeURIComponent(doc.file) + '" rel="noopener noreferrer">GitHub</a>';
    }

    body.innerHTML = "<p class=\"t-muted\">Loading…</p>";
    fetch(REFS_BASE + doc.file)
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.text();
      })
      .then(function (text) {
        if (doc.kind === "csv" || /\.csv$/i.test(doc.file)) {
          body.innerHTML = csvToHtml(text);
          if (toc) toc.innerHTML = '<div class="toc-label">Ball map</div><p style="margin:0;font-size:0.8rem;color:var(--muted)">CSV rendered as a table from the public pad map. No invented pin assignments.</p>';
          return;
        }
        if (typeof marked === "undefined") {
          body.innerHTML = '<pre class="prose">' + escapeHtml(text) + "</pre>";
          return;
        }
        marked.setOptions({ gfm: true, breaks: false });
        body.innerHTML = marked.parse(text);
        enhanceMarkdownHtml(body);
        buildToc(body, toc);
        if (location.hash) {
          var target = document.getElementById(location.hash.slice(1));
          if (target) target.scrollIntoView();
        } else if (doc.hash) {
          var t2 = document.getElementById(doc.hash);
          if (t2) history.replaceState(null, "", "#" + doc.hash);
        }
      })
      .catch(function (err) {
        body.innerHTML =
          '<div class="doc-error">Failed to load <code>' + escapeHtml(doc.file) +
          "</code>: " + escapeHtml(String(err.message || err)) +
          ". Ensure the Pages workflow copied <code>references/</code> into <code>site/references/</code>.</div>";
      });
  }

  function ensureSearchIndex() {
    if (searchIndex) return Promise.resolve(searchIndex);
    if (searchPromise) return searchPromise;
    searchPromise = Promise.all(
      uniqueDocs().map(function (d) {
        return fetch(REFS_BASE + d.file)
          .then(function (r) { return r.ok ? r.text() : ""; })
          .then(function (text) {
            return {
              id: d.id,
              title: d.title,
              file: d.file,
              summary: d.summary || "",
              text: text,
              href: docHref(d)
            };
          })
          .catch(function () {
            return { id: d.id, title: d.title, file: d.file, summary: d.summary || "", text: "", href: docHref(d) };
          });
      })
    ).then(function (items) {
      searchIndex = items;
      return items;
    });
    return searchPromise;
  }

  function snippet(text, q, radius) {
    var lower = text.toLowerCase();
    var idx = lower.indexOf(q);
    if (idx < 0) return text.slice(0, radius * 2).replace(/\s+/g, " ").trim();
    var start = Math.max(0, idx - radius);
    var end = Math.min(text.length, idx + q.length + radius);
    var snip = text.slice(start, end).replace(/\s+/g, " ").trim();
    if (start > 0) snip = "…" + snip;
    if (end < text.length) snip = snip + "…";
    var re = new RegExp("(" + q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "ig");
    return escapeHtml(snip).replace(re, "<mark>$1</mark>");
  }

  function runSearch(q) {
    var box = $("#search-results");
    if (!box) return;
    q = (q || "").trim().toLowerCase();
    if (q.length < 2) {
      box.classList.remove("open");
      box.innerHTML = "";
      return;
    }
    ensureSearchIndex().then(function (items) {
      var hits = [];
      items.forEach(function (it) {
        var hay = (it.title + "\n" + it.summary + "\n" + it.file + "\n" + it.text).toLowerCase();
        if (hay.indexOf(q) === -1) return;
        var score = 0;
        if (it.title.toLowerCase().indexOf(q) !== -1) score += 50;
        if (it.file.toLowerCase().indexOf(q) !== -1) score += 20;
        if (it.summary.toLowerCase().indexOf(q) !== -1) score += 10;
        score += Math.min(30, (hay.split(q).length - 1));
        hits.push({ it: it, score: score });
      });
      hits.sort(function (a, b) { return b.score - a.score; });
      hits = hits.slice(0, 12);
      if (!hits.length) {
        box.innerHTML = '<div style="padding:0.85rem 1rem;color:var(--muted);font-size:0.9rem">No matches for “' + escapeHtml(q) + '”</div>';
        box.classList.add("open");
        return;
      }
      box.innerHTML = hits.map(function (h) {
        return (
          '<a href="' + h.it.href + '">' +
            '<div class="sr-title">' + escapeHtml(h.it.title) + "</div>" +
            '<div class="sr-meta">' + escapeHtml(h.it.file) + "</div>" +
            '<div class="sr-snip">' + snippet(h.it.text || h.it.summary, q, 60) + "</div>" +
          "</a>"
        );
      }).join("");
      box.classList.add("open");
    });
  }

  function wireSearch() {
    var input = $("#site-search");
    var box = $("#search-results");
    if (!input) return;
    var t = null;
    input.addEventListener("input", function () {
      clearTimeout(t);
      t = setTimeout(function () { runSearch(input.value); }, 160);
    });
    input.addEventListener("focus", function () {
      if ((input.value || "").trim().length >= 2) runSearch(input.value);
      ensureSearchIndex();
    });
    document.addEventListener("click", function (e) {
      if (!box) return;
      if (e.target === input || box.contains(e.target)) return;
      box.classList.remove("open");
    });
    input.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        box && box.classList.remove("open");
        input.blur();
      }
    });
  }

  function init() {
    loadCatalog()
      .then(function () {
        if ($("#task-grid")) buildHub();
        if ($("#doc-body")) loadDocPage();
        wireSearch();
      })
      .catch(function (err) {
        var el = $("#task-grid") || $("#doc-body");
        if (el) el.innerHTML = '<div class="doc-error">Failed to load catalog: ' + escapeHtml(String(err.message || err)) + "</div>";
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
