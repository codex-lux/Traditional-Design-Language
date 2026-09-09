/* The only file in this app that imports three.js, and the only one that knows what a GPU is.

   WP-12.4. The brief is docs/prd/phase-12-the-sheet-in-the-round.md §§7.9, 7.11.

   IT IS REACHED ONLY BY `await import('./three-scene.js')` FROM Round.jsx. That is what makes
   Vite emit it as its own chunk with `three` folded inside, leaving the entry chunk alone —
   and it is also what keeps `no_bare_imports.test.mjs` green, because that walker deliberately
   does not follow a dynamic import (coastTiers.js code-splits with one). Do not import this
   module statically from anywhere.

   IT BUILDS NO GEOMETRY. `round/solids.js` turns the record's primitives into triangles and
   edges, in a leaf, under `node --test`; this file uploads them. The division is not tidiness:
   geometry inside a WebGL module can be checked only by looking at pixels, and writing
   solids.js found a winding defect that a picture would have shown as a sun lighting half the
   openings from inside.

   IT CARRIES NO COLOUR. Every ink and tone arrives in `tokens`, resolved from tokens.css by
   Round.jsx through getComputedStyle. A source-reading test refuses a hex or an 0x literal in
   this file, because the Drawn Language is one palette and a colour typed here would be a
   second one that no token can move. */

import * as THREE from 'three';
import { LineSegments2 } from 'three/addons/lines/LineSegments2.js';
import { LineSegmentsGeometry } from 'three/addons/lines/LineSegmentsGeometry.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';

import { edges as edgesOf, normalOf, triangles } from './solids.js';
import { basis, eyeDirection } from './frame.js';

/* Which pen an `ink` names, and which wash a `tone` names. The VALUES are tokens.css's; these
   are only the names, so a token may be re-ruled without touching this file. */
const PEN = { cut: 'lw-cut', profile: 'lw-heavy', seen: 'lw-medium', fine: 'lw-fine', hidden: 'lw-fine', grid: 'lw-construction' };
const INK = { cut: 'draw-cut', profile: 'draw-profile', seen: 'draw-seen', fine: 'draw-fine', hidden: 'draw-hidden', grid: 'draw-grid' };

