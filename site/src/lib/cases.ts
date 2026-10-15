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

/** Render metadata written by galleria next to the media (media.json). */
export interface MediaMeta {
  dimension: number;
  field: string;
  /** color range [min, max] (2D) or value range (1D) */
  range: [number, number];
  diverging?: boolean;
  /** colormap stops evenly spaced in value, hex (2D only) */
  legend?: string[];
  /** domain width / height (2D only) */
  aspect?: number;
  frames: number;
  mesh: { levels: number; cells: number };
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
  /** raw README.md contents (Markdown + LaTeX) */
  readme: string;
  /** raw source code shown on the case page (main.cpp, or the engine scenario) */
  code: string;
  /** file name of the displayed code (e.g. main.cpp or scenario.hpp) */
  codeFile: string;
  /** name of the external engine powering this case, if any */
  engine: string | null;
  /** samurai git ref this case is tested against (local cases) */
  samuraiRef: string | null;
  /** engine git ref this case is tested against (engine cases) */
  engineRef: string | null;
  /** site-relative, theme-specific media paths (populated by collect-media) */
  thumbnailDarkUrl: string;
  thumbnailLightUrl: string;
  heroDarkUrl: string;
  heroLightUrl: string;
  /** render metadata, null when the media have not been generated */
  media: MediaMeta | null;
}

function readIfExists(p: string): string {
  return fs.existsSync(p) ? fs.readFileSync(p, "utf-8") : "";
}

function readMedia(dir: string): MediaMeta | null {
  const raw = readIfExists(path.join(dir, "media.json"));
  if (!raw) return null;
  try {
    return JSON.parse(raw) as MediaMeta;
  } catch {
    return null;
  }
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
      const mediaBase = `media/${category}/${slug}`;

      // Displayed code: a local main.cpp, or the engine scenario file.
      const engine = meta.engine ?? null;
      const codeFile = engine?.code_file ?? "main.cpp";
      // Engine name shown on the site: the repo's last path segment.
      const engineName = engine?.repo
        ? engine.repo.split("/").pop()!.replace(/\.git$/, "")
        : engine
          ? "engine"
          : null;

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
        readme: readIfExists(path.join(dir, "README.md")),
        code: readIfExists(path.join(dir, codeFile)),
        codeFile,
        engine: engineName,
        samuraiRef: meta.samurai?.ref ?? null,
        engineRef: engine?.ref ?? null,
        thumbnailDarkUrl: `${mediaBase}/thumbnail-dark.png`,
        thumbnailLightUrl: `${mediaBase}/thumbnail-light.png`,
        heroDarkUrl: `${mediaBase}/preview-dark.mp4`,
        heroLightUrl: `${mediaBase}/preview-light.mp4`,
        media: readMedia(dir),
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

export const DIFFICULTY_LABELS: Record<string, string> = {
  beginner: "Beginner",
  intermediate: "Intermediate",
  advanced: "Advanced",
};

/** Tags that are acronyms or scheme names rather than words. */
export const TAG_LABELS: Record<string, string> = {
  hllc: "HLLC",
  weno5: "WENO5",
  "mesh-adaptation": "Mesh adaptation",
};

export const REQUIRES_LABELS: Record<string, string> = {
  mpi: "MPI",
  petsc: "PETSc",
  openmp: "OpenMP",
  cgal: "CGAL",
};

/**
 * Methods the gallery is built to show but has no case for yet. They appear on
 * the wall as screens on standby (the README lists them on the roadmap).
 */
export const ROADMAP_METHODS = ["lattice-boltzmann", "finite-difference"];

/** Typographic name of a field written by a solver (rho, phi, alpha_l...). */
export function fieldSymbol(field: string): string {
  const greek: Record<string, string> = {
    rho: "ρ",
    phi: "φ",
    alpha: "α",
    psi: "ψ",
    omega: "ω",
    theta: "θ",
  };
  const [head, ...rest] = field.split("_");
  const sym = greek[head] ?? head;
  return rest.length ? `${sym}_${rest.join("_")}` : sym;
}

/** A facet of the wall's console: one case.yaml field, its values and labels. */
export interface Facet {
  key: string;
  label: string;
  values: { value: string; label: string; count: number }[];
}

function facetOf(
  cases: GalleryCase[],
  key: string,
  label: string,
  pick: (c: GalleryCase) => string[],
  labels: Record<string, string> = {},
): Facet {
  const counts = new Map<string, number>();
  for (const c of cases) for (const v of pick(c)) counts.set(v, (counts.get(v) ?? 0) + 1);
  const values = [...counts.entries()]
    .map(([value, count]) => ({ value, label: labels[value] ?? titleize(value), count }))
    .sort((a, b) => b.count - a.count || a.label.localeCompare(b.label));
  return { key, label, values };
}

/** The facets of the console, built from every case's metadata. */
export function getFacets(cases: GalleryCase[]): Facet[] {
  return [
    facetOf(cases, "equation", "Equation", (c) => [c.equation]),
    facetOf(cases, "method", "Method", (c) => c.methods, METHOD_LABELS),
    facetOf(cases, "dimension", "Dimension", (c) => [`${c.dimension}d`], { "1d": "1D", "2d": "2D", "3d": "3D" }),
    facetOf(cases, "mesh", "Mesh", (c) => [c.adaptation], ADAPTATION_LABELS),
    facetOf(cases, "level", "Level", (c) => [c.difficulty], DIFFICULTY_LABELS),
    facetOf(cases, "requires", "Requires", (c) => c.requires, REQUIRES_LABELS),
    facetOf(cases, "tag", "Tags", (c) => c.tags, TAG_LABELS),
  ].filter((f) => f.values.length > 0);
}

/** Facet values of one case, as written in the wall's data attributes. */
export function facetValues(c: GalleryCase): Record<string, string[]> {
  return {
    equation: [c.equation],
    method: c.methods,
    dimension: [`${c.dimension}d`],
    mesh: [c.adaptation],
    level: [c.difficulty],
    requires: c.requires,
    tag: c.tags,
  };
}

export function titleize(slug: string): string {
  return slug.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
