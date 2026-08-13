# cowork_templates

Reusable project-repository templates for working with an AI agent (Claude
Cowork, Claude Code, or any agent that can read a folder) on real,
document-heavy projects — tenders, claims, studies, due diligence, litigation,
research.

The problem these solve: an AI session starts with no memory. Left to itself it
re-reads whatever it stumbles across, mixes what a client actually sent with
what it computed last week, and confidently quotes a number that was superseded
three revisions ago. The fix is not a better prompt. It is a folder structure
the agent is required to obey, a written context layer it must read first, and a
scan that forces it to notice what changed since last time.

## Templates

| Template | Version | Use it for |
|---|---|---|
| [`cowork-consultant`](templates/cowork-consultant) | 2.0.2 | Consulting engagements — any project that exchanges documents with another party: inputs arrive, work happens, documents are issued. |
| [`cowork-contractor`](templates/cowork-contractor) | 0.1.0 | Contracting work. **Not ready** — currently an unmodified copy of `cowork-consultant`, placed so its structure can be developed in the open. Do not start a real project from it yet. |

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

## Quickstart

```bash
git clone https://github.com/mladenpr/cowork_templates.git
cd cowork_templates
python3 bin/new_project.py ~/OneDrive/01_PROJECTS/ACME-Bridge-Cowork \
    --name "ACME Bridge" --client "ACME Infrastructure" --owner "Your Name"
```

`--template` selects which template to instantiate, and defaults to
`cowork-consultant`. `bin/new_project.py --help` lists what is available.

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

Each project records the template and version it was created from, in its own
`README.md` footer and its first WORKLOG entry. To survey a folder of projects:

```bash
grep -h "Instantiated from" ~/OneDrive/01_PROJECTS/*/README.md
```

The `VERSION` file itself never reaches a project — `new_project.py` strips it
on the way through, along with the `.gitkeep` markers. Both are scaffolding for
this repository, and the stamp already records what they were for.

**cowork-consultant v2.0 restructured the schema.** Projects created from v1.x
keep the v1.x layout — `01_SoT/`, `02_derivatives/`, `03_deliverables/` — and
there is no migration. That is deliberate: a live project should not have its rules changed
under it mid-engagement. Finish those projects as they are; start new ones on
v2.

### Upgrading a project that already exists

A project is a copy, not a link. Nothing propagates once it is created.

Within a major version, copying `templates/cowork-consultant/04_tools/*.py` over the
project's copies and re-running them is safe — the scripts hold no project
state. **Across v1 → v2 it is not**: the v2 scripts look for `01_basis/` and
`02_exchange/` and will not find a v1 project's directories.

Rule changes are a judgement call either way. Update the footer when you
upgrade, so the version stamp never claims something untrue.

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
