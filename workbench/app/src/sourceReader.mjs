/* THE SOURCE READER THE COPY RATCHETS SHARE (WP-14.33's audit). Test-only: two test files import
   it and nothing in the app does, so it never reaches the bundle, and `node --test` does not run it.

   Comments are not copy, and neither is code -- and the two ratchets that read the app's copy
   (`copy_ratchet.test.mjs`, `readerCopy.test.mjs`) each stripped comments with the same pair of
   regular expressions, which could not tell a comment from a string holding its characters: the
   file-type pattern in `Transcription.jsx`'s `accept=` attribute, a slash and then a star, opened a
   "comment" that ran to the next star-slash 79 lines later, and every scanner in both files was
   blind to those 79 lines. (This comment cannot quote the two characters: written here, the pair
   would end it -- which is the defect, once more.) The regexes were line-based on purpose, because
   a tokenizer tracking quotes would be thrown by the apostrophes in JSX text. This one is not: it
   knows when it is in JSX text, where an apostrophe is a letter, and when it is in JavaScript,
   where a quote opens a string.

   No parser may be imported (the suite runs with no npm install, `no_bare_imports.test.mjs`), so it
   lexes just enough: comments, strings, template literals, regular-expression literals, balanced
   brackets and JSX elements. HELD AGAINST `@babel/parser` over every file under src/ on the day it
   was written, outside the suite: the same 2,810 comments, and the same 43 JSX paragraphs and 67
   string literals of twelve or more words. That check shares the block-element list below with
   this reader, so it proves the lexing and the element tree, not the list. */

const IDENT = /[A-Za-z0-9_$]/;
const EXPR_KEYWORDS = new Set(['return', 'case', 'typeof', 'void', 'delete', 'in', 'of', 'new',
  'else', 'do', 'yield', 'await', 'throw']);

export const BLOCK = new Set(['p', 'div', 'section', 'article', 'header', 'footer', 'nav', 'aside',
  'main', 'ul', 'ol', 'li', 'dl', 'dt', 'dd', 'table', 'thead', 'tbody', 'tfoot', 'tr', 'td', 'th',
  'caption', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'figure', 'figcaption', 'form', 'fieldset',
  'legend', 'blockquote', 'pre', 'details', 'summary', 'svg', 'g', 'text', 'tspan', 'title',
  'desc', 'foreignObject', 'select', 'option', 'textarea', 'input', 'hr', 'img', 'canvas',
  'video', 'iframe']);

/* Does the `/` or `<` at `i` begin an operand (a regex, JSX) rather than an operator? */
function operandPosition(src, i) {
  let k = i - 1;
  while (k >= 0 && /\s/.test(src[k])) k -= 1;
  if (k < 0) return true;
  const c = src[k];
  if ('([{,;:=?!&|+-*%~^<>'.includes(c)) return true;
  if (IDENT.test(c)) {
    let s = k;
    while (s >= 0 && IDENT.test(src[s])) s -= 1;
    return EXPR_KEYWORDS.has(src.slice(s + 1, k + 1));
  }
  return false;
}

/* JavaScript's escapes, cooked the way the engine cooks them. */
export function cook(raw) {
  return raw.replace(/\\(u\{([0-9a-fA-F]+)\}|u([0-9a-fA-F]{4})|x([0-9a-fA-F]{2})|\r?\n|.)/g,
    (m, all, cp, u4, x2) => {
      if (cp) return String.fromCodePoint(parseInt(cp, 16));
      if (u4) return String.fromCharCode(parseInt(u4, 16));
      if (x2) return String.fromCharCode(parseInt(x2, 16));
      if (all === '\n' || all === '\r\n') return '';
      return { n: '\n', t: '\t', r: '\r', b: '\b', f: '\f', v: '\v', 0: '\0' }[all] ?? all;
    });
}

function stringEnd(src, i) {
  const q = src[i];
  let k = i + 1;
  while (k < src.length && src[k] !== q) {
    if (src[k] === '\\') k += 1;
    else if (src[k] === '\n') break;
    k += 1;
  }
  return k + 1;
}

