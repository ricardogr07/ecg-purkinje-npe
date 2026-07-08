import type { NextConfig } from "next";

// Static export, mirrors the shelter-pulse pattern (nginx serves the out/ dir,
// no CORS, one origin). The demo reads the bundled Contract-B mock, so it needs
// no live backend to render.
const nextConfig: NextConfig = {
  output: "export",
};

export default nextConfig;
