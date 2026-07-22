import MarkdownIt from "markdown-it";
import texmath from "markdown-it-texmath";
import katex from "katex";

// Markdown + LaTeX renderer used for case README files. Math is rendered to
// static HTML with KaTeX at build time (no client-side JS needed).
const md = new MarkdownIt({
  html: false,
  linkify: true,
  // typographer is off on purpose: it rewrites "--flag" into an en-dash,
  // which mangles the CLI options documented in case READMEs.
  typographer: false,
}).use(texmath, {
  engine: katex,
  delimiters: "dollars",
  katexOptions: { throwOnError: false },
});

export function renderMarkdown(source: string): string {
  return md.render(source ?? "");
}
