#!/usr/bin/env node

import { createHash } from "node:crypto";
import { createServer } from "node:http";
import { promises as fs } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import process from "node:process";
import { PDFDocument } from "pdf-lib";
import { chromium } from "playwright";

const require = createRequire(import.meta.url);
const PLAYWRIGHT_VERSION = require("playwright/package.json").version;
const MERMAID_VERSION = require("mermaid/package.json").version;
const PDF_LIB_VERSION = require("pdf-lib/package.json").version;
const SOURCE_FILES = ["index.html", "slides.css", "slides.js"];
const DIAGNOSTIC_ROOT = ".open-study-path/rendered-slides";
const PRINT_OVERRIDE = `
@page { size: 1280px 720px; margin: 0; }
html, body {
  width: 0 !important;
  height: 0 !important;
  min-width: 0 !important;
  min-height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: visible !important;
  background: #080a0f !important;
  print-color-adjust: exact !important;
  -webkit-print-color-adjust: exact !important;
}
.osp-slide, .osp-slide.is-active {
  display: flex !important;
  position: fixed !important;
  inset: 0 auto auto 0 !important;
  flex-direction: column !important;
  justify-content: center !important;
  width: 1280px !important;
  min-width: 1280px !important;
  max-width: 1280px !important;
  height: 720px !important;
  min-height: 720px !important;
  max-height: 720px !important;
  margin: 0 !important;
  break-before: auto !important;
  break-after: auto !important;
  break-inside: avoid-page !important;
  page-break-before: auto !important;
  page-break-after: auto !important;
  page-break-inside: avoid !important;
  box-shadow: none !important;
}
.osp-controls { display: none !important; }
`;

function parseArgs(argv) {
  const result = { root: process.cwd(), topics: [], check: false };
  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === "--root") result.root = argv[++index];
    else if (value === "--topic") result.topics.push(argv[++index]);
    else if (value === "--check") result.check = true;
    else if (value === "--help") {
      console.log("Usage: node scripts/render_study_slides.mjs [--root PATH] [--topic TOPIC-001] [--check]");
      process.exit(0);
    } else throw new Error(`Unknown argument: ${value}`);
  }
  return result;
}

function sha256(buffer) {
  return createHash("sha256").update(buffer).digest("hex");
}

async function fileHash(file) {
  return sha256(await fs.readFile(file));
}

async function aggregateHash(root, files) {
  const digest = createHash("sha256");
  for (const file of [...files].sort()) {
    const relative = path.relative(root, file).split(path.sep).join("/");
    digest.update(relative);
    digest.update("\0");
    digest.update(await fileHash(file));
    digest.update("\n");
  }
  return digest.digest("hex");
}

function contentType(file) {
  const extension = path.extname(file).toLowerCase();
  return {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".mjs": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
  }[extension] || "application/octet-stream";
}

async function startServer(root) {
  const resolvedRoot = path.resolve(root);
  const server = createServer(async (request, response) => {
    try {
      const requested = decodeURIComponent(new URL(request.url, "http://127.0.0.1").pathname);
      const candidate = path.resolve(resolvedRoot, `.${requested}`);
      if (candidate !== resolvedRoot && !candidate.startsWith(`${resolvedRoot}${path.sep}`)) {
        response.writeHead(403).end("Forbidden");
        return;
      }
      const stat = await fs.stat(candidate);
      const file = stat.isDirectory() ? path.join(candidate, "index.html") : candidate;
      response.writeHead(200, {
        "Content-Type": contentType(file),
        "Cache-Control": "no-store",
        "X-Content-Type-Options": "nosniff",
      });
      response.end(await fs.readFile(file));
    } catch (error) {
      response.writeHead(error?.code === "ENOENT" ? 404 : 500).end(String(error));
    }
  });
  await new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", resolve);
  });
  const address = server.address();
  return { server, origin: `http://127.0.0.1:${address.port}` };
}

async function findTopics(root, selected) {
  if (selected.length) return [...new Set(selected)].sort();
  const slidesRoot = path.join(root, "study", "slides");
  try {
    const entries = await fs.readdir(slidesRoot, { withFileTypes: true });
    return entries
      .filter((entry) => entry.isDirectory() && /^TOPIC-\d{3,}$/.test(entry.name))
      .map((entry) => entry.name)
      .sort();
  } catch (error) {
    if (error?.code === "ENOENT") return [];
    throw error;
  }
}

