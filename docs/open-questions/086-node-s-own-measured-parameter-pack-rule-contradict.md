# OQ 86 — a node's own MEASURED parameter and a pack rule contradict each other at 133 addresses, and nothing was comparing them

*Status: OPEN · Raised in: From the four rulings (WP-5.14, 27 Aug 2026)*

**OPEN — a node's own MEASURED parameter and a pack rule contradict each other at 133 addresses, and
nothing was comparing them.** OQ 48 measured pack against pack and closed at 0 own-scope collisions.
This is the same corruption one layer over and it was invisible to that measurement for a simple
reason: the kit writes a parameter called `projection_in` and a pack writes dimension `projection`, so
the two never met under one name. `tidewater-georgian` authored its brick sill's projection as **0–1 in,
`kind: measured`**, while `sash-light` delivered **2.25 in "sloped about 1 in 6 with a drip"** to the
same slot — more than twice the node's own figure, in a node whose kit FORBIDS the sloped sill and
gives its reason. The resolved slot carried both, under two names, and no checker looked.

`build/check_addresses.py` gained a third reporter, `kit_vs_pack()`, and the first measurement is
**133 contradicted parameters, 3 could not be judged**. It compares only parameters the node authored
as `measured` — a `derived` one is a pack's own value copied into the kit, agreeing with itself — and
compares VALUES rather than quantities, because a kit parameter has no `quantity` field. Ratcheted at
133 so it cannot grow, in the shape OQ 48's original 139 were handled: a real corruption, found by
measuring something nobody had measured, too large to fix in the package that found it.

**The distribution is concentrated and that is the good news:** `american-farmhouse-vernacular` 32,
`federal-style` 31, `greek-revival-american` 24, `craftsman-bungalow` 16,
`georgian-colonial-american` 13 — five nodes carry 116 of the 133. The sill that found it is not in
the count; it was fixed in the same commit.
