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
├── README.md              ← schema + working rules R1–R9
├── 00_AI_context/
│   ├── PROJECT.md         ← the brief: what this is, for whom, conventions
│   ├── INDEX.md           ← every file, one line each (descriptions survive)
│   ├── MANIFEST.json      ← scan baseline (path, size, mtime[, sha256])
│   ├── WORKLOG.md         ← dated decisions, never rewritten
│   └── sot/               ← one context md per logical dataset in 01_SoT
├── 01_SoT/                ← Source of Truth: raw inputs only, immutable
├── 02_derivatives/        ← regenerable outputs (tidy data, figures, extracts)
├── 03_deliverables/       ← issued controlled documents, by number & revision
├── 04_tools/              ← kept scripts that produce the derivatives
├── 05_temp/               ← disposable scratch
└── _to_delete/            ← cleanup staging (only the human empties it)
```

Numbering is pipeline order: inputs (01) → working outputs (02) → issued
documents (03) → machinery (04, 05).

Three ideas carry the whole thing:

**Immutable inputs.** `01_SoT/` holds only what arrived from outside, byte for
byte, wrong bits included. Nothing generated inside the project ever lands
there. When an input is demonstrably wrong, the correction is a *new file* in
`02_derivatives/` with the transformation written down — so months later you can
still prove what the client actually sent you, separately from what you did
about it.

**A context layer the agent must read.** Every dataset in `01_SoT/` gets a
markdown file recording where it came from, what is in it, what is wrong with
it, and what downstream depends on it. `PROJECT.md` carries the brief and the
conventions; `WORKLOG.md` carries dated decisions and is never rewritten
retroactively. This is the memory the model does not have.

**A scan that runs before anything else.** `update_index.py --diff` compares the
folder against `MANIFEST.json` and reports NEW / CHANGED / MISSING. New raw
files get ingested; changed or vanished ones get flagged to you rather than
silently absorbed. A session that skips the scan is a session working from a
stale picture.

The nine rules that formalise this are in
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
`{{CLIENT_SUFFIX}}`. Then run `python3 04_tools/update_index.py`.

**Then, in every session**, point the agent at the folder and say:

> Read CLAUDE.md and run the session-start scan.

## Using it day to day

```bash
python3 04_tools/update_index.py --diff    # what changed since last time
python3 04_tools/update_index.py           # rebuild INDEX.md + MANIFEST.json
python3 04_tools/update_index.py --hash    # same, but content-hashed
```

Use `--hash` if your sync client rewrites modification times and the plain diff
turns noisy: it compares sha256 instead of size+mtime. Manifests are
interoperable in both directions, so you can adopt or drop the flag whenever.

`INDEX.md` descriptions are hand-written and survive regeneration — that column
is where the "what is this file, actually" knowledge accumulates. Fill it in.

## Two constraints worth knowing before you start

**Do not `git init` inside a project folder that lives in OneDrive, Dropbox or
iCloud Drive.** The sync client and git's object store fight, and you will
eventually corrupt one of them. Version control lives here, at the template
level; project instances are backed up by the sync client's own version
history.

**Keep the project folder pinned for offline availability** — "Always Keep on
This Device" in OneDrive and equivalents elsewhere. A cloud-only placeholder
cannot be read through an agent's file bridge; the read fails outright and the
session stalls on a file that looks perfectly present in Finder.

## Documentation

- [`docs/pattern.md`](docs/pattern.md) — why the structure is shaped this way,
  and the failure mode each rule prevents.
- [`docs/adapting.md`](docs/adapting.md) — what the same skeleton looks like for
  litigation, due diligence, research and design projects.
- [`docs/cowork-notes.md`](docs/cowork-notes.md) — practical mechanics of
  running this with Claude Cowork: the device bridge, cloud placeholders,
  writing files back, why deletion is not available.

## Provenance

Extracted from a live engineering-tender project repository (a quay-wall pricing
tender) after the structure proved itself across several sessions, then
stripped of everything discipline-specific.