function regexEnd(src, i) {
  let k = i + 1;
  let klass = false;
  while (k < src.length) {
    const c = src[k];
    if (c === '\\') { k += 2; continue; }
    if (c === '\n') return i + 1;
    if (klass) { if (c === ']') klass = false; } else if (c === '[') klass = true;
    else if (c === '/') { k += 1; break; }
    k += 1;
  }
  while (k < src.length && /[a-z]/.test(src[k])) k += 1;
  return k;
}

class Reader {
  constructor(src) {
    this.src = src;
    this.comments = [];
    this.literals = [];     // [text, index]
    this.roots = [];        // JSX elements reached from JavaScript
  }

  /* A comment at `k`, if one starts there: its end, after recording it. */
  comment(k) {
    const s = this.src;
    if (s[k] !== '/') return -1;
    if (s[k + 1] === '/') {
      let e = s.indexOf('\n', k);
      if (e < 0) e = s.length;
      this.comments.push([k, e]);
      return e;
    }
    if (s[k + 1] === '*') {
      let e = s.indexOf('*/', k + 2);
      e = e < 0 ? s.length : e + 2;
      this.comments.push([k, e]);
      return e;
    }
    return -1;
  }

  template(k) {
    const s = this.src;
    let j = k + 1;
    let raw = '';
    while (j < s.length && s[j] !== '`') {
      if (s[j] === '\\') { raw += s.slice(j, j + 2); j += 2; continue; }
      if (s[j] === '$' && s[j + 1] === '{') {
        j = this.js(j + 2, '}') + 1;
        raw += ' {…} ';
        continue;
      }
      raw += s[j];
      j += 1;
    }
    return [j + 1, cook(raw)];
  }

  /* One operand after a `+` in a chain: an identifier, a member or call chain, a number or a
     bracketed expression. Returns its end. */
  operand(k) {
    const s = this.src;
    while (k < s.length && /\s/.test(s[k])) k += 1;
    if (s[k] === '(' || s[k] === '[') {
      const close = s[k] === '(' ? ')' : ']';
      k = this.js(k + 1, close) + 1;
    } else if (/[A-Za-z0-9_$]/.test(s[k] || '')) {
      while (k < s.length && /[A-Za-z0-9_$]/.test(s[k])) k += 1;
    } else return -1;
    for (;;) {
      if (s[k] === '.' && /[A-Za-z_$]/.test(s[k + 1] || '')) { k += 1; while (/[A-Za-z0-9_$]/.test(s[k] || '')) k += 1; }
      else if (s[k] === '?' && s[k + 1] === '.') { k += 2; while (/[A-Za-z0-9_$]/.test(s[k] || '')) k += 1; }
      else if (s[k] === '(') k = this.js(k + 1, ')') + 1;
      else if (s[k] === '[') k = this.js(k + 1, ']') + 1;
      else return k;
    }
  }

  /* JavaScript from `k` to the `stop` character at depth 0 (or the end). Returns stop's index. */
  js(k, stop) {
    const s = this.src;
    let depth = 0;
    let chain = null;
    const flush = () => { if (chain) this.literals.push(chain); chain = null; };
    const literal = (text, at) => {
      if (chain) chain[0] += text; else chain = [text, at];
      // a chain continues only across `+`
      let j = this.after;
      for (;;) {
        while (j < s.length && /\s/.test(s[j])) j += 1;
        const c = this.comment(j);
        if (c < 0) break;
        j = c;
      }
      if (s[j] === '+' && s[j + 1] !== '+' && s[j + 1] !== '=') {
        let n = j + 1;
        while (n < s.length && /\s/.test(s[n])) n += 1;
        if (s[n] === "'" || s[n] === '"' || s[n] === '`') return n;         // next literal joins
        const e = this.operand(n);
        if (e > 0) {
          chain[0] += ' {…} ';
          let m = e;
          while (m < s.length && /\s/.test(s[m])) m += 1;
          if (s[m] === '+' && s[m + 1] !== '+' && s[m + 1] !== '=') {
            let q = m + 1;
            while (q < s.length && /\s/.test(s[q])) q += 1;
            if (s[q] === "'" || s[q] === '"' || s[q] === '`') return q;
          }
          flush();
          return e;
        }
      }
      flush();
      return j;
    };
    while (k < s.length) {
      const c = s[k];
      if (/\s/.test(c)) { k += 1; continue; }
      const ce = this.comment(k);
      if (ce >= 0) { k = ce; continue; }
      if (c === "'" || c === '"') {
        const e = stringEnd(s, k);
        this.after = e;
        k = literal(cook(s.slice(k + 1, e - 1)), k);
        continue;
      }
      if (c === '`') {
        const [e, text] = this.template(k);
        this.after = e;
        k = literal(text, k);
        continue;
      }
      if (c === '/' && operandPosition(s, k)) { k = regexEnd(s, k); continue; }
      if (c === '<' && /[A-Za-z>]/.test(s[k + 1] || '') && operandPosition(s, k)) {
        const [e, el] = this.element(k);
        this.roots.push(el);
        k = e;
        continue;
      }
      if (depth === 0 && c === stop) { flush(); return k; }
      if (c === '(' || c === '[' || c === '{') depth += 1;
      else if (c === ')' || c === ']' || c === '}') depth -= 1;
      k += 1;
    }
    flush();
    return k;
  }

