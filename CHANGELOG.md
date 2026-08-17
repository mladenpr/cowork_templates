# Changelog

All notable changes to the templates in this repository.

Templates are versioned independently, each in its own
`templates/<template>/VERSION`. Every project stamps the template and version it
was created from into its own `README.md` footer and its first WORKLOG entry —
a project is a copy, not a link, so that stamp is the only record of which
rules and tooling it actually has. Releases are git tags on this repository.

Entries name their template in the heading from `cowork-consultant 2.0.2`
onwards. Everything below that point describes the single template this
repository started with — the one now called `cowork-consultant`, under the
names it carried at the time: `sot-project` through 1.x, `cowork-project` at
2.0.0 and 2.0.1. Those entries are left as they were written.

Semantic versioning, read for a template rather than a library:

- **major** — the schema or a rule changes such that an existing project cannot
  simply adopt it; upgrading means migrating a live project by hand.
- **minor** — new tooling, new rules or new template files that an existing
  project can take or leave.
- **patch** — fixes to the scripts or the documentation, with no change to the
  structure or the rules.

## cowork-consultant 2.0.3 — 2026-08-18

Fixes to the two scripts, prompted by an outside review of the template, and
the tests that should have caught them. No schema change, no new rule number.
An existing 2.0.x project takes it by copying `04_tools/*.py` over its own; the
first run after that redoes every extraction once, and says so.

### Fixed — a failed extraction was "current" forever

`extract_text.py` decided an extraction was up to date by comparing the
source's size and mtime with what the output recorded. That is the right test
for "did the document change" and the wrong test for "is this output any
good": a stub written because `pypdf` was missing matched its source perfectly,
so the next run reported it as *already current* — and kept doing so after
`pypdf` was installed. The same held for an output that recorded an extraction
error, and for output made by an older version of the script.

Freshness now has four reasons, and `--report` names the one that applies:
**source changed**; **previous attempt failed** (a `not-extracted` or
`extract-error` result is retried on every run until it succeeds — a missing
library and a bug are things that get fixed, unlike a scan or a password);
**extractor updated** (every extraction records the `EXTRACTOR_VERSION` it was
made with, and a bump redoes it); and **row limit changed** (a sheet that was
truncated is re-rendered when `--max-rows` differs). The run summary counts
what it retried and why it redid anything, so a stub is never mistaken for a
success and an upgrade never looks like a mystery.

### Fixed — spreadsheets lost their row numbers and one of their epochs

The sheet renderer appended only populated rows and used the first as the
table header. A value from row 100 sat directly under row 1, the blank rows
that separate one table from the next on a real sheet vanished, and the header
was whatever happened to be first, which on a real sheet is rarely the header.
Every row now carries its Excel number in a leading `#` column and the columns
are headed by their letters, so a cell in the text layer can be named the way
the sheet names it — the same coordinates the formulas list already used.
Blank rows are still dropped; the number carries the gap.

Dates were always read in Excel's 1900 system. A workbook saved in the 1904
system — legacy Excel for Mac, some exporters — puts the same serial 1,462 days
later, so every date came out four years early and looked entirely plausible.
`workbookPr/@date1904` is now honoured, and a 1904 workbook says
`date_system: 1904` in its front matter.

### Fixed — a mixed PDF was not called one

Scan detection averaged text length over the whole document, so a report with
a typed cover page and forty scanned pages could pass as text. It is now judged
page by page: `textless_pages: 2-3, 5` in the front matter, and a flag that
distinguishes `likely-scanned-needs-ocr` (every page) from
`mixed-text-and-scanned` (some) — which is what the dataset template's "mixed
(pages n–m)" line was asking for and had no way to fill.

### Added — orphaned extractions are reported

An extraction whose source has gone — moved to `_to_delete/`, renamed, filed
elsewhere — stayed in `03_working/_extracted/` and went on answering greps
about a document the project no longer held. Both `--report` and the normal
run now list them. Per R8 they are reported, not deleted.

### Added — the scan notices a missing directory

`update_index.py` records files, and an empty directory holds none, so a
schema directory that vanished left no trace in the manifest: removing
`05_temp/` from a project and running `--diff` said *Clean*. The schema's
directories are now checked by name; a missing one prints `MISSING DIR`, makes
`--diff` exit 1, and is a bullet in the session-start scan (`CLAUDE.md`, R7):
recreate it empty and say so — anything it held shows as MISSING alongside,
and that is the real event.