async function readMetaTags(page) {
  return page.evaluate(() => {
    const topic = document.querySelector('meta[name="open-study-path:topic-id"]')?.content || "";
    const rawVersion = document.querySelector('meta[name="open-study-path:content-version"]')?.content || "";
    return { topicId: topic, contentVersion: Number(rawVersion) };
  });
}

async function diagnostics(page) {
  return page.evaluate(() => {
    const slides = Array.from(document.querySelectorAll(".osp-slide"));
    const overflowSlides = slides
      .map((slide, index) => ({
        index: index + 1,
        horizontal: slide.scrollWidth > slide.clientWidth + 1,
        vertical: slide.scrollHeight > slide.clientHeight + 1,
      }))
      .filter((item) => item.horizontal || item.vertical)
      .map((item) => item.index);
    const mermaidNodes = Array.from(document.querySelectorAll(".mermaid"));
    const unrenderedMermaid = mermaidNodes
      .map((node, index) => ({
        index: index + 1,
        processed: node.dataset.processed === "true",
        svg: Boolean(node.querySelector("svg")),
      }))
      .filter((item) => !item.processed || !item.svg)
      .map((item) => item.index);
    const outcomeIds = [];
    for (const slide of slides) {
      for (const value of (slide.dataset.outcomeIds || "").split(/\s+/).filter(Boolean)) {
        if (!outcomeIds.includes(value)) outcomeIds.push(value);
      }
    }
    return {
      slideCount: slides.length,
      mermaidCount: mermaidNodes.length,
      overflowSlides,
      unrenderedMermaid,
      outcomeIds,
      runtimeError: window.__OPEN_STUDY_PATH_SLIDES_ERROR__ || null,
    };
  });
}

async function snapshotDeck(page) {
  return page.evaluate(() => {
    const styles = Array.from(document.styleSheets)
      .flatMap((sheet) => {
        try {
          return Array.from(sheet.cssRules, (rule) => rule.cssText);
        } catch {
          return [];
        }
      })
      .join("\n");
    const slides = Array.from(document.querySelectorAll(".osp-slide"), (slide) => slide.outerHTML);
    return { styles, slides };
  });
}

async function pdfPageCount(buffer) {
  const document = await PDFDocument.load(buffer, { ignoreEncryption: true });
  return document.getPageCount();
}

async function sourceMetadata(root, topic) {
  const topicDir = path.join(root, "study", "slides", topic);
  const lesson = path.join(root, "study", "modules", `${topic}.md`);
  const files = [...SOURCE_FILES.map((name) => path.join(topicDir, name)), lesson];
  const sourceSha256 = {};
  for (const file of files) {
    const relative = path.relative(root, file).split(path.sep).join("/");
    sourceSha256[relative] = await fileHash(file);
  }
  return { files, sourceSha256, sourceDigest: await aggregateHash(root, files) };
}

function arraysEqual(left, right) {
  return JSON.stringify(left) === JSON.stringify(right);
}

async function currentArtifactsAreFresh(topicDir, expected) {
  try {
    const meta = JSON.parse(await fs.readFile(path.join(topicDir, "slides.meta.json"), "utf8"));
    const pdf = await fs.readFile(path.join(topicDir, "slides.pdf"));
    const diagnosticsAreClean =
      arraysEqual(meta?.diagnostics?.console_errors, []) &&
      arraysEqual(meta?.diagnostics?.overflow_slides, []) &&
      arraysEqual(meta?.diagnostics?.external_requests, []);
    return (
      meta.contract_version === 1 &&
      meta.topic_id === expected.topicId &&
      meta.content_version === expected.contentVersion &&
      meta?.renderer?.playwright === PLAYWRIGHT_VERSION &&
      meta?.renderer?.mermaid === MERMAID_VERSION &&
      meta?.renderer?.pdf_lib === PDF_LIB_VERSION &&
      meta.slide_count === expected.slideCount &&
      meta.mermaid_count === expected.mermaidCount &&
      arraysEqual(meta.outcome_ids, expected.outcomeIds) &&
      meta.source_digest === expected.sourceDigest &&
      JSON.stringify(meta.source_sha256) === JSON.stringify(expected.sourceSha256) &&
      meta?.pdf?.pages === expected.slideCount &&
      meta?.pdf?.pages === await pdfPageCount(pdf) &&
      meta?.pdf?.bytes === pdf.length &&
      meta?.pdf?.sha256 === sha256(pdf) &&
      diagnosticsAreClean
    );
  } catch {
    return false;
  }
}

