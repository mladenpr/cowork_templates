# Changelog

All notable changes to the templates in this repository.

## [1.1.0] — 2026-08-07

Retargets the template at document work (Word, PDF, Excel) on a synced
OneDrive folder, with sessions running locally rather than through a cloud
file bridge.

### Added

- `templates/sot-project/04_tools/extract_text.py` — mirrors `01_SoT/` into
  `02_derivatives/_extracted/` as one markdown file per document, so the
  project can be searched instead of reparsed. Word, Excel and PowerPoint are
  handled with the standard library alone (they are ZIP archives of XML);
  captures tracked insertions and deletions, comments with their authors,
  tables, hidden sheets, formulas and speaker notes. PDFs use `pypdf` when it
  is installed and are recorded as unread when it is not; a PDF with no text
  layer is flagged as needing OCR. Rights-managed Office files are detected by
  their OLE signature and named as such — in a Microsoft 365 tenant that is the
  most common reason a document cannot be read.
- `templates/sot-project/03_deliverables/REGISTER.md` — one row per issue:
  document number, revision, date, recipient, transmittal, format, status.
  R5 required deliverables to be organised by number and revision but nothing
  recorded the facts that are not visible in the filesystem.
- **R10 — Document handling**: never re-save or clean up a source document;
  keep the extracted text layer current; record document condition (text layer
  vs scan, tracked changes, comments, protection) in the context md; issue PDFs
  and keep sources beside them. The text layer is explicitly **an index, not a
  substitute** — find things in the extraction, read them in the source, and
  never let a figure reach a deliverable without checking it against the
  document. Every extracted file opens with a banner saying so, since that is
  what an agent actually reads.
- `sot/_TEMPLATE.md` gains a "Document condition" section covering those
  properties, plus the sender's own document reference and revision.
- `update_index.py` now warns about suspected sync-conflict copies (keyed on
  the machine name OneDrive appends) and about names SharePoint refuses to
  sync — illegal characters, reserved device names, trailing dots, over-long
  paths. Warnings never affect the exit code.

### Fixed

- `update_index.py`: `--hash` was honoured by `--diff` but not by regeneration,
  so the first regeneration that omitted the flag silently dropped every
  sha256 and returned the project to mtime comparison — the exact mode a sync
  client breaks. Hashing is now sticky, with `--no-hash` to opt out and
  `--rehash` to force a full recompute.
- `update_index.py`: hashes are reused when size and mtime both match the
  baseline, so a scan no longer re-reads every byte of every PDF each session.
- `update_index.py`: Office save-temps (`~WRL0001.tmp`), LibreOffice locks and
  `.tmp` files are skipped. Only `~$` owner files were skipped before, so the
  rest were reported NEW and would have been ingested into `01_SoT/`.
- `extract_text.py`: six extraction losses found by testing against a document
  with the features a real specification has —
  - **Word list numbering was dropped entirely.** Word stores the scheme, not
    the numbers, so `1.` / `2.` / `2.1` simply vanished. In a specification
    that is how the document is referenced. Numbering is now reconstructed from
    `numbering.xml` for the ordinary case and the document is flagged
    `list-numbering-reconstructed`, since restarts and overrides will be wrong.
  - **Headers and footers were not read at all** — which is where a controlled
    document carries its number, revision and confidentiality marking.
  - **Footnotes and endnotes were not read at all**, and their reference marks
    were invisible in the body. Both are now extracted, with `[^n]` markers
    inline.
  - **Nested tables were flattened** into the containing cell, merging the
    inner table's values into one run-on string.
  - **Excel dates stayed as serial numbers.** Number formats are now resolved
    from `styles.xml` (built-in and custom) and serials converted to ISO dates,
    including Excel's fictional 1900-02-29.
  - **Merged cell ranges were unreported**, leaving header rows looking
    misaligned against the source.
- `extract_text.py`: paragraphs inside `w:sdt` content controls were invisible.
  Templates and forms wrap blocks in them, so whole sections could be missing.

### Changed

- **R8** is restated as a policy rather than a description of the environment.
  Through a cloud bridge deletion was impossible; running locally it is not, so
  the rule is now the only thing preventing an unrecoverable loss. R1 is marked
  the same way.
- **R9** covers sync-conflict copies, sync-legal filenames and Office file
  locks, and downgrades the cloud-placeholder failure from a hard error to a
  slow read — which is what it is on a local run.
- `CLAUDE.md` environment notes rewritten for local execution: no staging, no
  stale snapshots, no file-delivery write-back path, real shell, real write
  access. Adds the Windows `py -3` invocation and positions the Microsoft 365
  connector as a way to fetch inputs that are not on disk, never as a way to
  work on the project — it cannot run the scan, and it can delete.
- `PROJECT.md`'s conventions section is reframed for engineering work — units,
  standards and editions, rounding, sign and coordinate conventions, document
  numbering, language — with commercial terms as one item rather than the
  premise. The internal-position section is now explicitly optional.
- `new_project.py` seeds the first manifest with `--hash` and makes both tools
  executable.
- `docs/cowork-notes.md` rewritten around local sessions, with the bridge
  constraints kept as a closing section; `docs/pattern.md` gains R10 and the
  reasoning behind the R8 and R9 changes.

## [1.0.0] — 2026-08-03

Initial release.

### Added

- `templates/sot-project/` — the immutable-SoT project skeleton: `CLAUDE.md`
  session bootstrap, `README.md` with working rules R1–R9, a `00_AI_context/`
  layer (PROJECT / INDEX / MANIFEST / WORKLOG / per-dataset context files), and
  the `01_SoT` → `02_derivatives` → `03_deliverables` → `04_tools` → `05_temp`
  pipeline directories.
- `templates/sot-project/04_tools/update_index.py` — regenerates `INDEX.md` and
  `MANIFEST.json`, preserving hand-written descriptions; `--diff` implements the
  session-start scan.
- `bin/new_project.py` — instantiates the template into a new folder, fills the
  placeholders, and writes the first index baseline.
- `docs/pattern.md`, `docs/adapting.md`, `docs/cowork-notes.md`.

### Changed from the source project

The template was extracted from a live engineering-tender repository. Relative
to that original:

- All project, client and discipline specifics removed; replaced with
  `{{PLACEHOLDER}}` substitution.
- `update_index.py` no longer hard-codes the project name in the `INDEX.md`
  title — it resolves it from `--name`, else the `PROJECT.md` heading, else the
  folder name.
- `update_index.py` gained `--hash`: compares sha256 rather than size+mtime, for
  synced folders where the sync client rewrites modification times. Manifests
  written with and without it remain mutually diffable.
- `update_index.py` now skips non-regular files defensively.
- R9 generalised from OneDrive to any sync client, with the placeholder-read
  failure spelled out.
- `PROJECT.md` and `WORKLOG.md` converted from filled-in project documents into
  prompted templates.
