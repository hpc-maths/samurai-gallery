// Copy each case's generated media (thumbnail.png, preview.mp4) into
// public/media/<category>/<slug>/ so the built site can serve them.
// Missing media are skipped: the site falls back to a placeholder.
import fs from "node:fs";
import path from "node:path";

const ROOT = path.resolve(process.cwd(), "..");
const CASES = path.join(ROOT, "cases");
const DEST = path.resolve(process.cwd(), "public", "media");

const MEDIA_FILES = [
  "thumbnail-dark.png",
  "thumbnail-light.png",
  "preview-dark.mp4",
  "preview-light.mp4",
];

let copied = 0;
let missing = 0;

if (fs.existsSync(DEST)) fs.rmSync(DEST, { recursive: true, force: true });

for (const category of fs.existsSync(CASES) ? fs.readdirSync(CASES) : []) {
  const categoryDir = path.join(CASES, category);
  if (!fs.statSync(categoryDir).isDirectory()) continue;

  for (const slug of fs.readdirSync(categoryDir)) {
    const dir = path.join(categoryDir, slug);
    if (!fs.existsSync(path.join(dir, "case.yaml"))) continue;

    const out = path.join(DEST, category, slug);
    for (const file of MEDIA_FILES) {
      const src = path.join(dir, file);
      if (fs.existsSync(src)) {
        fs.mkdirSync(out, { recursive: true });
        fs.copyFileSync(src, path.join(out, file));
        copied++;
      } else {
        missing++;
        console.warn(`  (no ${file} for ${category}/${slug})`);
      }
    }
  }
}

console.log(`collect-media: ${copied} file(s) copied, ${missing} missing.`);
