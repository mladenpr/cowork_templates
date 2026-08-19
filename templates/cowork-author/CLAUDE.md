# CLAUDE.md — session bootstrap (read this first, every session)

Project: **{{PROJECT_NAME}}**{{CLIENT_SUFFIX}}

This repository follows a fixed schema and a set of working rules. Its centre
is the documents of one real project, written from the ground up across many
sessions by you and the user together — several of them, each under its own
slug, in this one folder. Before doing any work in this project:

1. Read `00_AI_context/PROJECT.md` — the brief, who the document is for, the
   deliverables table, and the conventions.
2. Read `README.md` — the schema and the working rules (R1–R12). The rules are
   binding; do not improvise around them.
3. Run the session-start scan: `python3 05_tools/update_index.py --diff`
   (`py -3` on Windows), and read the result by zone:
   - **NEW in `01_basis/`, `02_exchange/` or `03_revisions/`** → ingest it
     (procedure below), or ask where it belongs. NEW in `04_working/` or
     `00_AI_context/` is a draft, an extraction or a context file being
     written — expected.
   - **CHANGED or MISSING in `01_basis/`, `02_exchange/` or `03_revisions/`**
     → stop and raise it with the user. Something frozen moved. The two
     `LOG.md` files are exempt when they change — appending is routine — and
     not when they go missing.
   - **`DRAFT EDITED`** → the live draft changed since the last index, which
     means outside a session: the user edited it by hand. **Before anything
     else, run `python3 05_tools/draft_diff.py <slug>`**, read the draft,
     report what changed, and record it (procedure below). Do not undo it.
   - **CHANGED elsewhere in `04_working/` or `00_AI_context/`** → expected.
     Do not raise it. (`06_temp/` is not scanned at all.)
   - **`_inbox/` not empty** → say how many files are waiting and file them
     (procedure below). Do not read figures out of them in the meantime.
   - **A folder line with a count** (`photos/walk-01/ — 142 media files …`)
     → the scan rolled a media folder up. Treat the folder as the unit; the
     manifest still holds every file.
   - **`MISSING DIR`** → recreate it, empty, and say so. It held nothing; if
     it did, those files are listed as MISSING and that is the real event.
   - **`CONFLICT?` or `BAD NAME`** → report and do not touch the file.
4. Read the document md of every deliverable in play —
   `00_AI_context/documents/<slug>.md` — **before opening any draft.** It holds
   the outline and each section's status, the decisions in force, the open
   feedback, and where the revisions stand. Then `03_revisions/LOG.md` for the
   last freeze and anything that came back on it.
5. Read `02_exchange/LOG.md` — the state of the conversation, and what is
   outstanding — and `00_AI_context/WORKLOG.md` for the latest decisions, in
   particular the last session's entry on the draft.
6. Consult `00_AI_context/INDEX.md` before searching the tree. To search
   *inside* documents, grep `04_working/_extracted/` **and** the frozen zones
   themselves — a file that is already text is not mirrored into the
   extraction and would otherwise be missed. Then open the source in the
   frozen zone to read anything you intend to rely on (R10). The live draft is
   not in the extraction: open it.

## Invariants

- **`01_basis/`, `02_exchange/` and `03_revisions/` are frozen.** Never edit,
  rename, convert, re-save or "fix" a file in any of them. That includes a
  frozen revision of the draft and anything that came back on it — the markup
  is the content.
- **Direction is provenance; role is a lookup.** `received/` is theirs,
  `issued/` is ours; a copy of our own document returned to us marked up is
  *received*. In `01_basis/`, `reference/` is to be correct against,
  `examples/` is to imitate in form only, `templates/` is the shell the draft
  is copied from — never edited, never quoted.
- **The exchange is the conversation about the documents, not the project's
  whole paper trail.** Requests, comments sheets, approvals, submissions go in
  `02_exchange/`. Drawings, specifications, photos, standards are
  `01_basis/reference/` whoever sent them (R1).
- **Sub-folders are made on demand, by subject, never by document.** Do not
  create folders for subjects that have not arrived. When a set arrives or a
  subject accumulates, create one folder named for it and file into it; which
  documents use the material is recorded in the mds, not in the tree.