  /* A JSX element at `k` (its `<`): [end, {name, children}]. A child is {text}, {expr} or an
     element; JSX reached inside an attribute or an expression is a root of its own. */
  element(k) {
    const s = this.src;
    let j = k + 1;
    let name = '';
    while (j < s.length && /[A-Za-z0-9_$.:-]/.test(s[j])) { name += s[j]; j += 1; }
    while (j < s.length && s[j] !== '>' && !(s[j] === '/' && s[j + 1] === '>')) {
      const ce = this.comment(j);                            // a comment between attributes
      if (ce >= 0) { j = ce; continue; }
      if (s[j] === '"' || s[j] === "'") {
        const e = stringEnd(s, j);
        this.literals.push([s.slice(j + 1, e - 1), j]);    // an attribute's text: JSX does not cook
        j = e;
        continue;
      }
      if (s[j] === '{') { j = this.js(j + 1, '}') + 1; continue; }
      j += 1;
    }
    if (s[j] === '/') return [j + 2, { name, children: [] }];
    j += 1;
    const children = [];
    let text = '';
    const pushText = () => { if (text) children.push({ text }); text = ''; };
    while (j < s.length) {
      const c = s[j];
      if (c === '<' && s[j + 1] === '/') {
        pushText();
        while (j < s.length && s[j] !== '>') j += 1;
        return [j + 1, { name, children }];
      }
      if (c === '<' && /[A-Za-z>]/.test(s[j + 1] || '')) {
        pushText();
        const [e, el] = this.element(j);
        children.push(el);
        j = e;
        continue;
      }
      if (c === '{') {
        pushText();
        const e = this.js(j + 1, '}');
        children.push({ expr: true });
        j = e + 1;
        continue;
      }
      text += c;
      j += 1;
    }
    pushText();
    return [j, { name, children }];
  }
}

/* An element → its paragraphs. Text, `{…}` for an expression, and the flattened text of an
   inline child join one paragraph; a block child ends it and is read as paragraphs of its own. */
export function paragraphs(el, out = []) {
  let cur = '';
  const flush = () => { if (cur.trim()) out.push(cur); cur = ''; };
  const inline = (e) => {
    let t = '';
    for (const ch of e.children) {
      if (ch.text !== undefined) t += ch.text;
      else if (ch.expr) t += ' {…} ';
      else if (BLOCK.has(ch.name)) { paragraphs(ch, out); t += ' '; } else t += inline(ch);
    }
    return t;
  };
  for (const ch of el.children) {
    if (ch.text !== undefined) cur += ch.text;
    else if (ch.expr) cur += ' {…} ';
    else if (BLOCK.has(ch.name)) { flush(); paragraphs(ch, out); } else if (ch.name === 'br') cur += ' ';
    else cur += inline(ch);
  }
  flush();
  return out;
}

export function read(src) {
  const r = new Reader(src);
  r.js(0, '\u0000');
  const paras = [];
  for (const root of r.roots) paragraphs(root, paras);
  return { comments: r.comments, literals: r.literals.map(([t]) => t), paras };
}

/* The source with every comment blanked to spaces (newlines kept), as the lexer found them. */
export function stripComments(src) {
  const { comments } = read(src);
  let out = '';
  let at = 0;
  for (const [a, b] of comments) {
    out += src.slice(at, a) + src.slice(a, b).replace(/[^\n]/g, ' ');
    at = b;
  }
  return out + src.slice(at);
}
