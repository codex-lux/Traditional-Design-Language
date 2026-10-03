# oq/the-census-sweeps-every-style-over-one-dated-side-gabled-house — what the census cannot reach

*Status: OPEN · Raised in: WP-16.8, the audit of Phase 16 (3 October 2026), auditor B's eighth finding*

**The census draws every style on one house, and the sixteen shipped plans carry none of the cases
the audit found.** `tests/svg_census.py` reads two populations:

- **the style sweep** (`_style_sweep`): the shipped Tidewater record placed once, the style of each
  node with a kit written into it, and the elevation drawn; 41 styles are inside the elevation's
  gate. That record is two storeys, dated 1765, and declares `roof_form: side-gable`. (The sweep
  places the house a second time dated 1790, for the sidelights' run, and stamps the date back
  before it draws.) So every per-style row, V2, V19, V25 and X4 among them, reads every kit at 1765
  under a declared side gable;
- **the shipped plans.** Fifteen of the sixteen are undated and thirteen declare no roof, so B1's
  kit roof is drawn on them. But none of their styles' resolved kits carries a dated ban on the
  sidelights or a dated `none` return, the two rows B1 reached; the dated bans they do carry are on
  other slots (the roof's material, the window type, a fireplace surround, the landscape).
  And good-05, the one hipped house drawn, has a kit that forbids its return.

Two of the audit's findings lived in the gap between the two, and the census agreed with both:

- **B1**: an undated house read a dated row as a measured zero, and the zero decided two verdicts
  (`sidelights-as-storefront-glass` on all 13 composed Georgian candidates; `return-that-never-returns`
  on an undated first-period house);
- **B5**: on a hipped house whose kit is silent on the return, the return count was unmeasured while
  the gable count read zero.

Each is driven in `tests/test_audit_of_phase_16.py` now, by a fixture built for the case. The census
still cannot see the class.

**What it would take.** A second sweep over the same record undated and with its roof declaration
removed, so each style's own kit roof and dated rows are drawn. That is a solve per style per variant,
the cost WP-16.4 named for census V2's stack rows when it left them could-not-evaluate.

**What is wanted.** Whether the census should carry that second sweep, and at what cost per run, or
whether driven fixtures in the tests are the answer for these cases.

*Taken as recommended under Lucas's standing instruction of 1 Oct 2026, never put: raised and left
open. The audit's own fixes are guarded by tests, so nothing waits on the answer.*
