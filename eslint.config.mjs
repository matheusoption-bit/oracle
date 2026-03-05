import { defineConfig, globalIgnores } from "eslint/config";
import nextPlugin from "@next/eslint-plugin-next";
import tseslint from "typescript-eslint";

const nextCoreWebVitalsRules = nextPlugin.configs["core-web-vitals"]?.rules ?? {};

export default defineConfig([
  ...tseslint.configs.recommended,
  {
    files: ["src/**/*.{js,jsx,ts,tsx,mjs,cjs}", "*.config.{js,mjs,cjs,ts}"],
    plugins: {
      "@next/next": nextPlugin,
    },
    rules: {
      ...nextCoreWebVitalsRules,
    },
  },
  globalIgnores([
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
    "orchestrator/**",
    "workspace/**",
    "docker/**",
    "docs/**",
  ]),
]);
