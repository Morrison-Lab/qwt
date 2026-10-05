# Claude Code Instructions

Project guidance for Claude Code (CLI, IDE, and the GitHub Action). The same conventions apply to GitHub Copilot --- see [`.github/copilot-instructions.md`](.github/copilot-instructions.md), which is the source of truth for style.

## Project context

`qwt` (Quarto Website Template) is a template repository for [Quarto](https://quarto.org/) websites maintained by the UCD-SERG lab. Downstream repos are created from this template via the GitHub "Use this template" button, so changes here propagate to new books.

Authoritative style guide: [UCD-SERG Lab Manual](https://ucd-serg.github.io/lab-manual/) (source: <https://github.com/UCD-SERG/lab-manual>).

## Repository layout

- `index.qmd`, `chapters/`, `appendix-*.qmd` --- Quarto source pages
- `references.qmd` --- standalone reference page; excluded from the default website
  render (`!references.qmd` in `_quarto-website.yml`), so it isn't part of the
  normal site build
- `_quarto.yml`, `_quarto-website.yml` --- Quarto project + website config
- `_extensions/` --- vendored Quarto extensions (including `code-language-labels`, which labels each code block with its language in HTML and revealjs output; vendored from [`d-morrison/code-language-labels`](https://github.com/d-morrison/code-language-labels))
- `macros/` --- git submodule for shortcode/macro definitions (see `.gitmodules`)
- `R/`, `man/`, `DESCRIPTION`, `NAMESPACE` --- the project is also a small R package
- `references.bib` --- BibTeX bibliography
- `offwhite.scss`, `theme-picker.html` --- the website's Light / Off-white / Parchment / Dark theme dropdown (`theme-picker.html` builds it, `offwhite.scss` styles the two tinted palettes); the choice is saved under `mln-theme`, shared with the slides and with the other sites on this origin
- `page-navigation.html` --- opt-in HTML include (off by default; turn on with `format.html.include-after-body`) that adds floating previous/next arrows in the page margins and fixes navbar highlighting when Home is in the sidebar; vendored from [`Morrison-Lab/lbt`](https://github.com/Morrison-Lab/lbt)
- `styles.css` --- website styling; `styles-reveal.scss`, `qwt-reveal-toggle.html` (the same four-theme dropdown for slides), and the `revealjs-*.lua` filters drive the reveal.js slide output
- `assets/`, `images/` --- static image and asset files (site pages, docs, CI/PR screenshots)
- `.github/workflows/` --- CI workflow definitions
- `.github/scripts/` --- helper scripts used by workflows
- `.github/instructions/` --- path-scoped Copilot rules that attach by file glob (see `.github/copilot-instructions.md`)
- `CONTRIBUTING.md` --- contributor guide
- `_site/`, `_freeze/`, `.quarto/` --- build artifacts (do not edit by hand)

## Style conventions

Mirrors [`.github/copilot-instructions.md`](.github/copilot-instructions.md). Key points:

- **Lists of 3+ items**: use bullet lists rather than comma-separated prose. Always leave a blank line before a markdown bullet list (especially in `.qmd` files).
- **Code chunks**: HTML output folds code by default: `_quarto-website.yml` sets `code-fold: true` (with `code-tools: true`, so readers can show all code at once), as rme does. Keep the default when the *output* (plot, table) is the point and the code is incidental. Set `#| code-fold: false` on tutorial code, short examples, code that is the main focus, and chunks where the console output is the main content.
- **R style**: respect `.lintr.R`. Run `lintr::lint_dir()` before declaring R changes done.
- **Navigation**: `_quarto-website.yml` defines a docked sidebar because `page-navigation: true` builds its previous/next links from the sidebar. Add each new page to both the navbar and the sidebar, in the same order. Leave Home out of the sidebar unless `page-navigation.html` is turned on (see the README's "Page navigation" section).
- **Quarto chunks**: prefer chunk options as YAML-style `#|` directives, not as inline `r, opt = val` arguments.

## Working in this repo

- **Don't edit generated files**: `README.md` is built from `README.Rmd`; `_site/` and `_freeze/` are build outputs.
- **Local preview**: `quarto preview` (live reload). Full build: `quarto render`. When verifying a single edited page, render just that page (`quarto render <file>.qmd --to html`) rather than the whole site --- the `/render` command is for the full build.
- **Submodules**: `macros/` is the only git submodule (see `.gitmodules`). Run `git submodule update --init --recursive` after cloning.
- **Spell check**: words go in `inst/WORDLIST` (see `.github/workflows/check-spelling.yaml`). Update the wordlist instead of disabling the check.
- **Link check**: tuned in `lychee.toml`; prefer fixing broken links over adding exceptions.
- **Other CI checks**: workflows also verify bibliography DOIs (`check-bibliography-dois.yml`) and flag non-standard characters (`check-non-standard-chars.yaml`). Fix the flagged source rather than relaxing the check.
- **Dependencies**: Dependabot auto-updates the `macros` submodule and GitHub Actions (see `.github/dependabot.yml`); don't bump those by hand unless a PR needs it.

## ai-config plugin

`.claude/settings.json` declares the `Morrison-Lab` marketplace (source:
[`Morrison-Lab/ai-config`](https://github.com/Morrison-Lab/ai-config)) and enables
its `ai-config@Morrison-Lab` plugin, along with the `posit-dev-skills` and `sembr`
marketplaces this template also carries, matching
[`Morrison-Lab/qbt`](https://github.com/Morrison-Lab/qbt). Declaring is not
installing: a local session still needs `claude plugin install ai-config@Morrison-Lab`
once. Because this is a template repository, this declaration is copied once into
every repo created from it --- an omission here silently ships to every downstream
site.

## Pull request expectations

- Keep PRs scoped --- bug fixes shouldn't smuggle in refactors.
- Write commit messages and PR descriptions explaining the *why*, not just the *what*.
- Don't bypass CI failures (spell check, link check, lint, bibliography DOIs, non-standard chars) --- fix the underlying issue.
- Don't commit `_site/` or `_freeze/` changes unless that is genuinely the intent of the PR.

## Things to avoid

- Adding new top-level dependencies (R packages, Quarto extensions) without a clear reason; this is a template, so every dependency lands in every downstream book.
- Reformatting unrelated files.
- Inventing URLs or citations --- only use sources actually present in `references.bib` or explicitly provided.
