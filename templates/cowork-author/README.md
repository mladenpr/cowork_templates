# {{PROJECT_NAME}} — Repository Schema & Working Rules

This document defines how the repository is organized and the rules under which
humans and AI sessions work in it.

The pattern rests on one distinction: **some files are frozen and some are
still moving.** Everything that arrived from outside, everything that has been
sent out, and every revision of the document that was frozen on purpose is a
record and cannot be revised. Everything still being worked on is mutable and
authoritative for nothing. The directory layout is that distinction made
visible.

This is the **authoring** variant of the pattern. The project's centre is
documents being produced from the ground up — method statements, plans,
reports, technical proposals — through many revisions across many sessions,
from a brief, reference material, an example of what good looks like and a
branded template, and finishing with a submission. The role you hold while
writing, consultant or contractor, does not change the loop; only the document
type does. It is for the heavy lifting: a priced quotation, or the revision of
a document that has already been issued, is ordinarily a `cowork-consultant`
job.

**One repository per real project, all of its documents in it.** The folder is
created once; every document the project needs is written here, each under its
own slug. The structure is designed so that after ten documents and a few
hundred dropped-in photos and drawings it is still legible: a drop zone the
scan counts until it is empty, sub-folders created on demand and by subject
rather than predefined, and an index that rolls media-heavy folders up into
one line.

## Schema

```
{{PROJECT_FOLDER}}/
├── CLAUDE.md              ← AI session bootstrap (read first, every session)
├── README.md              ← this file: schema + working rules
├── 00_AI_context/
│   ├── PROJECT.md         ← the brief, the people, the deliverables, conventions
│   ├── INDEX.md           ← every file: path + one-line description
│   ├── MANIFEST.json      ← scan baseline (path, size, mtime, sha256)
│   ├── TEMPLATE.json      ← template stamp (tooling-maintained — do not edit)
│   ├── WORKLOG.md         ← dated decisions and open items
│   ├── datasets/          ← one context md per input dataset
│   └── documents/         ← one context md per DELIVERABLE: spec, outline, feedback
├── 01_basis/              ← FROZEN — what the documents rest on, by role
│   ├── reference/         ← what they must be correct against (sub-folders by subject, on demand)
│   ├── examples/          ← what good looks like — form, never content
│   └── templates/         ← the branded shells drafts are instantiated from
├── 02_exchange/           ← FROZEN — the conversation with the other parties
│   ├── received/          ← what came in
│   ├── issued/            ← what went out
│   └── LOG.md             ← both directions, one chronology
├── 03_revisions/          ← FROZEN — the document's own history
│   ├── LOG.md             ← every freeze, return and issue, one chronology
│   └── <doc-slug>/
│       └── Rnn/           ← the draft as frozen (source, PDF when it left your hands)
│           └── returns/   ← what came back on Rnn: marked-up copies, review notes
├── 04_working/            ← MUTABLE — nothing here is authoritative
│   ├── drafts/
│   │   └── <doc-slug>/    ← ONE live draft per deliverable, revised in place
│   ├── analysis/          ← calculations, figures, tables feeding the drafts (by slug, on demand)
│   ├── library/           ← project text reused across documents, written once (on demand)
│   └── _extracted/        ← searchable text layer of the frozen zones (regenerated)
├── 05_tools/              ← kept scripts
├── 06_temp/               ← disposable scratch, purgeable without thought
├── _inbox/                ← drop zone — counted by every scan until empty; not a zone
└── _to_delete/            ← cleanup staging (the user empties it)
```

Folders marked *on demand* are not created by the template. A session makes
one the first time it is needed and never before, because a tree of empty
folders predicting subjects nobody has dropped yet is clutter of exactly the
kind this layout exists to avoid.

The numbers are **not** pipeline order — `02_exchange/` holds both inputs and
outputs, so no pipeline reading is possible. They order the directories by
status: frozen first (`01`, `02`, `03`), then mutable (`04`), then machinery
(`05`, `06`).

One slug ties a deliverable together across three places:
`00_AI_context/documents/<slug>.md` describes it, `04_working/drafts/<slug>/`
holds its live draft, `03_revisions/<slug>/` holds its history. A project with
one deliverable has one slug; the level exists from day one so that a second
deliverable never means restructuring.

