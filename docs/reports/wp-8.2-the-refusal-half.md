# WP-8.2 — OQ 51's refusal half, and a meter that was wrong in the flattering direction

*28 August 2026. The 26 August adjudication pass found the ruling could only do half its job:
endorsing a gap was a line in `applies_to`, and refusing one had no mechanism at all. This builds
the refusal. It also found the meter that measures the backlog was wrong by 27 in the direction
that flatters, and fixed that first, because a pass measured against the old arithmetic re-pins
the wrong numbers.*

---

## The meter was wrong, and it is fixed before it is moved

`check_inheritance.measure()` walks each node's cascade twice — once for roles, once for packs —
and the two loops did not carry the same guard. The pack loop had `e["pack"] not in own_ids`; the
role loop had nothing.

That asymmetry was not a style choice. `resolve_packs` walks `[node] + cascade` and keys on
**pack id**, first wins, so when a node binds pack P itself at `chain[0]` an ancestor's binding of
P never governs anything — it lands in `_overridden_by_ancestor` and is dead. Attributing a role
gap to that dead delivery then asks **the wrong pack's** `applies_to` whether the node is
endorsed, and it usually says yes, *because the node binds that pack*.

| | published | corrected |
|---|---|---|
| `role_gaps` | 293 | **287** |
| `unendorsed` | 222 | **249** |
| `endorsed` | 71 | **38** |

**The backlog is 27 larger than was published and nearly half the endorsed figure was an
artefact.** Six role gaps vanish outright; thirty-three re-attribute to a pack whose `applies_to`
does not name the node. One of the six is `egyptian-revival / facade / facade-peristyle` — this
question's own poster child, reported as an unjudged delivery of the very pack OQ 49 deliberately
bound to it, scoped.

**And the ratchet could not have caught a regression.** It stood at 294/3367 against a live
293/3366 — stale-high on two of three keys, so `--strict` had two units of silence in it. Its own
comment said *"tests/test_wp46_packs.py imports THIS dict rather than restating the numbers,
because a threshold duplicated in two files drifts apart and a ratchet that has drifted is
slack."* No import existed. The test restated `(293, 3366, 222)` as a literal, and the two drifted
apart exactly as the comment says they cannot. The import is real now, and a test asserts the
test does not carry its own copy.

## The refusal half: `declined_packs`, per node

A style node may now name a pack that reaches it **by descent** and does not belong, with a
reason and — where the node's own record decides it — a verbatim quote from that record. It is
the exact mirror of `applies_to`: one records that somebody read the cascade and agreed, this
records that somebody read it and did not.

Enforced in **one** place, `resolve_kit.resolve_packs`, which is the function that decides pack
MEMBERSHIP. `eval_packs` decides which RULES a member contributes — that is what `slots` and
`slots_except` are for, and those live on the ANCESTOR's binding, so they change behaviour for
every descendant and for the ancestor itself.

Validated in `check_pack_bindings.py`, and **the check that matters is the lie-check**: a decline
naming a pack that does not actually reach the node refuses nothing while reading as an
adjudicated refusal, and the meter would count it as judged. Same shape, and deliberately the same
words, as the `slots_except`-that-refuses-nothing check it sits beside. A `node-record` basis with
no quote, or a quote not present in the node's own file, is an error.

### The per-edge deny was designed and refused, and the argument for it was mine

It was proposed on leverage — `english-georgian` delivers fifty of the unendorsed gaps, so one
edit should settle many. **Measured, that is false**, and the numbers are recorded here because
the proposal will be made again:

- **Most gaps have no edge to write the refusal on.** `english-georgian`'s fifty are **five
  direct**; the rest arrive transitively at cascade depths of two to twelve. There is no "the
  `english-georgian` edge" — there are thirty-one nodes each reaching it their own way.
  `gothic-revival-british` delivers fourteen gaps to fourteen nodes with **three** direct edges.
- **The blast radius is wrong.** A subtree deny of `english-georgian`/`storey-graduation` touches
  twenty-six receivers to fix eighteen, and **seven of the eight collateral were already
  endorsed — five of them by the 26 August pass that raised the proposal.** The mechanism would
  have undone the pass that motivated it.
- **It would not give subtree semantics anyway.** `build/build.py`'s `_cascade_scope` only picks
  up edges whose SOURCE is the node itself.
- **The wrongness is usually the node's, not the route's.** `ranch-style` receives
  `storey-graduation` because it descends from `english-georgian` *and* because it is a
  single-storey house. Only the second is a reason; the first is a route.

`--ancestors` prints a DIRECT column so the next reader can see this rather than re-derive it.

## Ten declines, and the headline number did not move once

| node | pack | its own words |
|---|---|---|
| `ranch-style` | storey-graduation | *"Everything about it is horizontal: a single storey"* |
| `craftsman-bungalow` | storey-graduation | *"One to one and a half storeys, 800 to 1,400 sq ft"* |
| `california-bungalow` | storey-graduation | *"Single storey … no full second floor"* |
| `minimal-traditional` | storey-graduation | *"one storey or one and a half"* |
| `gothic-revival-british` | chambers-ionic | *"Classical apparatus — orders, pediments, entablatures, quoins, symmetrical porticoes — is forbidden throughout."* (a hard constraint) |
| `arts-and-crafts-american` | chambers-ionic | *"Absence of applied classical orders"* |
| `arts-and-crafts-british` | chambers-ionic | *"No classical order, no pointed arch, no shaped gable, no period quotation of any kind"* |
| `scottish-baronial` | chambers-ionic | *"None classical. Composition is picturesque"* |
| `tudor-revival` | chambers-ionic | *"No classical module."* |
| `carpenter-gothic` | chambers-ionic | *"Ornament is flat … everything projects less than about two inches, because everything came off a plank"* |

