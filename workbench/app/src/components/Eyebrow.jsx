import React from "react";

function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/* The 10px / .16em uppercase mono label. A shipped convention; a component so the
   tracking cannot drift.

   THE DEFAULT INK IS `--ink-2` (WP-14.8). It was `--ink-3`, which measures 3.15:1 on
   `--paper` -- under the 4.5:1 a label this small needs -- and the eyebrow is what names a page,
   a section and a rail group, so the ink the reader meets most often was the one below the
   floor. `--ink-2` is 4.85:1 there (4.32:1 on `--paper-deep`) and is a token the standard already names; no colour is added.
   The count beside the label takes the label's own ink rather than `--ink-4` (2.26:1), because it
   is readable text and the standard keeps `--ink-4` for construction and disabled marks.

   AND THERE IS NO FAINT TONE TO ASK FOR (WP-14.31). `tertiary` (`--ink-3`) and `quiet`
   (`--ink-4`) were kept for a caller that asked for them by name, and two callers did: a
   pointer on Brief Intake and the decision kinds on the Candidate Set, both words a reader reads.
   An eyebrow is always text, so a faint tone on it is always faint text; both are gone, and
   `src/inks.test.mjs` refuses a table entry that brings one back. */
function Eyebrow({
  children,
  tone = 'secondary',
  count,
  as = 'div',
  style,
  ...rest
}) {
  const tones = {
    body: 'var(--ink)',
    secondary: 'var(--ink-2)',
    accent: 'var(--gilt-deep)',
    paper: 'var(--ink-2)'
  };
  const Tag = as;
  return /*#__PURE__*/React.createElement(Tag, _extends({
    style: {
      font: 'var(--type-eyebrow)',
      letterSpacing: 'var(--tr-eyebrow)',
      textTransform: 'uppercase',
      color: tones[tone] || tones.secondary,
      ...style
    }
  }, rest), children, count != null && /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'inherit',
      marginLeft: 8
    }
  }, count));
}
export default Eyebrow;
export { Eyebrow };
