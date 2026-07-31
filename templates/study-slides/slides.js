/* open-study-path:study-slides-runtime version=2 */
import mermaid from "/node_modules/mermaid/dist/mermaid.esm.min.mjs";

const slides = Array.from(document.querySelectorAll(".osp-slide"));
const currentLabel = document.querySelector("[data-current-slide]");
const totalLabel = document.querySelector("[data-total-slides]");
let current = 0;

function showSlide(index) {
  if (!slides.length) return;
  current = Math.max(0, Math.min(index, slides.length - 1));
  slides.forEach((slide, position) => {
    slide.classList.toggle("is-active", position === current);
    slide.setAttribute("aria-hidden", position === current ? "false" : "true");
  });
  if (currentLabel) currentLabel.textContent = String(current + 1);
  if (totalLabel) totalLabel.textContent = String(slides.length);
  history.replaceState(null, "", `#slide-${current + 1}`);
}

function initialSlide() {
  const match = location.hash.match(/^#slide-(\d+)$/);
  return match ? Number(match[1]) - 1 : 0;
}

function bindNavigation() {
  document.querySelector("[data-action='previous']")?.addEventListener("click", () => showSlide(current - 1));
  document.querySelector("[data-action='next']")?.addEventListener("click", () => showSlide(current + 1));
  document.addEventListener("keydown", (event) => {
    if (["ArrowRight", "PageDown", " "].includes(event.key)) {
      event.preventDefault();
      showSlide(current + 1);
    }
    if (["ArrowLeft", "PageUp"].includes(event.key)) {
      event.preventDefault();
      showSlide(current - 1);
    }
    if (event.key === "Home") showSlide(0);
    if (event.key === "End") showSlide(slides.length - 1);
  });
}

async function renderMermaid() {
  mermaid.initialize({
    startOnLoad: false,
    securityLevel: "strict",
    theme: "dark",
    fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
    themeVariables: {
      background: "#070910",
      primaryColor: "#14243a",
      primaryTextColor: "#f7f9fc",
      primaryBorderColor: "#73d8ff",
      lineColor: "#73d8ff",
      secondaryColor: "#182335",
      tertiaryColor: "#0d1320",
      noteBkgColor: "#182335",
      noteTextColor: "#f7f9fc",
      noteBorderColor: "#73d8ff"
    },
    flowchart: { htmlLabels: false, curve: "basis", nodeSpacing: 38, rankSpacing: 54 }
  });

  const diagrams = Array.from(document.querySelectorAll(".mermaid"));
  for (const diagram of diagrams) {
    const slide = diagram.closest(".osp-slide");
    slide?.classList.add("osp-slide--measure");
    try {
      await mermaid.run({ nodes: [diagram] });
    } finally {
      slide?.classList.remove("osp-slide--measure");
    }
  }
}

async function initialize() {
  window.__OPEN_STUDY_PATH_SLIDES_READY__ = false;
  window.__OPEN_STUDY_PATH_SLIDES_ERROR__ = null;
  try {
    bindNavigation();
    showSlide(initialSlide());
    await renderMermaid();
    await document.fonts.ready;
    window.__OPEN_STUDY_PATH_SLIDES_READY__ = true;
    document.documentElement.dataset.slidesReady = "true";
  } catch (error) {
    window.__OPEN_STUDY_PATH_SLIDES_ERROR__ = String(error?.stack || error);
    document.documentElement.dataset.slidesReady = "false";
    console.error(error);
  }
}

initialize();
