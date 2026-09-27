"""inkread.py — read the INK back: what an emitted SVG actually draws, in the plate's own units.

WHY THIS EXISTS (WP-14.1). WP-5.11's adversarial addendum recorded that "a green suite proved the
model and said nothing about the drawing": an inverted sweep flag drew all 245 arcs in the corpus
as their own mirrors through 34 checks, 970 tests, a selftest and a browser walk, because every
one of them interrogated the MODEL and none asked where the ink went. Phase 14 holds every SVG
surface to its record, and it can only do that by starting from the emitted string.

THIS MODULE SHARES NO CODE WITH ANYTHING IT READS. It imports nothing from `build/`,
`workbench/` or `mcp_server/`: a guard that shares an implementation with its subject cannot
catch that implementation being wrong. It is the ONE independent copy of the W3C SVG 1.1 F.6.5
endpoint-to-centre rule in this tree -- there were two, in `tests/test_drawn_geometry.py` and
`tests/test_sheet_coherence.py`, and both import this one now.

What it does, all with the standard library:

  * parses the document (`xml.etree`) and walks it with the CURRENT TRANSFORMATION MATRIX,
    composing `matrix`, `translate`, `scale`, `rotate` (with a centre), `skewX` and `skewY`;
  * resolves COMPUTED STYLE the way a browser does: a presentation attribute loses to any
    stylesheet rule, rules compete by specificity and then by source order, an inline `style`
    beats both, `!important` in a sheet beats a normal inline declaration, and the inherited
    properties inherit. The single-class matcher that `tests/test_drawn_labels.py` uses cannot
    see `.mt` overriding `.w-med` on an element carrying both classes; this can;
  * parses the full path grammar -- relative and implicit commands, compact numbers such as
    `1.5.5` and `-1-2`, and arc flags written with no separator (`A10 10 0 015 5`);
  * turns every drawn element into absolute commands in root user space (the viewBox units the
    renderers write), samples them, and fits circles to decide whether a curve IS a circle;
  * reads the `data-frame` attribute (`build/sheet_style.frame_attr`) and converts a pixel on a
    plate back to the plate's own model units.

The unit of everything returned is ROOT USER SPACE unless a function says otherwise; `to_model`
is the only door into model units and it goes through the frame the plate states about itself.
"""
import json
import math
import re
import xml.etree.ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
IDENTITY = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)

# ------------------------------------------------------------------ matrices
# An affine in SVG's own order: [a c e; b d f; 0 0 1], stored (a, b, c, d, e, f).


def mat_mul(m, n):
    """m then n applied to a point is `mat_mul(m, n)` applied once: the matrix product m·n,
    which is the order SVG composes a transform LIST in (left to right, outermost first)."""
    a1, b1, c1, d1, e1, f1 = m
    a2, b2, c2, d2, e2, f2 = n
    return (a1 * a2 + c1 * b2, b1 * a2 + d1 * b2,
            a1 * c2 + c1 * d2, b1 * c2 + d1 * d2,
            a1 * e2 + c1 * f2 + e1, b1 * e2 + d1 * f2 + f1)


def apply(m, x, y):
    a, b, c, d, e, f = m
    return (a * x + c * y + e, b * x + d * y + f)


def det(m):
    return m[0] * m[3] - m[1] * m[2]


def scale_of(m):
    """The (x, y) scale an affine applies to lengths along each LOCAL axis."""
    return (math.hypot(m[0], m[1]), math.hypot(m[2], m[3]))


_NUM = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")
_TF = re.compile(r"(matrix|translate|scale|rotate|skewX|skewY)\s*\(([^)]*)\)")


def parse_transform(s):
    """A `transform` attribute's list, composed left to right into one matrix."""
    m = IDENTITY
    if not s:
        return m
    for name, body in _TF.findall(s):
        v = [float(x) for x in _NUM.findall(body)]
        if name == "matrix":
            t = tuple(v[:6])
        elif name == "translate":
            t = (1.0, 0.0, 0.0, 1.0, v[0], v[1] if len(v) > 1 else 0.0)
        elif name == "scale":
            sx = v[0]
            sy = v[1] if len(v) > 1 else sx
            t = (sx, 0.0, 0.0, sy, 0.0, 0.0)
        elif name == "rotate":
            a = math.radians(v[0])
            ca, sa = math.cos(a), math.sin(a)
            t = (ca, sa, -sa, ca, 0.0, 0.0)
            if len(v) >= 3:
                cx, cy = v[1], v[2]
                t = mat_mul(mat_mul((1.0, 0.0, 0.0, 1.0, cx, cy), t), (1.0, 0.0, 0.0, 1.0, -cx, -cy))
        elif name == "skewX":
            t = (1.0, 0.0, math.tan(math.radians(v[0])), 1.0, 0.0, 0.0)
        else:  # skewY
            t = (1.0, math.tan(math.radians(v[0])), 0.0, 1.0, 0.0, 0.0)
        m = mat_mul(m, t)
    return m


