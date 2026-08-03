#!/usr/bin/env node
import { execFile } from "node:child_process";
import { cp, mkdtemp, mkdir, readFile, rm, symlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import process from "node:process";
import { promisify } from "node:util";
import { fileURLToPath } from "node:url";
import { PDFDocument } from "pdf-lib";

const execFileAsync = promisify(execFile);
const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const PDF_PRODUCER = "Open Study Path static SVG PDF renderer v3";
function assert(condition, message) { if (!condition) throw new Error(message); }

async function runRenderer(root, ...args) {
  const renderer = path.join(REPO_ROOT, "scripts", "render_study_slides.mjs");
  const { stdout, stderr } = await execFileAsync(process.execPath, [renderer, "--root", root, "--topic", "TOPIC-000", ...args], {
    cwd: REPO_ROOT, timeout: 180_000, maxBuffer: 8 * 1024 * 1024,
  });
  if (stdout) process.stdout.write(stdout); if (stderr) process.stderr.write(stderr);
}

async function main() {
  const root = await mkdtemp(path.join(tmpdir(), "open-study-path-static-svg-"));
  try {
    const topicDir = path.join(root, "study", "slides", "TOPIC-000");
    await mkdir(path.dirname(topicDir), { recursive: true });
    await cp(path.join(REPO_ROOT, "templates", "study-slides"), topicDir, { recursive: true });
    await mkdir(path.join(root, "templates"), { recursive: true });
    await cp(path.join(REPO_ROOT, "templates", "study-slides"), path.join(root, "templates", "study-slides"), { recursive: true });
    await symlink(path.join(REPO_ROOT, "node_modules"), path.join(root, "node_modules"), "dir");
    await writeFile(path.join(root, ".open-study-path-placeholder"), "test", "utf8");
    await runRenderer(root);

    const pdfPath = path.join(topicDir, "slides.pdf");
    const metaPath = path.join(topicDir, "slides.meta.json");
    const svgPath = path.join(topicDir, "diagrams", "flow.svg");
    const pdf = await readFile(pdfPath); const meta = JSON.parse(await readFile(metaPath, "utf8")); const svg = await readFile(svgPath, "utf8");
    const document = await PDFDocument.load(pdf, { ignoreEncryption: true });
    assert(svg.includes("<svg"), "renderer did not produce SVG");
    assert(!svg.toLowerCase().includes("<script"), "renderer SVG contains script");
    assert(pdf.subarray(0, 5).toString("ascii") === "%PDF-", "renderer PDF header is invalid");
    assert(meta.contract_version === 3, "renderer metadata contract mismatch");
    assert(meta.renderer.id === "open-study-path-html-svg-pdf-v3", "renderer id mismatch");
    assert(meta.slide_count === 12, "renderer slide count mismatch");
    assert(meta.diagram_count >= 1, "renderer diagram count mismatch");
    assert(meta.pdf.pages === meta.slide_count, "renderer PDF page count mismatch");
    assert(meta.pdf.producer === PDF_PRODUCER, "renderer PDF producer mismatch");
    assert(document.getTitle() === "TOPIC-000 study slides", "embedded title mismatch");
    assert(document.getSubject().includes(meta.source_digest), "PDF subject is not bound to source digest");
    assert(meta.diagnostics.console_errors.length === 0, "renderer console errors are not clean");
    assert(meta.diagnostics.overflow_slides.length === 0, "renderer overflow diagnostics are not clean");
    await runRenderer(root, "--check");
    console.log("Static Mermaid SVG and deterministic PDF renderer smoke test passed.");
  } finally { await rm(root, { recursive: true, force: true }); }
}

main().catch((error) => { console.error(`ERROR: ${error?.stack || error}`); process.exit(1); });
