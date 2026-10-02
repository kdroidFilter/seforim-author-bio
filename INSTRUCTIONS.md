# How to write one author file

You are researching rabbis and Jewish authors from a seforim database. The user asked for a biography in Hebrew, grounded in pages you actually open. Memory is not a source.

## Files

- Batch JSON: an array of `{id, name, book_count, books}`. `books` is the list of titles linked to that author in the database. Use those titles to decide which historical person this row is.
- Write `/Users/elie/seforim-author-biographies/authors/NNNN.md` where `NNNN` is the id padded to 4 digits (`165` → `0165.md`).
- If that file already exists and contains a line starting with `# `, skip it. Do not overwrite it.
- Read `/Users/elie/seforim-author-biographies/authors/0165.md` once, as the tone sample. Do not copy its facts onto other people.

## Research rules

1. For every author, run a web search that includes the database name and one distinctive book title. Then open at least one page whose text you can read (Hebrew Wikipedia, המכלול, Sefaria, אנציקלופדיה יהודית דעת, Jewish Encyclopedia, the National Library of Israel, or a library catalog). Open a second page when the person is well documented or when the first page is thin.
2. Prefer Hebrew sources. Use English sources to check dates and to separate people who share a name.
3. Disambiguate with the book list. Many rows are abbreviations (רש״י, רמב״ם, ר״ן, מהרש״א). Some rows are the same person twice (for example מלבי״ם and מאיר לייבוש מלבי״ם). Write one file per database id. If another id is the same person, say so and cite that other id. Do not merge files.
4. Every date, place, teacher, student, office, and book title in the biography must come from a page you opened in this session, or from the `books` array. If two sources disagree, say that they disagree and quote neither at length.
5. Do not invent. Do not fill gaps with the usual story of a famous rabbi if that story is not on the page you opened. If you cannot find a reliable page, write a short stub, set `confidence` to `unknown`, and list the database books. A stub is a valid result.
6. Do not paste sentences from Wikipedia, Sefaria, or any other site. Write your own Hebrew. Short titles of books are fine.
7. Do not copy long quotations. A few words of a title or a nickname are enough.
8. Write in clear modern Hebrew. Traditional honorifics (רבי, הרב) are appropriate when the sources use them. No nikud, except when the source’s spelling is otherwise ambiguous. Give the Hebrew year and the civil year when the source gives both.
9. Length: about 350–800 Hebrew words when the sources are rich; about 120–300 when they are thin; under 120 for an honest stub.
10. `confidence`: `high` if two sources agree on identity and the main dates; `medium` if one good source is enough to identify the person but details are thin or slightly conflicting; `low` if the match to the database name depends on the book list and the biography is incomplete; `unknown` if you cannot identify the person.

## File shape

```markdown
---
id: 165
name: "השם כפי שהוא במאגר"
db_books: 1
confidence: high
---

# השם כפי שהוא במאגר

## תקציר

פסקה אחת: מי זה, מתי והיכן, ועל מה הוא ידוע.

## חייו

פסקאות. רק עובדות שמצאת. אם המקורות חלוקים, אמור זאת.

## חיבורים

החיבורים שנזכרים במקורות, ובנפרד מה מצוי במאגר.

## במאגר

- ספר אחד בכל שורה. אם יש יותר מ-25 כותרות, כתוב את 25 הראשונות והוסף שורה: ועוד N כותרות במאגר.

## מקורות

- [כותרת העמוד](https://example.com) — מה נבדק שם
```

The `name` YAML value uses double quotes. Escape any double quote inside the name as `\"`.

## When you finish the batch

Reply with only this JSON object, no markdown fence:

{"written": [165], "skipped": [], "failed": []}

`written` and `skipped` are database ids. `failed` is a list of `{"id": 1, "reason": "short reason"}`.
