import React from "react";

/* The record IS the object: the shot spec is real, usable content and the alt text was written
   to be reasoned from. A record with no file must never render as a broken thumbnail — that
   would read as a bug rather than a stated state.

   AND A RECORD WITH A FILE MUST NOT RENDER AS THOUGH IT HAD NONE, which is what this did for as
   long as it existed: it drew the hatched "specified · unsourced" plate unconditionally, so
   acquiring an image changed nothing anybody could see. The corpus now holds eleven drawn
   plates and this would have shown all eleven as gaps.

   A generated plate says so on its face. A drawing filed where the record asked for a
   photograph is a false claim if the viewer cannot tell which they are looking at. */
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
      aspectRatio: record.file ? undefined : aspect,
      display: 'grid',
      placeItems: 'center',
      color: 'var(--unsourced)',
      backgroundImage: record.file ? undefined : 'var(--hatch-45)',
      padding: record.file ? 8 : 0,
      borderBottom: '1px solid var(--rule)'
    }
  }, record.file ? /*#__PURE__*/React.createElement("img", {
    src: '/' + String(record.file).replace(/^\//, ''),
    alt: record.alt || record.subject || record.id,
    style: { display: 'block', maxWidth: '100%', height: 'auto' }
  }) : /*#__PURE__*/React.createElement("span", {
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
  }, record.id, record.status ? ' \xB7 ' + record.status : ''), /*#__PURE__*/React.createElement("p", {
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
  }, "alt"), record.alt), record.generated_from && /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--type-data-s)',
      color: 'var(--ink-3)',
      margin: '9px 0 0'
    }
  }, "generated from ", record.generated_from.pack, " \u2014 a drawing of the rule, not a photograph of a building"), record.rights && /*#__PURE__*/React.createElement("p", {
    style: {
      font: 'var(--type-data-s)',
      color: record.rights.publishable ? 'var(--ink-4)' : 'var(--unsourced)',
      margin: '6px 0 0'
    }
  }, "licence: ", record.rights.license, record.rights.publishable ? '' : ' \u2014 not cleared to publish'), record.provenance_required && /*#__PURE__*/React.createElement("p", {
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
