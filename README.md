# cowork_templates

Reusable project-repository templates for working with an AI agent (Claude
Cowork, Claude Code, or any agent that can read a folder) on real,
document-heavy projects — tenders, claims, studies, due diligence, litigation,
research, and the long-form documents all of those produce.

The problem these solve: an AI session starts with no memory. Left to itself it
re-reads whatever it stumbles across, mixes what a client actually sent with
what it computed last week, and confidently quotes a number that was superseded
three revisions ago. The fix is not a better prompt. It is a folder structure
the agent is required to obey, a written context layer it must read first, and a
scan that forces it to notice what changed since last time.

## Templates

| Template | Version | Use it for |
|---|---|---|
| [`cowork-consultant`](templates/cowork-consultant) | 2.1.0 | Consulting engagements — any project that exchanges documents with another party: inputs arrive, work happens, documents are issued. |
| [`cowork-contractor`](templates/cowork-contractor) | 0.4.0 | Work performed under a contract, from award onwards — either tier, main or sub. Adds a contract zone, party sub-folders, a queryable exchange log and registers. Below 1.0 until it has been run on a live project. |
| [`cowork-author`](templates/cowork-author) | 0.2.0 | Writing a project's documents from the ground up — method statements, plans, reports, technical proposals — through many internal revisions across many sessions, from a brief, reference material, an example and a branded template, to submission. One repository per real project, all of its documents in it. Role-neutral: the loop is the same for a consultant and a contractor. A priced quotation, or a revision of a document already issued, is ordinarily a consultant job. Adds a frozen revision zone with its own log, a context file per deliverable, basis sub-folders by role, a drop zone, a draft diff, and an index that rolls media folders up. Below 1.0 until it has been run on a live project. |