### Clarified — two things the LOG did not say

- **Backfill.** R4 says a row is written at the moment of the event, never
  reconstructed later, and had no answer for a repository started for an
  engagement already under way — which is most of them. It backfills once, and
  every backfilled row says so in **Ref** (`backfilled YYYY-MM-DD from …`),
  with **Date** staying the date of the event. A reconstruction marked as one is
  a record; an unmarked one is a guess that looks like a fact.
- **Path for an issued pair.** R5 files the issued PDF and its source together,
  and the LOG has one **Path** column. That is one event and one row: Path
  names the PDF, since the PDF is what was sent, and the source sits beside it
  under the same stem.

### Added — tests

`tests/test_consultant_tools.py`, standard library only, run with
`python3 -m unittest discover tests` from the repository root. The Office
fixtures are built in code from the minimal OOXML that Excel writes, so there
are no binary files in the repository and every fixture states which behaviour
it exists to pin: both date systems, a sheet with a row gap, a hidden sheet, a
formula, truncation; each freshness reason; page ranges and the mixed-PDF flag;
orphans; the missing-directory scan; and an end-to-end instantiation with
`bin/new_project.py` that runs the real scripts twice with `pypdf` hidden, the
way the original bug was found. Run against the 2.0.2 scripts, eighteen of the
nineteen fail.

### Not done, deliberately

The review also proposed transactional `ingest.py`/`issue.py` commands, an
`_inbox/` arrival zone, a schema validator, and an agent-neutral `AGENTS.md`.
The steps a script could take over are not the ones that fail — the context md
and the WORKLOG entry need judgement, and every mechanical step is visible to
the next scan — and an arrival zone invites files to sit unclassified, which is
what the frozen/mutable split exists to prevent. The one fragile mechanical
step, appending to a markdown table, is what `cowork-contractor`'s `log.py`
already replaces; the consultant template inherits that once it has proved
itself there, as a minor release, along with a recorded-at timestamp per row.
`AGENTS.md` is a new template file and waits for the same release.

## cowork-contractor 0.1.0 — 2026-08-13

A starting point, not yet a template. `templates/cowork-contractor/` is an
unmodified copy of `cowork-consultant` 2.0.2, carrying its own name in the two
stamp lines and nothing else of its own, placed here so the contracting
structure can be developed in the open rather than in a branch.

It is deliberately numbered below 1.0.0 and marked **not ready** in the README.
Nothing in it has been adapted to contracting work yet, so a project started
from it today would carry a stamp naming a template that does not really exist.

### Not done, deliberately

- No structural change, no rule change, no guess at what contracting needs. The
  zones, R1–R10 and both procedures are consultant's, unexamined.
- The two templates each keep their own copy of `04_tools/*.py` rather than
  sharing one. Factoring out a script the moment a second copy exists is the
  wrong instinct here: the contractor tooling may need to diverge, and a shared
  script is much harder to split later than two identical ones are to merge.

## cowork-consultant 2.0.2 — 2026-08-13

Renames the template and moves its version number inside it. No schema change
and no rule change — an existing 2.0.x project is already current, apart from
one line in its README footer.

### Changed — the template is now `cowork-consultant`

`templates/cowork-project/` → `templates/cowork-consultant/`. This repository is
about to hold more than one template, and "project" says nothing about which
kind of work a template is shaped for; the consulting and the contracting sides
run differently enough to want different structures. Earlier changelog entries
keep the old paths, because that is what they were called at the time.

The stamp in a new project's README footer and first WORKLOG entry names the
template it came from, so it now reads `cowork-consultant`. Projects created
before this release say `cowork-project` and are not wrong — that was the name.

### Changed — each template carries its own `VERSION`

`templates/<template>/VERSION` is what `new_project.py` now stamps, falling back
to the repository's root `VERSION` for a template that has none.

**Why.** The stamp is a claim about which rules and which tooling a given
project has. With one template, that claim and the repository's release number
were the same number by accident. With two they are not: a patch to the
contractor template would have renumbered every consultant project created after
it, and the stamp would have quietly stopped meaning what the README promises it
means — while still looking exactly as authoritative.

