#!/usr/bin/env node

import { execFile } from "node:child_process";
import { mkdtemp, mkdir, cp, readFile, rm, symlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import process from "node:process";
import { promisify } from "node:util";
import { fileURLToPath } from "node:url";

const execFileAsync = promisify(execFile);
const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function assert(condition, message) {
  if (!condition) throw new Error(message);
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
    const { stdout, stderr } = await execFileAsync(
      process.execPath,
      [renderer, "--root", root, "--topic", "TOPIC-000"],
      { cwd: REPO_ROOT, timeout: 60_000, maxBuffer: 4 * 1024 * 1024 },
    );
    if (stdout) process.stdout.write(stdout);
    if (stderr) process.stderr.write(stderr);

    const pdf = await readFile(path.join(topicDir, "slides.pdf"));
    const meta = JSON.parse(await readFile(path.join(topicDir, "slides.meta.json"), "utf8"));
    assert(pdf.subarray(0, 5).toString("ascii") === "%PDF-", "renderer smoke PDF header is invalid");
    assert(pdf.length > 10_000, "renderer smoke PDF is unexpectedly small");
    assert(meta.contract_version === 1, "renderer smoke metadata contract mismatch");
    assert(meta.topic_id === "TOPIC-000", "renderer smoke topic mismatch");
    assert(meta.content_version === 1, "renderer smoke content version mismatch");
    assert(meta.slide_count === 6, "renderer smoke slide count mismatch");
    assert(meta.mermaid_count >= 1, "renderer smoke Mermaid diagram was not recorded");
    assert(meta.pdf.pages === meta.slide_count, "renderer smoke PDF page count mismatch");
    assert(meta.pdf.bytes === pdf.length, "renderer smoke PDF byte metadata mismatch");
    assert(meta.diagnostics.console_errors.length === 0, "renderer smoke has console errors");
    assert(meta.diagnostics.overflow_slides.length === 0, "renderer smoke has slide overflow");
    assert(meta.diagnostics.external_requests.length === 0, "renderer smoke made external requests");
    console.log("Study-slide Chromium and Mermaid rendering smoke test passed.");
  } finally {
    await rm(root, { recursive: true, force: true });
  }
}

main().catch((error) => {
  console.error(`ERROR: ${error?.stack || error}`);
  process.exit(1);
});
