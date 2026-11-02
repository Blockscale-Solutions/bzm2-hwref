#!/usr/bin/env python3
"""Check that every in-repository link and anchor resolves.

Covers the published tree (references/*.md, drawings/**.svg, site/index.html,
site/doc.html, site/data/catalog.json) and the repository front matter
(README.md, CONTRIBUTING.md, CLAIMS.md, docs/**.md).

A link to another file must name a file that exists. A link with a fragment
must name a heading in the target document, and it must resolve under BOTH
heading-id schemes a reader meets:

- the published site, whose viewer gives ids to h1-h3 only (`slugify` in
  site/js/app.js: lowercase, drop every character that is not ASCII word,
  space or hyphen, trim, collapse whitespace runs to one hyphen, no
  de-duplication);
- GitHub's renderer (lowercase, drop punctuation but keep Unicode letters and
  digits, each space becomes a hyphen with no collapsing, duplicates get -1,
  -2, ...), which readers reach through the "GitHub" link on every page.

A heading whose two ids differ, or two headings that share one site id, is
reported only when a link targets it, because only then does a reader land
in the wrong place.

External links (http, https, mailto) are not fetched. This script is for
contributors; run it from anywhere:  python3 scripts/check_links.py
"""
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent

CLAIM_TAG = re.compile(r"[ \t]*`?\[BZM2-[A-Z0-9]+-\d{3}\]`?")
FENCE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
# [text](target) and ![alt](target); target stops at whitespace or ')'.
MD_LINK = re.compile(r"!?\[(?:[^\[\]]|\[[^\]]*\])*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
HTML_REF = re.compile(r"""(?:href|src)\s*=\s*["']([^"']+)["']""")
INLINE_CODE = re.compile(r"`[^`]*`")


def heading_text(raw):
    """Plain text of a markdown heading, as a renderer would show it."""
    text = CLAIM_TAG.sub("", raw)
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.replace("`", "")
    text = re.sub(r"(\*\*|__|\*|_)(.+?)\1", r"\2", text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def site_slug(text):
    """Mirror of slugify() in site/js/app.js (JavaScript \\w is ASCII-only)."""
    s = text.lower()
    s = re.sub(r"[^A-Za-z0-9_\s-]", "", s)
    s = s.strip()
    return re.sub(r"\s+", "-", s)


def github_slug(text):
    s = text.lower()
    out = []
    for ch in s:
        cat = unicodedata.category(ch)
        if ch in "-_" or cat[0] in ("L", "N") or cat == "Mn":
            out.append(ch)
        elif ch == " ":
            out.append("-")
    return "".join(out)


def strip_code(lines):
    """Yield (lineno, line) outside fenced code blocks, with inline code removed."""
    in_fence = False
    for n, line in enumerate(lines, 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        yield n, INLINE_CODE.sub("", line)


class Doc:
    def __init__(self, path):
        self.path = path
        self.site_ids = {}     # site id -> [heading text]
        self.github_ids = {}   # github id -> heading text
        self.headings = []     # (level, text, site id, github id)
        seen = {}
        lines = path.read_text(encoding="utf-8").splitlines()
        in_fence = False
        for line in lines:
            if FENCE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = HEADING.match(line)
            if not m:
                continue
            level, text = len(m.group(1)), heading_text(m.group(2))
            gh = github_slug(text)
            if gh in seen:
                seen[gh] += 1
                gh = f"{gh}-{seen[gh]}"
            else:
                seen[gh] = 0
            sid = site_slug(text) if level <= 3 else None
            self.headings.append((level, text, sid, gh))
            self.github_ids[gh] = text
            if sid is not None:
                self.site_ids.setdefault(sid, []).append(text)

    def check_anchor(self, frag):
        """Return a problem string, or None when the fragment resolves on both renderers."""
        site_hit = frag in self.site_ids
        gh_hit = frag in self.github_ids
        if site_hit and gh_hit:
            if len(self.site_ids[frag]) > 1:
                return f"#{frag} names {len(self.site_ids[frag])} headings on the site (ids are not de-duplicated)"
            return None
        if gh_hit:
            for level, text, sid, gh in self.headings:
                if gh == frag:
                    if sid is None:
                        return f"#{frag} is an h{level} heading; the site gives ids to h1-h3 only"
                    return f"#{frag} resolves on GitHub only; the site id of '{text}' is #{sid}"
        if site_hit:
            text = self.site_ids[frag][0]
            gh = next(g for _, t, s, g in self.headings if s == frag)
            return f"#{frag} resolves on the site only; the GitHub id of '{text}' is #{gh}"
        return f"#{frag} matches no heading"


class Checker:
    def __init__(self, root):
        self.root = Path(root)
        self.docs = {}
        self.problems = []
        self.checked = 0

    def doc(self, path):
        path = path.resolve()
        if path not in self.docs:
            self.docs[path] = Doc(path)
        return self.docs[path]

    def rel(self, path):
        try:
            return path.resolve().relative_to(self.root.resolve()).as_posix()
        except ValueError:
            return str(path)

    def report(self, where, msg):
        self.problems.append(f"{where}: {msg}")

    def check_target(self, where, base_dir, target, self_path=None):
        if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
            return  # http:, https:, mailto:, data: ...
        self.checked += 1
        parts = urlsplit(target)
        path_part, frag = unquote(parts.path), unquote(parts.fragment)
        if path_part:
            dest = (base_dir / path_part)
            if not dest.exists():
                self.report(where, f"link target does not exist: {target}")
                return
        else:
            dest = self_path
        if frag and dest is not None and dest.suffix == ".md":
            problem = self.doc(dest).check_anchor(frag)
            if problem:
                self.report(where, f"{target}: {problem}")

    def check_markdown(self, path):
        lines = path.read_text(encoding="utf-8").splitlines()
        for n, line in strip_code(lines):
            for target in MD_LINK.findall(line):
                self.check_target(f"{self.rel(path)}:{n}", path.parent, target, path)
            for target in HTML_REF.findall(line):
                self.check_target(f"{self.rel(path)}:{n}", path.parent, target, path)

    def check_svg(self, path):
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for target in re.findall(r"""(?:xlink:)?href\s*=\s*["']([^"'#][^"']*)["']""", line):
                self.check_target(f"{self.rel(path)}:{n}", path.parent, target)

    def check_site_href(self, where, href, catalog):
        """A site-relative href: doc.html?doc=<id>#<frag>, a staged file, or ./."""
        if re.match(r"^[a-z][a-z0-9+.-]*:", href, re.I) or href in ("./", "#"):
            return
        self.checked += 1
        parts = urlsplit(href)
        if parts.path == "doc.html":
            ids = parse_qs(parts.query).get("doc", [])
            if not ids:
                self.report(where, f"{href}: doc.html without ?doc=")
                return
            entry = next((d for d in catalog.get("docs", []) if d.get("id") == ids[0]), None)
            if entry is None:
                self.report(where, f"{href}: no catalog doc with id '{ids[0]}'")
                return
            self.check_catalog_doc(where, entry, parts.fragment)
            return
        # Staged paths: references/ and drawings/ are copied into site/ at deploy.
        p = parts.path
        for prefix, real in (("references/", self.root / "references"), ("drawings/", self.root / "drawings")):
            if p.startswith(prefix):
                if not (real / p[len(prefix):]).exists():
                    self.report(where, f"{href}: no such file in {prefix}")
                return
        if not (self.root / "site" / p).exists():
            self.report(where, f"{href}: no such file under site/")

    def check_catalog_doc(self, where, entry, frag=None):
        f = self.root / "references" / entry.get("file", "")
        if not f.is_file():
            self.report(where, f"catalog doc '{entry.get('id')}': file references/{entry.get('file')} does not exist")
            return
        for fr in filter(None, [frag, entry.get("hash")]):
            if f.suffix == ".md":
                problem = self.doc(f).check_anchor(fr)
                if problem:
                    self.report(where, f"catalog doc '{entry.get('id')}' {problem}")

    def run(self):
        md = sorted((self.root / "references").glob("*.md"))
        md += [self.root / n for n in ("README.md", "CONTRIBUTING.md", "CLAIMS.md") if (self.root / n).exists()]
        md += sorted((self.root / "docs").rglob("*.md")) if (self.root / "docs").exists() else []
        md = [p for p in md if p.name != "bzm2-porting-conversation-log.md"]
        for p in md:
            self.check_markdown(p)
        if (self.root / "drawings").exists():
            for p in sorted((self.root / "drawings").rglob("*.svg")):
                self.check_svg(p)
        cat_path = self.root / "site" / "data" / "catalog.json"
        catalog = json.loads(cat_path.read_text(encoding="utf-8")) if cat_path.exists() else {}
        for i, entry in enumerate(catalog.get("docs", [])):
            self.check_catalog_doc(f"site/data/catalog.json docs[{i}]", entry)
        for i, task in enumerate(catalog.get("tasks", [])):
            where = f"site/data/catalog.json tasks[{i}]"
            if task.get("href"):
                self.check_site_href(where, task["href"], catalog)
            if task.get("diagram"):
                self.check_site_href(where, task["diagram"], catalog)
        task_ids = {t.get("id") for t in catalog.get("tasks", [])}
        for i, entry in enumerate(catalog.get("docs", [])):
            for t in entry.get("tasks", []):
                if t not in task_ids:
                    self.report(f"site/data/catalog.json docs[{i}]", f"task '{t}' is not a catalog task")
        for name in ("index.html", "doc.html"):
            page = self.root / "site" / name
            if not page.exists():
                continue
            for n, line in enumerate(page.read_text(encoding="utf-8").splitlines(), 1):
                for href in HTML_REF.findall(line):
                    self.check_site_href(f"site/{name}:{n}", href, catalog)
        return self.problems


def main(argv):
    root = Path(argv[1]) if len(argv) > 1 else ROOT
    checker = Checker(root)
    problems = checker.run()
    for p in problems:
        print(p)
    if checker.checked == 0:
        print("no in-repository links found: UNMEASURED")
        return 2
    if problems:
        print(f"{len(problems)} broken link(s) of {checker.checked} checked")
        return 1
    print(f"{checker.checked} in-repository links resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
