# cowork_templates

Reusable project-repository templates for working with an AI agent (Claude
Cowork, Claude Code, or any agent that can read a folder) on real, document-heavy
projects — tenders, claims, studies, due diligence, litigation, research.

The problem these solve: an AI session starts with no memory. Left to itself it
re-reads whatever it stumbles across, mixes what a client actually sent with
what it computed last week, and confidently quotes a number that was superseded
three revisions ago. The fix is not a better prompt. It is a folder structure
the agent is required to obey, a written context layer it must read first, and a
scan that forces it to notice what changed since last time.

## Templates

| Template | Use it for |
|---|---|
| [`sot-project`](templates/sot-project) | Any project where raw inputs arrive from outside, get analysed, and issued documents go back out. Currently the only template. |

## The `sot-project` pattern

```
<project>/
├── CLAUDE.md              ← AI session bootstrap (read first, every session)
├── README.md              ← schema + working rules R1–R10
├── 00_AI_context/
│   ├── PROJECT.md         ← the brief: what this is, for whom, conventions
│   ├── INDEX.md           ← every file, one line each (descriptions survive)
│   ├── MANIFEST.json      ← scan baseline (path, size, mtime, sha256)
│   ├── WORKLOG.md         ← dated decisions, never rewritten
│   └── sot/               ← one context md per logical dataset in 01_SoT
├── 01_SoT/                ← Source of Truth: raw inputs only, immutable
├── 02_derivatives/        ← regenerable outputs (tidy data, figures, extracts)
│   └── _extracted/        ← searchable text layer, mirroring 01_SoT
├── 03_deliverables/       ← issued controlled documents, by number & revision
│   └── REGISTER.md        ← what was issued, to whom, at what revision
├── 04_tools/              ← kept scripts that produce the derivatives
├── 05_temp/               ← disposable scratch
└── _to_delete/            ← cleanup staging (only the human empties it)
```

Numbering is pipeline order: inputs (01) → working outputs (02) → issued
documents (03) → machinery (04, 05).

Four ideas carry the whole thing:

**Immutable inputs.** `01_SoT/` holds only what arrived from outside, byte for
byte, wrong bits included. Nothing generated inside the project ever lands
there. When an input is demonstrably wrong, the correction is a *new file* in
`02_derivatives/` with the transformation written down — so months later you can
still prove what the client actually sent you, separately from what you did
about it. With documents this bites harder than it sounds: re-saving a `.docx`
in Word rewrites the package even with no edits, and accepting a tracked change
destroys a negotiation record.

**A context layer the agent must read.** Every dataset in `01_SoT/` gets a
markdown file recording where it came from, what is in it, what is wrong with
it, what condition it is in, and what downstream depends on it. `PROJECT.md`
carries the brief and the conventions; `WORKLOG.md` carries dated decisions and
is never rewritten retroactively. This is the memory the model does not have.

**A searchable text layer.** An agent cannot grep a PDF. `extract_text.py`
mirrors `01_SoT/` into `02_derivatives/_extracted/` as one markdown file per
document — tracked changes, comments, tables, sheets and slides included — so
"which document says X" becomes a text search instead of a session spent
reopening binaries. It is fully regenerable, so it costs nothing to throw away.

**A scan that runs before anything else.** `update_index.py --diff` compares the
folder against `MANIFEST.json` and reports NEW / CHANGED / MISSING, plus
suspected sync-conflict copies and filenames OneDrive will refuse to sync. New
raw files get ingested; anything else gets flagged to you rather than silently
absorbed. A session that skips the scan is a session working from a stale
picture.

The ten rules that formalise this are in
[`templates/sot-project/README.md`](templates/sot-project/README.md). They are
short, and they are meant to be binding — the point is that the agent cannot
improvise around them.

## Quickstart

**With the script** (clone this repo anywhere outside your synced drive):

```bash
git clone https://github.com/mladenpr/cowork_templates.git
cd cowork_templates
python3 bin/new_project.py ~/OneDrive/01_PROJECTS/ACME-Bridge-Cowork \
    --name "ACME Bridge" --client "ACME Infrastructure" --owner "Your Name"
```

It copies the template, fills in the placeholders, and writes the first
INDEX/MANIFEST baseline.

**Without the script:** download the repo as a ZIP, copy
`templates/sot-project/` to wherever the project should live, rename it, delete
the `.gitkeep` files, and search-replace `{{PROJECT_NAME}}`,
`{{PROJECT_FOLDER}}`, `{{CLIENT}}`, `{{OWNER}}`, `{{DATE}}` and
`{{CLIENT_SUFFIX}}`. Then run `python3 04_tools/update_index.py --hash`.

**Then, in every session**, point the agent at the folder and say:

> Read CLAUDE.md and run the session-start scan.

On Windows, use `py -3` wherever these commands say `python3`.

## Using it day to day

```bash
python3 04_tools/update_index.py --diff    # what changed since last time
python3 04_tools/update_index.py           # rebuild INDEX.md + MANIFEST.json
python3 04_tools/extract_text.py           # extract new/changed documents
python3 04_tools/extract_text.py --report  # what is in SoT and what state it is in
```

Manifests are content-hashed by default, because a sync client rewrites
modification times when it hydrates a file or resolves a conflict and an
mtime-based diff turns to noise. Hashing is sticky — once a manifest carries
hashes you never need the flag again — and unchanged files reuse their recorded
hash, so a scan only reads what looks touched. `--rehash` forces a full
recompute; `--no-hash` deliberately drops back to size+mtime.

`extract_text.py` handles Word, Excel and PowerPoint with the standard library
alone. PDFs need `pip install pypdf`; without it they are recorded as unread
rather than skipped silently. `--report` is the quickest way to find out that a
document you were about to rely on is a scan needing OCR, or carries a
sensitivity label that makes it unreadable to every tool you have.

`INDEX.md` descriptions are hand-written and survive regeneration — that column
is where the "what is this file, actually" knowledge accumulates. Fill it in.

## Three constraints worth knowing before you start

**Do not `git init` inside a project folder that lives in OneDrive, Dropbox or
iCloud Drive.** The sync client and git's object store fight, and you will
eventually corrupt one of them. Version control lives here, at the template
level; project instances are backed up by the sync client's own version
history.

**Keep the project folder pinned for offline availability** — "Always Keep on
This Device" in OneDrive and equivalents elsewhere. A session running locally
can read a cloud-only placeholder, but only by waiting for it to download, so
an unpinned project turns the session-start scan into a long stall and fails
outright when you are offline. (Through a cloud file bridge it is worse: the
read fails hard on a file that looks perfectly present in Finder.)

**The rules are the only protection you have.** A session running on your
machine can delete, overwrite and rename — R1 and R8 hold because they are
followed, not because anything enforces them. That is a change from the cloud
bridge, where deletion was simply impossible, and it is the reason cleanup goes
through `_to_delete/` rather than through `rm`.

## Documentation

- [`docs/pattern.md`](docs/pattern.md) — why the structure is shaped this way,
  and the failure mode each rule prevents.
- [`docs/adapting.md`](docs/adapting.md) — what the same skeleton looks like for
  litigation, due diligence, research and design projects.
- [`docs/cowork-notes.md`](docs/cowork-notes.md) — practical mechanics of
  running this with Claude Cowork: local vs cloud sessions, sync placeholders,
  Office locks, where the Microsoft 365 connector fits, and why deletion is a
  policy rather than a limit.

## Provenance

Extracted from a live engineering-tender project repository (a quay-wall pricing
tender) after the structure proved itself across several sessions, then
stripped of everything discipline-specific.
