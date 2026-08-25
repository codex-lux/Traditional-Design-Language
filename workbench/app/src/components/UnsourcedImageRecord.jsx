import React from "react";

/* 322 image records exist and zero images are sourced. The record IS the object: the shot
   spec is real, usable content and the alt text was written to be reasoned from. This must
   never render as a broken thumbnail — that would read as a bug rather than a stated state. */
function UnsourcedImageRecord({
  record,
  aspect = '4 / 3',
  onRequest,
  style
}) {
  return /*#__PURE__*/React.createElement("figure", {
    style: {
      margin: 0,
      border: '1px solid var(--rule)',
      background: 'var(--paper)',
      ...style
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      aspectRatio: aspect,
      display: 'grid',
      placeItems: 'center',
      color: 'var(--unsourced)',
      backgroundImage: 'var(--hatch-45)',
      borderBottom: '1px solid var(--rule)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-eyebrow)',
      letterSpacing: 'var(--tr-eyebrow)',
      textTransform: 'uppercase',
      color: 'var(--ink-2)',
      background: 'var(--paper)',
      padding: '3px 8px',
      border: '1px solid var(--rule)'
    }
  }, "specified \xB7 unsourced")), /*#__PURE__*/React.createElement("figcaption", {
    style: {
      padding: '11px 13px 13px'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--ink-4)'
    }
  }, record.id), /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--fw-med) 13px/1.5 var(--body)',
      color: 'var(--ink)',
      margin: '5px 0 0'
    }
  }, record.subject), /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--fw-reg) 12.5px/1.55 var(--body)',
      color: 'var(--ink-2)',
      margin: '7px 0 0',
      maxWidth: 'var(--measure-note)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-eyebrow)',
      letterSpacing: 'var(--tr-eyebrow)',
      textTransform: 'uppercase',
      color: 'var(--ink-3)',
      marginRight: 7
    }
  }, "shot spec"), record.shot_spec), record.alt && /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--fw-reg) 12.5px/1.55 var(--body)',
      color: 'var(--ink-3)',
      margin: '7px 0 0',
      maxWidth: 'var(--measure-note)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: 'var(--type-eyebrow)',
      letterSpacing: 'var(--tr-eyebrow)',
      textTransform: 'uppercase',
      color: 'var(--ink-4)',
      marginRight: 7
    }
  }, "alt"), record.alt), record.provenance_required && /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--ink-4)',
      margin: '9px 0 0'
    }
  }, "provenance required: ", record.provenance_required), onRequest && /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: function () {
      onRequest(record);
    },
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--gilt-deep)',
      marginTop: 10
    }
  }, "request this photograph")));
}
export default UnsourcedImageRecord;
export { UnsourcedImageRecord };
