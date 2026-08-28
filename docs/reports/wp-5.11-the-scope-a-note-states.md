# WP-5.11 — the scope a note states and the data does not carry

*28 August 2026. Closes OQ 88 and OQ 89, the two things WP-5.10's adversarial audit deferred
rather than patch in an audit pass. Both were named so they would be counted; this is the count
being paid.*

**On the work-package number:** OQ 90 is open and unruled and there are already two WP-5.7s. Cite
this report by filename, never by its number.

---

## 1. The headline: a fault was clearing houses on shutters that were not there

`shutter-on-an-unshutterable-opening` returned **CLEAR, value 1.0, `passes: true`** on
`tidewater-georgian` — the strongest statement this corpus can make about a house — built entirely
out of two numbers nobody measured. `elevation.py` published:

```python
"total_shutter_leaves": 2.0, "shutter_leaves_with_a_leaf_width_of_clear_hinge_side_wall": 2.0,
```

unconditionally, so the primary test read 2/2 = 1.0 on a style whose kit makes `none` **canonical**
and whose every window record already carried `shutters_carried: False` with its leaf dimensions
dropped for exactly that reason.

**The fact had been computed five hundred lines away since WP-5.9 and was never consulted.** That
is the whole defect, and it is worth naming precisely because it sits outside the guard built to
catch its own class: OQ 52's `NOT_MODELLED` test polices measurements that are **withheld**, and
nothing here was withheld — something was **invented**, in `_derive_measurements`, in the middle of
measurements that are real.

The counts are conditional now, in the three states this corpus keeps returning to:

| kit says | published | why |
|---|---|---|
| carries shutters | `2.0` / `2.0` | the real pair, both clearing on a computed `pier_width_in` |
| makes `none` canonical | **`0.0`** | a measured zero. The house has none; that is a fact about it |
| says nothing | **absent** | could-not-evaluate is not zero and is not two |

The middle row is the one that matters, and choosing it over withholding was deliberate: refusing
to state a quantity the record knows is the opposite error, and the same reasoning the WP-5.10
audit used to leave `dormer-wall` alone.

**Measured, before and after, across every style that composes an elevation:**

| | styles composing | fault clear | not-applicable |
|---|---|---|---|
| before | 41 | **41** | 0 |
| after | 41 | 40 | **1** |

One style in the corpus is affected today, and it is the right one. The other 40 genuinely carry
shutters and are still judged on a real evaluated 2/2 — a guard that silenced the fault everywhere
would have looked identical on the first two rows and is asserted against separately.

## 2. The zero armed a division that was listed as "not live today"

OQ 89's own closing paragraph counted unguarded `bounds_test` entries that divide by a count and
said *"None is live today."* Supplying `window_head_radius_in` made one of them live in the same
change that supplied it.

`shutter-on-an-unshutterable-opening` carries the expression `shutter_head_radius_in /
window_head_radius_in` in **two** places. The copy in `secondary_tests` gained an `applies_when` in
WP-5.10. The copy in `exceptions[0].bounds_test` — which `check_measurements` **substitutes for the
primary** on a matching style — did not. With the radius supplied as a measured 0 on a straight
head, the unguarded copy returned:

```
{'status': 'error', 'detail': 'float division by zero'}
```

Proved before it was guarded, and guarded in the same commit. This is the WP-5.9 lesson (*the
moment a record can state a zero, every rule that presupposed the thing runs on it*) and the
WP-5.10 audit's Second Empire finding (*a fault's tests live in three places and the third is the
one that bites*) arriving together, in the package that was written knowing both.

