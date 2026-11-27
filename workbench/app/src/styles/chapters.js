/* THE STYLES OUTLINE, AS CHAPTERS (26 Nov 2026).

   `styleTree` gives the outline as one list of rows in filing order, each with its depth: a
   tradition at 0, what is filed under it at 1, and so on down. The Styles index sets that list
   the way a book sets an index: a tradition heads a CHAPTER, each row filed directly under it
   heads a BLOCK (a family, or a style filed under the tradition itself), and every deeper row is
   read in its block.

   This says where one chapter and one block end and the next begin, and nothing else. EVERY ROW
   IT IS GIVEN COMES BACK EXACTLY ONCE, IN THE ORDER IT WAS GIVEN: a chapter's head, a block's
   head, or a row of a block. A filtered outline can begin below a tradition, or a tradition can
   hold a row deeper than 1 with no block above it; such a row heads a block of its own (and, with
   no tradition above it, a chapter with no head) so that it is still drawn and never dropped.

   Pure. `src/rooms.test.mjs` holds it. */
export function chaptersOf(rows) {
  const chapters = [];
  for (const r of Array.isArray(rows) ? rows : []) {
    if (r.depth === 0) { chapters.push({ head: r, blocks: [] }); continue; }
    if (!chapters.length) chapters.push({ head: null, blocks: [] });
    const ch = chapters[chapters.length - 1];
    if (r.depth === 1 || !ch.blocks.length) ch.blocks.push({ head: r, rows: [] });
    else ch.blocks[ch.blocks.length - 1].rows.push(r);
  }
  return chapters;
}

/* The rows of a chapter list, flattened back: what `chaptersOf` must return unchanged. */
export function rowsOf(chapters) {
  const out = [];
  for (const ch of chapters) {
    if (ch.head) out.push(ch.head);
    for (const b of ch.blocks) { out.push(b.head); out.push(...b.rows); }
  }
  return out;
}
