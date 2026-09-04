# oq/the-elevation-reads-five-packs-whatever-the-style-binds — every elevation is dimensioned from `opening-proportion`, `sash-light`, `facade-classical`, `brick-course` and `gibbs-ionic`, never from the style's bindings

*Status: OPEN · Raised in: WP-11.1, the precedent bench (4 Sep 2026)*

**OPEN — stated in a code comment since WP-8.3 and named by no question until now.**
`build/elevation.py:1424-1428`:

```
op_pack     = PE.resolve("opening-proportion")
sash_pack   = PE.resolve("sash-light")
facade_pack = PE.resolve("facade-classical")
brick_pack  = PE.resolve("brick-course")
gibbs_pack  = PE.resolve(GIBBS_ORDER_PACK_ID)
```

and the file's own comment at `:294-299`: *"`elevation.py` never calls `resolve_packs` or `eval_packs` --
it calls `PE.resolve(<pack>)` and picks slot dimensions straight out of the pack file. So it is blind to
bindings, to `slots`/`slots_except`, to `declined_packs`, and to the kit's `forbidden` … 40 (style, slot)
pairs over 15 styles are one of them reading a slot its resolved kit FORBIDS."* `structure.py` reads
`storey-graduation` the same way, and that pack's authority is *"current professional practice"*, with no
author, and it sets every storey height in the corpus.

**Why it is a research question and not only a generator defect.** WP-11.1 asked where deepening the bench
would change what the machine does. The answer for the elevation is: on exactly these six packs and nowhere
else. Sourcing `dutch-gambrel` or `opening-pointed` per rule changes what the corpus SAYS about a Dutch or a
Gothic house and changes nothing the elevation generator DRAWS for one, because it never reads them. Any
research budget spent on the other 51 packs to improve a drawing is spent on a reader that does not exist —
until this is fixed, or until the generator's scope gate (`:295`) is read as the honest statement that this
generator is a Palladian-sash-and-brick generator and refuses the rest.

**What must be decided.**
1. Is the elevation generator to read the style's resolved bindings (`resolve_packs`, scopes, declines,
   forbids), with the 40 forbidden reads becoming refusals? That is a behaviour change on every elevation
   drawn, and the reference-plan pins would move.
2. Or is it to be scoped honestly — an elevation is drawn only for a style whose cascade delivers those
   five packs, and COULD NOT EVALUATE for the rest?
3. Either way, the six packs' rules want per-rule sources (0 of 761 rules corpus-wide carry one; 650 carry
   an `authority_note`), starting with `storey-graduation`, the one with no author.

Not built in WP-11.1: it is a change to what is drawn, with 40 known forbidden reads behind it, and a
package of its own.
