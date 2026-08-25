import React from "react";

function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/* The 10px / .16em uppercase mono label. A shipped convention; a component so the
   tracking cannot drift. */
function Eyebrow({
  children,
  tone = 'tertiary',
  count,
  as = 'div',
  style,
  ...rest
}) {
  const tones = {
    body: 'var(--ink)',
    secondary: 'var(--ink-2)',
    tertiary: 'var(--ink-3)',
    accent: 'var(--gilt-deep)',
    quiet: 'var(--ink-4)',
    paper: 'var(--ink-2)'
  };
  const Tag = as;
  return /*#__PURE__*/React.createElement(Tag, _extends({
    style: {
      font: 'var(--type-eyebrow)',
      letterSpacing: 'var(--tr-eyebrow)',
      textTransform: 'uppercase',
      color: tones[tone] || tones.tertiary,
      ...style
    }
  }, rest), children, count != null && /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--ink-4)',
      marginLeft: 8
    }
  }, count));
}
export default Eyebrow;
export { Eyebrow };