Templates are versioned independently and each carries its own `VERSION` file;
see [Versioning](#versioning). Pick one with `--template`.

## The pattern

```
<project>/
├── CLAUDE.md              ← AI session bootstrap (read first, every session)
├── README.md              ← schema + working rules R1–R10
├── 00_AI_context/
│   ├── PROJECT.md         ← the brief: what this is, for whom, conventions
│   ├── INDEX.md           ← every file, one line each (descriptions survive)
│   ├── MANIFEST.json      ← scan baseline (path, size, mtime, sha256)
│   ├── TEMPLATE.json      ← template stamp: version + upgrade record (tooling-maintained)
│   ├── WORKLOG.md         ← dated decisions, never rewritten
│   └── datasets/          ← one context md per dataset or negotiation thread
├── 01_basis/              ← FROZEN — reference material the work rests on
├── 02_exchange/           ← FROZEN — the conversation with the other parties
│   ├── received/          ← what came in
│   ├── issued/            ← what went out
│   └── LOG.md             ← both directions, one chronology
├── 03_working/            ← MUTABLE — nothing here is authoritative
│   ├── drafts/            ← one live draft per deliverable
│   ├── analysis/          ← calculations, checks, comparisons
│   └── _extracted/        ← searchable text layer (regenerated)
├── 04_tools/              ← kept scripts
├── 05_temp/               ← disposable scratch
└── _to_delete/            ← cleanup staging (only the human empties it)
```

Four ideas carry the whole thing:

**Frozen and moving.** Everything received and everything issued is frozen — a
record of an exchange, never revised, only superseded. Everything still being
worked on is mutable and authoritative for nothing. Every rule follows from
which side of that line a file sits on, including how loudly the session-start
scan complains when something moves.

**Provenance is a lookup.** Direction is the folder boundary: `received/` is
theirs, `issued/` is ours. "Is this ours or theirs?" is the question that
decides claims and negotiations, and it must never come down to judgement. The
corollary catches people out — a copy of your own document returned to you
marked up is a *received* document.

**A context layer the agent must read.** Every dataset gets a markdown file
recording where it came from, what is in it, what is wrong with it, and what
condition it is in. A negotiation thread is one dataset whose members alternate
custody, with a member table carrying date, direction, version and *what
changed*. `PROJECT.md` holds the brief; `WORKLOG.md` holds dated decisions and
is never rewritten.

**Issuing is a step you ask for.** A document leaves the project only when you
say so. On that instruction the file moves from drafts into `issued/` under its
document number and revision, the PDF is filed with its source, the exchange log
gains a row and the WORKLOG a dated entry. You decide *when*; the clerical work
is not yours to remember. What this replaces — quietly renaming a draft — leaves
the project unable to say what was sent, to whom, or under what cover.

The ten rules that formalise this are in
[`templates/cowork-consultant/README.md`](templates/cowork-consultant/README.md).

### What `cowork-contractor` changes

The tree above is `cowork-consultant`'s. The contracting template keeps every
one of those four ideas and adds what a multi-year works contract needs that a
consulting engagement does not:

- **`01_contract/`** — the instruments that bind, `upstream/` and
  `downstream/`, separate from general reference material. The boundary is a
  rule rather than a judgement: instruments that *create or amend* a contract
  live here; everything that flows *under* one — instructions, variations,
  purchase orders, notices — is exchange, filed by direction. A purchase order
  is an issued document, so direction keeps its no-exceptions property.
- **Party sub-folders** under `received/` and `issued/`, mandatory from day
  one, with the labels fixed in `PARTIES.md`. Party sits inside direction, not
  above it.
- **A queryable log.** `LOG.jsonl` is the record, `LOG.md` a generated view of
  it, and `05_tools/log.py` adds, updates, queries, checks and renders — and
  refuses a row that contradicts the tree. A markdown table is fine for the
  fifty rows an engagement produces and useless for the thousands a contract
  produces.
- **Registers** (`00_AI_context/registers/`) for controlled series — variations,
  RFIs, POs, payment applications. The log says what happened; a register says
  where a series stands, and is read by its gaps.
- **`_inbox/`** for arrivals not yet filed, counted by every scan until empty.

Inserting the contract zone shifts the numbering, so a contractor project has
`04_working/`, `05_tools/`, `06_temp/`. The rules are R1–R11, in
[`templates/cowork-contractor/README.md`](templates/cowork-contractor/README.md).

### What `cowork-author` changes

The consultant template covers the two ends of a document's life — the inputs
arriving, the document leaving — and says nothing about the middle, where most
of the work is: the draft going round and round between you and the agent,
across sessions, with your own hand edits in between. `cowork-author` keeps
the four ideas and the first two zones unchanged and adds what that middle
needs:

- **`03_revisions/`** — a third frozen zone for the document's own history.
  A revision is frozen only by an explicit step, the internal mirror of issuing
  (R11): you ask for it by name, the session offers it at the moments that
  warrant it — before you edit by hand, before anyone else sees the draft,
  before issue — and never does it unasked. `03_revisions/<slug>/Rnn/` holds
  the draft as frozen and, in `returns/`, whatever came back on it; a revision
  log records every freeze, return and issue in one chronology, with the "what
  changed" column that sync history cannot give you. It is kept out of
  `02_exchange/` so that "left the building" stays a lookup with no exceptions.
- **A document md per deliverable** (`00_AI_context/documents/<slug>.md`) —
  the authoring counterpart of a dataset md: what the document is for, what
  form it borrows, a requirements-coverage table, an outline with a status per
  section (including `locked` and `user-edited`), the decisions in force, a
  feedback register, and where its revisions stand. Read before the draft is
  opened, every session; two of its tables are read by their gaps.
- **`01_basis/` by role** — `reference/` (to be correct against), `examples/`
  (form, never content) and `templates/` (the branded shell the draft is copied
  from). Each is used in a different way and carries a different hazard, so the
  role is a folder rather than a judgement. **Form is borrowed, content is not**
  (R12): a sample used as a shell is stripped at instantiation, an example's
  context md lists the terms to check for, and the draft is grepped for them
  before a revision leaves your hands.
- **The draft on disk is the truth** (R6) — one live `.docx` per deliverable,
  no markdown master beside it, read before it is written. The scan reports a
  change to it at session start as its own category, `DRAFT EDITED`, because
  that can only mean the user's hands were on it; `05_tools/draft_diff.py`
  then says what changed, by section, with reworded paragraphs marked word by
  word.
- **Built for one project, many documents, and years of drops.** `_inbox/` is
  where photos, drawings and spec sections land, counted by every scan until
  filed. Sub-folders are made **on demand and by subject, never by document**
  — `reference/` starts flat and grows `photos/…/`, `drawings/`, `spec/` as
  sets arrive, because a tree of empty folders predicting subjects nobody has
  dropped yet is clutter too. A set of media is one dataset with one md.
  `04_working/library/` holds project text written once and reused across
  documents. And the index **rolls media folders up**: ten or more photos,
  drawings or archives in one folder are one INDEX line with a count by
  extension, and one `--diff` line, while the manifest still records every
  file.

The numbering lands where the contractor's does — `04_working/`, `05_tools/`,
`06_temp/`. The rules are R1–R12, in
[`templates/cowork-author/README.md`](templates/cowork-author/README.md).

## Quickstart

### Once — clone the toolbox, somewhere that is not a project

```bash
git clone https://github.com/mladenpr/cowork_templates.git ~/tools/cowork_templates
```

This clone is a toolbox, not a project. It is never copied into a project
folder and never lives inside one. Keep it off the synced drive as well: it
carries a `.git` directory, and that is the same sync-client-versus-git fight
described below, just one level up.

Update it whenever you like — `git -C ~/tools/cowork_templates pull`. Existing
projects are unaffected either way; a project is a copy, not a link. When you
*want* a project brought up to the toolbox's version, that is an explicit step
with its own tool — see [Upgrading](#upgrading-a-project-that-already-exists).

### Per project — make the folder, then fill it

```bash
mkdir -p ~/OneDrive/01_PROJECTS/ACME-Bridge-Cowork

python3 ~/tools/cowork_templates/bin/new_project.py \
    ~/OneDrive/01_PROJECTS/ACME-Bridge-Cowork \
    --name "ACME Bridge" --client "ACME Infrastructure" --owner "Your Name"
```

**The destination receives one template and nothing else** — no `.git`, no
second template, none of this repository's own files. `VERSION` and the
`.gitkeep` markers are stripped on the way in, and every `{{PLACEHOLDER}}` is
substituted, so what you get is a working project folder rather than a checkout
to clean up. The folder need not exist beforehand; it simply may, which is why
the `mkdir` above is optional. An existing folder with files already in it needs
`--force`, so that nothing is written over a project by accident.

`--template` selects which template to instantiate, and defaults to
`cowork-consultant`. `bin/new_project.py --help` lists what is available.

Worth a shell function if you start projects often:

```bash
# ~/.zshrc
cowork-new() { python3 ~/tools/cowork_templates/bin/new_project.py "$@"; }

cowork-new ~/OneDrive/01_PROJECTS/ACME-Bridge-Cowork --name "ACME Bridge"
```

Then, in every session, point the agent at the folder and say:

> Read CLAUDE.md and run the session-start scan.

On Windows use `py -3` wherever these commands say `python3`.

## Using it day to day

```bash
python3 04_tools/update_index.py --diff    # what changed since last time
python3 04_tools/update_index.py           # rebuild INDEX.md + MANIFEST.json
python3 04_tools/extract_text.py           # extract new/changed documents
python3 04_tools/extract_text.py --report  # what is filed, and in what state
```

In a `cowork-author` project the tools sit in `05_tools/` and there is one more,
read-only, for the live draft:

```bash
python3 05_tools/draft_diff.py method-statement                  # live draft vs latest frozen revision
python3 05_tools/draft_diff.py method-statement --against R03    # vs a named revision
python3 05_tools/draft_diff.py method-statement --between R02 R04
python3 05_tools/draft_diff.py method-statement --summary        # sections only
```

In a `cowork-contractor` project the tools also sit in `05_tools/`, and the one
more of them is the log:

```bash
python3 05_tools/log.py add --date 2026-03-04 --dir in --party "ACME" \
    --type instruction --doc "SI-012" --path 03_exchange/received/ACME/SI-012.pdf \
    --action open --due 2026-03-18
python3 05_tools/log.py query --action open   # what is owed, either way
python3 05_tools/log.py check                 # the log against the tree
python3 05_tools/log.py render                # rebuild LOG.md from LOG.jsonl
```

Manifests are content-hashed by default, because a sync client rewrites
modification times when it hydrates a file or resolves a conflict and an
mtime-based diff turns to noise. Hashing is sticky — once a manifest carries
hashes you never need the flag again — and unchanged files reuse their recorded
hash, so a scan only reads what looks touched. `--rehash` forces a full
recompute; `--no-hash` drops back to size+mtime.

`extract_text.py` handles Word, Excel and PowerPoint with the standard library
alone. PDFs need `pip install pypdf`; without it they are recorded as unread
rather than skipped silently. `--report` is the quickest way to find out that a
document you were about to rely on is a scan needing OCR, or carries a
sensitivity label that makes it unreadable to every tool you have.

The extraction is an index, not a substitute: find things in it, then read them
in the source. It drops layout, page numbers, images and drawings, and
reconstructs Word list numbering and Excel dates rather than reading them.

## Versioning

**Each template is versioned on its own history**, in its own
`templates/<template>/VERSION`. A fix to one template must not renumber the
other: the version a project stamps is a claim about which rules and which
tooling *that* project has, and a shared number would make it a claim about
this repository instead. The `VERSION` at the root is the repository release,
and serves only as a fallback for a template that has none.

Releases are git tags, and [`CHANGELOG.md`](CHANGELOG.md) carries a section per
template explaining what each version changed — including what *major*, *minor*
and *patch* mean for a template as opposed to a library.

Each project records the template and version it was created from three times:
in prose, in its own `README.md` footer and its first WORKLOG entry — and
machine-readably in `00_AI_context/TEMPLATE.json`, which also records the
placeholder values that were substituted, a content hash of every scaffolding
file as tooling last wrote it, and every upgrade applied since. To survey a
folder of projects:

```bash
grep -h "Instantiated from" ~/OneDrive/01_PROJECTS/*/README.md
grep -h '"version"' ~/OneDrive/01_PROJECTS/*/00_AI_context/TEMPLATE.json
```

The first shows what each project started as; the second what it is now.

The `VERSION` file itself never reaches a project — `new_project.py` strips it
on the way through, along with the `.gitkeep` markers. Both are scaffolding for
this repository, and the stamp already records what they were for.

**cowork-consultant v2.0 restructured the schema.** Projects created from v1.x
keep the v1.x layout — `01_SoT/`, `02_derivatives/`, `03_deliverables/` — and
there is no migration. That is deliberate: a live project should not have its rules changed
under it mid-engagement. Finish those projects as they are; start new ones on
v2.

### Upgrading a project that already exists

A project is a copy, not a link — nothing propagates by itself. Upgrading is
an explicit step, and it has a tool:

```bash
python3 ~/tools/cowork_templates/bin/upgrade_project.py \
    ~/OneDrive/01_PROJECTS/ACME-Bridge-Cowork        # --dry-run to look first
```

It acts on the scaffolding and only the scaffolding: `CLAUDE.md`, `README.md`,
the scripts in the tools zone, and the `_TEMPLATE.md` stubs. Your documents,
the frozen zones, the context files, the logs and the drafts are never
upgrade candidates — never rewritten, never moved, never staged for deletion.
The only project files an upgrade writes are its own record: a dated entry
appended to `WORKLOG.md`, a line under the README footer, and the stamp.

Within the scaffolding, it decides per file, using the content hashes recorded
in `00_AI_context/TEMPLATE.json` when the project was created:

- **Unmodified since the tooling last wrote it** → replaced with the new
  version, placeholders re-substituted.
- **Locally edited** → left exactly as it is; the new version is written into
  the temp zone (`05_temp/template-upgrade-v<version>/`) for you to merge or
  discard. Nothing you wrote is ever overwritten.
- **No longer shipped by the template** → moved to `_to_delete/` if unmodified
  — nothing is deleted, per R8 — and left in place if edited.
- **Missing** → restored.

Every applied upgrade updates the README footer, appends a dated WORKLOG
entry, and records itself in `TEMPLATE.json`. Afterwards, run the
session-start scan (`update_index.py --diff`), read it, then rebuild the
baseline — the tool deliberately does not rebaseline for you, so nothing that
happened to be pending in the project gets silently absorbed.

**Across a major version it refuses.** A major bump means the schema or the
rules changed such that an existing project cannot simply adopt them; that
migration stays a hand job, and a live project may be better finished on the
rules it started with. For a template still below 1.0.0 the minor is the
compatibility boundary and is refused the same way.

**Projects created before `TEMPLATE.json` existed** are adopted on the first
run: template and version are read from the README footer, and the toolbox's
git history is used to prove which scaffolding files are unmodified. Anything
it cannot prove is proposed rather than replaced — the failure mode is a
review copy in the temp zone, never an overwrite.

### Tests

The scripts have regression tests in [`tests/`](tests) — standard library only,
one file per template plus one for the upgrade path. Each test instantiates
the template into a temporary directory with `bin/new_project.py` and drives
the real scripts, so what is tested is what a project gets:

```bash
python3 -m unittest discover tests
```

## Three constraints worth knowing before you start

**Do not `git init` inside a project folder that lives in OneDrive, Dropbox or
iCloud Drive.** The sync client and git's object store fight, and you will
eventually corrupt one of them. Version control lives here, at the template
level; project instances are backed up by the sync client's own version history.

**Keep the project folder pinned for offline availability.** A session running
locally can read a cloud-only placeholder, but only by waiting for it to
download, so an unpinned project turns the session-start scan into a long stall
and fails outright when you are offline.

**The rules are the only protection you have.** A session running on your
machine can delete, overwrite and rename — R1 and R8 hold because they are
followed, not because anything enforces them. That is why cleanup goes through
`_to_delete/` rather than through `rm`.

## Documentation

- [`docs/pattern.md`](docs/pattern.md) — why the structure is shaped this way,
  and the failure mode each rule prevents.
- [`docs/adapting.md`](docs/adapting.md) — what the same skeleton looks like for
  litigation, due diligence, research and design projects.
- [`docs/cowork-notes.md`](docs/cowork-notes.md) — practical mechanics of
  running this with Claude Cowork: local vs cloud sessions, sync placeholders,
  Office locks, where the Microsoft 365 connector fits.

## Provenance

Extracted from a live engineering-tender project repository (a quay-wall pricing
tender) after the structure proved itself across several sessions, then stripped
of everything discipline-specific.