- **`_inbox/` is not a zone.** It is where the user drops things. Nothing in it
  is quoted, extracted or relied on; every scan counts it until it is empty. A
  batch dropped as a folder is filed as one set.
- **The draft on disk is the truth.** Read it before you write it. Never
  regenerate it from memory or from the document md; never keep a markdown
  master beside it. One live draft per deliverable, in
  `04_working/drafts/<slug>/`, revised in place (R6) — the document and its
  true companions only; photos and figures live in basis or analysis and are
  embedded, never left loose beside the draft.
- **Reused project text lives in `04_working/library/`, once.** The project
  description, the site, the parties, the standard method paragraphs: written
  the first time they are needed, saved there as one file per block, taken as a
  copy into each draft. Updated only on instruction. Never copied from the
  last document instead (R6).
- **Locked and user-edited passages are not yours.** The outline in the
  document md says which sections are `locked` or `user-edited`. Do not
  rewrite them without an instruction that names the section.
- **Form is borrowed, content is not (R12).** Nothing from an example's
  content, and nothing left in a sample used as a shell, enters the draft.
- **Never delete anything.** Move it to `_to_delete/` and tell the user (R8).
- **Nothing enters `02_exchange/issued/` except through the issue procedure**,
  or as a transcript of correspondence the user has already sent (R3).
  **Nothing enters `03_revisions/` except through the freeze procedure**, or as
  a return on a frozen revision.
- **`00_AI_context/TEMPLATE.json` is tooling-maintained.** Only the template
  toolbox's `new_project.py` and `upgrade_project.py` write it — never edit it.
- After any file operation, regenerate `INDEX.md` and `MANIFEST.json` with
  `05_tools/update_index.py`.

## Procedure: ingest a document that arrived

Triggered whenever a **file** reaches the project from outside — dropped into
`_inbox/`, uploaded into the chat, an email attachment, found by the scan
anywhere it should not be. Text pasted into the chat window is not a file and
is not ingested (see below). A batch is ingested as a batch: fifty photos from
one walk are one decision, one folder, one md.

1. Decide the zone, then the role, and ask if it is not obvious:
   `02_exchange/received/` if it is the conversation about the documents — the
   request or instruction for one, the client's comments sheet on one;
   `01_basis/reference/` if it is material the documents are written from —
   drawings, specifications, photos, standards, data — whoever sent it;
   `01_basis/examples/` if it shows what good looks like;
   `01_basis/templates/` if it is a shell to write in.
2. Inside `reference/`, decide the subject folder: an existing one if the
   subject has one, a new one named for the subject if a set is arriving or a
   subject is accumulating (`drawings/`, `spec/`,
   `photos/2026-08-12_north-quay/`), the zone root while it is one file. By
   subject, never by deliverable. Inside `received/` and `issued/`, by slug
   once a document has more than a file or two there.
3. Move the files in unchanged. Do not rename, do not convert, do not "tidy"
   filenames — R1. If a name is useless, that is what the context md is for.
4. Write or extend the context md in `00_AI_context/datasets/`. A set of media
   is one dataset with one md: what the set shows, when and where, which
   documents draw on it. For an example or a template, fill in what to take
   from it, what not to take, and the **terms to check for** — the source
   project's names, figures and references (R12). For a series or a thread,
   add a member-table row instead of a new md.
5. Append a row to `02_exchange/LOG.md` for anything filed under `received/`.
6. If it is the request, scope or comments sheet a document answers to, add its
   items to the **requirements coverage** table of that document md, one row
   each, status `open`.
7. Run `05_tools/extract_text.py`, then `05_tools/update_index.py`. Write the
   one-line description of any rolled-up media folder on its INDEX line.
8. Report what was filed, and anything the extraction flagged — a scan needing
   OCR, a rights-managed file, tracked changes — since those belong in the
   context md. If `_inbox/` is not empty afterwards, say what is still in it
   and why.

## Email text pasted into the session

