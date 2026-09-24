/* A WORD, DEFINED WHERE IT STANDS (WP-14.8, PRD §I.1).

   <Term id="binding-forbidden" />              the visible word is the record's `term`
   <Term field="kit.binding" value="open" />    resolved through the server's `by_field`
   <Term id="judgment-unjudged">not judged</Term>   children replace the visible word ONLY

   Ruled 24 Sep 2026: every definition the workbench shows is a glossary record, and the app
   writes none. This is the primitive that makes the ruling hard to break by accident, so its
   whole design is what it REFUSES to take: THERE IS NO DEFINITION PROP AND NO FALLBACK TEXT. A
   caller cannot hand it a gloss "just for now", and a missing record is not papered over with
   the id or a guess — it renders `noEntry(id)`, visibly, which `src/glossary.test.mjs` makes
   unreachable from shipped code by holding every literal id in the app to a record.
   `src/definitions.test.mjs` reads this file and fails if a prop is added or a phrase appears
   that is not one of the popover's own labels.

   WHAT IT IS. A real `<button type="button" class="tdl-term">` — focusable, announced, operable
   by Enter and Space — that opens a NON-MODAL `role="dialog"` popover labelled by the term
   (never `aria-modal`: the page behind stays live, and a definition is not a decision the
   reader must dismiss). Click, tap, Enter or Space opens it; a mouse resting on the word opens
   it after `HOVER_OPEN_MS`; Escape closes it and gives focus back to the word; one is open at a
   time and none survives a change of place or the palette opening (`help/popoverStore.js`).

   What the popover says, in order: the definition; the analogy in italic; the provenance line
   (the record's `kind` as the plain word it is, then its first source or the files it read);
   "not to be confused with", linking each confusable's own page; and "more", which is
   `#/cite/term:<id>`. Every one of those strings but the two labels is the record's.

   A TERM IS NEVER NESTED IN A BUTTON OR AN ANCHOR — a button inside either is invalid HTML and
   an unreachable control. Inside one, `useTermDescription(id)` gives the control what it needs
   to carry the meaning itself: `aria-describedby`, a `title`, and a visually hidden element
   holding the definition. */
import React from 'react';
import { useGlossary } from '../api/useGlossary.js';
import { termView, describeTerm } from '../glossary/termView.js';
import { placePopover } from '../help/placePopover.js';
import {
  popovers, ensurePopoverDom, openedByKeyboard, HOVER_OPEN_MS, HOVER_CLOSE_MS,
} from '../help/popoverStore.js';

export { noEntry } from '../glossary/termView.js';

/* Capture listeners take the flag as an object in both the add and the remove -- the one form
   every EventTarget matches (help/popoverStore.js says where a bare `true` did not). */
const CAPTURE = { capture: true };

/* React's ids carry colons; an id attribute tolerates them and a CSS selector does not. */
const domId = (uid, part) => `tdl-${part}-${String(uid).replace(/[^A-Za-z0-9_-]/g, '')}`;

function viewportRect() {
  const vv = typeof window !== 'undefined' ? window.visualViewport : null;
  if (vv) return { x: vv.offsetLeft, y: vv.offsetTop, width: vv.width, height: vv.height };
  return { x: 0, y: 0, width: window.innerWidth, height: window.innerHeight };
}

