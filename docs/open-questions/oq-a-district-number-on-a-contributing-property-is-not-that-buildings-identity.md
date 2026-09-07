# oq/a-district-number-on-a-contributing-property-is-not-that-buildings-identity — the duplicate guard is dropping 51 identities, and some of the drops are right

*Status: OPEN · Raised in: WP-11.6, from a red test left by WP-11.5 (5 Sep 2026)*

**OPEN — and the honest form of it is that a single exemption is doing two opposite jobs.**
`check_precedents.py::identity_keys` collects every archival identity a record carries, and the
duplicate guard compares those sets across 695 records. On an nrhp/nhl reference it skips the id
when the record declares a `record_kind` in `NOT_ONE_BUILDING`, and — the fallback, for a record
that predates the field or forgets it — when `DISTRICT_RE` matches the reference's own title or
note. **Measured: the fallback fires 51 times.**

**Some of those drops are exactly right.** Four Great Smoky Mountains cabins
(`carter-shields-cabin`, `ephraim-bales-place`, `henry-whitehead-place`, `tipton-place`) all carry
NRHP **77000111**; two Cleveland Heights houses (`1251-oakridge-road`, `1315-inglewood-drive`) both
carry **09000210**; two Chestnut Hill records both carry **85001334**. In each the number names the
LISTING and not the building, so without the exemption the guard would report duplicates that are
not duplicates.

**And some are exactly wrong, in the direction that is invisible.** Twenty-seven of the 51 match on
the reference's TITLE alone, and they are individual buildings whose own listing happens to name the
district they contribute to: Marble House (71000025), The Elms (71000021), Rosecliff (73000059),
the Boston Athenaeum (66000132), the Boston Public Library McKim building (73000317), Cliveden
(66000677), Hill-Stead (91002056), the Palace of the Governors (66000489), Taos Pueblo (66000496),
and eighteen more. Each of those numbers IS that building's identity, and each is being dropped from
the guard. **It is a false silence and never a false error, which is why nothing caught it and why
neither the checker's exit code nor any ratchet moved when it began.**

## What is actually missing

The exemption is written as a property of the RECORD — is this one building? — and the thing it
needs to know is a property of the REFERENCE: **does this number name one building, or a listing
that covers many?** The corpus has no field for that. A contributing property and a district-only
listing look identical from inside a record: both are a real nrhp id on a real house whose paperwork
mentions a district.

## What must be ruled

1. **Where the fact lives.** A flag on the reference (`covers: building | listing`), or a rule that
   an id shared by two records is a listing id and an id held by one is a building id — the second
   needs no authoring and is circular with the guard it feeds.
2. **What an undeclared record means now.** `record_kind` is authoritative and 42 records declare a
   non-building kind. Declaring `building` on the 27 would fix them one at a time, because the
   fallback already refuses to exempt a declared building — but that is 27 hand-adjudications and
   it leaves the class open for the next tranche.
3. **Whether the fallback should read the NOTE at all.** Seven of the 51 match on the note only,
   and a note is where a record explains its context; a rule that reads context as classification
   will keep doing this.

## What was done instead of ruling it

`counts["identity_dropped_by_regex"]` is measured, ratcheted at **51** as a ceiling, and PRINTED on
every run saying that some drops are right and some are not and nothing tells them apart. That is
the *unjudged is not passed* discipline applied to a guard rather than to a measurement: the guard
declines to check 51 ids and now says so, where before it read exactly like a guard that checked
them and found nothing.

**Do not close this by deleting the fallback.** Measured: that would report the four Smoky Mountains
cabins and the two Cleveland Heights houses as duplicate archival ids, which they are not.
