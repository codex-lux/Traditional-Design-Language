# WP-8.3 — `forbidden` stops the pack cascade too, and the drawn half needed its own fix

*28 August 2026. `oq/forbidden-stops-the-pack-cascade`, raised by WP-8.2 and ruled the same day: a pack rule may not write to a
slot the resolved kit binds `forbidden`, with a human override. Building it found a second path
from packs to output that no plan and no open question had named, and half of that path is
deliberately left open.*

---

## What was wrong

`docs/inheritance.md`'s binding table has said `forbidden` means *"This node prohibits the slot.
Stops the cascade"* since the beginning. **It stopped the kit cascade and never the pack
cascade.** 776 (node, slot) pairs across 118 of 132 buildable nodes carried a pack-supplied
dimension for a slot the resolved kit prohibits — `entablature` 69, `parapet` 63, `column` 57,
`modillion_dentil` 54, `transom_sidelight` 49, `cornice_return` 48, `pilaster` 40.

**And not one of the 776 was chosen by a human.** Every one resolved by
`style.proportion_packs` precedence — numbers authored on ancestors, for the ancestors'
buildings, with no view of the descendant — and no slot carried a `packs` ruling for any of
them. `carpenter-gothic`'s resolved `pilaster` record reads *"No pilaster order."*, inherited
from `gothic-revival-american`, and the node published a pilaster width anyway.

## The ruling, and where it lives

**Absolute, with a human override.** A pack rule may not write to a forbidden slot *unless* that
slot's own `packs` block names the pack. That block is not a new mechanism: `choose_pack`'s own
docstring already calls it *"the author's explicit ruling and the only place a human has said
which pack wins"*, and consults it first for the same reason. **Zero of the 776 qualify**, so the
override strands nothing today — stated rather than claimed as coverage, and held to the data by
a test so it cannot go stale.

**The refused rule is MARKED, not deleted**, and that decision is load-bearing three ways.
Deleting would have destroyed the measurement itself, because the 787 count *is* the marks.
`build/check_addresses.py` reads these rows and never calls `choose_pack`, so a refusal placed
only in the chooser would not have reached it. And an absent rule is indistinguishable from "no
pack writes here", where a marked one carries the binding's own note. `eval_packs` flags
`refused_by_kit`; `choose_pack` will not choose a flagged row and returns `how: "kit.forbidden"`.
Same discipline as `openings.py` marking an opening it cannot realise `unplaced` and never
removing it.

**`eval_packs`' `kit` argument is required and has no default.** A `kit=None` default would let
every one of the eight call sites keep the old behaviour by saying nothing — the exact failure
the fault schema's own note describes for a mistyped guard: *"omit `expression` and the
precondition is ignored entirely, the test runs unguarded and convicts."* Callers with no kit
pass `{}` and mean it.

## The finding: a second path from packs to output, named by nothing

**`build/elevation.py` never calls `resolve_packs` or `eval_packs`.** It reaches packs by
`PE.resolve("<pack>")` and reads sixteen slots straight out of the pack files. So it is blind to
bindings, to `slots`/`slots_except`, to WP-8.2's `declined_packs`, and to the kit's `forbidden` —
and **the gate above does not reach a single figure it draws.** Nothing in the plan, the register
or `CLAUDE.md` had named that path.

Swept over every style rather than the two shipping plans: **40 styles pass the generator's own
scope gate, 15 of them forbid at least one slot it reads, and the exposure is 40 (style, slot)
pairs.**

| | slots | what happened |
|---|---|---|
| **16 refused** | `transom_sidelight` 8, `pilaster` 8 | The entrance composition already carried a `use_sidelights` branch, so the kit's refusal decides it instead of a width cap. Both figures are now **absent, not zero** — a zero is a measured claim that the sidelight is nothing wide, which is a different statement from "this style does not have one". |
| **24 read anyway, disclosed** | `frieze` 9, `belt_course` 6, `water_table` 6, `door_surround` 1, `cornice` 1, `window_head_wood` 1 | Published in the elevation record as `forbidden_slots_read_from_packs`. |

**The 24 are deliberately not zeroed and that is `oq/forbidden-stops-the-pack-cascade`'s open half.** A style whose resolved kit
forbids `frieze` while still passing a *classical* scope gate is two records contradicting each
other, not a number to silence. Zeroing them would pick a winner between the kit and the pack's
`applies_to` on nine styles without anybody having decided which is right. `cape-cod-colonial` is
the case to read first: its own `pilaster` note says *"The whole classical-apparatus group is
forbidden at the family"*, and it sits inside this generator's classical gate.

