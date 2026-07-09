# Component spec: HeartViewer3D (`/heart`)

A dark-mode, client-side 3D viewer that renders our hearts (crtdemo, Strocchi) and animates the Purkinje activation wavefront sweeping over the myocardium. Fully static (react-three-fiber on baked meshes), no backend. This is where a judge SEES how the model works.

## Description
Load a baked heart mesh with a per-vertex activation time (LAT), draw it, and animate a wavefront: as a virtual clock advances 0 -> max ms, vertices "light up" when their LAT is reached, colored by a sequential colormap. Orbit to inspect, scrub the clock, toggle geometry.

## Mesh format (the `export-web` pipeline output)
Emit one JSON per geometry to `ui/public/meshes/<id>.json`. Decimate the surface to about 8k to 15k vertices for smooth browser perf.
```jsonc
{
  "geometry_id": "crtdemo | strocchi_01",
  "label": "crtdemo (simplistic model rig) | Strocchi #01 (public anatomy)",
  "positions": [x0,y0,z0, x1,y1,z1, ...],   // Float32 flat, millimetres, centered at origin
  "indices":   [i0,i1,i2, ...],             // Uint32 flat triangle list
  "activation":[lat0, lat1, ...],           // Float32 per-vertex local activation time, ms
  "side":      [0,1,0, ...],                // optional: 0=LV, 1=RV per vertex
  "meta": { "n_vertices": 12000, "lat_min": 0.0, "lat_max": 145.0, "units_pos": "mm", "units_lat": "ms", "source": "myocardial-mesh crtdemo | Strocchi 2020 Zenodo 3890034 (CC-BY-4.0)" }
}
```
GLB with a custom `_ACTIVATION` attribute is a valid optimization later; JSON is the v1 contract (trivial to load, no GLTF custom-attr parsing).

## Activation colormap
- Sequential, perceptually uniform: **turbo** (or viridis) over `[lat_min, lat_max]`. Early = deep blue/purple, late = yellow/red.
- Non-activated vertices (LAT > clock): a dim base `--bg-hover` (#22262e) so the wavefront reads as "lighting up".
- Provide a horizontal **colorbar legend** (blue -> red, "early -> late activation, ms") under the canvas.
- Optional secondary mode: color by `side` (LV vs RV) as two flat tints, toggled by a small switch. Keep LAT as the default.
- Implementation: per-vertex `aLat` attribute + a ShaderMaterial with `uTime`; fragment does `activated = step(aLat, uTime)`, samples a turbo LUT at `aLat/latMax` when activated, else base color. In-shader = smooth 60fps; no per-frame CPU recolor.

## Camera and controls
- PerspectiveCamera (fov ~45), positioned to frame the mesh bounding box (auto-fit on load and on toggle).
- OrbitControls (@react-three/drei): rotate, zoom, pan, `enableDamping`, sensible min/max distance. Up vector matches the mesh (z-up unless the export says otherwise).
- Idle gentle auto-rotate (~0.3 rad/s), disabled on user interaction and under `prefers-reduced-motion`.
- A play/pause button + a **time scrubber** (0 to lat_max ms) driving `uTime`; default autoplay looping. A speed control (0.5x/1x/2x) optional.

## crtdemo / Strocchi toggle
- Segmented control (two pills, dark). Switches the loaded mesh JSON, refits the camera, updates the caption + the `meta.label`.
- Show geometry metadata chip: n_vertices + source + the honest label ("simplistic model rig" for crtdemo, "public Strocchi heart" for strocchi_01).
- If Strocchi is not yet exported, show the pill disabled with a "coming from the Strocchi pass" tooltip (do not fake it).

## Props / state
| Prop | Type | Default | Notes |
|---|---|---|---|
| `geometryIds` | string[] | ["crtdemo"] | pills; add "strocchi_01" when its mesh exists |
| `initial` | string | "crtdemo" | first loaded |
| `autoplay` | boolean | true | animate the wavefront |
| `colormap` | "turbo"\|"viridis" | "turbo" | LAT ramp |
State: `activeId`, `clockMs`, `playing`, `colorMode` ("lat"\|"side").

## Accessibility
- Canvas wrapped with an `aria-label` describing what it shows ("3D heart, activation wavefront animating from early blue to late red"), and a visually-hidden text summary.
- All controls (toggle, play, scrubber) are real buttons/inputs, keyboard reachable, with `--accent` focus rings.
- Respect `prefers-reduced-motion` (no auto-rotate, no autoplay; user scrubs).

## Do / Don't
| Do | Don't |
|---|---|
| Decimate to ~10k verts; ship one JSON | Ship the full 4.5k-node volumetric mesh raw |
| Animate LAT in-shader | Recolor vertices on the CPU each frame |
| Label crtdemo honestly as a model rig | Imply crtdemo is a real/synthetic heart |
| Fit camera on load + toggle | Hardcode a camera that clips large meshes |

## Tech + deps
`three`, `@react-three/fiber`, `@react-three/drei`. A `HeartViewer3D.tsx` (canvas + mesh + shader), `lib/mesh.ts` (fetch + parse the JSON into BufferGeometry with the `aLat` attribute), a `turbo.glsl` LUT or a small JS LUT baked into the shader. Lazy-load the route so three.js does not bloat the landing bundle.

## Code sketch (orientation only)
```tsx
// mesh -> BufferGeometry
const g = new THREE.BufferGeometry();
g.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
g.setAttribute("aLat", new THREE.Float32BufferAttribute(activation, 1));
g.setIndex(indices); g.computeVertexNormals();
// material: uniforms { uTime, uLatMax, uBase }, vertex passes aLat, fragment: step(aLat,uTime) ? turbo(aLat/uLatMax) : uBase
// useFrame: uTime = (t*speed) % latMax  (loop the wavefront)
```