## Working rules

**R1 — Frozen zones, and provenance as a lookup.** `01_basis/`, `02_exchange/`
and `03_revisions/` are frozen. A file there is never edited, renamed,
converted or re-saved once filed — not even when it is demonstrably wrong.
Corrections are new files in `04_working/`, with the transformation recorded
in the dataset's context md.

Within the exchange, direction is the folder boundary, because "is this ours or
theirs?" must be answerable by looking, never by judging. `received/` is
theirs. `issued/` is ours. Two consequences that catch people out:

- **What you issued is frozen too.** A document that has been sent exists in
  someone else's inbox. It cannot be revised, only superseded by a new
  revision, which is a new file.
- **Your own document, returned to you marked up, is a *received* document.**
  It goes in `received/` even though most of its bytes are yours. It is theirs
  now, and their markup is the content that matters.

Within the basis, **role is the folder boundary**, for the same reason: the
agent must never decide from a filename whether a document is something to be
correct against or something to imitate.

- `reference/` — what the document must be correct against: standards, codes,
  data, your own source material, a past project's document you are drawing
  facts from. Take facts from it; take nothing else.
- `examples/` — what good looks like: a document of the kind you are writing.
  Take its structure, tone, depth and table layouts; **never its content** —
  not a name, not a figure, not a project specific (R12).
- `templates/` — the company's branded document shell, empty or a sample from
  another project. The draft is instantiated from it by copy; it is never
  edited, and a sample is stripped to its skeleton on the way (R12).

`01_basis/` is not part of the conversation — and on a real project the
conversation is narrower than it looks. **`02_exchange/` is the conversation
*about the documents being written*:** the request or instruction that asks
for one, the comments sheet that comes back on one, the approval, the
submission itself. The drawings, the specification, the site photos, the
standards — material the documents are written *from* — are `reference/`
**whoever sent them**, because they are not correspondence about these
documents; they are what the documents rest on. A session that filed every
client drawing under `received/` would swell the exchange log with rows that
answer no question the log exists to answer. The test is: would this row tell
me what was asked, what was submitted, or what came back on a submission? If
not, it is reference.

If the same real project also has a `cowork-contractor` repository, the
drawings and the contract live there as the record; this repository holds
reference **copies**, and each dataset md names where the original is.

