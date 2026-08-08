# {{PROJECT_NAME}} — Repository Schema & Working Rules

This document defines how the repository is organized and the rules under which
humans and AI sessions work in it.

The pattern rests on one distinction: **some files are frozen and some are
still moving.** Everything that arrived from outside, and everything that has
been sent out, is frozen — it is a record of an exchange and cannot be revised.
Everything still being worked on is mutable and authoritative for nothing. The
directory layout is that distinction made visible.

## Schema

```
{{PROJECT_FOLDER}}/
├── CLAUDE.md              ← AI session bootstrap (read first, every session)
├── README.md              ← this file: schema + working rules
├── 00_AI_context/
│   ├── PROJECT.md         ← high-level project brief
│   ├── INDEX.md           ← every file: path + one-line description
│   ├── MANIFEST.json      ← scan baseline (path, size, mtime, sha256)
│   ├── WORKLOG.md         ← dated decisions and open items
│   └── datasets/          ← one context md per logical dataset or thread
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
├── 05_temp/               ← disposable scratch, purgeable without thought
└── _to_delete/            ← cleanup staging (the user empties it)
```

The numbers are **not** pipeline order — `02_exchange/` holds both inputs and
outputs, so no pipeline reading is possible. They order the directories by
status: frozen first (`01`, `02`), then mutable (`03`), then machinery (`04`,
`05`).

## Working rules

**R1 — Frozen zones, and provenance as a lookup.** `01_basis/` and
`02_exchange/` are frozen. A file there is never edited, renamed, converted or
re-saved once filed — not even when it is demonstrably wrong. Corrections are
new files in `03_working/`, with the transformation recorded in the dataset's
context md.

Within the exchange, direction is the folder boundary, because "is this ours or
theirs?" must be answerable by looking, never by judging. `received/` is
theirs. `issued/` is ours. `01_basis/` is neither: reference material — codes,
standards, site data, third-party sources — that the work rests on but that is
not part of the conversation.

Two consequences that catch people out:

- **What you issued is frozen too.** A document that has been sent exists in
  someone else's inbox. It cannot be revised, only superseded by a new
  revision, which is a new file.
- **Your own document, returned to you marked up, is a *received* document.**
  It goes in `received/` even though most of its bytes are yours. It is theirs
  now, and their markup is the content that matters.

**R2 — Every dataset gets context.** Each logical dataset in a frozen zone has
one context md in `00_AI_context/datasets/`. Granularity is the *logical
dataset*, not the file: a singular document gets its own; a series or a
negotiation thread gets one md covering the whole thing, with a member table
inside.

A thread is the important case. A subcontract exchanged back and forth — your
draft, their comments, your response — is one dataset whose members alternate
custody. Its member table carries date, direction, version, path and **what
changed**, which is the column you actually reread months later and the one no
folder layout can give you.

**R3 — Ingestion.** Anything arriving from outside is filed the same way, by a
named step: into `02_exchange/received/` if it is part of the conversation, or
`01_basis/` if it is reference material; its context md written or extended; a
row appended to the LOG; the text layer extracted; INDEX and MANIFEST
regenerated. Nothing raw is worked on where it landed.

**R4 — The exchange log.** `02_exchange/LOG.md` carries one row per document in
or out, in date order, with its direction, party and thread. It is the index of
the conversation, the way `INDEX.md` is the index of the files, and it is what
makes "what did we send them on the 24th" and "what have they still not
answered" one-glance questions. A row is written at the moment of the event,
never reconstructed later.

**R5 — Issuing is an explicit step, never a rename.** A document leaves the
project only by being issued, and issuing is something you ask for by name. On
that instruction, and not before, the file moves from `03_working/drafts/` into
`02_exchange/issued/` under its document number and revision, the PDF is filed
with its source document alongside, the LOG gains a row, the WORKLOG gains a
dated entry, and the index is regenerated.

You decide *when*. The mechanics are not yours to remember. What this replaces
— quietly renaming a draft — leaves the project unable to say what was sent, to
whom, or under what cover.

