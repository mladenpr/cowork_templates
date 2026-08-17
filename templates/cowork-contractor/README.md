# {{PROJECT_NAME}} — Repository Schema & Working Rules

This document defines how the repository is organized and the rules under which
humans and AI sessions work in it.

The pattern rests on one distinction: **some files are frozen and some are
still moving.** The contract, the reference material it rests on, everything
that arrived from outside and everything that has been sent out are frozen —
they are a record, and a record cannot be revised. Everything still being
worked on is mutable and authoritative for nothing. The directory layout is
that distinction made visible.

It is written for work performed under a contract, from award onwards, and it
does not care which tier you sit on. A subcontractor with no packages let and a
main contractor with thirty of them run the same schema; the difference shows
up as an empty folder, not as a different structure.

## Schema

```
{{PROJECT_FOLDER}}/
├── CLAUDE.md              ← AI session bootstrap (read first, every session)
├── README.md              ← this file: schema + working rules
├── 00_AI_context/
│   ├── PROJECT.md         ← high-level project brief
│   ├── PARTIES.md         ← who is who, and the label each is filed under
│   ├── INDEX.md           ← every file: path + one-line description
│   ├── MANIFEST.json      ← scan baseline (path, size, mtime, sha256)
│   ├── WORKLOG.md         ← dated decisions and open items
│   ├── datasets/          ← one context md per logical dataset or thread
│   └── registers/         ← one md per controlled series (variations, POs, …)
├── 01_contract/           ← FROZEN — the instruments that bind
│   ├── upstream/          ← the contract you perform under, and its amendments
│   └── downstream/        ← subcontracts you have let, one folder per party
├── 02_basis/              ← FROZEN — reference material the work rests on
├── 03_exchange/           ← FROZEN — the conversation with the other parties
│   ├── received/<party>/  ← what came in
│   ├── issued/<party>/    ← what went out
│   ├── LOG.jsonl          ← the record: one event per line (log.py)
│   └── LOG.md             ← the readable view, generated from it
├── 04_working/            ← MUTABLE — nothing here is authoritative
│   ├── drafts/            ← one live draft per deliverable
│   ├── analysis/          ← calculations, checks, comparisons
│   └── _extracted/        ← searchable text layer (regenerated)
├── 05_tools/              ← kept scripts
├── 06_temp/               ← disposable scratch, purgeable without thought (not scanned)
├── _inbox/                ← arrivals not yet filed (staging, not a zone)
└── _to_delete/            ← cleanup staging (the user empties it)
```

The numbers are **not** pipeline order — `03_exchange/` holds both inputs and
outputs, so no pipeline reading is possible. They order the directories by
status: frozen first (`01`, `02`, `03`), then mutable (`04`), then machinery
(`05`, `06`).

Two directories sit outside the numbering because neither is a zone: `_inbox/`
holds what has arrived and not yet been filed, and `_to_delete/` holds what is
on its way out. Nothing in either is authoritative, and both are meant to be
empty most of the time.

## Working rules

**R1 — Frozen zones, and provenance as a lookup.** `01_contract/`, `02_basis/`
and `03_exchange/` are frozen. A file there is never edited, renamed, converted
or re-saved once filed — not even when it is demonstrably wrong. Corrections
are new files in `04_working/`, with the transformation recorded in the
dataset's context md.

Within the exchange, direction is the folder boundary, because "is this ours or
theirs?" must be answerable by looking, never by judging. `received/` is
theirs. `issued/` is ours. There is no exception, for any document type.

`01_contract/` holds the instruments that **create or amend a contract** — the
agreement you perform under with everything incorporated into it, its executed
amendments and addenda, and the subcontracts you have let. Everything that
flows *under* a contract is exchange: instructions, variations, purchase
orders, notices, submittals, invoices, correspondence. The test is whether an
instrument came into existence, or whether one party acted under one that
already exists. A signed variation *addendum* is contract; a variation
*instruction* is exchange.

Two consequences of that boundary:

- **A purchase order is an issued document, not a contract instrument.** It
  goes in `03_exchange/issued/<supplier>/` with a row in the log and, if the
  project keeps one, a line in the PO register (R11). A project runs to tens or
  hundreds of them, for things as small as bolts, and filing them among the
  contracts would bury the four documents that actually govern the work.
- **The drafts exchanged on the way to signature are exchange documents.** They
  were genuinely sent and received; they belong in the negotiation thread. Only
  the executed instrument moves into `01_contract/`.