**What the radius is, and what it is not.** `_head_radius_in()` computes it from figures the record
already states — a circular segment's radius follows from rise and span exactly, `R = r/2 +
s²/(8r)` — so this is geometry off stated numbers, not a new measurement. Three states again:

- **curved** — a segmental arch with a definite rise. The real radius.
- **straight** — `0`. A square wood head, and *also a gauged flat arch*, on brick-course's own
  words: its camber exists so that when the wall settles the head **"reads level"**, and is
  **"invisible on paper and unmistakable on the building."** A jack arch is drawn straight and
  shuttered square. Reporting its 463 in camber radius as a curved head would convict houses of a
  crescent nobody can see. The corpus decided this, not the author.
- **unknown** — `None`. The kit permits more than one masonry head and the plan states no date, or
  the rise is a **band**. A band does not become a figure by being halved.

`shutter_head_radius_in` stays **absent**, and moved from a source comment into `NOT_MODELLED`
where the honesty test can see it. Nothing in this corpus says whether a shutter leaf follows a
curved head or stands square against it — which is precisely the question the fault asks, so
deriving it from the window would hand the fault its own conclusion.

## 3. `brick-front-vinyl-return`: the argument was right, the mechanism was wrong

Two measurements were withheld by a comment reasoning, correctly, that both are `at-least`
secondaries gating a legitimate material change at a real second volume, so supplying 0 would fail
them for the honest reason that no change exists. Right conclusion, no enforcement: a comment is
not a guard, `NOT_MODELLED` had no purchase because nothing was unmodelled, and a reader could not
tell a deliberate silence from an oversight.

The record now states `count_of_material_changes_on_the_elevation` as a **measured 0** and
`count_of_volumes_on_the_elevation` as 1, and both secondaries are preconditioned on the count.
"Withheld, see comment" becomes "not applicable, and here is the measurement that says so".

## 4. OQ 88: one scope field, and the thirteen styles that cannot be decided

Three rules state their own scope in prose and carried none in data. `sash-light`'s window sill
says, in as many words, *"In a frame wall this is a real sill member; in a masonry wall it is a
rowlock or a stone and belongs to the brick-course pack, **not this one**."*

**The corpus already had the mechanism and it needed a sibling, not a replacement.**
`calibrated_for` is a per-rule scope honoured in `proportion_engine.out_of_calibration()`, ruled at
OQ 68 with the argument that decides this one too — *judging a rule against a binding its own note
tells you not to use is unjudged reported as failed*. It compares numeric bands and cannot serve a
categorical scope, so `rule_scope()` sits beside it in the same file, so that a reader looking for
"when does a rule not apply" finds both together.

**This entry's own numbers were wrong, and the correction changed the design.** OQ 88 said 27
masonry nodes. Measured:

| | |
|---|---|
| nodes the sill rule reaches | **86** |
| with a masonry cladding canonical | **47** |
| with *only* masonry canonical | 34 |
| **with BOTH masonry and frame canonical** | **13** |

The thirteen — `charleston-georgian`, `georgian-colonial-american`, `greek-revival-american`,
`federal-style`, `new-england-federal` among them — were genuinely built both ways. For them the
construction is a fact about the **house**, and the "27+ scoped bindings" OQ 88 named as the worse
option is not merely tedious but **impossible**: no per-node scope can decide a style that is both.
So the field has three answers, not two, and the third is why it is not a filter:

- **in** — the rule governs. Nothing changes.
- **out** — dropped by `eval_packs`, **with its reason recorded**. A rule that vanishes silently is
  the failure this corpus polices hardest.
- **unknown** — still delivered, flagged `scope_unjudged` with the reason. Withholding would strand
  every frame house of a both-ways style; delivering silently is the bug.

**Measured across 164 nodes** (construction: 62 masonry, 30 frame, 17 mixed, 55 unstated):

| rule | dropped | delivered but unjudged |
|---|---|---|
| `opening-proportion` head assembly | 54 | 35 |
| `sash-light` window sill | 34 | 24 |
| `facade-gable` parapet height | 14 | 61 |
| | **102** | **120** |

`english-georgian` no longer resolves a 2.25 in sloped timber sill on a brick wall.

### The near-miss, which is the more useful finding

The variant predicate was first written with an `any_of` list **invented from the rule's prose**,
and read "not in my list" as OUT. Not one id in it matched the vocabulary the corpus actually uses
(`parapeted`, `shaped-scrolled-dutch-gable-with-small-pediment`, `pointed-gable-with-drip-mould`…),
so `facade-gable`'s parapet rule would have been **dropped on all twelve of its own nodes with
nothing said** — a silent corpus-wide deletion dressed as a fix, caught only by checking the
guessed ids against the data.

Two changes came out of it. The predicate carries `any_of` **and** `none_of`, and a variant in
neither is **unknown, never out** — a scope may only rule on variants somebody has classified. And
the lists are classified from each variant's **own record**: the Jacobean shaped gable "steps up to
a pediment" in concave and convex scrolls and its Elizabethan counterpart is "straight-sided and
finialled", both being wall carried above the roof plane, which is what a parapet gable is;
Carpenter Gothic's pointed gable with a drip mould and a half-timbered gable face are roof ends.

## 5. Deliberately not done

- **No plan-time wiring for the three scoped rules.** `elevation.py` consumes none of them — it
  takes the sill height from a constant quoted out of the pack's own note and never reads
  `window_sill/projection`. `structure.py`'s solved `section["wall"]["bearing"]` is a better
  construction fact than any kit reading, but adding that plumbing with no caller would be a second
  reading of "is this a brick house", which is the drift this corpus has been bitten by three times.
  When a consumer exists, it should delegate to `rule_scope`, not re-derive.
- **No cladding taxonomy.** Ruled out before starting: the ontology's `primary_cladding` carries
  only `examples`, so classifying variants corpus-wide is a new concept plus a migration, and it
  still could not decide the thirteen.
- **The remaining 14 unguarded dividing `bounds_test` entries are still listed, not guarded.**
  Guarding a division nobody can reach adds a precondition no test exercises. The one that became
  reachable was guarded because it became reachable.
- **The sheet does not say a shutterless house has no shutters.** It correctly draws none (main's
  Phase 6–7 work), and the *record* now says so in three ways. Adding a legend line is a drawing
  decision outside this package.

## 6. Verification, and what it did and did not prove

- **All 36 checks green**; the full suite green; 164-style sweep with **0 errors** in the pack
  layer, the elevation layer and the fault layer.
- **Every new assertion was mutation-tested.** Four mutations, each reverting one fix: the shutter
  counts back to an unconditional 2.0 (2 tests fail), the `exceptions[0]` guard removed (2 fail),
  `rule_scope` always returning "in" (3 fail), and an unclassified variant read as out of scope
  (1 fail). A test that does not bite when its fix is reverted is worth nothing here, and this
  package's whole subject is guards that were not guarding.
- **The ink is unchanged.** Both reference elevations render **byte-identical** before and after —
  this package changed what the record *says*, not what it draws — and the shutter marks were
  counted precisely (`class="sh w-med"`: 12 on the shuttered house, 0 on the shutterless one). The
  first count used `class="sh` and matched `shingle` and `shade`, reporting 76 shutters on a house
  with none: the broken-selector trap this corpus already names, committed while checking for it.
