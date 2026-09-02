# WP-4.4: the record that said 322, and the checker standing one field away

*2 September 2026. A follow-on to `docs/reports/wp-4.4-the-eleven-that-were-never-blocked.md`.*

## What this was supposed to be

The list of what to do next said: *give the 322 asset records their `provenance.building` names so
the queued HABS harvest does not degrade to a style-name search.* Both this file's own CLAUDE.md
entry and `STATE-OF-THE-PROJECT.md`'s numbered next-work list said the same thing, in the same
words, as the second item on the project.

## What was true

It was done. `build/name_asset_buildings.py` was written on 31 August, run with `--write`, and
committed. A dry run on 2 September assigns **zero**:

```
0 record(s) would gain a building, across 0 style node(s)
786 of 1850 record(s) would then name one
still unnamed, by reason:
    858  role: incorrect — the corpus names no building for a fault
    134  not a photograph — a drawing of a rule needs no building
     72  its style records no exemplars
```

And the figure in the instruction was wrong twice over. There are not 322 asset records; there are
**1,850**, since the 31 August regeneration took the manifest from a frozen three-node snapshot to
the corpus it had always described (`oq/regenerating-the-asset-manifest-discards-what-was-added-to-it`).
Nor is the naming step's own result 845, as four files said: the WP-4.4 adversarial audit had
already corrected the assigner to key on `kind` rather than `role`, stripping building names from
52 line-diagrams and 7 comparison drawings, and **845 became 786** in the same commit that fixed it.

**Twelve claims across eight files described a state that no longer existed**, and two of them were
instructions telling the next session to do work that was finished. That is the finding: not a
defect in the data, a defect in what the data's own documents say about it, of exactly the kind
WP-6.4 named — *"until X lands" is a lie the moment X lands*, here in its other direction, where the
thing that landed was the work itself.

## The number nobody could see, and the checker standing one field away

`build/check_counts.py` exists to make this class impossible. It derives every count that appears
in prose from the data and fails the build when the two disagree. It was computing `image_records`,
`image_sourced`, `image_wanted`, `image_pairs` and `image_critical` from `assets/manifest.json` —
and reported **0 stale** in the same run in which `PLAN-OF-ACTION.md` claimed 845 records naming a
building across 330 queries of which 188 were American, against a live 786, 305 and 180.

Every stale figure sat in exactly the fields no claim covered. And `PLAN-OF-ACTION.md`, which
carried three of the four, **was not in the checker's file list at all**.

Four values are computed now — `image_building_named`, `image_never_harvestable`, `image_queries`,
`image_queries_us` — and twenty claims guard them across four files, `PLAN-OF-ACTION.md` among
them for the first time. (An adversarial audit caught this sentence saying *five* files and
*nineteen* claims against a real four and twenty: a package whose whole finding is that an
unchecked figure goes stale published an unchecked figure about its own claims, off by one, in
the report that says so. The twentieth is the CLAUDE.md sentence the plan named and the first
pass pointed at a different file instead.) The query and the charter test are **loaded from the harvester** rather
than restated: `query_for` decides whether a record can be searched at all and `outside_the_survey`
is the US-state allowlist, and a second spelling of either is how the citation grammar came to
disagree with itself in three places.

Each of the three new claim families was proved to fail by mutation before being trusted.

## The check that was never there

`check_assets.py` validated the schema, that `sourced` means a file is really on disk with a
matching digest, that a drawing is never kinded `photograph` and says so on its own plate, and that
no licence is asserted without the evidence it was read from. It never asked where a building name
came from.

That is the field `harvest_habs.py` **searches on**. A wrong one does not fail loudly; it fetches a
photograph of the wrong building and files it against a style. And a hand-typed name was
indistinguishable from one the assigner dealt: 161 of the 786 were written by hand in `347d0ab`,
before the script existed.

The checker now requires a building name to be an `exemplars[].name` on a node the record itself
says it depicts, its location to be that exemplar's own location, and the record to be a
`photograph` that is not `role: incorrect`. The exemplar index is loaded from
`name_asset_buildings.py` — the module that writes the names — so the reader and the writer cannot
drift into two answers about what an exemplar is.

**All 786 pass, the 161 hand-authored among them.** That is worth stating as a measurement rather
than an absence: the assigner's round-robin and the hand pass agree with the corpus, and we now
know it rather than assume it. Four mutations enter the four branches in
`tests/test_asset_provenance.py`, one of them driving the real checker over a planted defect so the
test's own restatement of the rule cannot drift from the shipped one.

## What was deliberately not done

**The 72 residual records.** They are photographs of styles whose node records no `exemplars` — all
18 are higher-rank nodes (`english-classical` 17, `american-arts-and-crafts` 9, `early-republic` 7,
`victorian` 5). Two ways to name them, and neither is this package's to take. Authoring `exemplars`
on those nodes means authoring facts about real buildings, which needs sources this container cannot
reach — `loc.gov`, `archive.org` and `hathitrust` all fail to connect — and inventing them is
precisely how a guess gets laundered as `measured`. Letting the assigner walk `member_of` down to a
child style's exemplars means ruling that a child's exemplar may stand for its parent, which is a
claim about what a photograph of "Victorian" *is*, and it needs a ruling rather than a loop. The
number is pinned as a ceiling that may only fall.

**The acceptance line, which cannot be met from here.** WP-4.4 wants ≥100 records `sourced` or
`generated` and zero at `license: unknown`. It stands at 73 and 1,716. Both halves need bytes off
the network, and the route is ruled but unbuilt (`oq/fetching-through-a-tier-the-proxy-denies`):
Tavily's connector and a CI runner are the two tiers that can fetch, and the report that ruled it
also argued the workflow should be the LAST thing built, not the first. Nothing here changes that.

**The historical prose was left alone.** `build/link_asset_faults.py`'s docstring describes the
defect as it stood when there were 322 records; the WP-4.4 reports narrate 845 before their own
audit section corrects it; `CHANGELOG.md` records what was true when it was written. A record of
what was believed is not a stale claim, and rewriting it would destroy the only evidence of how the
number moved. Only sentences asserting the CURRENT state were changed.

## Files

`build/check_counts.py` (four computed values, nineteen claims, `PLAN-OF-ACTION.md` added to the
guarded set) · `build/check_assets.py` (the provenance check) · `tests/test_asset_provenance.py`
(new, ten tests) · `CLAUDE.md`, `STATE-OF-THE-PROJECT.md`, `README.md`, `PLAN-OF-ACTION.md`,
`build/harvest_habs.py` (the twelve claims) ·
`docs/open-questions/oq-regenerating-the-asset-manifest-discards-what-was-added-to-it.md` (a dated
correction under a closed ruling, its history left intact).
