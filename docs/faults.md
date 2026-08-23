# The fault corpus

209 named errors. This is the layer that turns a reference into a teaching tool, and the one that catches cheap execution before it gets built.

## Element-first, style as a facet

Faults hang off **slots**, not styles. The half-width shutter is wrong on every house that has shutters, and authoring it 164 times would hide the pattern rather than reveal it. 93 of 95 slots carry at least one fault — `wall_thickness_masonry` and `wall_thickness_frame` (added in WP-1.3, 23 Aug 2026) are the two not yet covered.

Style enters twice, and the second way matters more:

- **`applies_to`** — usually the single token `universal`.
- **`exceptions`** — where a style legitimately does the thing that is a fault everywhere else. There are **846 of these, 496 carrying a numeric bound**, and they are the difference between a corpus that improves a design system and one that makes it timid.

A Georgian entry portico is five feet deep. That is a fatal fault by Craftsman rules — a porch under seven feet cannot be inhabited — and entirely correct by its own, because a portico is a piece of the order rather than an outdoor room. Shingle Style runs shingles over a corner with no corner board, which is an omission fault anywhere else; the licence turns out to be narrower than it looks, because it permits *omitting* a member and not *substituting* one, so a mitred-and-caulked corner still fails. `inverted_by` handles the cases with a polarity: a crisp arris is correct almost everywhere and wrong on Cape Dutch, Pueblo and Andalusian, where the fault is the absence of softening — and the bounds show why a 3/8-inch machine bullnose is the worst answer of all, too hard to read as adobe and too soft to read as masonry.

## The cause is almost never ignorance

Of 209 faults, exactly **one** has `driver: ignorance`. The rest are stock sizes, trade sequences, catalog defaults, code minima, material substitutions and line items. The flush window in a masonry wall is a *schedule* problem — the window is set before the mason arrives, and the reveal is the leftover.

Naming the driver is what makes a fault fixable rather than merely deplorable, and it is why every entry carries `cost_saved`. **32 faults are `cost_negative`**: they cost money to get wrong. Nobody is defending a budget on those, which changes the conversation entirely.

Every fault carries three fixes: `right`, `cheap` — the best answer at no added cost, which is the tier that actually gets built — and `dishonest`, the tempting shortcut that looks like a fix and is not. Naming the third is protective.

## The corpus is executable

Every fault carries a `test`: an expression, a threshold, a direction, and whether it can be evaluated from a photograph. 209 primary tests plus 273 secondary; **175 are photograph-evaluable**.

```
tdl_measurement_vocabulary(slot="shutter")     → the variable names, exactly
tdl_check_measurements({"shutter_leaf_width_in": 12,
                        "window_opening_width_in": 32}, style="colonial-revival")

→ PRESENT [fatal] The Half-Width Shutter
  value 0.375, required at-least 0.48
  cheap fix: delete the shutters — on a facade where correct shutters cannot be
  afforded, none is not a compromise but a legitimate historical condition
```

Anything the corpus could not judge is returned as **unjudged, never as passed**. That distinction is the whole difference between a tool that helps and one that reassures.

## Two axes of severity

`severity` scores the style reading. `severity_in_use` scores whether the house is good to live in. They diverge: a waste stack with nowhere to land is invisible from the street and fatal in occupation. A corpus that scores only what shows from the sidewalk would quietly deprioritise everything that decides whether the plan works, so both are recorded.

`severity_by_style` handles the rest — a missing chimney is fatal on Tudor Revival and Prairie and unremarkable on a ranch.

## Provenance

Derived from HABS documentation, NPS Preservation Briefs, the model codes, period millwork and sash catalogues, Asher Benjamin, manufacturer literature for the modern failure modes, and first principles. The corpus deliberately does not reproduce the text, structure or illustration sequence of any in-copyright book; it stands on its own sources, cited per entry.
