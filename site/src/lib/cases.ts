import fs from "node:fs";
import path from "node:path";
import { parse as parseYaml } from "yaml";

// The gallery cases live outside the site, at <repo>/cases. The site is the
// single consumer: metadata, explanation and code are all read from there.
const CASES_DIR = path.resolve(process.cwd(), "..", "cases");

export interface Reference {
  text: string;
  url: string;
}

export interface CaseProfile {
  args: string[];
  nfiles: number;
}

export interface GalleryCase {
  /** category/slug, e.g. "getting-started/advection-2d" */
  id: string;
  category: string;
  slug: string;
  title: string;
  summary: string;
  authors: string[];
  methods: string[];
  equation: string;
  dimension: number;
  adaptation: string;
  difficulty: string;
  featured: boolean;
  tags: string[];
  requires: string[];
  references: Reference[];
  media: { thumbnail: string; hero: string };
  /** raw README.md contents (Markdown + LaTeX) */
  readme: string;
  /** raw main.cpp contents */
  code: string;
  /** site-relative media paths (populated by collect-media) */
  thumbnailUrl: string;
  heroUrl: string;
}

function readIfExists(p: string): string {
  return fs.existsSync(p) ? fs.readFileSync(p, "utf-8") : "";
}

export function getCases(): GalleryCase[] {
  const cases: GalleryCase[] = [];
  if (!fs.existsSync(CASES_DIR)) return cases;

  for (const category of fs.readdirSync(CASES_DIR)) {
    const categoryDir = path.join(CASES_DIR, category);
    if (!fs.statSync(categoryDir).isDirectory()) continue;

    for (const slug of fs.readdirSync(categoryDir)) {
      const dir = path.join(categoryDir, slug);
      const yamlPath = path.join(dir, "case.yaml");
      if (!fs.existsSync(yamlPath)) continue;

      const meta = parseYaml(fs.readFileSync(yamlPath, "utf-8")) ?? {};
      const media = meta.media ?? {};
      const thumbnail = media.thumbnail ?? "thumbnail.png";
      const hero = media.hero ?? "preview.mp4";

      cases.push({
        id: `${category}/${slug}`,
        category,
        slug,
        title: meta.title ?? slug,
        summary: meta.summary ?? "",
        authors: meta.authors ?? [],
        methods: meta.methods ?? [],
        equation: meta.equation ?? "",
        dimension: meta.dimension ?? 2,
        adaptation: meta.adaptation ?? "none",
        difficulty: meta.difficulty ?? "intermediate",
        featured: meta.featured ?? false,
        tags: meta.tags ?? [],
        requires: meta.requires ?? [],
        references: meta.references ?? [],
        media: { thumbnail, hero },
        readme: readIfExists(path.join(dir, "README.md")),
        code: readIfExists(path.join(dir, "main.cpp")),
        thumbnailUrl: `media/${category}/${slug}/${thumbnail}`,
        heroUrl: `media/${category}/${slug}/${hero}`,
      });
    }
  }

  // Featured first, then by category, then by title.
  cases.sort((a, b) => {
    if (a.featured !== b.featured) return a.featured ? -1 : 1;
    if (a.category !== b.category) return a.category.localeCompare(b.category);
    return a.title.localeCompare(b.title);
  });

  return cases;
}

/** Human labels for method slugs. */
export const METHOD_LABELS: Record<string, string> = {
  "finite-volume": "Finite volume",
  "lattice-boltzmann": "Lattice Boltzmann",
  "finite-difference": "Finite difference",
};

export const ADAPTATION_LABELS: Record<string, string> = {
  multiresolution: "Multiresolution",
  amr: "AMR",
  uniform: "Uniform",
  none: "No adaptation",
};

export function titleize(slug: string): string {
  return slug.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
