<script>
const theoremLikeClasses = new Set([
  "thm",
  "theorem",
  "lem",
  "lemma",
  "cor",
  "corollary",
  "prp",
  "proposition",
  "cnj",
  "conjecture",
  "def",
  "definition",
  "exm",
  "example",
  "exr",
  "exercise",
  "proof",
  "rem",
  "remark",
  "sol",
  "solution"
]);
const theoremLikePrefixes = [
  "thm-",
  "lem-",
  "cor-",
  "prp-",
  "cnj-",
  "def-",
  "exm-",
  "exr-",
  "rem-",
  "sol-"
];
const inlineAnchorSeparator = "\u00A0";
const maxAnchorRetryAttempts = 5;
const anchorRetryDelayMs = 50;

const isTheoremLikeDiv = (div) =>
  Array.from(div.classList).some((className) => theoremLikeClasses.has(className)) ||
  (div.id && theoremLikePrefixes.some((prefix) => div.id.startsWith(prefix)));

const addTheoremLikeDivAnchors = () => {
  for (const theoremDiv of window.document.querySelectorAll("div[id]")) {
    if (!isTheoremLikeDiv(theoremDiv)) {
      continue;
    }

    if (!theoremDiv.classList.contains("anchored")) {
      theoremDiv.classList.add("anchored");
    }

    if (!theoremDiv.dataset.anchorId) {
      theoremDiv.dataset.anchorId = theoremDiv.id;
    }
  }
};

const ensureSectionHeadingAnchorAttributes = () => {
  for (const sectionHeading of window.document.querySelectorAll(
    "section[id] > h1, section[id] > h2, section[id] > h3, section[id] > h4, section[id] > h5, section[id] > h6"
  )) {
    if (!sectionHeading.classList.contains("anchored")) {
      sectionHeading.classList.add("anchored");
    }

    if (!sectionHeading.dataset.anchorId) {
      sectionHeading.dataset.anchorId = sectionHeading.parentElement.id;
    }
  }
};

const normalizeInternalAnchorLinkIcons = () => {
  for (const link of window.document.querySelectorAll(
    "a.anchorjs-link, a.quarto-xref"
  )) {
    if (link.classList.contains("quarto-xref")) {
      link.classList.add("no-external");
      link.classList.remove("external");
      continue;
    }

    const href = link.getAttribute("href") || "";
    if (!href.startsWith("#")) {
      continue;
    }

    link.classList.add("no-external");
    link.classList.remove("external");
  }
};

const moveTheoremDivAnchorsInline = () => {
  let hasPendingAnchors = false;

  for (const theoremDiv of window.document.querySelectorAll("div[id]")) {
    if (!isTheoremLikeDiv(theoremDiv)) {
      continue;
    }

    const theoremTitle = theoremDiv.querySelector(".theorem-title, .proof-title");
    if (!theoremTitle) {
      continue;
    }

    const anchorLink = Array.from(
      theoremDiv.querySelectorAll("a.anchorjs-link")
    ).find((link) => {
      const href = link.getAttribute("href") || "";
      return href === `#${theoremDiv.id}` || href.endsWith(`#${theoremDiv.id}`);
    });

    if (anchorLink && anchorLink.parentElement === theoremTitle) {
      continue;
    }

    if (!anchorLink) {
      hasPendingAnchors = true;
      continue;
    }

    anchorLink.classList.remove("external");

    // If the title ends with whitespace (e.g. Quarto's proof-title ending in ". "),
    // trim the trailing whitespace so the non-breaking separator and anchor stay attached
    // to the title text, and ensure a trailing space separates the anchor from following content.
    let lastTextNode = theoremTitle.lastChild;
    while (lastTextNode && lastTextNode.nodeType !== Node.TEXT_NODE && lastTextNode.lastChild) {
      lastTextNode = lastTextNode.lastChild;
    }
    if (lastTextNode && lastTextNode.nodeType === Node.TEXT_NODE && /\s+$/.test(lastTextNode.textContent)) {
      lastTextNode.textContent = lastTextNode.textContent.replace(/\s+$/, "");
      if (theoremTitle.nextSibling &&
          !(theoremTitle.nextSibling.nodeType === Node.TEXT_NODE && /^\s/.test(theoremTitle.nextSibling.textContent))) {
        theoremTitle.after(" ");
      }
    }

    theoremTitle.append(inlineAnchorSeparator);
    theoremTitle.append(anchorLink);
  }

  return hasPendingAnchors;
};

const moveTheoremDivAnchorsInlineWithRetry = (
  attemptsRemaining = maxAnchorRetryAttempts
) => {
  const hasPendingAnchors = moveTheoremDivAnchorsInline();
  if (hasPendingAnchors && attemptsRemaining > 0) {
    window.setTimeout(() => {
      moveTheoremDivAnchorsInlineWithRetry(attemptsRemaining - 1);
    }, anchorRetryDelayMs);
  }
};

if (window.document.readyState === "loading") {
  window.document.addEventListener("DOMContentLoaded", () => {
    addTheoremLikeDivAnchors();
    ensureSectionHeadingAnchorAttributes();
    normalizeInternalAnchorLinkIcons();
    moveTheoremDivAnchorsInlineWithRetry();
  });
} else {
  addTheoremLikeDivAnchors();
  ensureSectionHeadingAnchorAttributes();
  normalizeInternalAnchorLinkIcons();
  moveTheoremDivAnchorsInlineWithRetry();
}

window.addEventListener("load", () => {
  normalizeInternalAnchorLinkIcons();
  moveTheoremDivAnchorsInlineWithRetry();
});
</script>