The user quotes email text into the chat window to have it read, checked
against the project, or answered. That is working material, not project
material. Use it; do not file it, and do not write a *fact* it states into
`WORKLOG.md`, `PROJECT.md` or a context md while a chat message is its only
source. If a paste changes what the project believes, say so and ask whether
it should be recorded. What belongs in the record is the user's judgement, and
they write the file — a markdown transcript headed as in `README.md` (R3),
dropped into `02_exchange/received/` or `issued/` — which the next scan sees
as NEW and you ingest without asking.

**The user's instructions about the document are not pastes.** "Shorten
section 3", "call it the jetty, not the pier" are decisions with a source —
the user, today — and go into the feedback register at once (procedure below).

## Procedure: instantiate a draft

Triggered by the user asking for the document to be started, once the shell is
in `01_basis/templates/`.

1. Agree the slug — short, lower-case, hyphenated, stable: it names the
   document md, the draft folder and the revision folder for the life of the
   project.
2. Copy the shell into `04_working/drafts/<slug>/`. If the shell is a sample
   from another project, strip it to its skeleton — headings, boilerplate that
   is genuinely standard, nothing else — and list what was kept.
3. Create `00_AI_context/documents/<slug>.md` from `documents/_TEMPLATE.md`:
   identity and brief, form (which shell, which examples, what was stripped),
   the outline as agreed with every section `planned`, the requirements
   coverage table seeded from the reference and the received request, decisions
   in force as the user has stated them so far.
4. Add the deliverable to the table in `PROJECT.md`; WORKLOG entry; reindex.

## Procedure: record feedback

Feedback is recorded **the moment it is given**, not when it is acted on. Each
item gets an `F-id` in the document md's feedback register with its date,
source, text and status `open`. Sources:

- **The user, in session** — source `user, session <date>`. An instruction
  that changes the approach (structure, tone, scope) also gets a WORKLOG line
  and, if it is a standing rule, a line under *Decisions in force*.
- **A return on a frozen revision** — file it in `03_revisions/<slug>/Rnn/returns/`
  unchanged, `return` row in `03_revisions/LOG.md` naming who it came from,
  extract it, then one F-id per comment or tracked change, with the author,
  source `return <path>, comment n`.
- **A client comments sheet** — a received document (R3); one F-id per item,
  source `CRS #n`, and the item also goes into the requirements coverage table.
- **Comments in the live draft** — the user commented in Word. One F-id per
  comment with the author; act; a resolved comment may then be removed from
  the live draft, since it is mutable — never from a frozen file.

A rejected item stays in the register with `rejected — why`. A register with
gaps is the point; a register that is edited clean is worthless.

## Procedure: revise the draft

The daily procedure. Triggered by the user asking for changes, or by open
feedback.

1. Read the document md, then the draft. If the scan said `DRAFT EDITED`, run
   `draft_diff.py <slug>` first and record what the user changed by hand: a
   WORKLOG line naming the sections, and `user-edited` in the outline's status
   column for each. Those passages are now theirs.
2. Make the changes asked for, in the live draft, in place, in the shell's
   styles (R10). Not in a locked section; not in a user-edited passage unless
   the instruction names it. Every figure, date and quotation comes from a file
   in a frozen zone, read in the source. Text that other documents on this
   project will also need — the project description, the site, standard
   method paragraphs — comes from `04_working/library/` if it is there, and is
   saved there, one file per block, the first time it is written; photos are
   embedded from `01_basis/reference/`, figures from
   `04_working/analysis/<slug>/`.
3. Update the outline's status column and the feedback register's status
   column as you go — `addressed in <live>` until a freeze assigns the Rnn.
4. At the end of the session, one WORKLOG entry: sections touched, F-ids
   addressed, what was decided, what is next. Then reindex.

If the user says they are about to edit by hand, **offer to freeze a revision
first** (R11) — it is what makes their edits diffable afterwards.

## Procedure: freeze a revision

Triggered **only** by the user saying so — "freeze this as R03", "checkpoint
it", "this goes to JD for review", "I'm going to edit it now" — or by the
user accepting your offer at one of the moments R11 names. Never on your own
initiative.

1. Confirm the slug and the next number: the revision LOG says the last one;
   numbers are never reused.
