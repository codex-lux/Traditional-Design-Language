# oq/a-source-is-a-free-string-and-nothing-can-tell-a-book-from-a-fiction — 422 strings, 0 locators, and one confirmed invention cited by five nodes

*Status: OPEN · Raised in: WP-11.7, Tranche 4 (7 Sep 2026)*

**Phase 11 built a locatable evidence layer for BUILDINGS and left the layer for BOOKS exactly as
it found it.** `precedents/` gives a building a record, a `survey`, archival refs that each state
`retrieved` and `via`, quotations held to the printed page by `as_printed`, and a checker that
holds the two directions to each other. A SOURCE, one field over in the same file, is this:

```json
"sources": { "type": "array", "items": { "type": "string" } }
```

Measured over the corpus after Tranche 4: **422 distinct strings, 762 citations, 0 URLs, 63 with
no year at all, 321 cited exactly once.** Nothing in the tree asks whether a source exists,
resolves, is quoted correctly, or is the work its citing node thinks it is. The `check_research.py`
meter counts strings and their sharing; it cannot read one.

## The live instance, and it is a fiction on five buildable nodes

`Dan Cruickshank and Peter Wyld, Georgian Buildings of Britain and Ireland (1975)` **names no book
that exists.** It is two real works welded together, found by the `british-isles` auditor searching
both directions and finding no catalogue anywhere that carries that author pair, that title and
that year:

- Cruickshank **and Wyld**, **1975** → *London: The Art of Georgian Building* (Architectural Press)
  — the authors and the year, a different title.
- *A Guide to the Georgian Buildings of Britain and Ireland* → **Cruickshank alone**, **1985**,
  Weidenfeld & Nicolson — the title, one author, a decade later.

It is cited by `english-georgian-country-house`, `english-georgian-townhouse`, `english-georgian`,
`english-palladian` and `regency`. **All five predate this package**; Tranche 4 nearly propagated it
to `english-classical` as a sixth and the auditor removed it there. **It survived every check this
corpus runs, on five nodes, for as long as it has existed**, because there is no check to survive.

Note what the removal could NOT do: the auditor deliberately did not substitute a corrected title,
because the corpus cannot record which of the two books was meant, and guessing is how a citation
becomes an invention in the first place.

## Why this is a question and not a patch

The obvious fix — give `sources` the `precedents/` treatment: a record per work, an id, a locator,
a `retrieved` and a `via` — is a package of its own, and inventing the mechanism late in a session
is how WP-9.4 shipped four guards that could not fire. Four things must be ruled first.

1. **Where a work's record lives.** `works/<id>.json` beside `precedents/`, or a `sources` block on
   the node that carries structure instead of a string. The first makes one work one record, which
   is the whole reason `precedents/` is shaped the way it is; the second is cheaper and keeps the
   defect that a work has as many identities as it has citing nodes
   (`oq/one-work-is-cited-under-several-strings-and-every-source-count-is-inflated`).
2. **What a locator IS for a book.** A building has an archival register with a stable number. A
   book has an ISBN (absent for anything before 1970 and for every journal article), an OCLC
   number, a DOI (journals only), or a URL to a catalogue page. **None of the four covers the
   corpus's actual population**, which runs from Vitruvius to a 1920 *Annales de Géographie*
   article to a 2013 field guide.
3. **What happens to the 422 that exist.** Retro-fitting every one needs a live research tier, and
   the tier is currently degraded: Tavily returned HTTP 433 (pay-as-you-go limit) to every call in
   this package, and `WebFetch` is egress-blocked for archive.org, WorldCat, Google Books,
   openlibrary, HathiTrust and JSTOR. **A structure nobody can populate is worse than a string**,
   because it reads as though it has been checked.
4. **Whether an unresolvable source is refused or recorded.** *Unjudged is not passed* says a work
   nobody could confirm must not read as a confirmed one — but 321 strings are cited once and most
   of them are perfectly real books whose catalogue page this container cannot reach.

## What was done instead of ruling it

Nothing mechanical, deliberately. The finding is recorded here, in
`docs/reports/wp-11.1-the-bench-without-a-literature.md` §XIV, and in the five nodes' own citation
of a book that is not a book — **which is left in place**, because deleting it would remove the
only evidence that the class exists while doing nothing about the class.