**`inherited_packs` 3,366 → 3,356. `judged` 38 → 48. `unendorsed` 249, before and after, every
time.** Each node's role simply re-attributed to the next ancestor, which nobody has judged
either. **Ten correct refusals moved the headline number by zero.**

That is the first pass's own objection — *"a falling `unendorsed` does not mean a corpus getting
more correct at the same rate, and the number does not say so"* — confirmed by measurement rather
than argued. So the meter gained a **FLOOR**: `judged` is endorsed plus declined and may only
rise, checked by `--strict` alongside the ceilings. `unendorsed` is a work list, not a score.

### One node was deliberately not declined

`jacobethan-revival`'s `proportional_system` reads *"There is no classical order except at the
entrance porch, where one is deliberately introduced as a quotation."* A classical order IS
present. Declining `chambers-ionic` outright would remove the only thing that could dimension
that porch — scoping stopping a wrong donor without supplying a right one, which is OQ 58's
stated limit. Left for a ruling, as `english-baroque` was by the first pass.

## Raised: OQ 99, and it is larger than the backlog it was found beside

**787 (node, slot) pairs where the resolved kit binds a slot `forbidden` and a proportion pack
dimensions it anyway**, across **118 of 132** buildable nodes — and **787 of 787 resolve by
precedence. Not one was chosen by a human.** `docs/inheritance.md`'s binding table says
`forbidden` means *"This node prohibits the slot. Stops the cascade."* It stops the kit cascade;
it has never stopped the pack cascade.

**Declining will not close it.** `--impact carpenter-gothic chambers-ionic` shows `pilaster` —
whose resolved record says *"No pilaster order."* — handed straight to `benjamin-ionic`. Counted
and ratcheted separately from OQ 51's numbers, because it measures a kit binding overruled by a
pack rather than a role nobody bound. Fixing it means `eval_packs` refusing to write to a
forbidden slot, which changes dimensions on 118 nodes and is its own package.

## Tooling

`check_inheritance.py` gains `--ancestors` (the reading order, with the DIRECT column that
refused the edge mechanism), `--full` (the five-node truncation made the work list unworkable —
the 26 August pass re-derived it by hand), `--gates`, `--impact NODE PACK`, and `--forbidden`.

**`--gates` exists because endorsing is not bookkeeping and nothing said so.** `applies_to` is a
live behavioural gate in three files: `structure.py::graduation_check` runs at all,
`structure.py::span_check`'s capacity table, and `elevation.py`'s whole scope gate (an AND of
`opening-proportion` and `facade-classical`). **The 26 August pass switched `graduation_check` ON
for eleven styles and recorded it nowhere.** The GATES table is held to the code by a test, so a
gate that moves fails a test instead of leaving the table quietly false.

## What was deliberately not done

- **The per-edge deny**, refused on the measurements above.
- **The `inherits_packs` opt-in flip**, which the ruling puts last and which needs
  `mcp_server/core.py`'s private cascade walk to move with it — that walk does not splice
  families the way `build/build.py` does and already diverges.
- **Fixing the 787.** Raised as OQ 99, ratcheted, not touched.
- **The other 239 unendorsed gaps.** `--ancestors` and `--full` make them workable; this package
  built the mechanism and proved it on the ten the records decide outright.

## Found by the first decline: a decline and an inherited slot-level ruling can contradict

It surfaced as a `KeyError`. `choose_pack` consults the resolved slot record's own `packs`
block — **a person's explicit ruling** — before precedence, and that block cascades like
everything else in the kit. So `ranch-style` declines `storey-graduation` on its own record while
its `chair_rail` still carries an ANCESTOR's ruling naming that pack.

The decline wins, and correctly: `resolve_packs` never delivers the pack, so the rule does not
exist to be chosen. But the stale ruling is real, and `--slots` now prints it —
`chair_rail <- storey-graduation  bound on DECLINED by this node — an inherited slot-level
\`packs\` ruling still names it` — rather than crashing or, worse, saying nothing. It is OQ 87's
class again: a slot record inherited in full, including a decision the descendant has since made
differently.

## A trap worth carrying: a same-second mutation check can read stale bytecode

Mutation-checking by editing a file and re-running within the same second can serve **stale
`__pycache__`** — Python's invalidation is mtime-based at one-second granularity. It cost a
confusing minute here, and it can do worse: a mutation test that appears to pass on the mutated
code is exactly the false confidence this codebase's audits keep finding. `rm -rf __pycache__`
between mutation and re-run.

## Verifying

```
python3 build/check_inheritance.py --strict          # 287 / 3356 / 249, floor judged 48
python3 build/check_inheritance.py --forbidden --strict   # 787, ratcheted apart
python3 build/check_inheritance.py --ancestors --full
python3 -m pytest tests/test_declined_packs.py       # 11 tests, mutation-checked
python3 build/check_all.py                           # 39 checks
```

Each new assertion was run against the unfixed code and confirmed to fail: the decline filter
neutered in `resolve_packs`, the RATCHET drifted by one, a decline naming an unreachable pack, a
decline quoting a sentence its node does not contain.