- **The documents an instrument incorporates go with it.** The drawings,
  specification and pricing document the contract lists as contract documents
  are contract, and are filed in `01_contract/` beside it — they are what the
  obligations refer to. A later revision of one of them, sent under the
  contract, is exchange.

Where a file is filed asserts nothing about its legal effect. A purchase order
may well form a contract; a letter may operate as a notice; an instruction may
turn out to be a variation. The folder records who sent it and whether it
created an instrument or acted under one, and that is all it records — the
legal characterisation is made in the analysis, against the contract's own
terms, and written down in the context md or the WORKLOG.

`02_basis/` is neither contract nor conversation: reference material — codes,
standards, site data, your rate library, third-party sources — that the work
rests on but that nobody sent you.

Two more that catch people out, wherever a document sits:

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

**R3 — Ingestion, and the inbox.** Anything arriving from outside is filed the
same way, by a named step: into `03_exchange/received/<party>/` if it is part
of the conversation, `02_basis/` if it is reference material, `01_contract/` if
it is an executed instrument; its context md written or extended; a row
appended to the log if it went into `03_exchange/` or `01_contract/`; the text
layer extracted; INDEX and MANIFEST regenerated. Nothing raw is worked on where
it landed.

Basis material gets no log row. The log is the chronology of the conversation
and of the instruments — every row has a direction and a party — and a
standard, a site investigation report bought from a third party or your own
rate library has neither. Its provenance is recorded in its context md, and it
is found through `INDEX.md`. If a party *sent* it, it is exchange, and it is
logged as such.

The date on a row is the date **on** the document — the letter's date, the
drawing's title block, the email's sent line — never the day it was filed, and
never inferred from a file timestamp. A batch of documents filed after the
event, off an old drive or from a predecessor's folder, is backfill: permitted,
one row per document, dated from the document's face and marked `--backfilled`
so that a reconstruction is never later read as a contemporaneous entry. A
document that carries no date waits for the user to supply one.

`_inbox/` exists because the alternative to a staging area is not tidiness, it
is documents left on a desktop. Drop anything there — a batch pulled off an old
drive, an attachment you have not decided about, a folder someone sent on a
stick — and file it properly later. Two things follow from it being staging
rather than a zone: **nothing in `_inbox/` is authoritative**, so no figure is
ever read from it into a draft, and the session-start scan counts what is
sitting there every time until it is empty.

**Text pasted into a chat window is not ingestion.** An email quoted into a
session so it can be read, checked or answered is working material. A session
may use it, cross-check it against the frozen zones and draft the reply that
was asked for — but it does not file it, and nothing it says (a figure, a date,
a commitment, a concession) is written into `WORKLOG.md`, `PROJECT.md`, a
register or a dataset context md while a chat message is its only source. Every
recorded fact resolves to a file in a frozen zone or to a script in
`05_tools/`. A paste is neither, and it is gone when the session closes.

Whether a piece of correspondence belongs in the record is a judgement, and it
is yours — the same seam as R5. When an email matters enough to keep, write it
into a markdown file and drop it into `03_exchange/received/<party>/`, or
`issued/<party>/` if it is one you sent. It appears as NEW in the next
session-start scan and is ingested by this rule like anything else. A
transcribed email you sent is correspondence, not a deliverable: it carries no
document number and no revision, and it does not go through the issue procedure
(R5), which exists for controlled documents leaving `04_working/drafts/`.

Head the file so that it declares what it is:

```markdown
# Email — <subject>

- **Direction / Party:** in — <who sent it> | out — <who it went to>
- **Sent:** <date, and time where it matters> — as stated in the email
- **From / To / Cc:**
- **Thread:** <the log thread this belongs to>
- **Transcribed by:** <name>, <date> — body verbatim, no corrections
- **Attachments named:** none | "<filename>" — not held in this project
- **Not captured:** header chain, formatting, the thread quoted below the reply

---

<the email body, verbatim>
```

Name it `YYYY-MM-DD_<party>_<subject-slug>.md`, dated the day the email was
sent rather than the day it was typed up, and it is frozen from that point like
everything else in the zone (R1).

Three of those lines carry the weight. **Transcribed by** is what stops the file
being read, months later, as the original — it is a copy, and a copy standing
next to genuine received documents is indistinguishable from one unless it says
so. **Attachments named** turns "this email refers to a drawing" into something
you discover now rather than when you go to rely on it. **Not captured** records
the shape of what was left behind. Delete the lines that do not apply; keep
those three.

