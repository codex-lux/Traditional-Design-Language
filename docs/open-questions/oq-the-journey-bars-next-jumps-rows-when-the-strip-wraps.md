# oq/the-journey-bars-next-jumps-rows-when-the-strip-wraps — the act's row is steady, the bar above it is not

*Status: CLOSED · Raised in: the audit of the candidate-click follow-up (16 October 2026) · Closed by WP-17.2 (29 October 2026)*

**CLOSED 29 Oct 2026 by WP-17.2, which retired the bar.** The house's journey is the sidebar's own block now, a vertical spine of stations (`components/JourneySpine.jsx`), so there is no row for Next to jump from: it stands on its own line below the stations at every width. The redesign ruled this (`docs/ui-redesign-2026-10-29.md`: "The journey spine replaces `JourneyBar` in the sidebar"), and its note named this question as going away with it. What follows is the question as it was raised.

**WAS OPEN — the Candidate Set's strip now holds its grid still while a pick changes the act's words, and
the journey bar above it does not: its Next control is `white-space: nowrap`, so when the bar is too
narrow to hold the step names, the held reason and Next together, Next moves to another row.**

## What was measured

The first pass at the strip moved the columns 27 px at 1100 px wide and 47 px at 1680 between a
refused pick and an open one. The act now has a row of its own with a two-line floor, and the grid
no longer moves for the strip's words (checked at 1100 and at 1680, picking each of two candidates in
turn). The bar's own reason string was shortened (`reasons.pickedRefused`) after a residual 21.5 px
showed that a longer reason moved Next to a second row of the bar.

What is not measured is every width and every reason: the bar's reasons run from "open it" to a
refusal's wording, and the floor on the act's row is two lines of the strip's own type, a measured
choice at the widths this shell is used at (1100 to 1680), not a bound. Below that, and with a longer
reason (a translated or edited word table), the bar can wrap again and the grid moves with it.

## What it would take

Either a floor on the bar's own row (the same device as the strip's), or Next taking its own position
so that no reason can push it, or the reasons being held to a length the bar can always hold: the
last is a cheaper guard than the first two (`journey.test.mjs` already pins the one reason's length).
No ruling is needed for the third; the first two change the bar's design and would want one.
