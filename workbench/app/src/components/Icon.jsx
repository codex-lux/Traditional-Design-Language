import React from "react";

function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/* Lucide, loaded from CDN and masked so it takes currentColor. SUBSTITUTION: the TDL
   sources define no icon set (see readme.md ICONOGRAPHY). Swap CDN + name map here and
   nothing else in the system changes. Icons never appear on the drawing sheet. */
const CDN = 'https://unpkg.com/lucide-static@0.474.0/icons/';
function Icon({
  name,
  size = 16,
  style,
  title,
  ...rest
}) {
  const url = 'url("' + CDN + name + '.svg")';
  return /*#__PURE__*/React.createElement("span", _extends({
    role: title ? 'img' : 'presentation',
    "aria-label": title,
    title: title,
    style: {
      display: 'inline-block',
      width: size,
      height: size,
      flex: 'none',
      background: 'currentColor',
      WebkitMaskImage: url,
      maskImage: url,
      WebkitMaskSize: 'contain',
      maskSize: 'contain',
      WebkitMaskRepeat: 'no-repeat',
      maskRepeat: 'no-repeat',
      WebkitMaskPosition: 'center',
      maskPosition: 'center',
      verticalAlign: 'middle',
      ...style
    }
  }, rest));
}
export default Icon;
export { Icon };
