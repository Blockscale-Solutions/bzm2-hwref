#!/usr/bin/env python3
"""Check that claim tags in references/ and rows in CLAIMS.md agree.

Tags such as [BZM2-ENG-003] stay in the markdown source; the published site
strips them when it renders. This script is for contributors.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TAG = re.compile(r"\[(BZM2-[A-Z0-9]+-\d{3})\]")
ROW = re.compile(r"^\|\s*`(BZM2-[A-Z0-9]+-\d{3})`", re.M)

used = {}
for md in sorted((ROOT / "references").glob("*.md")):
    for lineno, line in enumerate(md.read_text().splitlines(), 1):
        for tag in TAG.findall(line):
            used.setdefault(tag, []).append(f"{md.name}:{lineno}")

registered = set(ROW.findall((ROOT / "CLAIMS.md").read_text()))

missing = sorted(set(used) - registered)
unused = sorted(registered - set(used))
for tag in missing:
    print(f"tag not in CLAIMS.md: {tag} ({', '.join(used[tag])})")
for tag in unused:
    print(f"CLAIMS.md row not used in references/: {tag}")
if missing or unused:
    sys.exit(1)
print(f"{len(used)} claim tags match CLAIMS.md")
