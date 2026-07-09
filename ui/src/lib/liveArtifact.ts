"use client";

// Gated live-data path (Contract C), for the containerized demo ONLY
// (Dockerfile.demo: same-origin FastAPI serving both /infer and the static
// UI). The static S3 export never sets NEXT_PUBLIC_LIVE_API, so it always
// renders the build-time baked artifact from ./artifact.ts and this module
// does nothing. To turn it on for a build, set NEXT_PUBLIC_LIVE_API=1 before
// `npm run build` (e.g. an `ENV` line in Dockerfile.demo's ui build stage).
//
// ponytail: only the observation panels (EcgOverlay, ActivationMap) read this
// hook today; CornerPlot/PinnedUnknowable/CalibrationPanel/Header still read
// the static bake even in live mode. Wire paramSummary()/sampleColumn() etc.
// (lib/artifact.ts) to take an artifact argument if those need to go live too.
import { useEffect, useState } from "react";
import { results as baked, geometry as bakedGeometry, type ResultsArtifact, type Geometry } from "./artifact";

export const LIVE_API = process.env.NEXT_PUBLIC_LIVE_API === "1";

async function fetchLive(): Promise<{ results: ResultsArtifact; geometry: Geometry } | null> {
  try {
    const inferRes = await fetch("/infer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ geometry_id: baked.geometry_id, observation_kind: baked.observation_kind }),
    });
    if (!inferRes.ok) return null;
    const liveResults = (await inferRes.json()) as ResultsArtifact;

    // Contract C's /geometry/{id} is a descriptor today (no mesh yet, see
    // src/api/artifact.py::geometry_view), so keep the baked mesh unless a
    // future serializer actually starts returning vertices.
    let liveGeometry = bakedGeometry;
    const geomId = liveResults.geometry_id ?? baked.geometry_id;
    const geomRes = await fetch(`/geometry/${encodeURIComponent(geomId)}`);
    if (geomRes.ok) {
      const patch = (await geomRes.json()) as Partial<Geometry>;
      if (patch.vertices?.length) liveGeometry = patch as Geometry;
    }
    return { results: liveResults, geometry: liveGeometry };
  } catch {
    return null; // no backend at this origin (e.g. the static export): stay on the baked artifact
  }
}

// Client-only hook: starts on the build-time baked artifact, swaps to a live
// /infer + /geometry read once (if LIVE_API is on and the fetch succeeds).
export function useArtifact(): { results: ResultsArtifact; geometry: Geometry; live: boolean } {
  const [live, setLive] = useState<{ results: ResultsArtifact; geometry: Geometry } | null>(null);

  useEffect(() => {
    if (!LIVE_API) return;
    let cancelled = false;
    fetchLive().then((v) => {
      if (!cancelled && v) setLive(v);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  return live
    ? { results: live.results, geometry: live.geometry, live: true }
    : { results: baked, geometry: bakedGeometry, live: false };
}
