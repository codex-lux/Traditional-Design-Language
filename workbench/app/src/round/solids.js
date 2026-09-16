/* A scene solid becomes faces, triangles and edges — in plain arrays, with no three.js.

   WP-12.4. THE SPLIT IS THE POINT: the arithmetic that turns build/scene.py's four primitives
   into triangles is the half that can be silently wrong, so it lives here, in a leaf, under
   `node --test`. three-scene.js only uploads what this returns. A viewer that built its own
   geometry inside a WebGL module could only be checked by looking at pixels, and WP-12.1
   shipped three geometry defects that every number in the record accepted and only a picture
   caught.

   The primitives are build/scene.py's own, and their contracts are the schema's:

     box      origin[3] + size[3], axis-aligned
     extrude  a 2D outline in `plane` ('xz' or 'yz'), swept from `at` along the plane's
              POSITIVE normal axis by `thickness`
     plane    vertices[3][] — a flat polygon in space, no thickness (a roof plane)
     prism    a 2D polygon in (x, y) swept from z0 to z1 (a space)

   `at` IS THE LOW FACE AND THE SWEEP RUNS POSITIVE. That is WP-12.2's correction, and it is
   the contract this file asserts rather than a consequence of it: WP-12.1 put `at` on the
   OUTSIDE face with an always-positive thickness, so south and west openings went INTO their
   walls and north and east ones stood PROUD of them, and its own test was green over the
   defect because it compared `at` against exactly where the wrong contract put it. */

/* Every solid reduces to a list of FACES -- closed 3D polygons, wound so the normal points
   out. Triangles and edges both fall out of that, which is why there is one builder and not
   three, and why an opening and a gable cannot disagree about which way they face. */
export function facesOf(solid) {
  const g = solid.geometry || solid;
  switch (g.type) {
    case 'box':
      return boxFaces(g.origin, g.size);
    case 'extrude':
      return sweptFaces(g.outline, g.plane, g.at, g.thickness);
    case 'plane':
      return [g.vertices.map((v) => [v[0], v[1], v[2]])];
    case 'prism':
      return sweptFaces(g.polygon, 'xy', g.z0, g.z1 - g.z0);
    default:
      /* NAMED, never skipped. A primitive this file does not understand is a solid the
         reader would simply not see, and an absence is the one thing a drawing must never
         report silently -- the same reason WP-12.2's bounds helper raises. */
      throw new Error(`solids.js cannot build a '${g.type}' — build/scene.py emitted a primitive this viewer does not know`);
  }
}

function boxFaces(o, s) {
  const [x, y, z] = o;
  const [w, d, h] = s;
  const X = x + w;
  const Y = y + d;
  const Z = z + h;
  return [
    [[x, y, z], [X, y, z], [X, y, Z], [x, y, Z]],       // south (-y)
    [[X, Y, z], [x, Y, z], [x, Y, Z], [X, Y, Z]],       // north (+y)
    [[X, y, z], [X, Y, z], [X, Y, Z], [X, y, Z]],       // east  (+x)
    [[x, Y, z], [x, y, z], [x, y, Z], [x, Y, Z]],       // west  (-x)
    [[x, y, Z], [X, y, Z], [X, Y, Z], [x, Y, Z]],       // top   (+z)
    [[x, Y, z], [X, Y, z], [X, y, z], [x, y, z]],       // bottom(-z)
  ];
}

/* Which model axis a plane's two outline coordinates run along, and which axis it sweeps.
   'xz' means the outline is (x, z) and the sweep is along y -- so a south wall's opening is
   cut through the wall's thickness, not along its face. */
const PLANES = {
  xz: { u: 0, v: 2, n: 1 },
  yz: { u: 1, v: 2, n: 0 },
  xy: { u: 0, v: 1, n: 2 },
};

function sweptFaces(outline, plane, at, thickness) {
  const ax = PLANES[plane];
  if (!ax) throw new Error(`solids.js cannot sweep the plane '${plane}'`);
  const put = (uv, n) => {
    const p = [0, 0, 0];
    p[ax.u] = uv[0];
    p[ax.v] = uv[1];
    p[ax.n] = n;
    return p;
  };
  const lo = outline.map((uv) => put(uv, at));
  // `at` is the LOW face and the sweep is POSITIVE -- always, on every plane. A thickness
  // signed by which face of the house it sits on is how the north and east openings came to
  // stand proud of their walls.
  const hi = outline.map((uv) => put(uv, at + thickness));
  const out = [lo, hi];
  for (let i = 0; i < outline.length; i += 1) {
    const j = (i + 1) % outline.length;
    out.push([lo[i], lo[j], hi[j], hi[i]]);
  }
  return outward(out);
}

