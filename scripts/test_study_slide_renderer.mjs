#!/usr/bin/env node

import { execFile } from "node:child_process";
import { mkdtemp, mkdir, cp, readFile, rm, symlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import process from "node:process";
import { promisify } from "node:util";
import { fileURLToPath } from "node:url";
import { PDFDocument } from "pdf-lib";

const execFileAsync = promisify(execFile);
const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const PDF_PRODUCER = "Open Study Path HTML slide renderer v2";

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function runRenderer(renderer, root) {
  const { stdout, stderr } = await execFileAsync(
    process.execPath,
    [renderer, "--root", root, "--topic", "TOPIC-000"],
    { cwd: REPO_ROOT, timeout: 60_000, maxBuffer: 4 * 1024 * 1024 },
  );
  if (stdout) process.stdout.write(stdout);
  if (stderr) process.stderr.write(stderr);
}

async function main() {
  const root = await mkdtemp(path.join(tmpdir(), "open-study-path-slides-"));
  try {
    const topicDir = path.join(root, "study", "slides", "TOPIC-000");
    const moduleDir = path.join(root, "study", "modules");
    await mkdir(path.dirname(topicDir), { recursive: true });
    await mkdir(moduleDir, { recursive: true });
    await cp(path.join(REPO_ROOT, "templates", "study-slides"), topicDir, { recursive: true });
    await writeFile(
      path.join(moduleDir, "TOPIC-000.md"),
      "# Aula de teste\n\nConteúdo aprovado usado somente pelo smoke test do renderer.\n",
      "utf8",
    );
    await symlink(path.join(REPO_ROOT, "node_modules"), path.join(root, "node_modules"), "dir");

    const renderer = path.join(REPO_ROOT, "scripts", "render_study_slides.mjs");
    await runRenderer(renderer, root);

    const pdfPath = path.join(topicDir, "slides.pdf");
    const metaPath = path.join(topicDir, "slides.meta.json");
    const pdf = await readFile(pdfPath);
    const meta = JSON.parse(await readFile(metaPath, "utf8"));
    const document = await PDFDocument.load(pdf, { ignoreEncryption: true });
    assert(pdf.subarray(0, 5).toString("ascii") === "%PDF-", "renderer smoke PDF header is invalid");
    assert(pdf.length > 20_000, "renderer smoke PDF is unexpectedly small");
    assert(meta.contract_version === 2, "renderer smoke metadata contract mismatch");
    assert(meta.renderer.id === "open-study-path-html-v2", "renderer smoke renderer id mismatch");
    assert(meta.topic_id === "TOPIC-000", "renderer smoke topic mismatch");
    assert(meta.content_version === 1, "renderer smoke content version mismatch");
    assert(meta.slide_count === 10, "renderer smoke slide count mismatch");
    assert(meta.mermaid_count >= 1, "renderer smoke Mermaid diagram was not recorded");
    assert(meta.pdf.pages === meta.slide_count, "renderer smoke PDF page count mismatch");
    assert(meta.pdf.bytes === pdf.length, "renderer smoke PDF byte metadata mismatch");
    assert(meta.pdf.producer === PDF_PRODUCER, "renderer smoke PDF producer metadata mismatch");
    assert(document.getTitle() === "TOPIC-000 study slides", "renderer smoke embedded title mismatch");
    assert(document.getSubject().includes("open-study-path-html-v2"), "renderer smoke PDF is not bound to renderer identity");
    assert(document.getSubject().includes(meta.source_digest), "renderer smoke PDF is not bound to source digest");
    assert(document.getSubject().includes(meta.rendered_snapshot_sha256), "renderer smoke PDF is not bound to rendered snapshot");
    assert(meta.diagnostics.console_errors.length === 0, "renderer smoke has console errors");
    assert(meta.diagnostics.overflow_slides.length === 0, "renderer smoke has slide overflow");
    assert(meta.diagnostics.external_requests.length === 0, "renderer smoke made external requests");

    await rm(pdfPath, { force: true });
    await rm(metaPath, { force: true });
    await runRenderer(renderer, root);
    const secondPdf = await readFile(pdfPath);
    const secondMeta = JSON.parse(await readFile(metaPath, "utf8"));
    assert(
      secondMeta.rendered_snapshot_sha256 === meta.rendered_snapshot_sha256,
      "renderer smoke Mermaid snapshot changed between identical renders",
    );
    assert(secondMeta.pdf.sha256 === meta.pdf.sha256, "renderer smoke PDF hash changed between identical renders");
    assert(secondPdf.equals(pdf), "renderer smoke PDF bytes changed between identical renders");
    console.log("Study-slide Chromium, Mermaid and deterministic PDF provenance smoke test passed.");
  } finally {
    await rm(root, { recursive: true, force: true });
  }
}

main().catch((error) => {
  console.error(`ERROR: ${error?.stack || error}`);
  process.exit(1);
});
