# oq/two-id-namespaces — two id namespaces in one register, and nothing can tell that a slug and a number are the same question

*Status: OPEN · Raised in: From the OQ 99 ruling (main, 28 Aug 2026)*

**OPEN — a slug can restate a numbered question's subject, and nothing can tell.** Freezing the
numbers at 99 ends id collisions, and buys a different exposure in their place: the register now
has two namespaces, and a session that does not read all 99 legacy entries can raise
`oq/span-partial-bearing-wall` when OQ 98 already says exactly that. The failure is quieter than
a collision — two live entries on one subject, drifting apart as each is updated, with no
duplicate id to make it visible.
**It cannot be closed by a checker, and that is the finding rather than an excuse.** WP-8.1
established that no machine can verify a citation's SUBJECT matches the entry it names; the same
argument applies here, one level up. A checker can compare slugs to slugs and numbers to numbers.
It cannot tell that `oq/span-partial-bearing-wall` and OQ 98 are the same question, because that
is a judgment about meaning, and a check that pretended otherwise would be "unjudged reported as
passed" in a new place.
**What would actually help, unbuilt:** a subject index over the 99 legacy entries that a
person consults before naming a new one — cheap, and it makes the duplicate visible at the moment
of authoring rather than at the merge. Whether that is worth building depends on how often a new
question is raised, which is currently about one a day and will not stay there.

## Reissued 28 August 2026 — a FOURTH collision, and this block has now moved twice

*The third collision (below) moved this branch's questions from 72-79 to 78-85. While that was
being written, a second session was independently moving ITS block into 78-89 for the same
reason, and merged first as PR #14. So 78-85 collided a second time, in the same file, over the
same rule, four days running.*

**Main keeps 78-90** — the entablature datum, the eave cornice, the dormer layer, WP-5.10 and
its audit — by the rule this register has now applied four times: whoever merged first keeps the
numbers, and it is never the side still on a branch. **This branch's eight moved again, to
91-98.**

| raised as | became (3rd collision) | is now | subject |
|---|---|---|---|
| 72 | 78 | **91** | where a window's authority lives (grammar decides the role, the kit the sash kind) |
| 73 | 79 | **92** | furniture: sizing refused, arrangement to the rooms' own words |
| 74 | 80 | **93** | every door hinged `low`; no rule decides the hand |
| 75 | 81 | **94** | the reference plan cannot satisfy its own style's hard passage rule |
| 76 | 82 | **95** | declared stacking, and what the generator could not fix |
| 77 | 83 | **96** | `_shared`'s first-match-wins can report a corner kiss as a shared edge |
| 78 | 84 | **97** | the search had no span term |
| 79 | 85 | **98** | `span_check` credits a partial wall across the whole plate; the validator is silent on capacity |

**A commit message, report or code comment written on this branch before 28 August 2026 carries
one of the two older numbers**, and which one depends on whether it was written before or after
the third collision — the reports under `docs/reports/wp-6.*` and `wp-7.*` have been converted
twice and now read 91-98; the commit messages were not and cannot be. **Reading a bare "OQ 78"
in this branch's history is therefore ambiguous by date and the date is the only way to resolve
it**, which is the clearest argument yet that ids must not be issued from the working tree.

**Four collisions in four days. The register has now predicted its own next collision three
times and been right three times.** Nothing in this commit fixes that either.
