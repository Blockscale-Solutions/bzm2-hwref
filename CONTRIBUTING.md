# Contributing to bzm2-hwref

This repository is a hardware reference for developers integrating Intel Blockscale BZM2 ASICs into their own products. The published site (<https://blockscale-solutions.github.io/bzm2-hwref/>) renders `references/` and `drawings/` directly, so everything in those two trees is read by integrators. The rules below are for contributors; they are deliberately kept out of the published pages.

## Where things live

| Path | Purpose | Published to the site |
| --- | --- | --- |
| `references/*.md`, `references/bzm2-ballmap.csv` | The documents. Edit these, not the HTML. | yes (except `bzm2-porting-conversation-log.md`) |
| `drawings/**` | Reader-facing figures (SVG). | yes |
| `site/` | Static chrome: `index.html`, `doc.html`, `js/app.js`, `data/catalog.json`. | yes |
| `docs/` | Contributor notes (this kind of file), lab-chart planning material. | **no** |
| `CLAIMS.md`, `CONTRIBUTING.md`, `README.md` | Repository front matter. | no |
| `scripts/`, `footprints/` | Generators and generated outputs (pad map SVG, KiCad footprint). | no |

The Pages workflow (`.github/workflows/pages.yml`) copies `references/` and `drawings/` into `site/` at deploy time. Anything you put under `docs/` or in the repository root is not copied. Do not add contributor-facing text to a file in `references/`, `drawings/` or `site/`.

## Writing reader-facing text

Documents and figures are specifications for integrators. Write them in plain spec language:

- State the protocol, electrical or procedural fact. Do not narrate how the fact was established, who agreed to it, or which issue or PR discussed it.
- No issue or pull-request numbers for this repository, no "settled in", "post-#NN", "per review".
- No notes to future authors ("do not re-inline", "edit the markdown, not the HTML", "TODO: add chart").
- No publishing-policy statements in the page itself ("no invented numbers", "no vendor tracing", "not a lab measurement"). Policy lives here.
- No first-person-plural voice ("we connect", "our capture"). Use the imperative for recommendations ("Connect both pads") and the passive or third person for evidence ("measured on an RDS").
- Figure captions describe the figure. Add a source citation only where it helps a reader check the fact (a public repository and commit, a datasheet, a section of another page).
- Evidence caveats that change how a reader should use a fact are fine and wanted ("vendor-stated, not independently measured", "inferred", "not public"). State them as properties of the fact.
- Do not advertise tooling in reader-facing text (Mermaid sources, generator scripts, ledger ids).

## Publishing policy

- **No invented numbers.** Do not publish hashrates, temperatures, efficiencies, pad IDs, voltages or opcodes that are not backed by a public source or by a measurement recorded with its case and run. Charts wait for measured data; placeholders live in [`docs/lab-charts/`](docs/lab-charts/README.md) until then.
- **No NDA or vendor-confidential material.** Do not reproduce Product Brief content, vendor package art, vendor part selections or net names. The Product Brief PDF in the repository root is vendor collateral and is not republished.
- **Publish-safe topology only for the RDS.** Structure and reasoning are published; hostnames, filesystem paths, serial numbers and raw measurements are not, unless they are recorded as a measured figure in `references/rds-measured-reference.md` with its run.
- **Performance figures** (`N GH/s`, `J/TH`) need a case id or run id on the same line and must not read as final, peak or maximum.
- Run `tools/rds/check-public.sh` from `Blockscale-Solutions/mujina-bzm2-dev` (branch `rds/stock-image`) against your changed tree before opening a PR.

## Claims and provenance

Factual claims carry an opaque id such as `[BZM2-ENG-002]`, listed in [`CLAIMS.md`](CLAIMS.md). Each id resolves to source material in an internal ledger; some of that material is under NDA, so the public half records the claim and the kind of evidence behind it, not the source. A claim with no id is a claim nobody has stood behind yet.

- Tags stay in the markdown source, next to the claim they cover. The published site strips them when it renders (`stripClaimTags` in `site/js/app.js`), so readers never see them. To find where an id is used, search the source: `rg 'BZM2-ENG-003' references/`.
- Run `python3 scripts/check_claims.py` to confirm that every tag in `references/` has a row in `CLAIMS.md` and that every row is used.

## Spec text and observed data

- Specification text (what the ASIC requires and how to design for it) lives in the guides and references. Observed data from the RDS lives only in `references/rds-measured-reference.md`, which opens with a banner saying so.
- In that page, prose refers to runs by a short label (for example *hp2-1*). Full run ids appear only in the run tables and the figure tables. Do not put run ids, case ids or process notes in the spec documents; state what a host should do and link to the observation.

## Drawings

- Figures are original, editable SVGs (charcoal and teal). See [`docs/drawings.md`](docs/drawings.md) for the index of figures, their sources and the issues that introduced them.
- The SVG in `drawings/` is the published source for each figure. `drawings/bring-up/power-up-sequence.mmd` is an editable Mermaid sibling used for redraws only; if the flow changes, update the SVG and the `.mmd` together. Never inline a second copy of the flow in a document.
- The pad map SVG and the KiCad footprint are generated from `references/bzm2-ballmap.csv`. Edit `scripts/generate_padmap_svg.py` (or the CSV), regenerate, and run `python3 scripts/generate_padmap_svg.py --check`. Do not hand-edit the generated files.
- Keep all text inside a figure within its `viewBox`; check the rendered result in a browser.

## Previewing the site

Mimic the workflow's staging step in a scratch directory, then serve it:

```sh
rm -rf /tmp/hwref-site && cp -a site /tmp/hwref-site
rm -rf /tmp/hwref-site/references /tmp/hwref-site/drawings
mkdir /tmp/hwref-site/references
cp -a references/. /tmp/hwref-site/references/
rm -f /tmp/hwref-site/references/bzm2-porting-conversation-log.md
cp -a drawings /tmp/hwref-site/drawings
python3 -m http.server --directory /tmp/hwref-site 8000
```

## Pull requests

Describe the change as Summary / Changes / Test plan. Keep documentation changes separate from generator or workflow changes where practical.
