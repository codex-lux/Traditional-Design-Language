# oq/register-is-not-style — folk and polite are not two styles, and the corpus has nowhere to say so

*Status: RULED 1 Sep 2026 · Raised in: WP-9.2, the plan-layer study (1 Sep 2026)*

**Lucas's ruling, 1 Sep 2026: register is a first-class axis, not style.** Nothing is built yet;
this entry records the ruling and what it commits the corpus to, in the shape OQ 51's entry
records its own.

## The question, as the study put it

Glassie names two passage populations in one clause and the axis between them is **social
register** — the builders' manuals against the folk grammar — not geography and not date:

> "the hallway, like the old Y1 and Y2 volumes, was the result of subtracting units from the
> square. Its Y3 dimensions left it narrower than the hallway of the Georgian type as offered in
> the builder's manuals of the day or as materialized on the grand plantations farther east."
> — Glassie 1975, p. 89, quoted in `docs/reports/wp-9.2-what-the-tradition-actually-does.md`
> (**at one remove; no facsimile has been read here**)

`rooms/centre-passage.json` already has the two populations and reaches them from
furnishability — *"SIX TO SEVEN FEET is a passage that circulates … TEN TO TWELVE FEET is a
passage that is a room … Decide which of the two it is, because the answer changes the plan's
whole width."* It names the choice and gives the reader no way to record which was made. The
corpus has `style` and it has no register.

## What the ruling settles

That the same house type at two registers is **one type**, not two styles. A folk centre-passage
house and a polite one share a diagram, a massing and a construction; what differs is how much of
the household's display budget the plan spends — and that difference shows up as a dimension, a
trim grade and a service arrangement rather than as a different set of forms.

So register may not be encoded by adding style nodes. `styles/` describes what a building is made
of and looks like; register describes how far up the social scale this instance of it sits. Two
axes, and the corpus now has to admit the second.

## What follows, per the study — each of these is a consequence, not a ruling of its own

1. **The passage width.** Four floors are stated across four files and the fault contradicts
   itself inside one record (`wp-9.2-the-parti-is-not-the-type.md` §6). The measured distribution
   is continuous from 6'8" to about 18 ft with no gap. Register is the axis that makes the spread
   legible; without it, any single floor convicts one population to acquit the other.
2. **The dining room's floor.** Kerr's *"A small Dining-room ought never to be less than 16 feet
   wide"* describes an English gentleman's house with a sideboard, a served course and a serving
   room. `rooms/dining-room.json` cites Kerr and sets `width_ft [12, 18]`. **The fix is not to
   raise the number** — it is to say which establishment the band is conditioned on.
3. **The trim grade**, which the corpus already treats as the primary hierarchy marker, and the
   **service arrangement** — detached kitchen, basement, hyphen-and-dependency — which
   `oq/the-parti-dissolved-its-own-dependencies` is about.

## What is NOT ruled, and must be before anything is built

- **Where register lives.** A field on the plan record (a property of *this house*), a field on
  the brief (a property of what was asked for), or a precondition vocabulary on the bands
  themselves. The study's Q4 is the same question wearing a different hat.
- **How many values it takes, and whether they are ordered.** "Folk / polite" is two; Kerr's own
  establishment ladder is longer; a register that is a small ordered set can be compared, one that
  is a free string cannot.
- **Whether it conditions a band or selects between bands.** `applies_when` already exists on the
  fault side for a precondition on measurements (WP-5.13). Reusing it is cheap and puts register
  where the test is; a second band per record puts it where the number is. These are different
  contracts and the choice is an authoring decision.
- **What a record says when its register is unknown.** *Unjudged is not passed*: a band with a
  register precondition that cannot be resolved must report could-not-evaluate, never quietly pick
  the permissive end.

## The trap this ruling walks into, stated now because it is predictable

**Register is a licence to condition a band, and a licence to condition is a licence to invent.**
The moment a band may say "16 ft if polite, 12 ft if folk", two numbers exist where one was
authored, and only one of them has a source. The corpus's first rule applies with full force:
either the second number has a source, or it is `editorial` / `judgment: true` and says so in its
own note.

And the study's own caution travels with this ruling: **every period quotation supporting it
reaches this tree at one remove**, checked verbatim against reproductions by an adversarial pass
but never against a facsimile. That is enough to justify an axis. It is not enough to populate the
axis with numbers.