# ------------------------------------------------------------------ the path grammar
_PATH_TOK = re.compile(r"([MmLlHhVvCcSsQqTtAaZz])|([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)")
_ARGC = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7, "Z": 0}


def _tokens(d):
    """Commands and numbers, with the arc FLAGS split out where they were written with no
    separator. `A10 10 0 015 5` is legal SVG -- the two flags are the single characters 0 and 1
    -- and a number regex reads it as one number `015`, which is how a reader goes wrong on
    exactly the command this corpus gets wrong most often."""
    out = []
    pos = 0
    cmd = None
    argi = 0
    while pos < len(d):
        ch = d[pos]
        if ch in " \t\r\n,":
            pos += 1
            continue
        if ch.isalpha():
            if ch.upper() not in _ARGC:
                raise ValueError("unknown path command %r in %r" % (ch, d[:60]))
            out.append(ch)
            cmd, argi = ch.upper(), 0
            pos += 1
            continue
        if cmd == "A" and argi % 7 in (3, 4):
            if ch not in "01":
                raise ValueError("arc flag must be 0 or 1, got %r in %r" % (ch, d[:60]))
            out.append(float(ch))
            argi += 1
            pos += 1
            continue
        m = _NUM.match(d, pos)
        if not m:
            raise ValueError("cannot read a number at %d in %r" % (pos, d[:60]))
        out.append(float(m.group(0)))
        argi += 1
        pos = m.end()
    return out


def parse_path(d):
    """A path's `d` as a list of ABSOLUTE commands:

        ("M", x, y) ("L", x, y) ("C", x1, y1, x2, y2, x, y) ("Q", x1, y1, x, y)
        ("A", rx, ry, phi_deg, large_arc, sweep, x, y) ("Z",)

    H/V become L; S/T become C/Q with their reflected control point; relative commands become
    absolute; the implicit repeats after a command (and the implicit L after an M) are expanded;
    Z returns the pen to the subpath's own start."""
    toks = _tokens(d or "")
    out = []
    i = 0
    cx = cy = 0.0
    sx = sy = 0.0            # subpath start
    last_c = None            # last cubic control point, for S
    last_q = None            # last quadratic control point, for T
    cmd = None
    while i < len(toks):
        t = toks[i]
        if isinstance(t, str):
            cmd = t
            i += 1
            if cmd in "Zz":
                out.append(("Z",))
                cx, cy = sx, sy
                last_c = last_q = None
                continue
        elif cmd is None:
            raise ValueError("path data starts with a number: %r" % (d[:60],))
        up = cmd.upper()
        rel = cmd.islower()
        n = _ARGC[up]
        args = toks[i:i + n]
        if len(args) < n or any(isinstance(a, str) for a in args):
            raise ValueError("command %s wants %d numbers in %r" % (cmd, n, d[:60]))
        i += n
        if up == "M":
            x, y = args
            if rel:
                x, y = cx + x, cy + y
            out.append(("M", x, y))
            cx, cy = sx, sy = x, y
            cmd = "l" if rel else "L"          # the implicit lineto after a moveto
            last_c = last_q = None
        elif up == "L":
            x, y = args
            if rel:
                x, y = cx + x, cy + y
            out.append(("L", x, y))
            cx, cy = x, y
            last_c = last_q = None
        elif up == "H":
            x = args[0] + (cx if rel else 0.0)
            out.append(("L", x, cy))
            cx = x
            last_c = last_q = None
        elif up == "V":
            y = args[0] + (cy if rel else 0.0)
            out.append(("L", cx, y))
            cy = y
            last_c = last_q = None
        elif up == "C":
            x1, y1, x2, y2, x, y = args
            if rel:
                x1, y1, x2, y2, x, y = cx + x1, cy + y1, cx + x2, cy + y2, cx + x, cy + y
            out.append(("C", x1, y1, x2, y2, x, y))
            last_c, last_q = (x2, y2), None
            cx, cy = x, y
        elif up == "S":
            x2, y2, x, y = args
            if rel:
                x2, y2, x, y = cx + x2, cy + y2, cx + x, cy + y
            x1, y1 = (2 * cx - last_c[0], 2 * cy - last_c[1]) if last_c else (cx, cy)
            out.append(("C", x1, y1, x2, y2, x, y))
            last_c, last_q = (x2, y2), None
            cx, cy = x, y
        elif up == "Q":
            x1, y1, x, y = args
            if rel:
                x1, y1, x, y = cx + x1, cy + y1, cx + x, cy + y
            out.append(("Q", x1, y1, x, y))
            last_q, last_c = (x1, y1), None
            cx, cy = x, y
        elif up == "T":
            x, y = args
            if rel:
                x, y = cx + x, cy + y
            x1, y1 = (2 * cx - last_q[0], 2 * cy - last_q[1]) if last_q else (cx, cy)
            out.append(("Q", x1, y1, x, y))
            last_q, last_c = (x1, y1), None
            cx, cy = x, y
        elif up == "A":
            rx, ry, phi, fa, fs, x, y = args
            if rel:
                x, y = cx + x, cy + y
            out.append(("A", abs(rx), abs(ry), phi, int(fa), int(fs), x, y))
            cx, cy = x, y
            last_c = last_q = None
    return out


