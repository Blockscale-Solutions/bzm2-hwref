#!/usr/bin/env python3
"""Tests for check_links.py.  Run:  python3 -B -m unittest discover -s scripts -p '*_test.py'"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_links  # noqa: E402


def tree(files):
    d = tempfile.TemporaryDirectory()
    root = Path(d.name)
    for rel, text in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return d, root


def run(files):
    d, root = tree(files)
    with d:
        c = check_links.Checker(root)
        return c.run(), c.checked


class Slugs(unittest.TestCase):
    def test_site_slug_matches_app_js(self):
        # app.js: lowercase, drop non-[\w\s-], trim, collapse whitespace to one hyphen
        self.assertEqual(check_links.site_slug("Rail / stack topology (single ASIC)"),
                         "rail-stack-topology-single-asic")
        self.assertEqual(check_links.site_slug("25 levels × 4"), "25-levels-4")

    def test_github_slug_keeps_one_hyphen_per_space(self):
        self.assertEqual(check_links.github_slug("Rail / stack topology (single ASIC)"),
                         "rail--stack-topology-single-asic")

    def test_heading_text_strips_code_and_claim_tags(self):
        self.assertEqual(check_links.heading_text("The `NOOP` reply `[BZM2-ENG-003]`"), "The NOOP reply")


class Links(unittest.TestCase):
    def test_good_link_and_anchor_pass(self):
        problems, checked = run({
            "references/a.md": "# A\n\nSee [b](b.md#second-part) and [top](#a).\n",
            "references/b.md": "# B\n\n## Second part\n",
        })
        self.assertEqual(problems, [])
        self.assertEqual(checked, 2)

    def test_missing_file_fails(self):
        problems, _ = run({"references/a.md": "[x](missing.md)\n"})
        self.assertEqual(len(problems), 1)
        self.assertIn("does not exist", problems[0])

    def test_missing_anchor_fails(self):
        problems, _ = run({
            "references/a.md": "[x](b.md#nowhere)\n",
            "references/b.md": "## Somewhere\n",
        })
        self.assertEqual(len(problems), 1)
        self.assertIn("matches no heading", problems[0])

    def test_anchor_that_only_github_resolves_fails(self):
        problems, _ = run({
            "references/a.md": "[x](b.md#rail--stack)\n",
            "references/b.md": "## Rail / stack\n",
        })
        self.assertEqual(len(problems), 1)
        self.assertIn("GitHub only", problems[0])

    def test_h4_anchor_fails_on_site(self):
        problems, _ = run({
            "references/a.md": "[x](#deep)\n\n#### Deep\n",
        })
        self.assertEqual(len(problems), 1)
        self.assertIn("h1-h3 only", problems[0])

    def test_duplicate_site_id_fails_when_linked(self):
        problems, _ = run({
            "references/a.md": "[x](#notes)\n\n## Notes\n\n## Notes\n",
        })
        self.assertEqual(len(problems), 1)
        self.assertIn("2 headings", problems[0])

    def test_links_in_code_are_ignored(self):
        problems, checked = run({
            "references/a.md": "```\n[x](missing.md)\n```\n\n`[y](missing.md)`\n\n[z](a.md)\n",
        })
        self.assertEqual(problems, [])
        self.assertEqual(checked, 1)

    def test_catalog_hash_and_task_href_are_checked(self):
        cat = {
            "docs": [{"id": "a", "file": "a.md", "tasks": ["t"], "hash": "missing"}],
            "tasks": [{"id": "t", "href": "doc.html?doc=a#also-missing", "diagram": "drawings/none.svg"}],
        }
        problems, _ = run({
            "references/a.md": "# A\n",
            "site/data/catalog.json": json.dumps(cat),
        })
        joined = "\n".join(problems)
        self.assertIn("#missing matches no heading", joined)
        self.assertIn("#also-missing matches no heading", joined)
        self.assertIn("drawings/none.svg", joined)

    def test_site_page_unknown_doc_id_fails(self):
        problems, _ = run({
            "references/a.md": "# A\n",
            "site/data/catalog.json": json.dumps({"docs": [{"id": "a", "file": "a.md"}], "tasks": []}),
            "site/index.html": '<a href="doc.html?doc=zzz">x</a>\n',
        })
        self.assertEqual(len(problems), 1)
        self.assertIn("no catalog doc with id 'zzz'", problems[0])

    def test_no_links_is_unmeasured_not_pass(self):
        d, root = tree({"references/a.md": "# nothing linked\n"})
        with d:
            self.assertEqual(check_links.main(["check_links.py", str(root)]), 2)

    def test_repository_links_resolve(self):
        c = check_links.Checker(check_links.ROOT)
        problems = c.run()
        self.assertEqual(problems, [], "\n".join(problems))
        self.assertGreater(c.checked, 0)


if __name__ == "__main__":
    unittest.main()
