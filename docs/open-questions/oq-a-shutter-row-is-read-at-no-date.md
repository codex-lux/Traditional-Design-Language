# oq/a-shutter-row-is-read-at-no-date — whether a house carries shutters is decided without its date

*Status: OPEN · Raised in: the audit of WP-16.8's own diff (3 October 2026)*

**The elevation decides whether a house carries shutters from its resolved `shutter` slot and reads
no row's date.** The rule is `bool(slot) and slot["none"] != "canonical"`: shutters are carried
unless `none` is canonical. No row's `applies_when.date_range` is read. Three readings of dated rows
are in force, and none reaches this slot:
- A3 (30 Sep) reads a forbidden row's range against the house's date.
- U14 carried A3 to a dated canonical `none` return.
- U15 withholds a count that rests on an unstated date.

U14 and U15 are readings taken as recommended under Lucas's standing instruction of 1 Oct 2026,
never put.

**Measured.** Auditor A found it; it was reproduced before it was recorded.
georgian-colonial-american's resolved slot:
- makes `raised-panel-pair` canonical for 1700–1800;
- permits `louvered-pair` for 1750–1800 and `panel-below-louver-above` for 1760–1800;
- permits `none`, undated;
- forbids two rows, undated.

The Tidewater house restyled to it publishes `total_shutter_leaves` 2.0 dated 1765, dated 1850 and
undated. **One shipped plan reaches it.** good-03 (greek-revival-american, undated) inherits those
three dated rows and publishes 2.0.

**Why it is not fixed.** Under the rule as written the count does not depend on the date: shutters
are carried unless `none` is canonical, and `none` is undated. So U15 does not reach it. The date
matters only once someone decides what a canonical row out of its period means to a house. That is
A3's reading turned to the other status, and it is a ruling, not a reading of an existing one.

**What is not ruled:**
1. Is a canonical row read at the house's date, as A3 reads a forbidden one?
2. If it is, what does a dated house with no shutter-carrying canonical row in period draw? There
   are three candidates:
   - the corpus's default for a silent slot ("the older half of the corpus draws them");
   - no shutters;
   - unjudged, with the count withheld.
3. Does an undated house whose shutter rows are all dated withhold the count, as U15 withholds the
   sidelights' and the returns'?

The shutter fault's own constants are a separate question:
`oq/the-shutter-fault-clears-on-the-rhythm-while-the-sheet-refuses-the-leaves`.