# ------------------------------------------------------------------ arcs
def arc_centre(x1, y1, rx, ry, phi, fa, fs, x2, y2):
    """W3C SVG 1.1 F.6.5 endpoint-to-centre parameterisation, with `phi` in RADIANS.

    Returns (cx, cy, rx, ry, theta1, dtheta) -- the radii corrected by F.6.6's lambda scaling
    where the endpoints are too far apart for the radii given. A zero radius or coincident
    endpoints are the spec's own degenerate cases (a line, or nothing) and are returned with
    `dtheta` 0 and the centre at the chord's midpoint, never as a division by zero.

    THIS IS THE ONE INDEPENDENT COPY IN THE TREE. It was written twice before WP-14.1, in
    `tests/test_drawn_geometry.py` (the mouldings) and `tests/test_sheet_coherence.py` (the door
    leaves); both import it now, proved equal to the copies they replaced on a seeded sweep of
    ten thousand arcs before either was deleted."""
    if rx == 0 or ry == 0 or (x1 == x2 and y1 == y2):
        return (x1 + x2) / 2.0, (y1 + y2) / 2.0, abs(rx), abs(ry), 0.0, 0.0
    rx, ry = abs(rx), abs(ry)
    cphi, sphi = math.cos(phi), math.sin(phi)
    dx2, dy2 = (x1 - x2) / 2.0, (y1 - y2) / 2.0
    x1p, y1p = cphi * dx2 + sphi * dy2, -sphi * dx2 + cphi * dy2
    lam = (x1p * x1p) / (rx * rx) + (y1p * y1p) / (ry * ry)
    if lam > 1:
        rx *= math.sqrt(lam)
        ry *= math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    co = math.sqrt(max(0.0, num / den)) if den else 0.0
    if fa == fs:
        co = -co
    cxp, cyp = co * (rx * y1p / ry), co * (-ry * x1p / rx)
    cx = cphi * cxp - sphi * cyp + (x1 + x2) / 2.0
    cy = sphi * cxp + cphi * cyp + (y1 + y2) / 2.0

    def ang(ux, uy, vx, vy):
        nrm = math.hypot(ux, uy) * math.hypot(vx, vy)
        if nrm == 0:
            return 0.0
        d = (ux * vx + uy * vy) / nrm
        a = math.acos(max(-1.0, min(1.0, d)))
        return -a if (ux * vy - uy * vx) < 0 else a

    th1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dth = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if fs == 0 and dth > 0:
        dth -= 2 * math.pi
    if fs == 1 and dth < 0:
        dth += 2 * math.pi
    return cx, cy, rx, ry, th1, dth


def arc_point(cx, cy, rx, ry, phi, th):
    cphi, sphi = math.cos(phi), math.sin(phi)
    x, y = rx * math.cos(th), ry * math.sin(th)
    return cx + cphi * x - sphi * y, cy + sphi * x + cphi * y


