/* The three analytic overlay rules, in ONE spelling (WP-12.5).

   Until this file they lived inline in `Sheet.jsx`'s JSX — the privacy opacity ramp, the
   daylight reach and the wet predicate, written as expressions inside the elements that draw
   them. Surface ⑦ was the only reader, so that was tenable; the Round is the second, and a
   second transcription of a wash rule is this repository's most-repeated defect. The GATE was
   already shared (`derive.js::litWalls`, which answers "which of this room's declared window
   walls did the placement actually put on a boundary"); the ARITHMETIC was not.

   THE LIFT IS BEHAVIOUR-PRESERVING ON EVERY ROOM THIS CORPUS HOLDS, and the two places it is
   not are both cases the corpus authorises and does not yet contain. Each is named below and
   driven by a hand-built fixture in `overlays.test.mjs`, because a guard over what the sheets
   draw today could not fire on either.

   No React, no DOM: `round/overlays.js` runs under `node --test` and imports this. */

/* ---------------------------------------------------------------------- privacy

   The ramp `Sheet.jsx` has drawn since WP-5.2: rank 1 the palest, rank 5 the deepest. Its own
   comment records the fix that produced it — *"privacy_rank runs 1-5 across rooms/, not 1-6,
   so dividing by 6 meant the most private room never reached the top of the ramp"* — and that
   fix read the range off WHAT THE ROOM RECORDS USE.

   `build/check_rooms.py::PRIVACY_BANDS` states the range the corpus ALLOWS, and it is 0 to 5:
   *"0 street, 1 threshold, 2 public, 3 family, 4 private, 5 intimate"*, with `threshold` and
   `outdoor` both admitting 0. Measured: 60 room records, ranks 1-5 in use (8/13/23/12/4) and
   **no record carries 0**.

   THE FIRST VERSION OF THIS COMMENT SAID THE SHIPPED RAMP DREW RANK 0 AT AN OPACITY OF −0.01,
   AND A MUTATION PROVED THAT FALSE. `if (!rank) return null` catches 0 as FALSY before the
   arithmetic runs, so the shipped code returns null for it — reverting to that expression left
   the whole suite green, because a test on the VALUE could not tell the two apart. The guard
   was about nothing. What the shipped ramp really does, derived rather than re-read:

     rank  −1 →  −0.06   a NEGATIVE opacity            (not authorised)
     rank   0 →   null    dropped as though unranked    (AUTHORISED)
     rank 1-5 →  0.04 … 0.24                            (authorised, and unchanged here)
     rank   6 →   0.29    DARKER than the deepest room  (not authorised)

   So there are two defects and the falsy guard covers exactly one of them by accident. The
   ramp has **no bound in either direction**, and an out-of-band rank is washed rather than
   refused — that is the half a mutation can see, and the half these functions fix. Rank 0 is
   the other half: authorised, silently dropped as unranked, and told apart from a genuinely
   unranked room only by `privacyRefusal` naming it. Neither is reachable from the corpus.

   A street-rank room is REFUSED here rather than clamped or re-ramped. Clamping would draw it
   exactly like rank 1, which says the two are the same; re-ramping over 0-5 would move all
   five ranks a reader has been looking at since WP-5.2, to accommodate a room that does not
   exist. Where a street-rank room sits on this ramp is a question about the drawing that
   nobody has ruled, and the honest third state is to say so.
   See `oq/the-privacy-ramp-is-unbounded-and-does-not-cover-the-rank-its-own-band-admits`. */
export const PRIVACY_RAMP_MIN = 1;
export const PRIVACY_RAMP_MAX = 5;
export const PRIVACY_BASE = 0.04;
export const PRIVACY_RANGE = 0.20;

/* The wash, or `null` where none may be drawn. `null` is BOTH "no rank" and "a rank outside
   the ramp"; `privacyRefusal` is what tells them apart, so a surface that wants to disclose
   can, and one that does not simply draws nothing. */
