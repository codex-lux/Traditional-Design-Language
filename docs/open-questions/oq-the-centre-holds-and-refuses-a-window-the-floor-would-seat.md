# oq/the-centre-holds-and-refuses-a-window-the-floor-would-seat — the window nearer the centre keeps a place nobody composed

*Status: OPEN · Raised in: WP-16.6, the pier and the alignment (1 October 2026)*

**R5a keeps the inner window where the placer put it, and that place was never chosen for the
floor.** Lucas ruled (29 Sep 2026): *"windows nearer the entrance keep their places, and on other
faces those nearer the face's centre do; the outer window moves along its own wall, or is refused
by name if it can't."* WP-16.6 executes it literally. A window's place is the placer's default,
`(k + 1) / (n + 1)` of its room's wall, which the placer has used since WP-6.2 and which nothing
ever composed. The inner window holds there, and the outer one moves outward or is refused.

**Measured on the 16 shipped plans** (`engine="heuristic"`), against the most units each face line
could seat at the floor if no window held its place:

| plan | line | seated | the floor alone |
|---|---|---|---|
| spec-builder-colonial | dining, W | 1 | 2 |
| bad-02-flex-room-craftsman | master suite, W | 1 | 2 |
| bad-05-two-story-spec-colonial | master suite, W | 1 | 2 |
| bad-06-open-concept-render | great room and kitchen, N | 3 | 4 |
| good-02-portico-library-house | guest bedroom and kitchen, N | 2 | 3 |
| good-02-portico-library-house | library and living room, S | 3 | 4 |
| good-05-lobby-gallery-mansion | dining room and library, S | 2 | 3 |

The pier floor refuses **16 units** on these plans: 11 newly refused, and 5 the old foot already
refused, now said in the floor's words. **7 of the 16** would stand at the floor if the window
nearer the centre moved along its own wall. Of the other nine, eight are the floor's (the wall is
too short at any spacing), and one is held by the axis of the opening below it (the spec
Colonial's upper south face). A driven case states the cost in one line:
three 3 ft windows on a 10 ft wall seat one, at the middle, where two would stand 3 ft apart at
1.5 and 8.5 ft (`tests/test_window_pier.py`).

**The instrument** is `tests/window_piers.py` for the piers, and for this count a pass over the
placer's own free runs, recorded in WP-16.6's report.

**What is wanted.** Whether the window nearer the centre may move along its own wall, away from
the centre, where that lets the outer window stand at the floor. The centre itself would still hold:
the entrance's axis and the face's centre do not move. Or whether "keep their places" means the
placer's default places, as executed.

*Taken as recommended under Lucas's standing instruction of 1 Oct 2026, never put: raised and left
open, because the ruling's words are "keep their places" and reading them otherwise is a second
ruling.*

## Amended 2 Oct 2026 (WP-16.8, the audit of Phase 16, auditor A)

The figures above were measured on a placer that seated aligned upper units before every other
unit and called the order R6. No ruling states it, and it ran R5a backwards: an outer aligned
window was seated first, and the window nearer the centre was refused (the spec Colonial's upper S
face) or moved 0.9 ft (Tidewater's chamber3). The audit seats one queue by distance from the
centre, each aligned unit at its axis, which is R5a and the ruled "read together" in their own
words. Re-derive the counts above on the new placement before quoting them; this question --
whether the centre should yield where the floor would seat both -- is unchanged by it.