**Sub-folders are by subject, never by document, and made on demand.**
`reference/` starts flat. When a set arrives or a subject accumulates — a
batch of photos from one walk, the drawing register, the specification
sections — the session creates a folder for it, named for the subject
(`photos/2026-08-12_north-quay/`, `drawings/`, `spec/`), and files into it.
Never a folder per deliverable: a drawing serves three method statements and
exists once; which documents use it is recorded in the mds (the document md's
*Inputs*, the dataset md's *Downstream use*), not in the tree. The same on
demand, by-slug rule applies inside the exchange — `issued/<slug>/` and
`received/<slug>/` once a document has more than a file or two there — and
inside `04_working/analysis/`. Direction and role stay folder boundaries; the
sub-folders inside them carry no meaning and can be adopted at any time.

Within a revision, **snapshot and return are a folder boundary**: the frozen
draft sits in `Rnn/`, and anything that came back on it — a colleague's marked-up
copy, your own scanned annotations, a review note — sits in `Rnn/returns/`. A
return is never cleaned up; the markup is the content, exactly as for a
received document.

**R2 — Every dataset gets context; every deliverable gets a document md.**
Each logical dataset in a frozen zone has one context md in
`00_AI_context/datasets/`. Granularity is the *logical dataset*, not the file:
a singular document gets its own; a series or a negotiation thread gets one md
covering the whole thing, with a member table inside. **A set of media is one
dataset**: the photos from one site walk, the drawing issue of one date, get
one md saying what the set shows and which documents draw on it — never one md
per photo. An example or a template gets one too, and its md says what to take
from it, what not to take, and which of its terms must not appear in the draft
(R12).

Each **deliverable** has one document md in `00_AI_context/documents/<slug>.md`
— the authoring counterpart of a dataset md. A dataset md describes something
that arrived; a document md describes the thing being made: what it is for and
for whom, what form it borrows, which requirements it must answer and where,
how far each section has got, what you have said you want, what feedback is
still open, and where its revisions stand. It is read **before the draft is
opened**, every session, and it holds the *current* state — history lives in
the revision log and the WORKLOG. Two of its tables are read by their gaps: the
**requirements coverage** table answers "have we answered everything they
asked", the **feedback register** answers "have we done everything you said".
Neither can be reconstructed from the draft.

**R3 — Ingestion, and the inbox.** Anything arriving from outside is filed the
same way, by a named step: into `02_exchange/received/` if it is part of the
conversation about the documents, or `01_basis/<role>/` — and within
`reference/`, the subject folder, existing or new — if it is what they rest on;
its context md written or extended; a row appended to the exchange LOG for
anything received; the text layer extracted; INDEX and MANIFEST regenerated.
Nothing raw is worked on where it landed.

**`_inbox/` is where things land.** Drop a batch of photos, a drawing issue, a
spec section there and stop thinking about it; the next session-start scan
counts what is waiting and files it by this rule. Drop a batch as a folder
(`_inbox/2026-08-12_north-quay/`) and it arrives as one set, one line, one
decision. The inbox is not a zone: nothing in it is authoritative, nothing in
it is quoted, nothing in it is extracted, and every scan says how many files
it holds until it is empty. A file dropped anywhere else still surfaces as NEW
and is filed the same way — the inbox is the courtesy, not the rule.

**Text pasted into a chat window is not ingestion.** An email quoted into a
session so it can be read, checked or answered is working material. A session
may use it, cross-check it against the frozen zones and draft the reply that
was asked for — but it does not file it, and no *fact about the world* it
states (a figure, a date, a commitment, a concession) is written into
`WORKLOG.md`, `PROJECT.md` or a context md while a chat message is its only
source. Every recorded fact resolves to a file in a frozen zone or to a script
in `05_tools/`.

**Your instructions about the document are different, and are recorded.**
"Make section 3 shorter", "use the client's term for the jetty", "drop the
risk table" are decisions about the deliverable, and you are their source. They
go into the feedback register of the document md the moment they are given,
dated and attributed to you, and into the WORKLOG where they change the
approach. The line is provenance: a decision you make has a source — you, on a
date; a figure you quote from an email you have not filed does not.

When a piece of correspondence matters enough to keep, write it into a
markdown file headed as below and drop it into `02_exchange/received/`, or
`02_exchange/issued/` if it is one you sent. It appears as NEW in the next
session-start scan and is ingested by this rule like anything else.

```markdown
# Email — <subject>

- **Direction / Party:** in — <who sent it> | out — <who it went to>
- **Sent:** <date, and time where it matters> — as stated in the email
- **From / To / Cc:**
- **Thread:** <the LOG thread this belongs to>
- **Transcribed by:** <name>, <date> — body verbatim, no corrections
- **Attachments named:** none | "<filename>" — not held in this project
- **Not captured:** header chain, formatting, the thread quoted below the reply

---

<the email body, verbatim>
```

Name it `YYYY-MM-DD_<party>_<subject-slug>.md`, dated the day the email was
sent, and it is frozen from that point like everything else in the zone.
**Transcribed by**, **Attachments named** and **Not captured** are the lines
that carry the weight; keep those three.

**R4 — The exchange log.** `02_exchange/LOG.md` carries one row per document in
or out, in date order, with its direction, party and thread. It is the index of
the conversation, the way `INDEX.md` is the index of the files. A row is
written at the moment of the event, never reconstructed later — with one
exception: a repository that starts mid-engagement backfills its history once,
and every backfilled row says so in Ref. In an authoring project the exchange
is usually thin — the request in, the submission out, perhaps a comments sheet
and a response — and the log still matters for exactly those rows.

**R5 — Issuing is an explicit step, never a rename.** A document leaves the
project only by being issued, and issuing is something you ask for by name. A
document is issued **from a frozen revision**: if the live draft is ahead of
the last freeze, issuing freezes it first (R11). On that instruction, and not
before, the frozen files are **copied** into `02_exchange/issued/` under the
document number and revision of the project's naming convention, the PDF with
its source document alongside; the exchange LOG gains a row, the revision LOG
an `issued` row that names both the internal revision and the external label,
the WORKLOG a dated entry, the document md its revision state; and the index is
regenerated. Before any of that, the contamination check of R12 runs.

The live draft **stays** in `04_working/drafts/` — it is the base of the next
revision, and R6 keeps it singular. The frozen revision is the record of what
was sent; the live draft never was.

You decide *when*. The mechanics are not yours to remember. What this replaces
— quietly renaming a draft — leaves the project unable to say what was sent, to
whom, or under what cover.

**R6 — Working is mutable and singular; the draft on disk is the truth.**
`04_working/drafts/<slug>/` holds one live draft per deliverable, revised in
place — the document and whatever travels with it, appendices, a figures
workbook. Do not generate a new draft file per revision. **Its history is
`03_revisions/`**, frozen by you at the moments you choose (R11); **its
reasoning is the WORKLOG**; the sync client's version history is the safety
net, not the record.

A session **reads the draft before it writes it**, every time. It does not
regenerate the draft from what it remembers or from the document md; it does
not keep a parallel master — no markdown twin that the `.docx` is rendered
from — because the moment you edit the `.docx` by hand the twin is stale and
the project has two truths. Passages the document md's outline marks
**locked** or **user-edited** are not rewritten without an instruction that
names them. Nothing in `04_working/` is authoritative and nothing there is
evidence.

**The draft folder holds the document and its true companions, nothing
else.** Photos and figures live in `01_basis/reference/` or
`04_working/analysis/<slug>/` and are embedded; anything loose in
`drafts/<slug>/` is copied by every freeze.

**Text the project reuses across documents is written once, in
`04_working/library/`.** The project description, the site, the parties, the
emergency arrangements, the standard method paragraphs — on a project of ten
method statements these are written for the first and needed by the other
nine, and copying from the last document is how they drift. The library is
mutable and project-specific: one file per block, created on demand; a draft
takes a copy; the library is updated only on instruction. It is not a twin of
any draft, and a draft's copy may lawfully diverge from it.

**R7 — Index, manifest and the session-start scan.** `INDEX.md` lists every
file with a one-line description; `MANIFEST.json` records path, size, mtime and
sha256. Both are regenerated by `05_tools/update_index.py` after any file
operation, and hand-written descriptions in `INDEX.md` survive regeneration.

Every session diffs the repository against the manifest before other work. The
severity of a result depends on where it is:

- **NEW** anywhere → ingest it per R3, or ask.
- **CHANGED or MISSING in `01_basis/`, `02_exchange/` or `03_revisions/`** →
  stop and raise it. Something frozen moved: either a rule was broken or the
  sync client did something. Not for a session to resolve. The two `LOG.md`
  files are exempt when they change — appending is the ordinary case — and not
  when they go missing.
- **CHANGED in `04_working/drafts/`** → the draft was edited since the last
  index, which means outside a session: in practice, you, by hand. Not a stop,
  not routine. **Read it, run `draft_diff.py` against the last frozen
  revision, report what changed, record it** in the WORKLOG and the outline's
  status column — then, and only then, edit.
- **CHANGED elsewhere in `04_working/`** → normal. That is analysis being
  worked on.
- **`_inbox/` not empty** → say how many files are waiting and file them
  (R3). Do not read figures out of them in the meantime.
- **MISSING DIR** → a directory of the schema is gone. Recreate it, empty, and
  say so; anything it held is listed as MISSING and is the real event.

The scan **rolls media up**. A folder holding ten or more photos, drawings,
archives or videos is one line in `INDEX.md` — `photos/walk-01/ — 142 media
files (.jpg ×142) — your description` — and one line in a `--diff` section,
with the count; the manifest still records every file, and Office documents
and PDFs are never rolled up, since each of those is something a session opens
and cites. Write the folder's one-line description on that line; it survives
regeneration like any other. The inbox rolls up too: sixty photos waiting
there are one line saying sixty photos are waiting, which is what you need to
know before a session files them.

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
  and leave `~$` owner files behind; a locked file cannot be rewritten. In this
  template that is the live draft, most days.
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
  zone. In a received document, and in a return, the markup *is* the content.
- **Edit the live draft in place, as a package.** It is a `.docx` instantiated
  from the shell: use the shell's styles, preserve its headers, footers,
  numbering and fields, never round-trip it through a converter, never rebuild
  it from scratch unless asked. Comments found in the live draft are
  feedback: register them as F-ids in the document md first, act, and only
  then may a resolved comment be removed — the live draft is mutable, so that
  is allowed where it never is in a frozen zone.
- **Keep the text layer current.** `05_tools/extract_text.py` mirrors the
  frozen zones into `04_working/_extracted/`, so the project is greppable. Run
  it after every ingestion, every freeze and every issue. Files that are
  already text are deliberately not mirrored; a search covers `_extracted/`
  **and** the frozen zones, or it misses them. The live draft is not mirrored
  either — a stale copy of it would be read instead of it; `draft_diff.py`
  reads the draft directly.
- **The text layer is an index, not a substitute.** Use it to find things, then
  open the source. Any figure, date or quotation entering the draft is read
  from the file in the frozen zone, not from the extraction.
- **Record document condition in the context md** (R2): text layer or scan,
  tracked changes, comments, protection. A return that is a scan of hand
  annotations needs OCR and says so.
- **Rights-managed files cannot be read** by any tool. Record it and ask for a
  decrypted copy in `04_working/`; do not work around it.
- **Issue PDFs, keep sources.** The issued artefact is normally the PDF; its
  source document is filed beside it at the same revision.

**R11 — Revisions are frozen by an explicit step, and are the record.** This
is the internal mirror of R5. Freezing a revision is something you ask for by
name — "freeze this as R03", "checkpoint before I edit", "send R03 to JD" — and
something a session **offers**, without being asked, at the moments that
warrant it: before you edit the draft by hand, before anyone else sees it, at a
milestone, before issue. It never freezes on its own initiative; the sequence
is yours.

On that instruction the live draft folder is copied into
`03_revisions/<slug>/Rnn/` — the source always, a PDF whenever the revision
leaves your hands — under the name `<slug>_Rnn.<ext>`; a row is appended to
`03_revisions/LOG.md` with what changed against the previous revision and which
feedback it addresses (`draft_diff.py` writes the raw material for both); the
WORKLOG gets a dated entry; the document md its revision state; the text layer
and the index are regenerated. The live draft is untouched: a freeze is a copy,
not a move.

Anything that comes back on a revision — a colleague's marked-up copy, your own
annotated print, a review note — is filed in `Rnn/returns/` as a received
document would be: unchanged, with a `return` row in the revision LOG naming
who it came from, extracted, and its comments turned into feedback-register
items with their author. Rolling the draft back to Rnn is a freeze of the
current state, a copy of Rnn's source over the live draft, and a `restored`
row.

`R01, R02, …` is the project's own sequence — never reused, never the client's
label. The external revision ("Rev A", "P02") belongs to the exchange LOG, and
the `issued` row is where the two are written down against each other.

**R12 — Form is borrowed, content is not.** The draft is instantiated by
**copying** the shell from `01_basis/templates/`; the shell itself is never
edited. A sample from another project is stripped to its skeleton at
instantiation — headings, boilerplate that is genuinely standard, nothing
else — and what was kept is recorded in the document md. Nothing from an
example's content enters the draft: structure, tone, depth and layout only.

The context md of every example and sample lists the **terms to check for** —
the source project's proper nouns, figures, references, client names. **Before
a revision leaves your hands, and always before issue, the draft is grepped
for them.** With the examples extracted into the text layer that is one
command, and it is the difference between a confidential figure from another
client's proposal appearing in this one and not. It is cheap to prevent and
impossible to recall.

## Decision log

Dated decisions, corrections and open items are recorded in
`00_AI_context/WORKLOG.md` — one dated entry per decision, never rewritten
retroactively. In this template every session that changes the draft ends with
an entry naming the sections touched and the feedback items addressed: that is
the reasoning R6 refers to, and it is what the next session reads first.

---

Instantiated from the `cowork-author` template **v{{TEMPLATE_VERSION}}**
(<https://github.com/mladenpr/cowork_templates>) on {{DATE}}.

A project is a copy, not a link — nothing propagates from the template by
itself. Upgrades are an explicit step: the toolbox's `upgrade_project.py`
brings the scaffolding up to date, adds a dated line below this footer, and
keeps the machine-readable record in `00_AI_context/TEMPLATE.json`. This
footer is how you tell, months later, which rules and which tooling this
project actually has.