**R4 — The exchange log is a record, and a view of it.** `03_exchange/LOG.jsonl`
carries one JSON object per line, one line per event — a document in, or a
document out — with its id, date, direction, party, type, title, reference,
revision, thread, path, status, action, due date, note, when it was recorded
and whether it was backfilled. `03_exchange/LOG.md` is generated from it by
`05_tools/log.py`. Rows are added with `log.py add`; typing into the markdown
table changes nothing a query will ever see.

The split is a concession to length, and only to length. A works contract runs
for years and produces thousands of events, and at that size a markdown table
cannot be filtered, counted or sorted, while every hand-edit risks mangling a
column. One JSON object per line stays diffable, stays readable in a text
editor, and can be queried in a single pass — by `log.py query`, or by a
session reading the file directly. The markdown view exists so the log is still
legible to someone with no tools at all.

The log is the index of the conversation, the way `INDEX.md` is the index of
the files, and it is what makes "what did we send them on the 24th" and "what
have they still not answered" one-glance questions. A row is written at the
moment of the event, never reconstructed later.

A row carries two states, because two different questions get asked of it.
`status` is the document's — `current`, `superseded by #n`, `withdrawn` — and
`action` is what is owed on it — `open`, `answered by #n`, `closed`, or nothing.
An issued letter that asks a question is `current` and `open` at once; when the
answer arrives it stays current and becomes answered; when the next revision
goes out it becomes superseded whether or not it was answered. One column
cannot hold both, and a log that tries loses one of them.

Rows are append-only with one exception: `status`, `action`, `due` and `note`
may be updated in place through `log.py set`, because those are what changes
after the event — a query gets answered, a revision gets superseded, a deadline
is agreed. Every such change is kept in the row's `history`, with what changed
and when. Everything else about a filed row stays as written; a row that was
wrong is corrected by a new row carrying a note, not by a rewrite. A row may be
logged `--pending` when its file has genuinely not landed yet, and its path
filled in once, later; a path is otherwise fixed the moment it is written.

The row and the tree agree by construction. `log.py add` refuses a row whose
direction contradicts the `received/`/`issued/` folder its path sits in, whose
party contradicts the party folder, whose date is not a real calendar date, or
whose path points at nothing — the procedure files first and logs second, so a
missing file is a mistake, not a state. Nothing is written until the whole row
is right, and a row and the rows it supersedes or answers are written together
or not at all.

Path names what was filed. For an issued document — PDF plus source at the
same revision (R10) — it names the PDF, since the PDF is what was sent, and the
source sits beside it under the same stem. An event made of many files — a
transmittal that brought thirty drawings — may be one row whose path is the
folder they were filed in, or thirty rows if each drawing's revision has to be
followed; the project decides, and a register (R11) is where a series is
followed. `log.py check` reads the log against the tree and reports what does
not add up — files in the exchange no row mentions (a source beside a logged
PDF, under the same stem, counts as mentioned), rows pointing at nothing,
dangling `#n` references, actions past their due date — and it is part of the
session-start scan.

An executed contract or subcontract gets a log row too — `--type contract` or
`amendment`, dated the day it became executed — even though the instrument
itself is filed in `01_contract/`. The log is the chronology of everything that
moved; it is not a second copy of the filing system.

One writer at a time. The log is a file in a synced folder; two machines
appending at the same moment produce a sync-conflict copy, which the scan
reports, and possibly a duplicated id, which `check` reports. Neither is
silent, and neither is worth a locking scheme.

**R5 — Issuing is an explicit step, never a rename.** A document leaves the
project only by being issued, and issuing is something you ask for by name. On
that instruction, and not before, the file moves from `04_working/drafts/` into
`03_exchange/issued/<party>/` under its document number and revision, the PDF is
filed with its source document alongside, the log gains a row, the WORKLOG gains
a dated entry, and the index is regenerated.

You decide *when*, and you export the PDF — the tools here do not render
documents. The mechanics are not yours to remember. What this replaces —
quietly renaming a draft — leaves the project unable to say what was sent, to
whom, or under what cover.

Issuing is also the only way anything leaves. **The project folder is
internal**: it holds both sides' contracts, every party's correspondence and
your own position — cost, margin, the view you take of a claim — and nothing in
it is shared with a counterparty. What they receive is a copy that left through
`03_exchange/issued/`. The folder is not shared, synced to, or opened for a
party you correspond with, and internal-position material (PROJECT.md) is never
carried into a draft that goes out.

