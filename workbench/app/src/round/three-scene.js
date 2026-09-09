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

  const raycaster = new THREE.Raycaster();
  let meshes = [];
  let lineMats = [];
  let shaded = [];          // { geometry, normals, base } — recoloured when the camera moves
  let viewport = { width: 1, height: 1 };

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
     same geometry the axon draws, rather than from a second drawing of the same house. */
  function setClip(zFt) {
    const planes = zFt == null ? [] : [new THREE.Plane(new THREE.Vector3(0, 0, -1), zFt)];
    for (const m of meshes) m.material.clippingPlanes = planes;
    for (const m of lineMats) m.clippingPlanes = planes;
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
    renderer.dispose();
  }

  return { load, setPose, setClip, resize, pick, render, dispose };
}