# ------------------------------------------------------------------ sampling and fitting
def sample_commands(cmds, m=IDENTITY, n=16, lines=False):
    """Where the ink goes: every command sampled in LOCAL coordinates and carried through the
    matrix `m`. Sampling before transforming is exact for an affine, which is every transform
    this tree emits. Returns a list of SUBPATHS, each a list of points.

    `lines=True` subdivides straight segments into `n` steps as well, for a caller asking where
    the ink is at some height between two vertices -- a fillet's face is a straight line whose
    only sampled points would otherwise be its two ends."""
    subs, cur, pts = [], None, None
    start = None
    for c in cmds:
        k = c[0]
        if k == "M":
            if pts:
                subs.append(pts)
            cur = (c[1], c[2])
            start = cur
            pts = [apply(m, *cur)]
        elif k == "L":
            if lines and cur is not None:
                for i in range(1, n):
                    t = i / n
                    pts.append(apply(m, cur[0] + (c[1] - cur[0]) * t, cur[1] + (c[2] - cur[1]) * t))
            cur = (c[1], c[2])
            pts.append(apply(m, *cur))
        elif k == "C":
            p0 = cur
            for i in range(1, n + 1):
                t = i / n
                u = 1 - t
                x = u ** 3 * p0[0] + 3 * u * u * t * c[1] + 3 * u * t * t * c[3] + t ** 3 * c[5]
                y = u ** 3 * p0[1] + 3 * u * u * t * c[2] + 3 * u * t * t * c[4] + t ** 3 * c[6]
                pts.append(apply(m, x, y))
            cur = (c[5], c[6])
        elif k == "Q":
            p0 = cur
            for i in range(1, n + 1):
                t = i / n
                u = 1 - t
                x = u * u * p0[0] + 2 * u * t * c[1] + t * t * c[3]
                y = u * u * p0[1] + 2 * u * t * c[2] + t * t * c[4]
                pts.append(apply(m, x, y))
            cur = (c[3], c[4])
        elif k == "A":
            rx, ry, phi, fa, fs, x2, y2 = c[1:]
            cx, cy, rx2, ry2, th1, dth = arc_centre(cur[0], cur[1], rx, ry, math.radians(phi), fa, fs, x2, y2)
            if dth == 0.0:
                pts.append(apply(m, x2, y2))
            else:
                for i in range(1, n + 1):
                    pts.append(apply(m, *arc_point(cx, cy, rx2, ry2, math.radians(phi), th1 + dth * i / n)))
            cur = (x2, y2)
        elif k == "Z":
            if start is not None:
                if lines and cur is not None:
                    for i in range(1, n):
                        t = i / n
                        pts.append(apply(m, cur[0] + (start[0] - cur[0]) * t, cur[1] + (start[1] - cur[1]) * t))
                pts.append(apply(m, *start))
                cur = start
    if pts:
        subs.append(pts)
    return subs