**R6 — Working is mutable, and singular.** `04_working/` holds one live draft
per deliverable, revised in place. Do not generate a new draft file per
revision: the current draft is the current draft, its history is the sync
client's version history, and the reasoning behind each change belongs in the
WORKLOG. Nothing in `04_working/` is authoritative and nothing there is
evidence.

The next revision of an issued document starts by copying its source back out
of `03_exchange/issued/` into `04_working/drafts/`.

**R7 — Index, manifest and the session-start scan.** `INDEX.md` lists every
file outside `06_temp/` and `_to_delete/` with a one-line description;
`MANIFEST.json` records path, size, mtime and sha256. Both are regenerated by
`05_tools/update_index.py` after any file operation, and hand-written
descriptions in `INDEX.md` survive regeneration.

Every session diffs the repository against the manifest before other work. The
severity of a result depends on where it is:

- **NEW in a frozen zone** → ingest it per R3, or ask. NEW in `04_working/` or
  `00_AI_context/` is a draft, an extraction or a context file being written.
- **CHANGED or MISSING in `01_contract/`, `02_basis/` or `03_exchange/`** →
  stop and raise it. Something frozen moved: either a rule was broken or the
  sync client did something. Not for a session to resolve. The scan already
  knows the one routine case — `LOG.jsonl` and `LOG.md` change on every
  ingestion and are listed as plain CHANGED, never as an alarm; their going
  MISSING still is one.
- **CHANGED in `04_working/` or `00_AI_context/`** → normal. That is a draft
  being drafted, or the context layer being kept.
- **MISSING DIR** → the schema's skeleton is checked by name, because a
  manifest of files cannot see that an empty zone has vanished. Recreate it,
  empty; if it held files, those are listed as MISSING and that is the event.
- **Anything in `_inbox/`** → reported as a count every scan, until it is
  filed. It is not an alarm; it is a reminder that the project's record is
  incomplete by exactly that much.

**R8 — Never delete; stage instead.** Cleanup means moving files into
`_to_delete/` under non-colliding names and reporting what was moved. The user
empties it; no session does. A session running locally can delete, overwrite
and rename — so this rule, not the environment, is what stands between a
misread instruction and an unrecoverable loss.

**R9 — Sync discipline.** The folder lives in a synced cloud drive for backup,
version history and access from more than one of your own machines — not for
sharing with a counterparty (R5). That imposes five habits:

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
- **Keep the text layer current.** `05_tools/extract_text.py` mirrors the frozen
  zones into `04_working/_extracted/`, so the project is greppable. Run it after
  every ingestion and every issue. Files that are already text — a markdown
  email transcript, the log itself — are deliberately not mirrored, since the
  copy would be the original; a search covers `_extracted/` **and** the frozen
  zones, or it misses them.
- **The text layer is an index, not a substitute.** Use it to find things, then
  open the source. Any figure, date or quotation entering a document is read
  from the file in the frozen zone, not from the extraction — which drops
  layout, page numbers, images and drawings, and *reconstructs* list numbering
  and dates rather than reading them.
- **Record document condition in the context md** (R2): text layer or scan,
  tracked changes, comments, protection.
- **Rights-managed files cannot be read** by any tool. Record it and ask for a
  decrypted copy in `04_working/`; do not work around it.
- **Issue PDFs, keep sources.** The issued artefact is normally the PDF; its
  source document is filed beside it at the same revision, so the next revision
  starts from the source rather than a reconstruction.

**R11 — Controlled series get a register.** A series that is numbered and
carries a status — variations, RFIs, purchase orders, payment applications,
test certificates — gets one md in `00_AI_context/registers/`, with a row per
item and a status column.

This is not a second log. The log answers "what happened, and in what order";
a register answers "where does this series stand, and what is missing". The
second question is the one a numbered series exists to raise: an RFI with no
answer, a variation instructed and never valued, an application with no
certificate against it. **A register is read by its gaps**, so each entry cites
the log id it corresponds to and the register never restates what the log
already holds.

Which registers a project keeps is a project decision, made when you notice
yourself asking the same status question twice. A project with four variations
does not need a variations register; one with eighty cannot be run without one.

## Decision log

Dated decisions, corrections and open items are recorded in
`00_AI_context/WORKLOG.md` — one dated entry per decision, never rewritten
retroactively. Entries that were true when written stay as written; later
changes get their own entry.

---

Instantiated from the `cowork-contractor` template **v{{TEMPLATE_VERSION}}**
(<https://github.com/mladenpr/cowork_templates>) on {{DATE}}.

A project is a copy, not a link — nothing propagates from the template after
this point. This line is how you tell, months later, which rules and which
tooling this project actually has.
