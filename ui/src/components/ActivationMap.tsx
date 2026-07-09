"use client";

import { useEffect, useRef, useState } from "react";
import { geometry, results } from "@/lib/artifact";
import { viridis } from "@/lib/colormap";
import { EmptyState } from "@/components/Layout";

// 2.5D biventricular activation map on a 2D canvas (dependency-light, no
// three.js). The surface is painted by local activation time (LAT) via viridis;
// a turntable spin plus a wavefront time-sweep make it read as a propagating
// depolarization. Missing activation degrades to a neutral surface.

const LIGHT = normalize([0.3, 0.55, 0.75]);

function normalize(v: number[]): [number, number, number] {
  const n = Math.hypot(v[0], v[1], v[2]) || 1;
  return [v[0] / n, v[1] / n, v[2] / n];
}

export default function ActivationMap() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const angleRef = useRef(0.5);
  const sweepRef = useRef(1); // 1 = fully activated (whole map shown)
  const playingRef = useRef(false);
  const rotatingRef = useRef(true);
  const [playing, setPlaying] = useState(false);
  const [rotating, setRotating] = useState(true);
  const [sweepPct, setSweepPct] = useState(100);
  const [showPk, setShowPk] = useState(true);
  const showPkRef = useRef(true);

  const verts = geometry?.vertices;
  const faces = geometry?.faces;
  const lat = results.activation_map?.values;
  const chamber = geometry?.chamber;
  const purk = geometry?.purkinje;

  const hasGeom = !!(verts?.length && faces?.length);
  const hasLat = !!(lat?.length && lat.length === verts?.length);

  useEffect(() => {
    if (!hasGeom) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const reduced =
      typeof window !== "undefined" &&
      window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

    // center + scale
    const V = verts as [number, number, number][];
    const cx = V.reduce((a, p) => a + p[0], 0) / V.length;
    const cy = V.reduce((a, p) => a + p[1], 0) / V.length;
    const cz = V.reduce((a, p) => a + p[2], 0) / V.length;
    let radius = 0;
    for (const p of V)
      radius = Math.max(radius, Math.hypot(p[0] - cx, p[1] - cy, p[2] - cz));
    radius = radius || 1;

    let latMin = Infinity;
    let latMax = -Infinity;
    if (hasLat) {
      for (const v of lat as number[]) {
        latMin = Math.min(latMin, v);
        latMax = Math.max(latMax, v);
      }
    }
    const latRange = latMax - latMin || 1;

    const F = faces as [number, number, number][];
    const tilt = 1.32; // view long axis roughly vertical, apex down
    const st = Math.sin(tilt);
    const ctil = Math.cos(tilt);

    // scratch buffers
    const sx = new Float32Array(V.length);
    const syb = new Float32Array(V.length);
    const sz = new Float32Array(V.length);
    const order = new Uint32Array(F.length);
    const fdepth = new Float32Array(F.length);

    // Purkinje network (real LV + RV fractal trees, same coord frame as the surface). Flatten
    // both trees into one node list + an edge list tagged by chamber, projected each frame.
    const pkNodes: [number, number, number][] = [];
    const pkEdges: [number, number][] = [];
    const pkRv: boolean[] = [];
    if (purk) {
      for (const [tree, isRv] of [
        [purk.lv, false] as const,
        [purk.rv, true] as const,
      ]) {
        const off = pkNodes.length;
        for (const n of tree.nodes) pkNodes.push(n);
        for (const [a, b] of tree.edges) {
          pkEdges.push([off + a, off + b]);
          pkRv.push(isRv);
        }
      }
    }
    const pkx = new Float32Array(pkNodes.length);
    const pky = new Float32Array(pkNodes.length);
    const pkz = new Float32Array(pkNodes.length);

    let raf = 0;
    let frame = 0;

    let lastW = -1;
    let lastH = -1;
    function resize() {
      if (!canvas) return { w: 0, h: 0, dpr: 1 };
      const dpr = Math.min(2, window.devicePixelRatio || 1);
      const w = canvas.clientWidth;
      const h = canvas.clientHeight;
      // Only reallocate the backing store when the size actually changes;
      // reassigning canvas.width every frame clears and reallocates it.
      if (w !== lastW || h !== lastH) {
        canvas.width = Math.max(1, Math.round(w * dpr));
        canvas.height = Math.max(1, Math.round(h * dpr));
        lastW = w;
        lastH = h;
      }
      return { w, h, dpr };
    }

    function draw() {
      if (!canvas || !ctx) return;
      const { w, h, dpr } = resize();
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, w, h);

      const a = angleRef.current;
      const ca = Math.cos(a);
      const sa = Math.sin(a);
      const fit = (Math.min(w, h) * 0.42) / radius;
      const ox = w / 2;
      const oy = h / 2;

      // transform vertices: spin about long axis (z), then view tilt about x.
      for (let i = 0; i < V.length; i++) {
        const px = V[i][0] - cx;
        const py = V[i][1] - cy;
        const pz = V[i][2] - cz;
        const x1 = px * ca - py * sa;
        const y1 = px * sa + py * ca;
        const z1 = pz;
        const y2 = y1 * ctil - z1 * st;
        const z2 = y1 * st + z1 * ctil;
        sx[i] = ox + x1 * fit;
        syb[i] = oy + y2 * fit; // apex (z<0) -> larger y -> down
        sz[i] = z2; // depth toward camera
      }

      // painter's sort by face depth (far first)
      for (let f = 0; f < F.length; f++) {
        const [i0, i1, i2] = F[f];
        fdepth[f] = (sz[i0] + sz[i1] + sz[i2]) / 3;
        order[f] = f;
      }
      order.sort((p, q) => fdepth[p] - fdepth[q]);

      const thresh = hasLat ? latMin + sweepRef.current * latRange : Infinity;

      for (let k = 0; k < order.length; k++) {
        const f = order[k];
        const [i0, i1, i2] = F[f];
        // view-space normal for lambert shading
        const ax = sx[i1] - sx[i0];
        const ay = syb[i1] - syb[i0];
        const bx = sx[i2] - sx[i0];
        const by = syb[i2] - syb[i0];
        const az = sz[i1] - sz[i0];
        const bz = sz[i2] - sz[i0];
        const nx = ay * bz - az * by;
        const ny = az * bx - ax * bz;
        const nz = ax * by - ay * bx;
        const nn = Math.hypot(nx, ny, nz) || 1;
        const ndl = Math.abs((nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]) / nn);
        const shade = 0.45 + 0.55 * ndl;

        let r: number;
        let g: number;
        let b: number;
        if (hasLat) {
          const flat = ((lat as number[])[i0] + (lat as number[])[i1] + (lat as number[])[i2]) / 3;
          const activated = flat <= thresh;
          if (activated) {
            const t = (flat - latMin) / latRange;
            [r, g, b] = viridis(t);
            // leading-edge highlight
            const edge = (thresh - flat) / latRange;
            if (sweepRef.current < 0.999 && edge >= 0 && edge < 0.06) {
              const m = 1 - edge / 0.06;
              r = r + (255 - r) * 0.7 * m;
              g = g + (255 - g) * 0.7 * m;
              b = b + (255 - b) * 0.7 * m;
            }
          } else {
            // not yet reached: dim resting tissue
            r = 40;
            g = 40;
            b = 48;
          }
        } else {
          // no activation field: neutral chamber tint
          const isRv = chamber ? chamber[i0] === 1 : false;
          [r, g, b] = isRv ? [120, 113, 108] : [113, 113, 122];
        }
        ctx.fillStyle = `rgb(${Math.round(r * shade)},${Math.round(g * shade)},${Math.round(b * shade)})`;
        ctx.beginPath();
        ctx.moveTo(sx[i0], syb[i0]);
        ctx.lineTo(sx[i1], syb[i1]);
        ctx.lineTo(sx[i2], syb[i2]);
        ctx.closePath();
        ctx.fill();
      }

      // Purkinje network overlay: project the tree nodes with the same transform, draw the edges
      // with a depth fade (front branches brighter). LV cyan, RV amber.
      if (showPkRef.current && pkEdges.length) {
        for (let i = 0; i < pkNodes.length; i++) {
          const px = pkNodes[i][0] - cx;
          const py = pkNodes[i][1] - cy;
          const pz = pkNodes[i][2] - cz;
          const x1 = px * ca - py * sa;
          const y1 = px * sa + py * ca;
          const y2 = y1 * ctil - pz * st;
          const z2 = y1 * st + pz * ctil;
          pkx[i] = ox + x1 * fit;
          pky[i] = oy + y2 * fit;
          pkz[i] = z2;
        }
        ctx.lineWidth = 1;
        for (let e = 0; e < pkEdges.length; e++) {
          const [a, b] = pkEdges[e];
          const depth = Math.max(0, Math.min(1, ((pkz[a] + pkz[b]) / 2 + radius) / (2 * radius)));
          const alpha = 0.12 + 0.65 * depth;
          ctx.strokeStyle = pkRv[e] ? `rgba(255,176,80,${alpha})` : `rgba(110,220,255,${alpha})`;
          ctx.beginPath();
          ctx.moveTo(pkx[a], pky[a]);
          ctx.lineTo(pkx[b], pky[b]);
          ctx.stroke();
        }
      }
    }

    function tick() {
      frame++;
      // Honor prefers-reduced-motion: disable auto-spin on the first frame
      // (setState here is in the rAF callback, not the synchronous effect body).
      if (frame === 1 && reduced) {
        rotatingRef.current = false;
        setRotating(false);
      }
      if (rotatingRef.current) angleRef.current += 0.006;
      if (playingRef.current) {
        sweepRef.current += 0.006;
        if (sweepRef.current >= 1) {
          sweepRef.current = 1;
          playingRef.current = false;
          setPlaying(false);
        }
        if (frame % 4 === 0) setSweepPct(Math.round(sweepRef.current * 100));
      }
      draw();
      raf = requestAnimationFrame(tick);
    }

    raf = requestAnimationFrame(tick);
    const onResize = () => draw();
    window.addEventListener("resize", onResize);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", onResize);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hasGeom, hasLat]);

  if (!hasGeom) {
    return <EmptyState label="No geometry in this run (vertices/faces missing)." />;
  }

  const latMin = hasLat ? Math.min(...(lat as number[])) : 0;
  const latMax = hasLat ? Math.max(...(lat as number[])) : 0;

  function playSweep() {
    if (sweepRef.current >= 0.999) sweepRef.current = 0;
    playingRef.current = true;
    setPlaying(true);
  }
  function pauseSweep() {
    playingRef.current = false;
    setPlaying(false);
  }
  function onScrub(v: number) {
    playingRef.current = false;
    setPlaying(false);
    sweepRef.current = v / 100;
    setSweepPct(v);
  }
  function toggleRotate() {
    rotatingRef.current = !rotatingRef.current;
    setRotating(rotatingRef.current);
  }
  function togglePk() {
    showPkRef.current = !showPkRef.current;
    setShowPk(showPkRef.current);
  }

  return (
    <div>
      <div
        className="relative rounded-xl border border-zinc-800 bg-linear-to-b from-zinc-950 to-zinc-900 overflow-hidden"
        style={{ aspectRatio: "4 / 3" }}
      >
        <canvas
          ref={canvasRef}
          className="w-full h-full"
          role="img"
          aria-label="Rotating biventricular surface colored by local activation time; a wavefront sweep reveals the depolarization order."
        />
        {hasLat ? (
          <div className="absolute top-2 left-2 rounded-md bg-black/40 px-2 py-1 font-mono text-[10px] text-zinc-300">
            LAT sweep: {sweepPct}% {sweepPct < 100 ? `(${(latMin + (sweepPct / 100) * (latMax - latMin)).toFixed(0)} ms)` : "(full map)"}
          </div>
        ) : (
          <div className="absolute top-2 left-2 rounded-md bg-black/40 px-2 py-1 font-mono text-[10px] text-amber-300">
            activation_map missing: showing bare surface
          </div>
        )}
      </div>

      {/* controls */}
      <div className="mt-3 flex flex-wrap items-center gap-3">
        {hasLat ? (
          <>
            <button
              onClick={playing ? pauseSweep : playSweep}
              className="rounded-lg border border-indigo-500/50 bg-indigo-500/10 px-3 py-1.5 text-sm font-medium text-indigo-200 hover:bg-indigo-500/20"
            >
              {playing ? "Pause" : "Play wavefront"}
            </button>
            <label className="flex flex-1 items-center gap-2 text-xs text-zinc-400">
              <span className="font-mono">t</span>
              <input
                type="range"
                min={0}
                max={100}
                value={sweepPct}
                onChange={(e) => onScrub(Number(e.target.value))}
                className="flex-1 accent-indigo-400"
                aria-label="Activation-time sweep"
              />
            </label>
          </>
        ) : null}
        <button
          onClick={toggleRotate}
          className="rounded-lg border border-zinc-700 px-3 py-1.5 text-sm text-zinc-300 hover:bg-zinc-800"
          aria-pressed={rotating}
        >
          {rotating ? "Stop spin" : "Spin"}
        </button>
        {purk ? (
          <button
            onClick={togglePk}
            className="rounded-lg border border-zinc-700 px-3 py-1.5 text-sm text-zinc-300 hover:bg-zinc-800"
            aria-pressed={showPk}
          >
            {showPk ? "Hide Purkinje" : "Show Purkinje"}
          </button>
        ) : null}
      </div>

      {purk ? (
        <p className="mt-2 text-[11px] text-zinc-500">
          <span className="text-cyan-300">LV</span> and <span className="text-amber-300">RV</span>{" "}
          fractal Purkinje networks (the real trees that seed this activation:{" "}
          {purk.lv.nodes.length + purk.rv.nodes.length} nodes,{" "}
          {(purk.lv.n_pmj ?? 0) + (purk.rv.n_pmj ?? 0)} Purkinje-muscle junctions).
        </p>
      ) : null}

      {/* colorbar */}
      {hasLat ? (
        <div className="mt-3 flex items-center gap-2 text-[10px] font-mono text-zinc-500">
          <span>{latMin.toFixed(0)} ms</span>
          <div
            className="h-2 flex-1 rounded-full"
            style={{
              background:
                "linear-gradient(90deg, rgb(68,1,84), rgb(49,104,142), rgb(31,158,137), rgb(110,206,88), rgb(253,231,37))",
            }}
            aria-hidden="true"
          />
          <span>{latMax.toFixed(0)} ms</span>
          <span className="ml-1 text-zinc-600">early to late</span>
        </div>
      ) : null}
    </div>
  );
}
