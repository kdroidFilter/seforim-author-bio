"""MkDocs hook: adapts the repo's markdown to the web site."""

import re

BOOK = re.compile(r"\[([^\]]+)\]\(zayit://book/\d+\)")
SEARCH = re.compile(r"\]\(zayit://search/([^)]+)\)")
# INDEX.md row: | name | id | books | confidence | [file](authors/file) |
ROW = re.compile(r"^\| (.+?) \| \d+ \| (\d+) \| \w+ \| \[[^\]]+\]\((authors/\d+\.md)\) \|$", re.M)
CONFIDENCE = {"high": "גבוהה", "medium": "בינונית", "low": "נמוכה"}


def on_page_markdown(markdown, page, **_):
    # zayit:// opens the desktop app: books become plain text, searches open the site search.
    root = "../" * page.url.count("/")
    markdown = BOOK.sub(r"\1", markdown)
    markdown = SEARCH.sub(lambda m: f"]({root}?q={m.group(1)})", markdown)

    if page.file.src_uri == "index.md":
        markdown = markdown.replace(
            "| שם | מזהה | ספרים | ודאות | קובץ |\n| --- | ---: | ---: | --- | --- |",
            "| שם | ספרים במאגר |\n| --- | ---: |",
        )
        markdown = ROW.sub(lambda m: f"| [{m.group(1)}]({m.group(3)}) | {m.group(2)} |", markdown)
    elif page.meta.get("confidence") in CONFIDENCE:
        # Book count and confidence right under the title.
        books = page.meta.get("db_books")
        books = "ספר אחד" if books == 1 else f"{books} ספרים"
        info = f"*{books} במאגר · ודאות {CONFIDENCE[page.meta['confidence']]}*"
        markdown = re.sub(r"^(# .+)$", lambda m: f"{m.group(1)}\n\n{info}\n", markdown, count=1, flags=re.M)
    return markdown
