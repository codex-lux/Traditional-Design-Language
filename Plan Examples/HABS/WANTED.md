# HABS measured drawings wanted — the centre-passage / Georgian family

**For Lucas.** WP-9.2's ruling was that the session curates the list and you download the batch in
your browser. This is the list. Everything below has been verified to exist: the survey numbers,
item ids and drawing counts were read from loc.gov, and the *written* data for each building has
already been read and quoted in
`docs/reports/wp-9.2-the-parti-is-not-the-type.md`. What is missing is the **sheets** — the
measured drawings themselves — which are images and cannot be read from here.

**Where to put them:** `Plan Examples/HABS/<habs-number>/`, e.g.
`Plan Examples/HABS/VA-141/` for Gunston Hall. Keep the Library's own filename if you can; if you
rename, keep the sheet number in the name (`va0433-sheet-05.jpg`), because a transcription cites
the sheet and a sheet with no number cannot be cited.

**What to grab, in priority order:** the **first-floor plan** first, then the **basement or ground
plan**, then the **second-floor plan**, then any **section**. Elevations are the least useful for
this work — the arrangement layer is what Phase 9 is about, and the elevation layer already has
what it needs. Two or three plans from one building beat one plan each from six.

**Rights.** Do not let me or anyone else write a `license` field for these.
`build/harvest_habs.py` records the Library's rights sentence **verbatim** in `rights_evidence`
with the URL it was read from, and a person draws the conclusion — that is a settled decision of
this project and the reason is in that script's docstring. When you are on the item page, copy the
"Rights Advisory" line as it stands and drop it in with the images; I could not read it from here,
because `loc.gov/pictures` refuses extraction while `tile.loc.gov` allows it.

**And know what that line is worth before you rely on it.** It is collection-level boilerplate —
*"No known restrictions on images made by the U.S. Government; images copied from other sources
may be restricted"* — and `harvest_habs.py`'s docstring records that it is **byte-identical on a
government photograph and on a HABS photograph OF a third party's 1897 drawing held by the Free
Library of Philadelphia**. So copying it is necessary and settles nothing: it is evidence to
record, not clearance to publish. A measured drawing delineated for HABS by a named architect is
the ordinary case and is generally fine; a sheet the survey photographed from someone else's
drawing is not, and the rights line will read the same on both.

---

## The six buildings

| Building | HABS no. | item | landing page | sheets / data pages |
|---|---|---|---|---|
| **Gunston Hall**, 1755–59 | VA-141 | `va0433` | `loc.gov/pictures/item/va0433` | 30 drawings · 56 data pages |
| **Drayton Hall**, 1738–42 | SC-377 | `sc0132` | `loc.gov/pictures/item/sc0132` | 14–15 sheets · 14 + 19 data pages |
| **Hammond-Harwood House**, 1774–77 | MD-251 | `md0035` | `loc.gov/pictures/item/md0035` | — |
| **Mount Airy**, c. 1758 | VA-72 | `va0892` | `loc.gov/pictures/item/va0892` | — |
| **Westover**, c. 1726 | VA-402 | `va0315` | `loc.gov/pictures/item/va0315` | — |
| **Shirley** | VA-388 | `va0313` | `loc.gov/pictures/item/va0313` | — |

The gallery of sheets for any of them is
`https://www.loc.gov/resource/hhh.<item>.sheet?st=gallery` — that page shows every sheet as a
thumbnail with its number and title, which is how to find which one is the first-floor plan
without guessing. A single sheet is
`https://www.loc.gov/pictures/item/<item>.sheet.000NNa`.

**Sheet numbers confirmed so far** (read from loc.gov, not guessed — the rest are on the gallery
page):

- Gunston Hall `va0433`: sheet **2** is the location map and site plan; sheet **23** is the
  central passage. The plans are elsewhere in the 30 and the gallery will name them.
- Drayton Hall `sc0132`: sheet **7** is the southwest elevation, of 14. A published checklist
  cites "sheet 11/14 of 15" for a measured drawing by Belmont Freeman, 1974, and "Section B-B" —
  so the numbering has been quoted two ways and the gallery is the authority.

## Why these six and not others

They are the buildings the corpus's own partis name as exemplars —
`centre-passage-double-pile` names Drayton Hall, Hammond-Harwood and Gunston Hall;
`centre-passage-single-pile` names Tuckahoe and Shirley — plus Mount Airy and Westover, which
WP-9.2's package text asks for. **There is no point widening beyond this family**: Phase 9 exists
because of one complaint about one Tidewater Georgian sheet, and a precedent set that wanders into
other traditions calibrates nothing.

**One caveat carried forward.** `centre-passage-single-pile` names Shirley, and `va0313`'s written
data says of it: *"There is no hallway in the usual sense of the word, the stairhall being the
architectural feature of the house."* That reads like a misattribution, and Shirley's plan sheets
would settle it. It has not been changed on the strength of one extracted span.

## What happens when they land

1. Transcribe 5–10 plans into `plans/precedents/*.json` by multimodal reading — the WP-2.1
   precedent — with `provenance.method: "multimodal-reading"`, `field_confidence` per field, and
   the sheet cited by number. **Printed dimension strings are read as printed.** A figure scaled
   off the drawing by eye says so, at lower confidence, and never becomes `measured`.
2. **`build/measure_precedents.py` does not exist yet — it is to be written.** When it does, it
   runs the `build/arrangement.py` derivations (that one is real) over them and emits a generated
   table: passage-to-facade ratio, room proportions by type, flanking symmetry, stair
   position, portico alignment, service placement — per building, per sheet.
3. **The calibration run is the point.** The WP-9.1 critic goes over every precedent, and any
   conviction of a period building is either a band corrected here, citing the sheet, or a
   conviction defended by name in the report. A critic that convicts Drayton Hall is wrong until
   proven otherwise.
