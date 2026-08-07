# {{PROJECT_NAME}} — Repository Schema & Working Rules

This document defines how the repository is organized and the rules under which
humans and AI sessions work in it. The pattern separates immutable inputs from
generated outputs, keeps a machine-readable context layer for every input, and
makes every generated artefact traceable to a script and a source.

The schema is project-agnostic: it does not assume any particular discipline or
deliverable format. It does assume the working material is documents — Word,
PDF, Excel, PowerPoint — held in a synced cloud drive.

## Schema

```
{{PROJECT_FOLDER}}/
├── CLAUDE.md              ← AI session bootstrap (read first, every session)
├── README.md              ← this file: schema + working rules
├── 00_AI_context/
│   ├── PROJECT.md         ← high-level project brief
│   ├── INDEX.md           ← every file: path + one-line description
│   ├── MANIFEST.json      ← scan baseline (path, size, mtime[, sha256])
│   ├── WORKLOG.md         ← dated decisions and open items
│   └── sot/               ← one context md per logical dataset in 01_SoT
├── 01_SoT/                ← Source of Truth: raw inputs only, immutable
├── 02_derivatives/        ← regenerable outputs (tidy data, figures, extracts)
│   └── _extracted/        ← searchable text layer, mirroring 01_SoT
├── 03_deliverables/       ← issued controlled documents, by number & revision
│   └── REGISTER.md        ← what was issued, to whom, at what revision
├── 04_tools/              ← kept scripts that produce derivatives
├── 05_temp/               ← disposable scratch, purgeable without thought
└── _to_delete/            ← cleanup staging (the user empties it)
```

Directory numbering is pipeline order: inputs (01) → working outputs (02) →
issued documents (03) → machinery (04, 05). `_to_delete/` is deliberately
unnumbered — it is transient staging, not part of the structure.

## Working rules

**R1 — SoT is immutable.** `01_SoT/` contains only files received as input to
the project (from the client, third parties, or external sources) — never files
generated within the project. Raw files are never edited, renamed, converted or
"fixed" in place, even when they are demonstrably wrong. A corrected version is
a new file in `02_derivatives/`, and the correction is documented in the
dataset's context md. This preserves the audit trail back to what was actually
received.

This is a **policy, not a capability limit**. A session running locally has
ordinary write access to these files and nothing stops it from modifying one.
The rule holds because it is followed, not because it is enforced.

**R2 — Every input gets context.** Each logical dataset in `01_SoT/` has one
context md in `00_AI_context/sot/`, mirroring SoT's structure. Granularity is
the *logical dataset*, not the file: a singular document gets its own md; a
homogeneous series (e.g. a monthly report collection) gets one md covering the
whole series, with a member list and coverage table inside. A context md
records: origin (who sent it, when, how), content summary, known issues/QA
findings, document condition (per R10), and any transformations applied
downstream (with the script named).

Received files often arrive with useless names — `Scan0047.pdf`,
`document (3).docx`. The context md is the answer to that, not renaming: R1
forbids the rename, and the md is where the file acquires a meaning.

**R3 — Ingestion.** Any raw input entering the project — via chat upload,
email attachment, or copied into the folder — is stored or moved into
`01_SoT/`, gets its context md (new or extended), is put through the extraction
step in R10, and INDEX/MANIFEST are regenerated. Nothing raw lives outside
`01_SoT/`.

**R4 — Session-start scan.** Every new AI session diffs the repository against
`00_AI_context/MANIFEST.json` before other work, using
`04_tools/update_index.py --diff`. New files are ingested per R3; changed or
vanished files are flagged to the user, not silently accepted. Files the scan
reports as suspected sync-conflict copies are never ingested until the user has
said which copy is real.

**R5 — Derivatives vs deliverables.** `02_derivatives/` holds regenerable
working outputs: cleaned/tidy data, figures, dashboards, extracts. Anything
here can be rebuilt from `01_SoT/` + `04_tools/`, and may be deleted on that
basis. `03_deliverables/` holds issued, controlled documents — reports,
transmittals, presentations — organized by document number and revision, and
listed in `03_deliverables/REGISTER.md`. The two are never mixed: the
distinction is the rebuild-vs-issued property, not tidiness.

