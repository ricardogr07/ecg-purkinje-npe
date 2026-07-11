import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Ignore build output, generated mocks, and the gitignored design-system tooling/bundle
  // (.ds-sync, ds-bundle: internal, not app source, includes a vendored minified react).
  globalIgnores([
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
    "mock/**",
    ".ds-sync/**",
    "ds-bundle/**",
  ]),
]);

export default eslintConfig;
