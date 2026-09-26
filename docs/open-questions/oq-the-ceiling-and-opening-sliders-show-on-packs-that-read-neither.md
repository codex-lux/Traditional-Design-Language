# oq/the-ceiling-and-opening-sliders-show-on-packs-that-read-neither — the Proportions page offers a ceiling and an opening slider on every non-order pack, and 22 of the 32 name neither in any rule

*Status: OPEN · Raised in: WP-14.24 (25 September 2026)*

**The finding.** WP-14.24 gave a class-A pack its own building-input slider and, on the ruling
of `oq/which-packs-module-is-a-building-input`, gave NO pack a slider for a dimension its module
is not. That ruling quotes the reason: *"a slider on these would be a lie about how they were set
out"*. The page's two older sliders, the ceiling and the opening, have been on every non-order
pack since WP-5.2. WP-14.24's own first draft of the comment beside them said *"(the rules read
them)"*. **Measured before it was committed, that is true of 10 of the 32 non-order packs.**

- **By expression.** A pack names `ceiling_height` or `opening_width` in some derived rule's
  expression on `adobe-module`, `brick-course`, `facade-classical`, `facade-picturesque`,
  `opening-pointed`, `opening-proportion`, `sash-light`, `timber-bay`, `trim-classical` and
  `trim-craftsman`. The other 22 name neither: `balcony-gallery`, `corbel-course`,
  `dutch-gambrel`, `facade-arcade`, `facade-gable`, `facade-medieval-english`, `facade-pavilion`,
  `facade-peristyle`, `facade-portada`, `jetty-overhang`, `log-module`, `moorish-arch`,
  `octagon-geometry`, `opening-craftsman`, `opening-mullioned`, `room-harmonic`,
  `room-vernacular`, `stone-course`, `storey-graduation`, `timber-panel`, `trim-prairie` and
  `trim-sawn`.
- **By behaviour.** The served payload was compared at the defaults, at a 132 in ceiling and at a
  60 in opening. The ceiling moved 4 packs and the opening 8, and 23 moved at neither. The 23rd
  is `timber-bay`, which does read the opening, through
  `floor((module - part * 2) / (opening_width + part * 2))`. That floor happens not to step
  between 36 and 60 in, so it is a step function and not a dead input. **The behavioural figure
  is a property of the two values tried.** The expression figure, 22, is the one that says a
  slider can never move a pack.

So on 22 packs, `room-harmonic` among them, the reader is offered two sliders that move nothing
on the plate or in the rules. Beside them, on `room-harmonic`, sits the one slider that does.

**What would have to be ruled.**

1. **Offer a slider only where the pack's rules read the input.** The list and pack routes would
   serve which inputs a pack reads (derived from the expressions, as `build/check_systems.py`
   already reads them), and the page gates on that, as it now gates the class-A slider on
   `module_bound_to`.
2. **Keep both sliders everywhere and say, on the page, which of them this pack reads.** A reader
   is not lied to, and the strip stays the same on every pack.
3. **Leave it.** The sliders are harmless in the sense that nothing wrong is drawn, and a slider
   that moves nothing is only a slider that moves nothing.

Nothing was changed for this at WP-14.24, because the ruling that package executed is about the
class-A slider. The comment in `workbench/app/src/proportions/page.js` states the measurement and
names this entry.