**R6 — Working is mutable, and singular.** `03_working/` holds one live draft
per deliverable, revised in place. Do not generate a new draft file per
revision: the current draft is the current draft, its history is the sync
client's version history, and the reasoning behind each change belongs in the
WORKLOG. Nothing in `03_working/` is authoritative and nothing there is
evidence.

The next revision of an issued document starts by copying its source back out
of `02_exchange/issued/` into `03_working/drafts/`.

**R7 — Index, manifest and the session-start scan.** `INDEX.md` lists every
file with a one-line description; `MANIFEST.json` records path, size, mtime and
sha256. Both are regenerated by `04_tools/update_index.py` after any file
operation, and hand-written descriptions in `INDEX.md` survive regeneration.

Every session diffs the repository against the manifest before other work. The
severity of a result depends on where it is:

- **NEW** anywhere → ingest it per R3, or ask.
- **CHANGED or MISSING in `01_basis/` or `02_exchange/`** → stop and raise it.
  Something frozen moved: either a rule was broken or the sync client did
  something. Not for a session to resolve.
- **CHANGED in `03_working/`** → normal. That is a draft being drafted.

**R8 — Never delete; stage instead.** Cleanup means moving files into
`_to_delete/` under non-colliding names and reporting what was moved. The user
empties it; no session does. A session running locally can delete, overwrite
and rename — so this rule, not the environment, is what stands between a
misread instruction and an unrecoverable loss.

**R9 — Sync discipline.** The folder lives in a synced cloud drive for backup,
version history and sharing. That imposes five habits:

- **Pin the folder for offline availability.** A dehydrated placeholder is read
  by downloading it, so an unpinned project turns the session-start scan into a
  long stall and fails outright when you are offline.
- **Close documents before a session works on them.** Word and Excel hold locks
  and leave `~$` owner files behind; a locked file cannot be rewritten.
- **Let sync settle after mass file operations** before opening the folder on
  another machine.
- **Keep names sync-legal.** OneDrive and SharePoint reject `" * : < > ? / \ |`,
  leading/trailing spaces, trailing dots and the reserved DOS names, and cap
  the item URL at 400 characters. `update_index.py` warns about all of these.
- **Do not `git init`** inside a synced project folder — git's object store and
  the sync client fight each other.

**R10 — Document handling.** The working material is documents, which have
properties a file tree does not express:

- **Never re-save a source document.** Opening a `.docx` in Word and saving it —
  with no edits — rewrites the package and changes its hash. Never accept or
  reject tracked changes, resolve comments, or convert a format inside a frozen
  zone. In a received document the markup *is* the content.
- **Keep the text layer current.** `04_tools/extract_text.py` mirrors the frozen
  zones into `03_working/_extracted/`, so the project is greppable. Run it after
  every ingestion and every issue.
- **The text layer is an index, not a substitute.** Use it to find things, then
  open the source. Any figure, date or quotation entering a document is read
  from the file in the frozen zone, not from the extraction — which drops
  layout, page numbers, images and drawings, and *reconstructs* list numbering
  and dates rather than reading them.
- **Record document condition in the context md** (R2): text layer or scan,
  tracked changes, comments, protection.
- **Rights-managed files cannot be read** by any tool. Record it and ask for a
  decrypted copy in `03_working/`; do not work around it.
- **Issue PDFs, keep sources.** The issued artefact is normally the PDF; its
  source document is filed beside it at the same revision, so the next revision
  starts from the source rather than a reconstruction.

## Decision log

Dated decisions, corrections and open items are recorded in
`00_AI_context/WORKLOG.md` — one dated entry per decision, never rewritten
retroactively. Entries that were true when written stay as written; later
changes get their own entry.

---

Instantiated from the `sot-project` template **v{{TEMPLATE_VERSION}}**
(<https://github.com/mladenpr/cowork_templates>) on {{DATE}}.

A project is a copy, not a link — nothing propagates from the template after
this point. This line is how you tell, months later, which rules and which
tooling this project actually has.