export function Term({ id, field, value, children }) {
  const glossary = useGlossary();
  const view = termView(glossary, { id, field, value });
  const uid = React.useId();
  const popId = domId(uid, 'term-pop');
  const labelId = domId(uid, 'term-label');
  const isOpen = React.useSyncExternalStore(
    popovers.subscribe, () => popovers.get() === uid, () => false);
  const btnRef = React.useRef(null);
  const popRef = React.useRef(null);
  const how = React.useRef(null);            // 'hover' | 'click' | 'keyboard'
  const focusPending = React.useRef(false);
  const timers = React.useRef({ open: null, close: null });
  const [pos, setPos] = React.useState(null);

  const clearTimers = React.useCallback(() => {
    clearTimeout(timers.current.open);
    clearTimeout(timers.current.close);
    timers.current = { open: null, close: null };
  }, []);
  const open = React.useCallback((by) => {
    clearTimers();
    how.current = by;
    focusPending.current = by === 'keyboard';
    popovers.open(uid);
  }, [uid, clearTimers]);
  const close = React.useCallback(() => {
    clearTimers();
    popovers.close(uid);
  }, [uid, clearTimers]);
  const closeSoon = React.useCallback(() => {
    clearTimeout(timers.current.close);
    timers.current.close = setTimeout(() => popovers.close(uid), HOVER_CLOSE_MS);
  }, [uid]);

  React.useEffect(() => { ensurePopoverDom(); }, []);
  React.useEffect(() => () => { clearTimers(); popovers.close(uid); }, [uid, clearTimers]);
  React.useEffect(() => {
    if (!isOpen) { how.current = null; focusPending.current = false; setPos(null); }
  }, [isOpen]);

  /* PLACEMENT. The popover is rendered hidden at (0, 0), measured, and moved to where
     `placePopover` says. It is `position: fixed`, and fixed is relative to the nearest
     TRANSFORMED ancestor where there is one (the loupe scales its plate with a transform), so
     the offset between where the style put it and where it actually landed is read back and
     subtracted: the popover lands where the arithmetic said whatever it is nested in. */
  React.useLayoutEffect(() => {
    if (!isOpen) return undefined;
    const place = () => {
      const b = btnRef.current;
      const p = popRef.current;
      if (!b || !p) return;
      const r = p.getBoundingClientRect();
      const offX = r.left - (parseFloat(p.style.left) || 0);
      const offY = r.top - (parseFloat(p.style.top) || 0);
      const a = b.getBoundingClientRect();
      const at = placePopover({
        anchor: { x: a.left, y: a.top, width: a.width, height: a.height },
        popover: { width: p.offsetWidth, height: p.scrollHeight },
        viewport: viewportRect(),
      });
      setPos({ left: at.left - offX, top: at.top - offY, maxWidth: at.maxWidth,
        maxHeight: at.maxHeight, side: at.side });
    };
    place();
    window.addEventListener('resize', place);
    window.addEventListener('scroll', place, CAPTURE);
    return () => {
      window.removeEventListener('resize', place);
      window.removeEventListener('scroll', place, CAPTURE);
    };
  }, [isOpen]);

  // A keyboard reader is taken INTO the definition, once it is where it will stay.
  React.useEffect(() => {
    if (isOpen && pos && focusPending.current && popRef.current) {
      focusPending.current = false;
      popRef.current.focus({ preventScroll: true });
    }
  }, [isOpen, pos]);

  /* Escape, and a pointer pressed anywhere else. Escape gives focus back to the word only when
     focus was on the word or in its definition — a definition that opened under a resting mouse
     while the reader types in a filter must not take the caret away, nor swallow the Escape the
     filter uses to clear itself. */
  React.useEffect(() => {
    if (!isOpen) return undefined;
    const onKey = (ev) => {
      if (ev.key !== 'Escape') return;
      const b = btnRef.current;
      const p = popRef.current;
      const active = typeof document !== 'undefined' ? document.activeElement : null;
      const inside = Boolean(active && ((b && b.contains(active)) || (p && p.contains(active))));
      close();
      if (inside) {
        ev.stopPropagation();
        if (b) b.focus();
      }
    };
    const onDown = (ev) => {
      const b = btnRef.current;
      const p = popRef.current;
      const t = ev.target;
      if ((b && b.contains(t)) || (p && p.contains(t))) return;
      close();
    };
    window.addEventListener('keydown', onKey, CAPTURE);
    document.addEventListener('pointerdown', onDown, CAPTURE);
    return () => {
      window.removeEventListener('keydown', onKey, CAPTURE);
      document.removeEventListener('pointerdown', onDown, CAPTURE);
    };
  }, [isOpen, close]);

  if (view.state === 'missing') {
    return <span className="tdl-term" data-term={view.key} data-missing="">{view.text}</span>;
  }
  if (view.state === 'loading') {
    return (
      <span className="tdl-term" data-term={view.key} data-loading="" aria-busy="true">
        {children ?? '…'}
      </span>
    );
  }
  if (view.state === 'failed') {
    return <span className="tdl-term" data-term={view.key} data-failed="">{children ?? view.text}</span>;
  }

  const onClick = (ev) => {
    if (isOpen && how.current !== 'hover') { close(); return; }
    open(openedByKeyboard(ev) ? 'keyboard' : 'click');
  };
  const onPointerEnter = (ev) => {
    if (ev.pointerType !== 'mouse') return;
    clearTimeout(timers.current.close);
    if (isOpen) return;
    clearTimeout(timers.current.open);
    timers.current.open = setTimeout(() => open('hover'), HOVER_OPEN_MS);
  };
  const onPointerLeave = () => {
    clearTimeout(timers.current.open);
    if (isOpen && how.current === 'hover') closeSoon();
  };
  const onPopBlur = (ev) => {
    const next = ev.relatedTarget;
    const p = popRef.current;
    if (!next || (p && p.contains(next)) || next === btnRef.current) return;
    close();
  };

  const style = pos
    ? { left: pos.left, top: pos.top, maxWidth: pos.maxWidth ?? undefined,
      maxHeight: pos.maxHeight ?? undefined }
    : { left: 0, top: 0, visibility: 'hidden' };

  return (
    <>
      <button type="button" ref={btnRef} className="tdl-term" data-term={view.key}
        aria-haspopup="dialog" aria-expanded={isOpen} aria-controls={popId}
        onClick={onClick} onPointerEnter={onPointerEnter} onPointerLeave={onPointerLeave}>
        {children ?? view.word}
      </button>
      {isOpen && (
        <span role="dialog" id={popId} aria-labelledby={labelId} ref={popRef} tabIndex={-1}
          className="tdl-term-pop" data-term-popover={view.key} data-side={pos ? pos.side : undefined}
          style={style}
          onPointerEnter={() => clearTimeout(timers.current.close)}
          onPointerLeave={() => { if (how.current === 'hover') closeSoon(); }}
          onBlur={onPopBlur}>
          <span className="tdl-term-pop-head">
            <span id={labelId} className="tdl-term-pop-word">{view.word}</span>
            {view.sense && <span className="tdl-term-pop-sense">{view.sense}</span>}
          </span>
          <span className="tdl-term-pop-def">{view.definition}</span>
          {view.analogy && <span className="tdl-term-pop-analogy">{view.analogy}</span>}
          <span className="tdl-term-pop-prov" data-kind={view.provenance.kind || undefined}>
            {view.provenance.kind}
            {view.provenance.items.map((item) => (
              <React.Fragment key={item}>{' · '}<code>{item}</code></React.Fragment>
            ))}
          </span>
          {view.confusables.length > 0 && (
            <span className="tdl-term-pop-conf">
              not to be confused with{' '}
              {view.confusables.map((c, i) => (
                <React.Fragment key={c.id || c.missing}>
                  {i > 0 && ', '}
                  {c.missing
                    ? <span data-missing="">{c.text}</span>
                    : <a href={c.href} data-confusable={c.id}>{c.term}</a>}
                  {c.sense && <span className="tdl-term-pop-sense">{c.sense}</span>}
                </React.Fragment>
              ))}
            </span>
          )}
          <a className="tdl-term-pop-more" href={view.moreHref}>more</a>
        </span>
      )}
    </>
  );
}

/* For a control a Term may not sit inside: spread `aria-describedby={describedBy}` and
   `title={title}` on it and render `element` beside it. The element is visually hidden and
   holds the definition — or, where there is no record, `noEntry(id)`, so the gap is announced
   rather than silent. */
export function useTermDescription(id) {
  const glossary = useGlossary();
  const uid = React.useId();
  const describedBy = domId(uid, 'term-desc');
  const d = describeTerm(glossary, id);
  const element = (
    <span id={describedBy} className="tdl-sr-only" data-term-description={id}>{d.text}</span>
  );
  return { describedBy, title: d.title, element };
}