export function privacyOpacity(rank) {
  if (typeof rank !== 'number' || Number.isNaN(rank)) return null;
  if (rank < PRIVACY_RAMP_MIN || rank > PRIVACY_RAMP_MAX) return null;
  const t = (rank - PRIVACY_RAMP_MIN) / (PRIVACY_RAMP_MAX - PRIVACY_RAMP_MIN);
  return PRIVACY_BASE + t * PRIVACY_RANGE;
}

/* Why no wash — a sentence, or null where one was drawn. Three states, never two: an unranked
   room type is UNJUDGED and a rank outside the ramp is REFUSED, and calling both "not drawn"
   in a caption would be the collapse this corpus names first. */
export function privacyRefusal(rank) {
  if (typeof rank !== 'number' || Number.isNaN(rank)) {
    return 'the room catalogue states no privacy_rank for this type';
  }
  if (rank < PRIVACY_RAMP_MIN || rank > PRIVACY_RAMP_MAX) {
    return `privacy_rank ${rank} is outside the ramp this sheet draws `
      + `(${PRIVACY_RAMP_MIN} to ${PRIVACY_RAMP_MAX}); no room in the corpus carries it and `
      + 'where it belongs on the ramp is unruled';
  }
  return null;
}

/* ---------------------------------------------------------------------- daylight

   Reach inward from a lit wall: the room's own window head times its own depth multiplier.

   **`|| 2.25` TURNED A STATED ZERO INTO THE DEFAULT.** `Sheet.jsx` read
   `roomsMeta[r.type]?.daylight_multiplier || 2.25`, and three room records — `closet`,
   `cold-room`, `linen-press` — state `daylight.depth_multiplier: 0`, which is a MEASURED ZERO
   meaning the room takes no daylight depth at all. `0 || 2.25` is 2.25, so a closet would have
   been washed to 2.25 × its head exactly like a parlour.

   MEASURED, because the honest count is not the alarming one: those three types are placed
   **12 times across 6 plans** including both shipped ones — and **0 of the 12 draw a wash**,
   because none of them declares a window and the overlay is gated on `litWalls`. So the defect
   is real in the code, authorised by the records, and unreachable from the corpus: latent, not
   drawn. Publishing 12 would have been three times its true size in the flattering direction
   for the fix (WP-11.14's rule), and the guard has to be DRIVEN (WP-8.11's).

   The fallback is kept for a type the catalogue does not hold at all — all 60 records state a
   multiplier, so it is unreachable too, and it is a decision about an unknown room rather than
   a check that cannot fire. */
export const DAYLIGHT_MULTIPLIER_FALLBACK = 2.25;
export const WINDOW_HEAD_FALLBACK_FT = 7;

/* The wash strengths. `Sheet.jsx` carried these as inline literals on the elements that draw
   them (`opacity=".16"`, `opacity=".2"`), and the Round would have re-typed both — which is
   how one overlay comes to read differently on two surfaces of the same house. They are the
   SOLID tokens at an opacity, exactly as the sheet draws them, and not the `--wash-*-1`
   tokens: `THREE.Color` cannot parse an `rgba()` and a viewer that silently failed to would
   have drawn the wash at full strength. */
export const DAYLIGHT_TOKEN = 'green';
export const DAYLIGHT_OPACITY = 0.16;
export const WET_TOKEN = 'blue';
export const WET_OPACITY = 0.20;
export const PRIVACY_TOKEN = 'sepia';

export function daylightReachFt(room, meta) {
  const head = (room && room.window_head_ft) || WINDOW_HEAD_FALLBACK_FT;
  const m = meta && meta.daylight_multiplier;
  // `== null` and not `||`: a stated 0 is the record's own answer and must survive.
  const mult = m == null ? DAYLIGHT_MULTIPLIER_FALLBACK : m;
  return mult * head;
}

/* ---------------------------------------------------------------------- wet

   A room on the plumbing stack. Two clauses because the records answer in two vocabularies:
   `servicing.plumbing` (measured: none 44, light 7, **heavy 9**) and `function_class`
   (**sanitary 6**). Both are reachable, so neither clause is dead. `light` is deliberately not
   wet — a bar sink is not a stack. */
export function isWet(meta) {
  if (!meta) return false;
  return meta.plumbing === 'heavy' || meta.function_class === 'sanitary';
}
