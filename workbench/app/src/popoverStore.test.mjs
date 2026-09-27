/* ONE DEFINITION OPEN AT A TIME, AND NONE ACROSS A CHANGE OF PLACE (WP-14.8, PRD §I.1).

   `help/popoverStore.js` is driven here with bare `EventTarget`s standing in for the window and
   the document, so every closing condition is exercised under `node --test` with no browser.
   Each "closes" case is paired with the nearest case that must NOT close, because a store that
   closed on every keystroke or every focus would pass a test that only asked for closing. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  createPopoverStore, bindPopoverDom, isPaletteKey, isInsideModal, openedByKeyboard,
  HOVER_OPEN_MS, HOVER_CLOSE_MS,
} from './help/popoverStore.js';

/* An EventTarget event carrying the fields a real one would. */
function ev(type, fields = {}) {
  const e = new Event(type);
  for (const [k, v] of Object.entries(fields)) Object.defineProperty(e, k, { value: v });
  return e;
}

/* A target for a focusin: a stand-in element whose `closest` answers as a DOM element would. */
const insideModal = { closest: (sel) => (sel === '[aria-modal="true"]' ? {} : null) };
const outsideModal = { closest: () => null };

test('the hover delay is the PRD’s 400 ms, and the grace to cross to the popover is shorter', () => {
  assert.equal(HOVER_OPEN_MS, 400);
  assert.ok(HOVER_CLOSE_MS > 0 && HOVER_CLOSE_MS < HOVER_OPEN_MS);
});

test('opening one closes the other: there is one slot', () => {
  const s = createPopoverStore();
  let heard = 0;
  s.subscribe(() => { heard += 1; });
  s.open('a');
  assert.equal(s.get(), 'a');
  assert.ok(s.isOpen('a'));
  s.open('b');
  assert.equal(s.get(), 'b');
  assert.ok(!s.isOpen('a'));
  assert.equal(heard, 2);
  s.open('b');
  assert.equal(heard, 2, 'opening what is already open changes nothing and says nothing');
});

test('a late close cannot close the popover that replaced it', () => {
  const s = createPopoverStore();
  s.open('a');
  s.open('b');
  s.close('a');                      // a hover timer on 'a' firing after 'b' was clicked
  assert.equal(s.get(), 'b');
  s.close('b');
  assert.equal(s.get(), null);
});

test('closeAll closes whatever is open, and is silent when nothing is', () => {
  const s = createPopoverStore();
  let heard = 0;
  s.subscribe(() => { heard += 1; });
  s.closeAll();
  assert.equal(heard, 0);
  s.open('a');
  s.closeAll();
  assert.equal(s.get(), null);
  assert.equal(heard, 2);
  assert.ok(!s.isOpen(null) && !s.isOpen(undefined));
});

test('a change of place closes every popover', () => {
  const s = createPopoverStore();
  const win = new EventTarget();
  const doc = new EventTarget();
  bindPopoverDom(s, { win, doc });
  s.open('a');
  win.dispatchEvent(ev('hashchange'));
  assert.equal(s.get(), null);
});

test('the palette key closes every popover; a plain k does not', () => {
  const s = createPopoverStore();
  const win = new EventTarget();
  bindPopoverDom(s, { win, doc: new EventTarget() });
  s.open('a');
  win.dispatchEvent(ev('keydown', { key: 'k' }));
  assert.equal(s.get(), 'a', 'typing the letter k in a field is not the palette');
  win.dispatchEvent(ev('keydown', { key: 'k', metaKey: true }));
  assert.equal(s.get(), null);
  s.open('b');
  win.dispatchEvent(ev('keydown', { key: 'K', ctrlKey: true }));
  assert.equal(s.get(), null);
});

test('focus arriving inside a modal closes every popover; focus elsewhere does not', () => {
  const s = createPopoverStore();
  const doc = new EventTarget();
  bindPopoverDom(s, { win: new EventTarget(), doc });
  s.open('a');
  doc.dispatchEvent(ev('focusin', { target: outsideModal }));
  assert.equal(s.get(), 'a');
  doc.dispatchEvent(ev('focusin', { target: insideModal }));
  assert.equal(s.get(), null);
});

test('the returned function stops listening, on both targets', () => {
  const s = createPopoverStore();
  const win = new EventTarget();
  const doc = new EventTarget();
  const unbind = bindPopoverDom(s, { win, doc });
  unbind();
  s.open('a');
  win.dispatchEvent(ev('hashchange'));
  win.dispatchEvent(ev('keydown', { key: 'k', metaKey: true }));
  doc.dispatchEvent(ev('focusin', { target: insideModal }));
  assert.equal(s.get(), 'a');
});

test('the predicates read what they say and nothing else', () => {
  assert.ok(isPaletteKey({ key: 'k', metaKey: true }));
  assert.ok(isPaletteKey({ key: 'K', ctrlKey: true }));
  assert.ok(!isPaletteKey({ key: 'k' }));
  assert.ok(!isPaletteKey({ key: 'j', metaKey: true }));
  assert.ok(!isPaletteKey(null));
  assert.ok(isInsideModal(insideModal));
  assert.ok(!isInsideModal(outsideModal));
  assert.ok(!isInsideModal({}), 'a target that is not an element is inside nothing');
  assert.ok(!isInsideModal(null));
  assert.ok(openedByKeyboard({ detail: 0 }));
  assert.ok(!openedByKeyboard({ detail: 1 }));
  assert.ok(!openedByKeyboard(null));
});