**It shows on a shipped plan immediately.** `spec-builder-colonial` (`colonial-revival`) forbids
`transom_sidelight`: `sidelight_width_in` and `transom_height_in` are now absent from its
measurements, `sidelights_present` is False, and the entrance note says which record decided it,
while `belt_course`, `frieze` and `water_table` are listed as read anyway.

## The finding: Colonial Revival was inheriting a Gothic prohibition on its own front door

Making the refusal bite immediately turned two faults red on a shipped plan —
`fanlight-before-its-date` and `six-panel-door-everywhere`, both on `spec-builder-colonial`, both
reporting the same value: *"1.3333 against at-least 1.6"*. Both carry a `colonial-revival`
exception whose `bounds_test` is `entrance_composition_width_in / door_leaf_width_in at-least
1.6`, and `check_measurements` **substitutes** that for the primary on a style match — CLAUDE.md's
"third location, and the one that bites". With the sidelights refused, the composition is door
plus casing: `1 + 2/6 = 1.3333`.

**The generator was right and the data was wrong.** `colonial-revival`'s resolved
`transom_sidelight` binding was **`forbidden`, inherited from `gothic-revival-british`**, on an
editorial note reading *"not directly documented either way; forbidden on the strength of c05's
general prohibition rather than a direct quotation about fanlights specifically."* That node's
c05 forbids classical apparatus throughout — so Colonial Revival was carrying a **Gothic Revival
prohibition on the one feature it is most known for.**

Its own record says the opposite, twice:

> `defining_characteristics[1]`: *"An entry assembly of pilasters or engaged columns with an
> entablature, pediment, or portico, **plus fanlight and/or sidelights** — larger and more
> elaborate than any colonial precedent"*
>
> `constraints[0]`: *"**sidelights not wider than 12 in. each**"* — a style does not set a width
> limit on a thing it forbids.

**This is OQ 87's mechanism exactly**, and this is the second time on this very node: the slot
was bound `open`, and `resolve_slots` stops its walk only on `specified` or `forbidden`, so an
unstated slot inherits its nearest ancestor's record in full. `colonial-revival`'s **`dormer`**
slot was fixed for the identical reason on 27 August — *"the style could not declare the only
dormer it is built with"*. Nobody looked at the slot next door.

**It was invisible until now because nothing read `forbidden` on the pack path.** The slot said
forbidden; the pack supplied a sidelight width; the drawing showed sidelights; every check
passed. WP-8.3 made the two records disagree out loud.

`kits/colonial-revival.kit.json` now binds the slot on the node's own evidence —
`elliptical-fanlight` and `sidelights` canonical, `rectangular-multi-light-transom` permitted,
`none` atypical. The two faults went back to clear, the entrance draws its sidelights again, and
**the forbidden-slot ratchet fell 787 → 776**: one evidenced binding on one node removed eleven
pairs, and the elevation exposure fell 46 → 40 with it.

**The lesson for the remaining 776 is that they are not all defects.** Some are a kit correctly
refusing a pack. Some — like this one — are a kit that inherited a refusal it never made, and the
pack was right. The meter counts the disagreement, not the verdict, and each one has to be read.

## Found on the way: the meter had been counting slots with no figure on them

`--slots carpenter-gothic` reported **"75 slot(s) dimensioned"**. Eleven of those slots had every
pack rule refused, so they carry no figure at all; the honest report is **64 dimensioned plus 11
named as refused**, which is what it prints now. `ranch-style` moved 78/69 → 67/60 for the same
reason. Both test pins were re-pinned with the reason, not the number, in the comment.

The `--forbidden` meter now counts the gate's **own marks** rather than re-deriving the same
judgment a second way — two copies of one rule is how the citation grammar came to be spelled
three times — and the two agree at 787.

## What was deliberately not done

- **The 24 read-anyway pairs**, above. Counted, disclosed, and left for a ruling.
- **`kit_vs_pack` still reads `load_kit(nid)`**, the node's own file rather than the cascade.
  That is OQ 86 and WP-8.4's; the resolved kit is passed to `eval_packs` there for the gate only,
  and the two are deliberately not conflated.
- **Nothing was zeroed to make a number smaller.** Every refusal is a slot the kit itself
  forbids, and every non-refusal is named.

## Verifying

```
python3 build/check_inheritance.py --forbidden --strict     # 787, ratcheted apart from OQ 51
python3 build/check_inheritance.py --slots carpenter-gothic # 64 dimensioned + 11 refused, named
python3 -m pytest tests/test_forbidden_slots.py             # 7 tests, mutation-checked
python3 build/check_all.py
```

Both halves were run against the unfixed code and confirmed to fail: the resolver gate neutered
in `_refused()` (two tests red), and the elevation refusal neutered at `sidelights_forbidden`
(the elevation test red). `rm -rf __pycache__` between mutating and re-running — a same-second
edit serves stale bytecode.