- **`check_addresses.py`'s ratchets did not move** (own 0, cascade 9, kit_vs_pack 62), and that was
  checked rather than assumed. The 62 are `casing/width` and `baseboard/height` addresses; the sill
  contradiction OQ 86 named was already fixed by WP-5.10's `slots_except`.

**One thing recorded rather than explained:** a single `validate.py` run reported `slot cornice:
derives_from_module cannot reference itself` and has not reproduced in any run since, on the same
tree or on main. It is noted here rather than given an explanation it does not have.

## 7. A mistake worth recording

Mid-package I ran `git checkout build/elevation.py` to undo a mutation and destroyed every edit in
that file — the mutation harness reverting the file wholesale rather than the one line it had
changed. Nothing was lost permanently because the work was reconstructible from the session, but
the lesson is cheap to state and was not free to learn: **mutation-test against a file copy, never
against version control**, when the working tree holds uncommitted work. The remaining mutations in
§6 were run against backups.

---

## 8. The merge with main, and a ruling that landed underneath this package

`origin/main` moved twice while this PR was open. The second time brought **WP-8.1 and the ruling
on OQ 99: the numeric open-question ids are FROZEN AT 99, and every question raised from now on is
named — `### oq/<slug>`**, with `build/check_citations.py` refusing a numbered entry above the
ceiling so the old mechanism is unavailable rather than merely discouraged.

That is the answer to the problem this session raised twice and could not fix from inside it. The
register's own note had predicted each next collision and been right four times in four days; the
diagnosis it kept restating — *an id issued by reading the working tree collides whenever two
sessions run at once* — is exactly what the ruling acts on. A slug is **derived from its subject
rather than issued**, so two sessions that pick the same one have raised the same question and the
conflict is the one you want.

**One conflict, in `CLAUDE.md`, and it was the tally line.** Main's count said 100 entries and 34
open, listing 88 and 89 among them; this branch closes both. Resolved by taking main's paragraph
wholesale — the freeze ruling is new content and must not be dropped by a branch that merely
disagrees about two numbers — and recomputing the tally **from the merged register** rather than by
arithmetic: 99 numbered entries plus one named, 31 numbered open plus the named one, so **100
entries, 32 open**. The derivation test PR #15 extended to read named entries confirms it.

`check_citations.py` was run against this package's own work: **1,634 citations across 249 files,
0 dangling, 0 bare, 0 over the ceiling.** Nothing here issues a new numbered id — closing OQ 88 and
OQ 89 edits entries that already existed, which the freeze permits.

**OQ 90 is unaffected and still open.** It is about the two WP-5.7s, and the freeze does not
renumber work packages. Cite this report by filename.