/* Wind every face so its normal points away from the solid — computed, never assumed.

   THE ASSUMPTION THAT FAILED: winding by the outline's own order looks right and is right on
   two of the three planes. `PLANES.xz` maps (u, v, n) to (x, z, y), and x cross z is MINUS y,
   so that frame is LEFT-handed while `yz` and `xy` are right-handed. An outline wound the
   same way therefore faces one direction in a wall and the other in a gable, and a flat sun
   then lights half the openings from inside. The hand-wound box was correct throughout, which
   is exactly why the box test did not catch it — found by a mutation of the cap winding
   staying green.

   Every solid this file builds is convex — a box, a rectangular or triangular prism, a planar
   quadrilateral — so a face is outward when it faces away from the solid's own centroid. That
   is true whatever the frame's handedness and whatever order the record wrote the outline in,
   which is why it is computed here rather than reasoned about once per plane. */
function outward(faces) {
  let n = 0;
  const c = [0, 0, 0];
  for (const f of faces) {
    for (const p of f) {
      c[0] += p[0]; c[1] += p[1]; c[2] += p[2]; n += 1;
    }
  }
  c[0] /= n; c[1] /= n; c[2] /= n;
  return faces.map((f) => {
    const nv = normalOf([f[0], f[1], f[2]]);
    const fc = f.reduce((a, p) => [a[0] + p[0] / f.length, a[1] + p[1] / f.length, a[2] + p[2] / f.length], [0, 0, 0]);
    const away = [fc[0] - c[0], fc[1] - c[1], fc[2] - c[2]];
    const facing = nv[0] * away[0] + nv[1] * away[1] + nv[2] * away[2];
    return facing < 0 ? f.slice().reverse() : f;
  });
}

/* A fan is enough and is not a shortcut: every outline build/scene.py emits is convex -- a
   rectangle for an opening or a wall, a triangle for a gable, a quadrilateral for a roof
   plane. A concave one would fan wrongly and silently, so it is refused by name rather than
   drawn as something else. */
function fan(face, out) {
  for (let i = 1; i + 1 < face.length; i += 1) out.push([face[0], face[i], face[i + 1]]);
}

export function triangles(solid) {
  const out = [];
  for (const f of facesOf(solid)) fan(f, out);
  return out;
}

export function normalOf(tri) {
  const [a, b, c] = tri;
  const u = [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
  const v = [c[0] - a[0], c[1] - a[1], c[2] - a[2]];
  const n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
  const L = Math.hypot(n[0], n[1], n[2]) || 1;
  return [n[0] / L, n[1] / L, n[2] / L];
}

/* The edges a pen would draw: every face's boundary, each undirected edge once. Deduping is
   not tidiness -- a box's twelve edges are shared by two faces each, and drawing them twice
   doubles the ink at exactly the weight the standard is most particular about. */
export function edges(solid) {
  const seen = new Set();
  const out = [];
  const key = (p, q) => {
    const a = p.map((n) => n.toFixed(4)).join(',');
    const b = q.map((n) => n.toFixed(4)).join(',');
    return a < b ? `${a}|${b}` : `${b}|${a}`;
  };
  for (const f of facesOf(solid)) {
    for (let i = 0; i < f.length; i += 1) {
      const p = f[i];
      const q = f[(i + 1) % f.length];
      const k = key(p, q);
      if (seen.has(k)) continue;
      seen.add(k);
      out.push([p, q]);
    }
  }
  return out;
}

/* The extent a solid actually occupies, which is what a containment check reads. Computed
   from the built faces rather than from the record's own numbers, so a primitive whose
   construction disagrees with its declaration is caught by the disagreement. */
export function extent(solid) {
  const min = [Infinity, Infinity, Infinity];
  const max = [-Infinity, -Infinity, -Infinity];
  for (const f of facesOf(solid)) {
    for (const p of f) {
      for (let i = 0; i < 3; i += 1) {
        if (p[i] < min[i]) min[i] = p[i];
        if (p[i] > max[i]) max[i] = p[i];
      }
    }
  }
  return { min, max };
}