def bbox(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (min(xs), min(ys), max(xs), max(ys))


def fit_circle(points):
    """Least-squares circle through points (Kasa's algebraic fit): (cx, cy, r, rms).

    Used to ask whether a drawn curve IS a circle -- a gauged or segmental arch head is a
    circular segment, and a quadratic Bezier through the same three points is a parabola whose
    residual against its own best circle is measurably larger. `rms` is in the points' units."""
    n = len(points)
    if n < 3:
        raise ValueError("a circle needs three points")
    sx = sum(p[0] for p in points)
    sy = sum(p[1] for p in points)
    sxx = sum(p[0] * p[0] for p in points)
    syy = sum(p[1] * p[1] for p in points)
    sxy = sum(p[0] * p[1] for p in points)
    sz = [p[0] * p[0] + p[1] * p[1] for p in points]
    szx = sum(z * p[0] for z, p in zip(sz, points))
    szy = sum(z * p[1] for z, p in zip(sz, points))
    szs = sum(sz)
    # [sxx sxy sx][A]   [szx]
    # [sxy syy sy][B] = [szy]      x^2+y^2 = A x + B y + C
    # [sx  sy  n ][C]   [szs]
    a = [[sxx, sxy, sx, szx], [sxy, syy, sy, szy], [sx, sy, float(n), szs]]
    for col in range(3):
        piv = max(range(col, 3), key=lambda r: abs(a[r][col]))
        a[col], a[piv] = a[piv], a[col]
        if abs(a[col][col]) < 1e-12:
            raise ValueError("collinear points: no circle")
        for r in range(3):
            if r != col:
                f = a[r][col] / a[col][col]
                for k in range(col, 4):
                    a[r][k] -= f * a[col][k]
    A, B, C = (a[i][3] / a[i][i] for i in range(3))
    cx, cy = A / 2.0, B / 2.0
    r = math.sqrt(max(0.0, C + cx * cx + cy * cy))
    rms = math.sqrt(sum((math.hypot(p[0] - cx, p[1] - cy) - r) ** 2 for p in points) / n)
    return cx, cy, r, rms


# ------------------------------------------------------------------ CSS
INHERITED = frozenset((
    "fill", "fill-opacity", "fill-rule", "stroke", "stroke-width", "stroke-dasharray",
    "stroke-dashoffset", "stroke-linecap", "stroke-linejoin", "stroke-opacity", "font",
    "font-size", "font-family", "font-weight", "font-style", "letter-spacing", "text-anchor",
    "visibility", "color", "dominant-baseline"))
PRESENTATION = frozenset(INHERITED | {"opacity", "vector-effect", "display"})


def _strip_comments(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def parse_css(css):
    """[(selector, specificity, order, {prop: (value, important)})] from a stylesheet.

    At-rules (`@font-face`, `@media`) are skipped whole: none of them carries a drawing
    property in this tree, and reading a font face as a rule would be a false match. A selector
    carrying a pseudo-class or an attribute test is recorded and never matches -- no renderer
    here emits one, and matching it wrongly would be worse than not matching it."""
    css = _strip_comments(css or "")
    rules = []
    order = 0
    i = 0
    n = len(css)
    while i < n:
        j = css.find("{", i)
        if j < 0:
            break
        head = css[i:j].strip()
        depth, k = 1, j + 1
        while k < n and depth:
            if css[k] == "{":
                depth += 1
            elif css[k] == "}":
                depth -= 1
            k += 1
        body = css[j + 1:k - 1]
        i = k
        if head.startswith("@"):
            continue
        decls = {}
        for part in body.split(";"):
            if ":" not in part:
                continue
            prop, val = part.split(":", 1)
            prop, val = prop.strip().lower(), val.strip()
            imp = val.endswith("!important")
            if imp:
                val = val[:-len("!important")].strip()
            decls[prop] = (val, imp)
        for sel in head.split(","):
            sel = sel.strip()
            if not sel:
                continue
            rules.append((sel, _specificity(sel), order, decls))
            order += 1
    return rules


_SIMPLE = re.compile(r"^([a-zA-Z][\w-]*|\*)?((?:\.[\w-]+)*)$")


def _specificity(sel):
    ids = cls = tags = 0
    for part in sel.split():
        if part in (">", "+", "~"):
            continue
        ids += part.count("#")
        cls += part.count(".") + part.count(":") + part.count("[")
        m = re.match(r"^[a-zA-Z][\w-]*", part)
        if m:
            tags += 1
    return (ids, cls, tags)


def _compound_matches(part, tag, classes):
    m = _SIMPLE.match(part)
    if not m:
        return False            # a pseudo-class, an attribute test or an id: never ours
    t, cl = m.group(1), m.group(2)
    if t and t != "*" and t != tag:
        return False
    need = [c for c in cl.split(".") if c]
    return all(c in classes for c in need)


def selector_matches(sel, chain):
    """`chain` is [(tag, classes)] from the root to the element. Descendant combinators only,
    which is the only combinator any renderer in this tree writes."""
    parts = [p for p in sel.split() if p not in (">", "+", "~")]
    if not parts or not chain:
        return False
    if not _compound_matches(parts[-1], *chain[-1]):
        return False
    j = len(chain) - 2
    for p in reversed(parts[:-1]):
        while j >= 0 and not _compound_matches(p, *chain[j]):
            j -= 1
        if j < 0:
            return False
        j -= 1
    return True


def _inline(style):
    out = {}
    for part in (style or "").split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            v = v.strip()
            imp = v.endswith("!important")
            out[k.strip().lower()] = (v[:-len("!important")].strip() if imp else v, imp)
    return out


# ------------------------------------------------------------------ the document
def _local(tag):
    return tag.split("}", 1)[1] if "}" in tag else tag


class Item:
    """One drawn element: its tag, attributes, classes, computed style, matrix and geometry.

    `cmds` is the element as absolute path commands in its LOCAL space (a rect is four lines
    and a Z, a circle is two arcs), so one sampler serves every shape. `text` carries a text
    element's string; its anchor point is (x, y) through the matrix."""
    __slots__ = ("tag", "attrs", "classes", "style", "ctm", "cmds", "text", "depth", "index")

    def __init__(self, tag, attrs, classes, style, ctm, cmds=None, text=None, depth=0, index=0):
        self.tag, self.attrs, self.classes, self.style = tag, attrs, classes, style
        self.ctm, self.cmds, self.text, self.depth, self.index = ctm, cmds, text, depth, index

    def points(self, n=16, lines=False):
        """Every sampled point of the ink, in root user space."""
        return [p for sub in sample_commands(self.cmds or [], self.ctm, n, lines) for p in sub]

    def subpaths(self, n=16, lines=False):
        return sample_commands(self.cmds or [], self.ctm, n, lines)

    def bbox(self, n=16):
        pts = self.points(n)
        return bbox(pts) if pts else None

    def stroke_width(self):
        """The stroke width in ROOT user space: the computed width times the matrix's scale,
        unless `vector-effect: non-scaling-stroke` holds it to the viewport."""
        w = self.style.get("stroke-width")
        if w is None:
            return 1.0
        w = float(_NUM.match(str(w)).group(0)) if _NUM.match(str(w)) else 1.0
        if self.style.get("vector-effect") == "non-scaling-stroke":
            return w
        sx, sy = scale_of(self.ctm)
        return w * math.sqrt(abs(sx * sy))

    def anchor(self):
        x = float(self.attrs.get("x", "0").split()[0] or 0)
        y = float(self.attrs.get("y", "0").split()[0] or 0)
        return apply(self.ctm, x, y)

    def __repr__(self):
        return "<Item %s %s>" % (self.tag, " ".join(sorted(self.classes)))


def _num(v, default=0.0):
    if v is None:
        return default
    m = _NUM.match(str(v).strip())
    return float(m.group(0)) if m else default


def _shape_cmds(tag, a):
    if tag == "path":
        return parse_path(a.get("d", ""))
    if tag == "rect":
        x, y, w, h = _num(a.get("x")), _num(a.get("y")), _num(a.get("width")), _num(a.get("height"))
        return [("M", x, y), ("L", x + w, y), ("L", x + w, y + h), ("L", x, y + h), ("Z",)]
    if tag == "line":
        return [("M", _num(a.get("x1")), _num(a.get("y1"))), ("L", _num(a.get("x2")), _num(a.get("y2")))]
    if tag in ("polyline", "polygon"):
        v = [float(x) for x in _NUM.findall(a.get("points", ""))]
        pts = list(zip(v[0::2], v[1::2]))
        if not pts:
            return []
        out = [("M",) + pts[0]] + [("L",) + p for p in pts[1:]]
        return out + ([("Z",)] if tag == "polygon" else [])
    if tag in ("circle", "ellipse"):
        cx, cy = _num(a.get("cx")), _num(a.get("cy"))
        rx = _num(a.get("r")) if tag == "circle" else _num(a.get("rx"))
        ry = _num(a.get("r")) if tag == "circle" else _num(a.get("ry"))
        return [("M", cx + rx, cy), ("A", rx, ry, 0.0, 0, 1, cx - rx, cy),
                ("A", rx, ry, 0.0, 0, 1, cx + rx, cy), ("Z",)]
    return None


DRAWN = ("path", "rect", "line", "polyline", "polygon", "circle", "ellipse", "text")


class Ink:
    """A parsed SVG with every drawn element resolved to geometry and computed style."""

    def __init__(self, svg):
        self.svg = svg
        self.root = ET.fromstring(svg)
        css = "".join((el.text or "") for el in self.root.iter() if _local(el.tag) == "style")
        self.rules = parse_css(css)
        self.items = []
        self._walk(self.root, IDENTITY, {}, [], 0)

    # -- style
    def _computed(self, el, tag, classes, chain, parent_style):
        a = el.attrib
        cand = {}          # prop -> (rank tuple, value)
        # presentation attributes lose to every stylesheet rule: rank below specificity (0,0,0)
        for p in PRESENTATION:
            if p in a:
                cand[p] = ((0, -1, (0, 0, 0), -1), a[p])
        for sel, spec, order, decls in self.rules:
            if not selector_matches(sel, chain):
                continue
            for p, (v, imp) in decls.items():
                rank = (2 if imp else 1, 0, spec, order)
                if p not in cand or rank > cand[p][0]:
                    cand[p] = (rank, v)
        for p, (v, imp) in _inline(a.get("style")).items():
            rank = (3 if imp else 1, 1, (9, 9, 9), 10 ** 9)
            if p not in cand or rank > cand[p][0]:
                cand[p] = (rank, v)
        style = {p: v for p, v in parent_style.items() if p in INHERITED}
        for p, (_r, v) in cand.items():
            if v == "inherit":
                if p in parent_style:
                    style[p] = parent_style[p]
                continue
            style[p] = v
        return style

    def _walk(self, el, ctm, parent_style, chain, depth):
        tag = _local(el.tag)
        classes = frozenset((el.attrib.get("class") or "").split())
        chain = chain + [(tag, classes)]
        m = mat_mul(ctm, parse_transform(el.attrib.get("transform")))
        style = self._computed(el, tag, classes, chain, parent_style)
        if tag in ("defs", "style", "title", "desc", "metadata", "clipPath", "mask", "symbol",
                   "marker", "pattern", "linearGradient", "radialGradient"):
            return
        if tag in DRAWN:
            text = None
            cmds = None
            if tag == "text":
                text = "".join(el.itertext())
            else:
                cmds = _shape_cmds(tag, el.attrib)
            self.items.append(Item(tag, dict(el.attrib), classes, style, m, cmds, text, depth,
                                   len(self.items)))
        for ch in list(el):
            self._walk(ch, m, style, chain, depth + 1)

    # -- selection
    def select(self, tag=None, cls=None, has=None, where=None):
        """Items by tag, by class (all of `cls` present), by attribute presence and predicate."""
        need = set(cls.split()) if isinstance(cls, str) else set(cls or ())
        out = []
        for it in self.items:
            if tag and it.tag != tag and not (isinstance(tag, (tuple, list)) and it.tag in tag):
                continue
            if need and not need <= it.classes:
                continue
            if has and has not in it.attrs:
                continue
            if where and not where(it):
                continue
            out.append(it)
        return out

    def texts(self):
        return [(it.text, it.anchor(), it) for it in self.items if it.tag == "text"]

    # -- the canvas and the frame
    def viewbox(self):
        v = [float(x) for x in _NUM.findall(self.root.attrib.get("viewBox", ""))]
        if len(v) == 4:
            return tuple(v)
        return (0.0, 0.0, _num(self.root.attrib.get("width")), _num(self.root.attrib.get("height")))

    def frames(self):
        """The plates this SVG says it holds (`data-frame`), or [] where it states none."""
        raw = self.root.attrib.get("data-frame")
        if not raw:
            return []
        return (json.loads(raw.replace("&apos;", "'")).get("plates") or [])

    def frame(self, plate_id=None, proj=None):
        for p in self.frames():
            if (plate_id is None or p.get("id") == plate_id) and (proj is None or p.get("proj") == proj):
                return p
        return None


def to_model(plate, x_px, y_px):
    """A root-user-space point to the plate's own (u, v) in its own unit, by the frame the plate
    states. The inverse of `build/sheet_style.frame_attr`'s documented affine,

        px_x = origin_px[0] + (u - at_origin[0]) * px_per_unit
        px_y = origin_px[1] + (at_origin[1] - v) * px_per_unit

    written here from the DOCUMENTATION and not imported, so a renderer and this reader cannot
    agree with each other by sharing a mistake. A plate states `px_per_ft` or `px_per_in`."""
    k = plate.get("px_per_ft") or plate.get("px_per_in")
    ox, oy = plate["origin_px"]
    au = plate.get("at_origin_ft", plate.get("at_origin_in"))
    return (au[0] + (x_px - ox) / k, au[1] - (y_px - oy) / k)


def from_model(plate, u, v):
    k = plate.get("px_per_ft") or plate.get("px_per_in")
    ox, oy = plate["origin_px"]
    au = plate.get("at_origin_ft", plate.get("at_origin_in"))
    return (ox + (u - au[0]) * k, oy + (au[1] - v) * k)