async function renderSinglePage(printPage, styles, slideHtml, slideIndex) {
  const document = `<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<style>${styles}\n${PRINT_OVERRIDE}</style>
</head>
<body>${slideHtml}</body>
</html>`;
  await printPage.setContent(document, { waitUntil: "load" });
  await printPage.evaluate(() => document.fonts.ready);
  const bytes = await printPage.pdf({
    width: "1280px",
    height: "720px",
    printBackground: true,
    preferCSSPageSize: true,
    margin: { top: "0", right: "0", bottom: "0", left: "0" },
  });
  const pdf = await PDFDocument.load(bytes, { ignoreEncryption: true });
  if (pdf.getPageCount() !== 1) {
    throw new Error(`slide ${slideIndex + 1} rendered as ${pdf.getPageCount()} PDF pages`);
  }
  return pdf;
}

async function renderDeckPdf(browser, snapshot) {
  const printPage = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
  await printPage.emulateMedia({ media: "print" });
  const merged = await PDFDocument.create();
  try {
    for (let index = 0; index < snapshot.slides.length; index += 1) {
      const source = await renderSinglePage(printPage, snapshot.styles, snapshot.slides[index], index);
      const [copied] = await merged.copyPages(source, [0]);
      merged.addPage(copied);
    }
  } finally {
    await printPage.close();
  }
  const bytes = await merged.save({ useObjectStreams: false });
  return Buffer.from(bytes);
}