`VERSION` is dropped on instantiation, alongside the `.gitkeep` markers. Both
are scaffolding for this repository — one so git tracks empty folders, the other
so this script knows what to stamp — and a project has no use for either once
the two places that matter already record it.

### Added — `--template`

`new_project.py --template cowork-contractor` picks a sibling directory under
`templates/`. It defaults to `cowork-consultant`, so every command documented
before this release still does what it did. An unknown name exits with the list
of what is actually available rather than a traceback or a half-written folder.

## [2.0.1] — 2026-08-12

Closes an ambiguity in R3 about email text pasted into a chat window. No
schema change, no new rule number, nothing an existing v2.0.0 project has to
adopt — copy the three template files over if you want it.

### Clarified — R3 does not cover pasted text

R3 says ingestion is triggered by "anything arriving from outside", and
`CLAUDE.md` listed chat uploads among the triggers. An email quoted into a
session reads as arrival, so a session applying the rule literally would file
it — inventing a filename inside a frozen zone, which R1 has no vocabulary for,
since every other file there enters already formed and is never renamed.

Pasting email to have it reviewed or answered is now stated to be working
material. A session may use it and draft from it; it does not file it, and it
does not write what the paste said into `WORKLOG.md`, `PROJECT.md` or a dataset
context md while a chat message is the only source.

**Why the second half matters more than the first.** Losing the text is not the
risk — the risk is a fact entering the context layer with no provenance, which
happens without any file being created and is invisible afterwards. The frozen
zones guarantee provenance by holding the artefact; nothing guarantees it for a
sentence somebody typed into a window.

### Added — the correspondence transcript

Deciding an email belongs in the record stays with the user, on the same seam as
R5: they write a markdown transcript and drop it in, the scan sees it as NEW,
and the session ingests it without asking, since the judgement it needed has
already been made.

- A header block in R3 the transcript carries: direction and party, sent date,
  from/to, thread, **transcribed by** (so a copy is never read as an original),
  **attachments named** but not held, and **not captured**. Filename
  `YYYY-MM-DD_<party>_<subject-slug>.md`, dated when the email was sent.
- `LOG.md` gains `email (transcript)` as a **Ref** value, so a row cannot imply
  the project holds the original.
- The `issued/` invariant in `CLAUDE.md` now names a second door: a transcript
  of correspondence already sent. It is a record being written down, not a
  document being released, and it takes no document number or revision — the
  issue procedure remains the only route for anything leaving
  `03_working/drafts/`.
- `docs/pattern.md` and `docs/cowork-notes.md` carry the reasoning and the
  day-to-day version.

### Fixed — searching would have missed transcripts

`extract_text.py` skips files that are already text, correctly: mirroring a
markdown file into `03_working/_extracted/` produces a copy of the original.
But `CLAUDE.md` told sessions to search inside documents by grepping the
extraction, and an email transcript is never in it — so a session searching
exactly as instructed would find no email at all. The search instruction in
`CLAUDE.md` and the text-layer bullet in R10 now say to cover `_extracted/` and
the frozen zones both. No script change.

Sessions asked to write a transcript must request the sent date, recipients and
attachments rather than infer them. A LOG row with a guessed date is worse than
no row, because it reads as a fact.

### Not done, deliberately

No automatic filing of pasted email, and no prompt offering it. Most pasted
correspondence is not worth keeping, and a `received/` folder holding
everything that passed through a chat window stops meaning "this is the
record". The filter is the value of the frozen zone, and the filter is human.

## [2.0.0] — 2026-08-07

Restructures the template around the distinction between documents that are
**frozen** and documents that are **moving**, and treats the flow of documents
to and from another party as a conversation rather than as inputs and outputs.

Projects created from v1.x keep the v1.x layout. There is no migration and none
is planned — a live project should not have its rules changed under it
mid-engagement. Finish those as they are; start new ones on v2.

### Changed — the schema

The template directory is renamed `templates/sot-project/` →
`templates/cowork-project/`. It was named for the concept it was built around,
and that concept is gone: SoT is now one zone among three rather than the
organising idea. Earlier changelog entries keep the old path, because that is
what it was called at the time.

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
