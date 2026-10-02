#!/usr/bin/env python3
"""Rebuild INDEX.md from author files. Does not invent biographies."""

import json
import re
from pathlib import Path

ROOT = Path("/Users/elie/seforim-author-biographies")
AUTHORS = ROOT / "authors"
DATA = json.loads((ROOT / "data" / "authors.json").read_text(encoding="utf-8"))

HEADING = re.compile(r"^#\s+(.+)$", re.M)
CONF = re.compile(r"^confidence:\s*(\w+)\s*$", re.M)

rows = []
for author in DATA:
    aid = int(author["id"])
    path = AUTHORS / f"{aid:04d}.md"
    if not path.exists():
        rows.append((author["name"], aid, author["book_count"], None, path.name))
        continue
    text = path.read_text(encoding="utf-8")
    heading = HEADING.search(text)
    confidence = CONF.search(text)
    rows.append(
        (
            heading.group(1).strip() if heading else author["name"],
            aid,
            author["book_count"],
            confidence.group(1) if confidence else "?",
            path.name,
        )
    )

written = [r for r in rows if r[3] is not None]
missing = [r for r in rows if r[3] is None]

lines = [
    "# ביוגרפיות המחברים",
    "",
    "תיקייה זו יושבת מחוץ למאגר זית. כל קובץ הוא מחבר אחד מטבלת `author` בבסיס הנתונים של היישום.",
    "",
    f"- מחברים במאגר: {len(rows)}",
    f"- קבצים שנכתבו: {len(written)}",
    f"- חסרים: {len(missing)}",
    "",
    "| שם | מזהה | ספרים | ודאות | קובץ |",
    "| --- | ---: | ---: | --- | --- |",
]
for name, aid, books, confidence, filename in sorted(rows, key=lambda r: r[0]):
    label = confidence if confidence is not None else "חסר"
    link = f"[{filename}](authors/{filename})" if confidence is not None else filename
    safe = name.replace("|", "\\|")
    lines.append(f"| {safe} | {aid} | {books} | {label} | {link} |")

if missing:
    lines += ["", "## חסרים", ""]
    for name, aid, books, _, filename in missing:
        lines.append(f"- {aid} {name} ({books} ספרים) — `{filename}`")

(ROOT / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"written={len(written)} missing={len(missing)}")
