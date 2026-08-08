# Changelog

All notable changes to the templates in this repository.

Releases are git tags on this repository (`v1.0.0`, `v1.1.0`), and the current
number lives in `VERSION`. Every project stamps the template version it was
created from into its own `README.md` footer and its first WORKLOG entry —
a project is a copy, not a link, so that stamp is the only record of which
rules and tooling it actually has.

Semantic versioning, read for a template rather than a library:

- **major** — the schema or a rule changes such that an existing project cannot
  simply adopt it; upgrading means migrating a live project by hand.
- **minor** — new tooling, new rules or new template files that an existing
  project can take or leave.
- **patch** — fixes to the scripts or the documentation, with no change to the
  structure or the rules.

## [2.0.0] — 2026-08-07

Restructures the template around the distinction between documents that are
**frozen** and documents that are **moving**, and treats the flow of documents
to and from another party as a conversation rather than as inputs and outputs.

Projects created from v1.x keep the v1.x layout. There is no migration and none
is planned — a live project should not have its rules changed under it
mid-engagement. Finish those as they are; start new ones on v2.

### Changed — the schema

```
01_SoT/            →  01_basis/              reference material only
02_derivatives/    →  03_working/            drafts/, analysis/, _extracted/
03_deliverables/   →  02_exchange/issued/
                   +  02_exchange/received/  (new)
00_AI_context/sot/ →  00_AI_context/datasets/
REGISTER.md        →  02_exchange/LOG.md     both directions, one chronology
```

The numbers no longer mean pipeline order — `02_exchange/` holds both inputs
and outputs, so no pipeline reading is possible. They now order by status:
frozen first, then mutable, then machinery.

**Why.** The old axis was *reproducibility*: regenerable outputs in one folder,
issued documents in another. That axis never survived contact with real work —
`docs/adapting.md` filed review memos, chronologies and issue matrices under
derivatives, none of which any script can regenerate, so the promise that the
folder could be safely purged was already false. Drafts made the gap visible
rather than creating it. Frozen-versus-moving has no such hole and needs no
exceptions.

**And why received/issued rather than SoT/deliverables.** What you receive and
what you issue carry equal weight and are two halves of one exchange; naming one
"Source of Truth" and the other "deliverables" hid that. `SoT` was the right
name only for the third thing — reference material the work rests on, from
sources that are not party to the conversation — which is now `01_basis/`.

### Added

- **`02_exchange/LOG.md`** — one row per document in or out, in date order, with
  direction, party, thread, revision, transmittal and status, plus an
  outstanding-items section. The index of the conversation, the way `INDEX.md`
  is the index of the files. Rows are written at the moment of the event.
- **R5, the issue step.** A document leaves the project only when the user asks
  for it by name. On that instruction the file moves from `03_working/drafts/`
  into `02_exchange/issued/` under its number and revision, the PDF is filed
  with its source, the LOG gains a row, the WORKLOG a dated entry, the thread's
  context md a member row, and the index is regenerated. Silently renaming a
  draft leaves the project unable to say what was sent, to whom, or under what
  cover. `CLAUDE.md` carries this and the ingest procedure as explicit steps.
- **R6, one live draft per deliverable**, revised in place rather than copied to
  a new file per revision.
- **Negotiation threads** as a first-class case of R2: a document whose
  revisions alternate custody is one dataset with a member table carrying date,
  direction, version, path and *what changed*. The files stay in their direction
  folders; the thread lives in the context layer. Folders per thread were
  considered and rejected — they reduce the ours/theirs boundary to a filename
  convention.
- **Zone-aware scan severity** in `update_index.py`: movement inside a frozen
  zone is reported first and separately as something to stop for, while CHANGED
  in `03_working/` is routine. Without this, a live draft would report CHANGED
  every session and train you to skim past the reports that matter.
- **Multi-party support at no cost to single-party projects.** Party is a LOG
  column, not a folder level. Sub-foldering `received/` or `issued/` by party is
  available when volume justifies it and carries no semantics — the rules, the
  scripts and the LOG read identically either way.
- `VERSION` at the repository root as the single source of truth, and a
  `{{TEMPLATE_VERSION}}` placeholder stamped into each new project's README
  footer and first WORKLOG entry; `new_project.py --version`. (Merged before
  this release; the version stamp is what distinguishes a v1 project from a v2
  one on disk.)
- `PROJECT.md` gains a Parties table for multi-party projects.

### Changed — the rules

R1–R10 rewritten around the frozen/moving distinction:

- **R1** now covers both frozen zones and makes direction the provenance
  boundary. Two consequences are stated explicitly because both catch people
  out: what you issued is frozen too, and your own document returned to you
  marked up is a *received* document.
- **R2** extended to threads. **R3** ingestion now decides a zone and writes a
  LOG row. **R4** is the exchange log. **R5** is issuing. **R6** is working.
  **R7** merges the old index/manifest and session-start-scan rules and adds
  zone-aware severity. **R8** (never delete), **R9** (sync discipline) and
  **R10** (document handling) carry over.
- `extract_text.py` now walks both frozen zones and writes to
  `03_working/_extracted/`, keeping the full zone-relative path so the two
  cannot collide. `03_working/` is not extracted — extracting a live draft would
  only produce a stale copy of something that changes hourly.

### Not done, deliberately

No `issue.py` or `ingest.py`. Both steps are clerical enough to script, but the
workflow has not been run once, so the arguments would be guesswork and the LOG
row is the part that must not be wrong. They are documented as procedures the
agent performs on your instruction; automate whatever proves stable after a real
project.

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