async function renderTopic({ browser, root, origin, topic, check }) {
  const topicDir = path.join(root, "study", "slides", topic);
  for (const source of SOURCE_FILES) await fs.access(path.join(topicDir, source));
  const consoleErrors = [];
  const externalRequests = [];
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  page.on("pageerror", (error) => consoleErrors.push(String(error?.stack || error)));
  await page.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (url.origin !== origin) {
      externalRequests.push(route.request().url());
      await route.abort("blockedbyclient");
      return;
    }
    await route.continue();
  });

  await page.goto(`${origin}/study/slides/${topic}/index.html`, { waitUntil: "domcontentloaded" });
  await page.waitForFunction(() => window.__OPEN_STUDY_PATH_SLIDES_READY__ === true, null, { timeout: 30_000 });
  await page.evaluate(() => document.fonts.ready);
  const tags = await readMetaTags(page);
  if (tags.topicId !== topic) throw new Error(`${topic}: HTML topic metadata is ${tags.topicId || "missing"}`);
  if (!Number.isInteger(tags.contentVersion) || tags.contentVersion <= 0) {
    throw new Error(`${topic}: invalid content version metadata`);
  }
  const browserDiagnostics = await diagnostics(page);
  if (browserDiagnostics.runtimeError) throw new Error(`${topic}: ${browserDiagnostics.runtimeError}`);
  if (browserDiagnostics.unrenderedMermaid.length) {
    throw new Error(`${topic}: Mermaid diagrams not rendered: ${browserDiagnostics.unrenderedMermaid.join(", ")}`);
  }
  if (browserDiagnostics.overflowSlides.length) {
    throw new Error(`${topic}: overflowing slides: ${browserDiagnostics.overflowSlides.join(", ")}`);
  }
  if (consoleErrors.length) throw new Error(`${topic}: browser console errors: ${consoleErrors.join(" | ")}`);
  if (externalRequests.length) throw new Error(`${topic}: external requests are forbidden: ${externalRequests.join(" | ")}`);

  const snapshot = await snapshotDeck(page);
  await page.close();
  if (snapshot.slides.length !== browserDiagnostics.slideCount) {
    throw new Error(`${topic}: rendered slide snapshot count changed unexpectedly`);
  }

  const source = await sourceMetadata(root, topic);
  const expected = {
    topicId: topic,
    contentVersion: tags.contentVersion,
    slideCount: browserDiagnostics.slideCount,
    mermaidCount: browserDiagnostics.mermaidCount,
    outcomeIds: browserDiagnostics.outcomeIds,
    sourceSha256: source.sourceSha256,
    sourceDigest: source.sourceDigest,
  };

  if (!check && (await currentArtifactsAreFresh(topicDir, expected))) {
    return { topic, status: "unchanged", output: topicDir };
  }

  const pdfBuffer = await renderDeckPdf(browser, snapshot);
  const pageCount = await pdfPageCount(pdfBuffer);
  if (pageCount !== browserDiagnostics.slideCount) {
    throw new Error(`${topic}: rendered PDF has ${pageCount} pages for ${browserDiagnostics.slideCount} slides`);
  }
  const meta = {
    contract_version: 1,
    topic_id: topic,
    content_version: tags.contentVersion,
    generated_at: new Date().toISOString(),
    renderer: {
      playwright: PLAYWRIGHT_VERSION,
      mermaid: MERMAID_VERSION,
      pdf_lib: PDF_LIB_VERSION,
      strategy: "isolated_rendered_snapshot_merge",
    },
    slide_count: browserDiagnostics.slideCount,
    mermaid_count: browserDiagnostics.mermaidCount,
    outcome_ids: browserDiagnostics.outcomeIds,
    source_sha256: source.sourceSha256,
    source_digest: source.sourceDigest,
    pdf: { pages: pageCount, bytes: pdfBuffer.length, sha256: sha256(pdfBuffer) },
    diagnostics: { console_errors: consoleErrors, overflow_slides: [], external_requests: externalRequests },
  };

  if (!check) {
    await fs.writeFile(path.join(topicDir, "slides.pdf"), pdfBuffer);
    await fs.writeFile(path.join(topicDir, "slides.meta.json"), `${JSON.stringify(meta, null, 2)}\n`);
    return { topic, status: "rendered", output: topicDir };
  }

  const diagnosticDir = path.join(root, DIAGNOSTIC_ROOT, topic);
  await fs.mkdir(diagnosticDir, { recursive: true });
  await fs.writeFile(path.join(diagnosticDir, "slides.pdf"), pdfBuffer);
  await fs.writeFile(path.join(diagnosticDir, "slides.meta.json"), `${JSON.stringify(meta, null, 2)}\n`);

  const committedPdf = path.join(topicDir, "slides.pdf");
  const committedMeta = path.join(topicDir, "slides.meta.json");
  let mismatch = false;
  try {
    const currentMeta = JSON.parse(await fs.readFile(committedMeta, "utf8"));
    const currentPdf = await fs.readFile(committedPdf);
    const currentPages = await pdfPageCount(currentPdf);
    const comparable = [
      [currentMeta.contract_version, 1],
      [currentMeta.topic_id, topic],
      [currentMeta.content_version, meta.content_version],
      [currentMeta?.renderer?.playwright, PLAYWRIGHT_VERSION],
      [currentMeta?.renderer?.mermaid, MERMAID_VERSION],
      [currentMeta?.renderer?.pdf_lib, PDF_LIB_VERSION],
      [currentMeta?.renderer?.strategy, "isolated_rendered_snapshot_merge"],
      [currentMeta.slide_count, meta.slide_count],
      [currentMeta.mermaid_count, meta.mermaid_count],
      [JSON.stringify(currentMeta.outcome_ids), JSON.stringify(meta.outcome_ids)],
      [JSON.stringify(currentMeta.source_sha256), JSON.stringify(meta.source_sha256)],
      [currentMeta.source_digest, meta.source_digest],
      [currentMeta?.pdf?.pages, currentPages],
      [currentMeta?.pdf?.pages, meta.slide_count],
      [currentMeta?.pdf?.bytes, currentPdf.length],
      [currentMeta?.pdf?.sha256, sha256(currentPdf)],
      [JSON.stringify(currentMeta?.diagnostics?.console_errors), "[]"],
      [JSON.stringify(currentMeta?.diagnostics?.overflow_slides), "[]"],
      [JSON.stringify(currentMeta?.diagnostics?.external_requests), "[]"],
    ];
    mismatch = comparable.some(([left, right]) => left !== right);
  } catch {
    mismatch = true;
  }
  if (mismatch) {
    throw new Error(`${topic}: committed PDF or metadata is missing or stale; rendered output is in ${path.relative(root, diagnosticDir)}`);
  }
  return { topic, status: "checked", output: diagnosticDir };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const root = path.resolve(args.root);
  const topics = await findTopics(root, args.topics);
  if (!topics.length) {
    console.log("No materialized study-slide sources found.");
    return;
  }
  await fs.rm(path.join(root, DIAGNOSTIC_ROOT), { recursive: true, force: true });
  const { server, origin } = await startServer(root);
  const browser = await chromium.launch({ headless: true });
  try {
    for (const topic of topics) {
      const result = await renderTopic({ browser, root, origin, topic, check: args.check });
      console.log(`${result.topic}: ${result.status}`);
    }
  } finally {
    await browser.close();
    await new Promise((resolve, reject) => server.close((error) => (error ? reject(error) : resolve())));
  }
}

main().catch((error) => {
  console.error(`ERROR: ${error?.stack || error}`);
  process.exit(1);
});