export function mount(canvas, tokens) {
  const colour = (name, fallback) => new THREE.Color(tokens[name] || tokens[fallback] || tokens.ink);
  const width = (name) => parseFloat(tokens[name] || tokens['lw-medium'] || '1.6') || 1.6;

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setClearColor(colour('paper'), 1);
  renderer.localClippingEnabled = true;

  const scene = new THREE.Scene();
  const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, -5000, 5000);
  const group = new THREE.Group();
  scene.add(group);

  const overlayGroup = new THREE.Group();
  scene.add(overlayGroup);

  const raycaster = new THREE.Raycaster();
  let meshes = [];
  let lineMats = [];
  let shaded = [];          // { geometry, normals, base } — recoloured when the camera moves
  let parts = [];           // { obj, solid } — every drawn object beside the solid it came from,
                            // which is what lets `setExplode` move a storey or an element
  let overlayBits = [];
  let viewport = { width: 1, height: 1 };
  let clipPlanes = [];

  /* THE SUN IS FIXED TO THE SHEET, NOT TO THE WORLD, which is what a drawing's sun is: the
     light comes over the reader's left shoulder whichever way the house is turned. So the
     shading is recomputed when the camera moves — flat, two-tone, never a gradient, and never
     a cast shadow, because a cast shadow is a photograph's idea and not a drawing's. */
  function reshade(pose) {
    const b = basis(pose.azimuthDeg, pose.elevationDeg);
    const a = (parseFloat(tokens['shadow-angle']) || 45) * (Math.PI / 180);
    // upper-left of the plate, in the camera's own right/up, then into world space
    const sx = -Math.cos(a);
    const sy = Math.sin(a);
    const sun = [
      b.right[0] * sx + b.up[0] * sy - b.forward[0],
      b.right[1] * sx + b.up[1] * sy - b.forward[1],
      b.right[2] * sx + b.up[2] * sy - b.forward[2],
    ];
    const L = Math.hypot(sun[0], sun[1], sun[2]) || 1;
    const dim = 1 - (parseFloat(tokens['shadow-strength']) || 0.15);
    for (const s of shaded) {
      const col = s.geometry.getAttribute('color');
      for (let t = 0; t < s.normals.length; t += 1) {
        const n = s.normals[t];
        const lit = (n[0] * sun[0] + n[1] * sun[1] + n[2] * sun[2]) / L > 0;
        const k = lit ? 1 : dim;
        for (let v = 0; v < 3; v += 1) {
          col.setXYZ(t * 3 + v, s.base.r * k, s.base.g * k, s.base.b * k);
        }
      }
      col.needsUpdate = true;
    }
  }

  function clear() {
    for (const m of meshes) {
      m.geometry.dispose();
      if (m.material.dispose) m.material.dispose();
    }
    for (const m of lineMats) m.dispose();
    group.clear();
    meshes = [];
    lineMats = [];
    shaded = [];
    parts = [];
  }

  function load(sceneRecord) {
    clear();
    const refused = [];
    for (const solid of sceneRecord.solids || []) {
      let tris;
      let segs;
      try {
        tris = triangles(solid);
        segs = edgesOf(solid);
      } catch (err) {
        /* NAMED, never dropped — the reader is told which solid could not be built and why,
           because a piece of a house that is silently absent is the one failure a drawing may
           not have. */
        refused.push({ id: solid.id, why: String(err.message || err) });
        continue;
      }

      const pos = new Float32Array(tris.length * 9);
      const col = new Float32Array(tris.length * 9);
      const normals = [];
      tris.forEach((t, i) => {
        normals.push(normalOf(t));
        for (let v = 0; v < 3; v += 1) {
          pos[i * 9 + v * 3] = t[v][0];
          pos[i * 9 + v * 3 + 1] = t[v][1];
          pos[i * 9 + v * 3 + 2] = t[v][2];
        }
      });
      const geom = new THREE.BufferGeometry();
      geom.setAttribute('position', new THREE.BufferAttribute(pos, 3));
      geom.setAttribute('color', new THREE.BufferAttribute(col, 3));
      geom.computeVertexNormals();

      const base = colour(solid.tone || 'paper-mat', 'paper-mat');
      const mesh = new THREE.Mesh(geom, new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.DoubleSide }));
      mesh.userData.solid = solid;
      group.add(mesh);
      meshes.push(mesh);
      parts.push({ obj: mesh, solid });
      shaded.push({ geometry: geom, normals, base });

      // The pen: screen-space width, so it does NOT magnify with the zoom. That answers OQ 66
      // in the Round by construction rather than by a setting -- a loupe over an SVG scales
      // the ink with the drawing, and this does not.
      const flat = [];
      for (const [p, q] of segs) flat.push(p[0], p[1], p[2], q[0], q[1], q[2]);
      const lg = new LineSegmentsGeometry();
      lg.setPositions(flat);
      const lm = new LineMaterial({
        color: colour(INK[solid.ink] || 'draw-seen', 'draw-seen'),
        linewidth: width(PEN[solid.ink] || 'lw-medium'),
        worldUnits: false,
      });
      lm.resolution.set(viewport.width, viewport.height);
      const seg = new LineSegments2(lg, lm);
      seg.userData.solid = solid;
      group.add(seg);
      lineMats.push(lm);
      parts.push({ obj: seg, solid });
    }
    return { solids: meshes.length, refused };
  }

  function setPose(pose, aspect) {
    const h = pose.halfHeightFt;
    const w = h * aspect;
    camera.left = -w; camera.right = w; camera.top = h; camera.bottom = -h;
    const d = eyeDirection(pose.azimuthDeg, pose.elevationDeg);
    const far = Math.max(h * 8, 400);
    camera.position.set(
      pose.target[0] + d[0] * far,
      pose.target[1] + d[1] * far,
      pose.target[2] + d[2] * far,
    );
    // Model +z is up, except looking straight down, where the Sheet's rule takes over and
    // model-north is up. frame.js::basis is the one place that decides this.
    const b = basis(pose.azimuthDeg, pose.elevationDeg);
    camera.up.set(b.up[0], b.up[1], b.up[2]);
    camera.lookAt(pose.target[0], pose.target[1], pose.target[2]);
    camera.updateProjectionMatrix();
    reshade(pose);
  }

  /* A plan is a cut, and the cut is a clipping plane — so plan views get their poché from the
     same geometry the axon draws, rather than from a second drawing of the same house.

     WP-12.5 generalised it to any axis, because §7.6's `cut` modifier is the same mechanism
     turned on its side: with a face selected, this is the building section the project does
     not yet draw flat, and the caption says so rather than letting it pass for a plate. */
  const AXIS_NORMAL = { x: [-1, 0, 0], y: [0, -1, 0], z: [0, 0, -1] };

  function setClip(cut) {
    // a bare number is the plan cut, as WP-12.4 called it; an object is the modifier
    const c = typeof cut === 'number' ? { axis: 'z', at_ft: cut } : cut;
    if (!c || c.at_ft == null || !AXIS_NORMAL[c.axis]) {
      clipPlanes = [];
    } else {
      const n = AXIS_NORMAL[c.axis];
      clipPlanes = [new THREE.Plane(new THREE.Vector3(n[0], n[1], n[2]), c.at_ft)];
    }
    for (const m of meshes) m.material.clippingPlanes = clipPlanes;
    for (const m of lineMats) m.clippingPlanes = clipPlanes;
    // an overlay is clipped with the model it annotates, or it floats through the cut face
    for (const b of overlayBits) {
      if (b.material) b.material.clippingPlanes = clipPlanes;
    }
  }

  /* THE MODEL COMES APART BY WHOLE STOREYS AND WHOLE ELEMENTS, never by solid. The offsets
     are `overlays.js::explodeOffsets`'s and are not recomputed here — a viewer that derived
     its own would be a second answer to a question the leaf already answers under test. */
  function setExplode(offsets) {
    const byLevel = (offsets && offsets.byLevel) || {};
    const byElement = (offsets && offsets.byElement) || {};
    for (const { obj, solid } of parts) {
      const d = byLevel[solid.level] || byElement[solid.element || 'main'] || [0, 0, 0];
      obj.position.set(d[0], d[1], d[2]);
    }
  }

  /* The overlays, as translucent geometry over the model. EVERY SHAPE HERE IS COMPUTED IN
     `round/overlays.js` and every colour comes from a token — this function places what it is
     handed and decides nothing, which is the same division that put the geometry in
     `solids.js` and found a winding defect there. */
  function clearOverlays() {
    for (const b of overlayBits) {
      if (b.geometry) b.geometry.dispose();
      if (b.material && b.material.dispose) b.material.dispose();
    }
    overlayGroup.clear();
    overlayBits = [];
  }

  function wash(colourName, opacity) {
    const m = new THREE.MeshBasicMaterial({
      color: colour(colourName, 'sepia'), transparent: true, opacity,
      side: THREE.DoubleSide, depthWrite: false,
    });
    m.clippingPlanes = clipPlanes;
    return m;
  }

  function boxAt(x, y, w, d, z0, z1, material) {
    const g = new THREE.BoxGeometry(w, d, Math.max(z1 - z0, 0.01));
    const mesh = new THREE.Mesh(g, material);
    mesh.position.set(x + w / 2, y + d / 2, (z0 + z1) / 2);
    return mesh;
  }

  function prismAt(polygon, z0, z1, material) {
    const shape = new THREE.Shape(polygon.map(([px, py]) => new THREE.Vector2(px, py)));
    const g = new THREE.ExtrudeGeometry(shape, { depth: Math.max(z1 - z0, 0.01), bevelEnabled: false });
    const mesh = new THREE.Mesh(g, material);
    mesh.position.set(0, 0, z0);
    return mesh;
  }

  function add(obj) { overlayGroup.add(obj); overlayBits.push(obj); return obj; }

  function lineOf(points, inkName, penName) {
    const flat = [];
    for (const [a, b] of points) flat.push(a[0], a[1], a[2], b[0], b[1], b[2]);
    const lg = new LineSegmentsGeometry();
    lg.setPositions(flat);
    const lm = new LineMaterial({
      color: colour(inkName, 'draw-grid'), linewidth: width(penName), worldUnits: false,
    });
    lm.resolution.set(viewport.width, viewport.height);
    lm.clippingPlanes = clipPlanes;
    const seg = new LineSegments2(lg, lm);
    overlayBits.push(seg);
    overlayGroup.add(seg);
    return seg;
  }

  /* RETURNS WHAT IT DREW, per overlay. A wash is translucent by design and a wash that draws
     NOTHING looks exactly like one drawn faintly over a sepia floor — which is what shipped for
     an hour, with the chip lit, the URL right and the caption correct. A count is the only
     thing that can tell those apart, so the canvas carries it and the walk asserts a positive.
     WP-12.5, and it is WP-11.14's "assert the denominator" one surface over. */
  function setOverlays(ov) {
    clearOverlays();
    const drew = {};
    if (!ov) return drew;

    if (ov.grid && ov.grid.lines) {
      const pts = ov.grid.lines.flatMap((l) => ([
        [[l.x_ft, l.y0_ft, l.z0_ft], [l.x_ft, l.y1_ft, l.z0_ft]],
        [[l.x_ft, l.y0_ft, l.z0_ft], [l.x_ft, l.y0_ft, l.z1_ft]],
      ]));
      if (pts.length) { lineOf(pts, 'draw-grid', 'lw-construction'); drew.grid = ov.grid.lines.length; }
    }

    if (ov.datums && ov.datums.length && ov.extent) {
      const [x0, y0, x1, y1] = ov.extent;
      lineOf(ov.datums.map((d) => ([[x0, y1, d.z_ft], [x1, y1, d.z_ft]])), 'draw-dim', 'lw-fine');
      drew.datums = ov.datums.length;
    }

    if (ov.daylight) {
      const m = wash(ov.daylightToken, ov.daylightOpacity);
      for (const v of ov.daylight) add(boxAt(v.x_ft, v.y_ft, v.width_ft, v.depth_ft, v.z0_ft, v.z1_ft, m));
      drew.daylight = ov.daylight.length;
    }

    if (ov.wet) {
      const m = wash(ov.wetToken, ov.wetOpacity);
      for (const w of ov.wet) add(prismAt(w.polygon, w.z0_ft, w.z1_ft, m));
      drew.wet = ov.wet.length;
    }

    if (ov.privacy) {
      // one material per wash strength: the ramp is the whole point of this overlay
      for (const w of ov.privacy) {
        add(prismAt(w.polygon, w.z_ft, w.z_ft + 0.05, wash(ov.privacyToken, w.opacity)));
      }
      drew.privacy = ov.privacy.length;
    }

    if (ov.relaxations) {
      // the hollow triangle, in INK and never in colour (WP-6.3): a mark that cannot be
      // located is not drawn here at all — the caption names it instead.
      const r = 1.6;
      const pts = [];
      for (const m of ov.relaxations) {
        const x = m.x_ft || 0;
        const y = m.y_ft || 0;
        const z = m.z_ft || 0.1;
        const a = [x, y + r, z];
        const b = [x - r * 0.87, y - r * 0.5, z];
        const c = [x + r * 0.87, y - r * 0.5, z];
        pts.push([a, b], [b, c], [c, a]);
      }
      if (pts.length) { lineOf(pts, 'draw-seen', 'lw-medium'); drew.relaxations = ov.relaxations.length; }
    }
    return drew;
  }

  function resize(w, h) {
    viewport = { width: w, height: h };
    renderer.setSize(w, h, false);
    for (const m of lineMats) m.resolution.set(w, h);
  }

  function pick(px, py) {
    const ndc = new THREE.Vector2((px / viewport.width) * 2 - 1, -(py / viewport.height) * 2 + 1);
    raycaster.setFromCamera(ndc, camera);
    const hit = raycaster.intersectObjects(meshes, false)[0];
    return hit ? hit.object.userData.solid : null;
  }

  function render() {
    renderer.render(scene, camera);
  }

  function dispose() {
    clear();
    clearOverlays();
    renderer.dispose();
  }

  return { load, setPose, setClip, setExplode, setOverlays, resize, pick, render, dispose };
}