2. Run `draft_diff.py <slug>` against the last frozen revision; that is the
   "what changed" column, in a sentence, and the list of F-ids it closes.
3. Copy the live draft folder into `03_revisions/<slug>/Rnn/`, naming the
   document `<slug>_Rnn.<ext>`. Add a PDF if the revision is going to a
   reviewer or out — ask the user to produce it if you cannot render faithfully.
4. Append a `frozen` row to `03_revisions/LOG.md`: date, document, Rnn,
   purpose, what changed, F-ids, path, status `current`; mark the previous
   revision `superseded by Rnn`.
5. Set each addressed F-id to `addressed in Rnn`; update the document md's
   revision state; WORKLOG entry.
6. Run `05_tools/extract_text.py`, then `05_tools/update_index.py`. Report.

Rolling back to Rnn: freeze the current state first (nothing is lost), copy
Rnn's source over the live draft, `restored` row, WORKLOG.

## Procedure: issue a document

Triggered **only** by the user saying so — "issue this", "this is final",
"submit as Rev A". Never inferred from a file looking finished.

Ask for whatever is missing: document number, external revision label,
recipient, transmittal reference, issue date.

1. **Contamination check (R12):** grep the live draft's text (`draft_diff.py`
   output, or `extract_text.extract_file`) for every term listed under *terms
   to check for* in the context mds of `01_basis/examples/` and
   `01_basis/templates/`. A hit stops the issue until the user rules on it.
2. If the live draft is ahead of the last frozen revision, freeze it (above).
3. Copy the frozen revision's PDF and source into `02_exchange/issued/` under
   the naming convention in `PROJECT.md`.
4. Append a row to `02_exchange/LOG.md`: date, `out`, party, thread, document
   number, external revision, transmittal, status `current`; mark the previous
   issued revision `superseded`. Append an `issued` row to
   `03_revisions/LOG.md` naming Rnn and the external label together.
5. Requirements coverage: every row should be closed or consciously `n/a`; an
   open row is reported before the issue goes ahead.
6. WORKLOG entry; document md revision state; extract; reindex. Report.

The live draft stays where it is (R5). The user decides when a document is
finished; everything after that decision is clerical, and clerical work is
what gets skipped at six o'clock on a Friday — so it is yours, in full.

## Environment notes

- **This session runs locally, on the user's machine.** The project folder is a
  real path with ordinary filesystem access and a real shell.
- **The folder is inside a synced cloud drive.** Reading a cloud-only
  placeholder triggers a download rather than an error — it works, slowly, and
  not at all offline. If the scan crawls, ask the user to pin the folder (R9).
- **The live draft is open in Word more often than not.** If a write fails or a
  `~$name.docx` sits beside the file, the user has it open. Ask them to close
  it; do not write to a different name to get around the lock.
- **Python invocation differs by platform**: `python3` on macOS and Linux,
  `py -3` on Windows. PDF extraction needs `pypdf`; Word, Excel and PowerPoint
  need nothing beyond the standard library.
- **Rendering a PDF of the draft** needs Word or an equivalent; a converter
  that loses the shell's styling is worse than asking the user to export it.
- **Rights-managed documents cannot be opened** by any tool (R10). Report and
  ask; do not attempt to defeat it.

### The Microsoft 365 connector is a secondary path

If a connector to Microsoft 365 / SharePoint is available, use it only to fetch
inputs that are not on disk, then ingest what you fetched through the normal
procedure above, on disk. Do not work on the project through it: the scan
cannot run over it, so nothing notices what changed, and it can delete, move
and overwrite, which R8 forbids by any route.

## Working style

- Traceability over speed: every figure in the draft resolves to a file in a
  frozen zone or a script in `05_tools/`.
- When a working file and a frozen one disagree, the frozen one wins — and the
  conflict is recorded in the dataset's context md, not silently resolved.
- Decisions get a dated WORKLOG entry the moment they are made, including the
  ones the user rules on verbally; instructions about the document get an
  F-id the moment they are given.
- When the user asks for a change to the draft, change the draft. Do not
  produce a new version alongside it (R6).
- Offer a freeze at the moments R11 names; never perform one unasked.
