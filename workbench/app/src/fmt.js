/* DRAUGHTSMAN'S NOTATION: A DIMENSION IN FEET, INCHES AND SIXTEENTHS (WP-14.6).

   `feetInches16(x)` is a PORT, not a reimplementation, of `build/proportion_engine.py::_fmt_in`,
   the function every CLI and printed plate in this corpus has used to write an inch figure
   ("8 1/2\"", "9'-6\""). The workbench printed decimal inches ("8.5263 in") where the rest of the
   corpus prints notation, and the fix is to print what the engine prints, not something that looks
   like it. `tests/test_fmt_parity.py` holds the two to one answer: it reads the vector table out of
   `src/fmt.test.mjs` and asks `_fmt_in` for each string, and it sweeps a few thousand inputs
   through both languages and compares them one by one.

   FAITHFUL MEANS FOUR THINGS A NATURAL PORT GETS WRONG, and each is reproduced deliberately
   rather than improved:

   1. `frac * 16` IS ROUNDED HALF-TO-EVEN, because Python's `round()` is. `Math.round` rounds a
      half UP, so a natural port prints 0.03125 in (exactly half a sixteenth) as `0 1/16"` where the
      engine prints `0"`, and 0.15625 as `0 3/16"` where the engine prints `0 1/8"`.
   2. A SIXTEENTH THAT ROUNDS UP TO SIXTEEN CARRIES INTO THE INCH, AND AN INCH THAT REACHES
      TWELVE CARRIES INTO THE FOOT, so 23.99 prints `2'-0"` and 11.97 prints `1'-0"`. Until
      WP-14.20 the engine stopped at the inch and printed `1'-12"` and `12"`, and tranche 1 ported
      that deliberately rather than improving it on one side; WP-14.20 fixed it on BOTH sides in
      one commit. The inch is tested and not the sixteenth, because `divmod` can hand back a
      remainder of exactly 12.0 with no sixteenth at all (item 3). A natural port that carries
      only on the sixteenth fails -1e-20.
   3. `divmod(x, 12)` IS PYTHON'S FLOOR DIVMOD, not JavaScript's truncating `%`: a negative figure
      takes a negative foot and a positive remainder (-3.5 prints `-1'-8 1/2"`), and a vanishing
      negative figure lands on a remainder of exactly 12.0, which item 2 carries into the foot
      (-1e-20 prints `0"`, where it printed `-1'-12"` until WP-14.20). The float
      algorithm below is CPython's `_float_div_mod` line for line, because a floor written as
      `Math.floor(x / 12)` disagrees with it at the edges.
   4. `int(ft)` PRINTS THE WHOLE INTEGER. Past 2**53 a JavaScript number's `String()` prints its
      shortest round-trip digits and pads with zeros (`83333333333333330000`); Python prints the
      double's exact value (`83333333333333327872`). BigInt prints what Python prints.

   And the refusals are Python's too: `None` (here `null` or `undefined`) prints `-`, the corpus's
   mark for a figure that is not there; a boolean is a number, as it is in Python; NaN and the
   infinities are REFUSED (Python raises ValueError converting the NaN its own divmod produces), and
   anything else that is not a number is refused as Python refuses it. A plate that hands this a
   non-number has a defect upstream of the plate, and printing `-` over it would make a broken
   figure look like an absent one — unjudged is not passed, and garbage is not absent.

   Pure, and imports nothing. */

const FOOT = 12;
const SIXTEENTHS = 16;

/* CPython's `_float_div_mod(vx, wx)` (Objects/floatobject.c), for a positive divisor. `%` on two
   JavaScript numbers IS C's `fmod` — IEEE remainder by truncation, exact — so the two start from the
   same number and take the same corrections. */
function floorDivmod(vx, wx) {
  let mod = vx % wx;
  let div = (vx - mod) / wx;
  if (mod) {
    if ((wx < 0) !== (mod < 0)) {
      mod += wx;
      div -= 1.0;
    }
  } else {
    mod = wx < 0 ? -0 : 0;                       // copysign(0.0, wx)
  }
  let floordiv;
  if (div) {
    floordiv = Math.floor(div);
    if (div - floordiv > 0.5) floordiv += 1.0;
  } else {
    floordiv = (vx / wx < 0 || Object.is(vx / wx, -0)) ? -0 : 0;   // copysign(0.0, vx / wx)
  }
  return [floordiv, mod];
}

/* Python 3's `round(x)` for a float with no ndigits: nearest integer, a half to the even one. The
   subtraction is exact for any |v| < 2**52, and v here is below 16. */
function roundHalfEven(v) {
  const f = Math.floor(v);
  const d = v - f;
  if (d < 0.5) return f;
  if (d > 0.5) return f + 1;
  return f % 2 === 0 ? f : f + 1;
}

const gcd = (a, b) => (b ? gcd(b, a % b) : a);

/* Python's `str(int(n))` for an integral double. */
function intString(n) {
  if (Math.abs(n) < 2 ** 53) return String(Object.is(n, -0) ? 0 : n);
  return BigInt(n).toString();
}

/* The engine's `_fmt_in`, ported. Returns `-` for null/undefined; throws where Python raises. */
export function feetInches16(x) {
  if (x === null || x === undefined) return '-';
  if (typeof x === 'boolean') x = Number(x);
  if (typeof x !== 'number') {
    throw new TypeError(`feetInches16: ${typeof x} is not a number (_fmt_in raises TypeError)`);
  }
  if (!Number.isFinite(x)) {
    throw new RangeError(`feetInches16: ${x} is not finite (_fmt_in raises ValueError)`);
  }
  const [ft, rem] = floorDivmod(x, FOOT);
  let whole = Math.trunc(rem);
  const frac = rem - whole;
  let six = roundHalfEven(frac * SIXTEENTHS);
  if (six === SIXTEENTHS) { whole += 1; six = 0; }          // into the inch...
  let foot = ft;
  if (whole === FOOT) { foot += 1; whole = 0; }             // ...and a full foot into the foot
  let fs = '';
  if (six) {
    const g = gcd(six, SIXTEENTHS);
    fs = ` ${six / g}/${SIXTEENTHS / g}`;
  }
  return (foot ? `${intString(foot)}'-` : '') + `${whole}${fs}"`;
}
