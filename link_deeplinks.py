#!/usr/bin/env python3
"""Link database books and authors inside the biographies.

Book titles become zayit://book/<id>. An author who is not the subject of the
file becomes zayit://search/<name>. Cross-references such as "מזהה 349" use the
same search link, because the app has no author route.
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

ROOT = Path("/Users/elie/seforim-author-biographies")
AUTHORS = json.loads((ROOT / "data" / "authors.json").read_text(encoding="utf-8"))
BOOKS = json.loads(Path("/tmp/seforim-books.json").read_text(encoding="utf-8"))

QUOTE_MAP = str.maketrans({
    '"': "״",
    "״": "״",
    "“": "״",
    "”": "״",
    "'": "׳",
    "׳": "׳",
    "‘": "׳",
    "’": "׳",
    "«": "",
    "»": "",
})


def norm(text: str) -> str:
    return text.translate(QUOTE_MAP)


def search_link(query: str) -> str:
    return "zayit://search/" + quote(query, safe="")


def book_link(book_id: int) -> str:
    return f"zayit://book/{book_id}"


def flex(title: str) -> str:
    parts = []
    for char in title:
        if char in '"״“”':
            parts.append('["״“”]')
        elif char in "'׳‘’":
            parts.append("['׳‘’]")
        else:
            parts.append(re.escape(char))
    return "".join(parts)


BOUNDARY = r"(?<![\u0590-\u05FFA-Za-z0-9])(?:{body})(?![\u0590-\u05FFA-Za-z0-9])"

# A single common given name, and the generic work-name used as an author row.
SKIP_AUTHOR_IDS = {133, 129}

books_by_author = defaultdict(list)
title_groups = defaultdict(list)
for row in BOOKS:
    books_by_author[row["author_id"]].append(row)
    title_groups[norm(row["title"])].append(row)

author_by_id = {author["id"]: author for author in AUTHORS}

LINK = re.compile(r"\[[^\]]*\]\([^)]*\)")
TRUNCATION = re.compile(r"^ועוד \d+")
FIRST_N = re.compile(
    r"\s*עשרים וחמש(?:ה)? (?:הראשונות|הראשונים|הכותרות הראשונות):?\s*$"
)


def url_for_title(title: str, author_id: int) -> str:
    rows = title_groups[norm(title)]
    own = [row for row in rows if row["author_id"] == author_id]
    if len(own) == 1:
        return book_link(own[0]["book_id"])
    if len(rows) == 1:
        return book_link(rows[0]["book_id"])
    return search_link(title)


TITLE_PATTERNS = sorted(
    (
        (
            key,
            len(key),
            re.compile(BOUNDARY.format(body=flex(rows[0]["title"]))),
            rows[0]["title"],
        )
        for key, rows in title_groups.items()
        if len(key) >= 2
    ),
    key=lambda item: -item[1],
)

AUTHOR_PATTERNS = sorted(
    (
        (
            author["id"],
            len(norm(author["name"])),
            re.compile(BOUNDARY.format(body=flex(author["name"]))),
            search_link(author["name"]),
        )
        for author in AUTHORS
        if author["id"] not in SKIP_AUTHOR_IDS and author["name"].strip()
    ),
    key=lambda item: -item[1],
)


def patterns_for(text: str, author_id: int):
    folded = norm(text)
    patterns = []
    for key, _length, pattern, original in TITLE_PATTERNS:
        if key in folded:
            patterns.append((pattern, url_for_title(original, author_id)))
    for other_id, _length, pattern, url in AUTHOR_PATTERNS:
        if other_id != author_id and norm(author_by_id[other_id]["name"]) in folded:
            patterns.append((pattern, url))
    return patterns


def link_plain(text: str, patterns) -> str:
    pieces = []
    cursor = 0
    for match in LINK.finditer(text):
        pieces.append(apply_patterns(text[cursor:match.start()], patterns))
        pieces.append(match.group(0))
        cursor = match.end()
    pieces.append(apply_patterns(text[cursor:], patterns))
    return "".join(pieces)


def apply_patterns(text: str, patterns) -> str:
    if not text or not patterns:
        return text
    occupied = [False] * len(text)
    replacements = []
    for pattern, url in patterns:
        for match in pattern.finditer(text):
            start, end = match.span()
            if any(occupied[start:end]):
                continue
            for index in range(start, end):
                occupied[index] = True
            label = match.group(0)
            replacements.append((start, end, f"[{label}]({url})"))
    if not replacements:
        return text
    replacements.sort()
    out = []
    cursor = 0
    for start, end, replacement in replacements:
        out.append(text[cursor:start])
        out.append(replacement)
        cursor = end
    out.append(text[cursor:])
    return "".join(out)


def link_cross_references(text: str) -> str:
    pattern = re.compile(
        r"(?<![\u0590-\u05FF])((?:[בה])?(?:מזהה|ערך|רשומה)(?: הנפרדת)?\s+)(\d{1,4})"
    )

    def replace(match):
        author_id = int(match.group(2))
        author = author_by_id.get(author_id)
        if author is None or not author["name"].strip():
            return match.group(0)
        label = match.group(1) + match.group(2)
        return f"[{label}]({search_link(author['name'])})"

    pieces = []
    cursor = 0
    for match in LINK.finditer(text):
        pieces.append(pattern.sub(replace, text[cursor:match.start()]))
        pieces.append(match.group(0))
        cursor = match.end()
    pieces.append(pattern.sub(replace, text[cursor:]))
    return "".join(pieces)


def rebuild_catalog(section: str, author_id: int) -> str:
    notes = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("- ") or stripped.startswith("#"):
            continue
        if TRUNCATION.match(stripped):
            continue
        notes.append(FIRST_N.sub("", stripped).rstrip())
    notes = [note for note in notes if note]
    rows = books_by_author.get(author_id, [])
    bullets = [
        f"- [{row['title']}]({book_link(row['book_id'])})"
        for row in rows
    ]
    parts = []
    if notes:
        parts.append("\n\n".join(notes))
    parts.append("\n".join(bullets))
    return "\n\n".join(parts) + "\n"


def process(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    author_id = int(path.stem)
    end = text.find("\n---", 3)
    front = text[: end + 4]
    body = text[end + 4 :]
    sources_at = body.find("\n## מקורות")
    if sources_at == -1:
        head, sources = body, ""
    else:
        head, sources = body[:sources_at], body[sources_at:]
    catalog_at = head.find("\n## במאגר")
    if catalog_at == -1:
        prose, catalog = head, ""
    else:
        prose, catalog = head[:catalog_at], head[catalog_at:]
    # Titles are listed before author names, so a book title wins on overlap.
    prose_patterns = patterns_for(prose, author_id)
    prose = link_plain(prose, prose_patterns)
    prose = link_cross_references(prose)
    if catalog:
        catalog_body = re.sub(r"^\n*## במאגר\n", "", catalog, count=1)
        catalog_body = link_plain(catalog_body, patterns_for(catalog_body, author_id))
        catalog_body = link_cross_references(catalog_body)
        catalog = "\n## במאגר\n" + rebuild_catalog(catalog_body, author_id)
    updated = front + prose + catalog + sources
    if not updated.endswith("\n"):
        updated += "\n"
    path.write_text(updated, encoding="utf-8")
    return {
        "id": author_id,
        "books": len(books_by_author.get(author_id, [])),
        "book_links": updated.count("zayit://book/"),
        "search_links": updated.count("zayit://search/"),
    }


def main():
    stats = [process(path) for path in sorted((ROOT / "authors").glob("*.md"))]
    print(
        f"files={len(stats)} book_links={sum(item['book_links'] for item in stats)} "
        f"search_links={sum(item['search_links'] for item in stats)}"
    )


if __name__ == "__main__":
    main()
