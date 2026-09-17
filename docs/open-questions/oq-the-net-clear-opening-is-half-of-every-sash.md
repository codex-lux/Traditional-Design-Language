# oq/the-net-clear-opening-is-half-of-every-sash — a double-hung's model applied to a casement, and a fault cleared by 1.4 inches on it

*Status: OPEN · Raised in: WP-13.1, the detection layer (15 September 2026)*

`build/elevation.py` supplies

```python
"net_clear_opening_height_in": upper_w["opening_height_in"] * 0.5,
```

and `egress-window-flips-the-proportion` carries a secondary test `net_clear_opening_height_in
at-least 24.0`. On `spec-builder-colonial` the supplied figure is **25.42 in**: the fault clears by
**1.4 inches** on a number that is half of another number.

## The 0.5 is not invented, which is why nothing was withheld

It is the lower sash's travel, and the fault record's own secondary note states that model in as
many words: *"In a double-hung the net clear opening is only the lower sash's travel, so the unit
needs roughly twice the ..."*. A figure derived from the corpus's own stated model is not the OQ 52
class, and treating it as one would have withheld a defensible number.

## What is wrong is the scope

**It is applied to every sash without asking what kind of sash it is.** A casement's leaf opens
whole: its net clear opening height is the full opening height, not half of it, so this halving
understates a casement's egress opening by a factor of two — in the direction that CONVICTS, which
is the safe-looking one and is still wrong. A hopper or an awning is different again.

The corpus already knows the answer. OQ 91 is the question *"two layers decide — the window grammar
says a window's ROLE, the kit its SASH KIND"*, and its vocabulary half is merged and ratcheted:
**119 of 159 styles answer the sash-kind question through the lineage.** The measurement has a
discriminator available and does not consult it.

## How it was found, which is the part worth carrying

By `build/detection.py --contradictions`. `arrangement.NOT_DERIVABLE` refuses this exact name with
the reason *"an egress-sash question; the plan states no sash operation or clear opening"* — and
the elevation layer supplies it anyway, so a reader of that table would conclude the corpus
declines to state a quantity on which a fault is being judged. Two layers, one quantity, opposite
answers, and nothing compared them until a reader was built for the join.

`critic_suspects.literal_ratios()` had the name on its list the whole time (`Mult 0.5`, line 1103).
It is invisible to `critique.classify` because the fault PASSES — see
`oq/clear-counts-a-pass-and-a-tautology-as-one-thing`.

## What has to be ruled

1. **Does the elevation layer read the sash kind for this?** The cascade answers on 119 of 159
   styles; the other 40 are the real question, and *unjudged is not passed* says the answer there
   is to withhold the measurement, not to keep halving.
2. **Is `0.5` right even for a double-hung?** The net clear opening is the travel less the meeting
   rail's own thickness, and the corpus states a meeting rail height (`sash_meeting_rail_height_in
   = 1.25`, itself a literal). Whether that refinement is worth making is a separate call from
   whether the sash kind is.
3. **Do not close it by widening the threshold.** 24.0 in is IRC R310.2.1 and is the one number in
   this question with a source.

## What must not be done

Do not delete the `arrangement.NOT_DERIVABLE` entry. Its reason has been corrected to name the
supplier; the entry itself is what stops a SECOND derivation of the quantity arriving in the
arrangement layer, which would be two numbers under one name — the OQ 48 error.