**R6 — Tools vs temp.** Scripts that produce anything referenced by a
deliverable or kept derivative live in `04_tools/`, are kept and maintained,
and each figure/dataset context md names the script that produced it. `05_temp/`
is for genuinely disposable scratch and may be purged at any time without
review.

**R7 — Index and manifest.** `00_AI_context/INDEX.md` lists every file with a
one-line description; `00_AI_context/MANIFEST.json` records path, size, mtime
and (by default in a synced folder) sha256 for every file. Both are regenerated
by `04_tools/update_index.py` after any file operation. Hand-written
descriptions in INDEX.md are preserved across regenerations.

**R8 — Never delete; stage instead.** Cleanup means moving files into
`_to_delete/` under non-colliding names and reporting what was moved. The user
empties that folder; no session does.

This rule used to be a description of the environment — through a cloud file
bridge, deletion was impossible. On a local run it is not: `rm` works, and so
do overwrite and rename. R8 is therefore the *only* thing standing between a
misread instruction and unrecoverable loss, and it binds regardless of what the
session is technically able to do. The OneDrive recycle bin is a backstop, not
a plan: it has a retention limit, and it will not save you from an overwrite.

**R9 — Sync discipline.** The folder lives in a synced cloud drive (OneDrive,
SharePoint, Dropbox, iCloud Drive) for backup, version history and company
sharing. That imposes five habits:

- **Pin the folder for offline availability** — "Always Keep on This Device" in
  OneDrive, equivalents elsewhere. On a local run a dehydrated placeholder is
  read by triggering a download rather than by failing outright, so this is no
  longer a hard blocker; it is still worth doing, because an unpinned project
  makes the session-start scan stall while gigabytes hydrate, and fails
  properly when you are offline.
- **Close documents before a session works on them.** Word and Excel hold locks
  on open files and leave `~$` owner files beside them. A locked file cannot be
  rewritten, and on Windows the failure is obscure.
- **Let sync settle after mass file operations** before opening the folder on
  another machine.
- **Keep names sync-legal.** OneDrive and SharePoint reject `" * : < > ? / \ |`,
  leading/trailing spaces, trailing dots, and the reserved DOS names; the whole
  item URL is limited to 400 characters. `update_index.py` warns about all of
  these — engineering document names run long, and a file that silently stops
  syncing is worse than one that never arrived.
- **Do not `git init`** inside a synced project folder — git's object store and
  the sync client fight each other. Version control lives at the template
  level, not the instance level.

**R10 — Document handling.** The working material is documents, and they have
properties a plain file tree does not express:

- **Never re-save a source document.** Opening a `.docx` in Word and saving it —
  even with no edits — rewrites the entire package and changes its hash. Never
  accept or reject tracked changes, resolve comments, or convert a format in
  `01_SoT/`. In a received document the markup *is* content: a marked-up
  specification is a negotiation record.
- **Keep the text layer current.** `04_tools/extract_text.py` mirrors `01_SoT/`
  into `02_derivatives/_extracted/` as one markdown file per document, so the
  project is greppable. Run it after every ingestion. It is a derivative in the
  full R5 sense — regenerable, deletable, never edited by hand.
- **Record document condition in the context md** (R2): whether a PDF has a
  text layer or needs OCR, whether a Word file carries tracked changes or
  comments, whether the file is rights-managed. These are expensive to
  rediscover and cheap to write down once.
- **Rights-managed files cannot be read.** An Office document carrying an
  encrypting sensitivity label (Confidential / IRM) is not a readable package;
  no tool and no agent can open it. Do not work around it — record it in the
  context md and ask the user for a decrypted copy in `02_derivatives/`.
- **Issue PDFs, keep sources.** A deliverable's issued form is normally the PDF;
  keep the source `.docx`/`.xlsx` beside it at the same revision, so the next
  revision starts from the source rather than from a reconstruction.

## Decision log

Dated decisions, corrections, and open items are recorded in
`00_AI_context/WORKLOG.md` — one dated entry per decision, never rewritten
retroactively. Entries that were true when written stay as written; later
changes get their own entry.

---

Instantiated from the `sot-project` template
(<https://github.com/mladenpr/cowork_templates>) on {{DATE}}.
