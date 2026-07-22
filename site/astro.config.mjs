import { defineConfig } from "astro/config";

// For GitHub Pages the site is served under /<repo>/. Both values can be
// overridden from the environment in CI (SITE_URL / BASE_PATH).
const site = process.env.SITE_URL ?? "https://hpc-math-samurai.github.io";
const base = process.env.BASE_PATH ?? "/samurai-gallery";

export default defineConfig({
  site,
  base,
  trailingSlash: "ignore",
  markdown: {
    syntaxHighlight: "shiki",
    shikiConfig: { theme: "github-dark" },
  },
});
