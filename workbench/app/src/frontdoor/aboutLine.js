/* THE ONE SENTENCE A STRANGER MAY READ, OR NOTHING (WP-14.14, PRD §C.3; ruled 24 Sep 2026).

   The Gate stands in front of a private corpus and used to say nothing about what it guards.
   Lucas ruled that it says ONE sentence: exactly `GET /api/glossary/about-tdl` is ungated
   (`auth.OPEN_PATHS`), and the Gate shows that record's `definition` and nothing else. Every other
   glossary path, and every other corpus route, answers 401 to a signed-out visitor, and the Gate
   asks none of them.

   IF THE READ FAILS, THE GATE SAYS NOTHING. Not an error, not "could not load", and above all not a
   sentence of its own in place of the record's: the app writes no definitions, and a fallback line
   typed here would be a definition the glossary's checker never reads, shown to exactly the person
   least able to tell. A password screen with no description is what the Gate was for years; that
   is the honest failure. So every way this can go wrong — a rejected request, a body of the wrong
   shape, a record with no definition — answers `null`, and `Gate.jsx` draws the sentence only
   where there is one.

   Pure: the request is handed in, so `src/frontDoor.test.mjs` drives every branch without a
   server, and a source guard there holds `Gate.jsx` to drawing this function's answer and nothing
   else. */

/* A §C.2 body → the record's definition, or null. */
export function lineOf(body) {
  const term = body && typeof body === 'object' && body.term && typeof body.term === 'object'
    ? body.term : null;
  const d = term && typeof term.definition === 'string' ? term.definition.trim() : '';
  return d || null;
}

/* request() → a promise of the §C.2 body. Resolves to the definition or null; never rejects. */
export async function aboutLine(request) {
  try {
    return lineOf(await request());
  } catch {
    return null;
  }
}
