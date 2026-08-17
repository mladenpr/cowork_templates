# CLAUDE.md — session bootstrap (read this first, every session)

Project: **{{PROJECT_NAME}}**{{CLIENT_SUFFIX}}

This repository follows a fixed schema and a set of working rules. Before doing
any work in this project:

1. Read `00_AI_context/PROJECT.md` — what this project is and who it is for.
2. Read `README.md` — the schema and the working rules (R1–R11). The rules are
   binding; do not improvise around them.
3. Run the session-start scan: `python3 05_tools/update_index.py --diff`
   (`py -3` on Windows), and read the result by zone:
   - **NEW in `01_contract/`, `02_basis/` or `03_exchange/`** → ingest it
     (procedure below), or ask where it belongs. NEW in `04_working/` or
     `00_AI_context/` is a draft, an extraction or a context file being
     written — expected.
   - **CHANGED or MISSING in `01_contract/`, `02_basis/` or `03_exchange/`** →
     stop and raise it with the user. Something frozen moved. The one routine
     exception is already built into the scan: `03_exchange/LOG.jsonl` and
     `LOG.md` change on every ingestion and are listed as plain CHANGED, never
     as an alarm — MISSING is still an alarm for them.
   - **CHANGED in `04_working/` or `00_AI_context/`** → expected. Do not raise
     it. (`06_temp/` is not scanned at all.)
   - **`MISSING DIR`** → recreate it, empty, and say so. It held nothing; if it
     did, those files are listed as MISSING and that is the real event.
   - **`_inbox/` not empty** → say how many files are waiting and offer to file
     them. Do not read figures out of them in the meantime.
   - **`CONFLICT?` or `BAD NAME`** → report and do not touch the file.
4. Check the log, both ways: `python3 05_tools/log.py query --action open` —
   what is owed, in either direction — and `python3 05_tools/log.py check` —
   the log against the tree: files in the exchange that no row mentions, rows
   that point at nothing, actions past their due date. A `check` finding is
   filed, logged or `set` right, as its line says; it is never fixed by editing
   `LOG.jsonl`.
5. Check `00_AI_context/WORKLOG.md` for the latest decisions and open items.
6. Consult `00_AI_context/INDEX.md` before searching the tree, and
   `00_AI_context/PARTIES.md` before deciding who a party is. To search
   *inside* documents, grep `04_working/_extracted/` **and** the frozen zones
   themselves — a file that is already text, such as an email transcript, is
   not mirrored into the extraction and would otherwise be missed. Then open
   the source in the frozen zone to read anything you intend to rely on (R10).

## Invariants

- **`01_contract/`, `02_basis/` and `03_exchange/` are frozen.** Never edit,
  rename, convert, re-save or "fix" a file in any of them. That includes
  documents this project issued — once sent, they cannot be revised, only
  superseded.
- **Direction is provenance.** `received/` is theirs, `issued/` is ours, with
  no exception for any document type. A copy of our own document returned to us
  marked up is *received*. The log agrees with the tree by construction:
  `log.py` refuses a row whose direction or party contradicts the folder the
  file sits in.
- **`01_contract/` is for instruments, not for everything contractual.** The
  executed contract with the documents it incorporates, its amendments, and
  the subcontracts we let. A purchase order, an instruction, a variation, a
  notice — all of those flow *under* a contract and are filed in `03_exchange/`
  by direction (R1). Where a file is filed says nothing about its legal effect;
  it says who sent it and whether it created a contract or acted under one.
- **The project folder is internal.** It holds both sides' contracts, every
  party's correspondence and the internal position. Nothing in it is shared
  with a counterparty; what they receive is a copy that left through
  `03_exchange/issued/` (R5). Do not send, sync, or grant access to the folder
  or any zone of it, and do not carry internal-position material into a draft
  that goes out.
- **Never delete anything.** Move it to `_to_delete/` and tell the user (R8).
  You have real write access on this machine; this rule is what stands in for
  the protection the filesystem does not give.
- **Nothing enters `03_exchange/issued/` except through the issue procedure**,
  or as a transcript of correspondence the user has already sent (R3). The
  second is a record being written down, not a document being released.
- **`04_working/` holds one live draft per deliverable**, revised in place —
  not a new file per revision.
- **Nothing in `_inbox/` is authoritative.** It is unfiled material. Do not
  quote a figure from it, and do not cite it in a draft; file it first.
- After any file operation, regenerate `INDEX.md` and `MANIFEST.json` with
  `05_tools/update_index.py`.

## Procedure: ingest a document that arrived

Triggered whenever a **file** reaches the project from outside — uploaded into
the chat, an email attachment, dropped into the folder or into `_inbox/`, found
by the scan. Text pasted into the chat window is not a file and is not
ingested; see below.

1. Decide the zone, and ask if it is not obvious:
   - `03_exchange/received/<party>/` if it is part of the conversation with
     another party — which is most things, including instructions, variations,
     notices, invoices and drawings issued to us;
   - `02_basis/` if it is reference material the work rests on and nobody sent
     it as part of the conversation;
   - `01_contract/upstream/` or `01_contract/downstream/<party>/` only if it is
     an **executed instrument** — the contract itself, a signed amendment, a
     subcontract we have let — or a document the instrument incorporates: the
     drawings, specification and pricing document it lists as contract
     documents belong with it. A later revision of one of those, sent under the
     contract, is exchange.
2. Use the party's label from `PARTIES.md` as the folder name, and add the
   party there first if it is new.
3. Move the file in unchanged. Do not rename it, do not convert it, do not
   "tidy" the filename — R1. If the name is useless, that is what the context
   md is for.
4. Write or extend its context md in `00_AI_context/datasets/`. If it belongs
   to a series or a negotiation thread, add a member-table row to that thread's
   md rather than creating a new one. If it belongs to a controlled series with
   a register (R11), add its row there too.
5. Log the event — for anything filed into `03_exchange/` or `01_contract/`.
   Basis material has no direction and no party: it gets its context md and its
   INDEX line, not a log row.

   ```bash
   python3 05_tools/log.py add --date <ISO date of the event> --dir in \
       --party "<label>" --type <letter|drawing|instruction|…> \
       --doc "<what it is>" --ref "<their number, or how it arrived>" \
       --rev "<their revision>" --thread <thread> --path <repo-relative path> \
       [--action open --due <date>] [--backfilled]
   ```

   - `--action open` when a reply is owed, and `--due` when the contract or the
     letter says by when.
   - The date is the date **on** the document — the letter's date, the drawing's
     title block, the email's sent line — never the day it was filed, and never
     guessed. If neither the document nor the user states it, ask before
     logging; a row with a guessed date looks like a fact.
   - `--path` must exist and must agree with `--dir` and `--party`; the tool
     refuses a row that contradicts the tree, and refuses a date that is not a
     real calendar date. Nothing is written until the whole row is right.
   - An executed instrument is logged with `--type contract` (or `amendment`),
     usually `--dir in`: an instrument becomes executed when the last signature
     goes on and the fully signed copy comes back to you.
   - A batch off an old drive is **backfill** — rows written from the documents
     after the event. Log each with `--backfilled` so the row says so; the date
     is still the document's own.
6. Run `05_tools/extract_text.py`, then `05_tools/update_index.py`.
7. Report what was filed, and anything the extraction flagged — a scan needing
   OCR, a rights-managed file, tracked changes — since those belong in the
   context md.

## Procedure: clear the inbox

Triggered by the user asking, or offered when the scan reports `_inbox/` is not
empty.

1. List what is there, grouped by what it looks like, and say what you propose
   for each — zone, party, thread. Do not move anything yet. Read the dates off
   the documents themselves while you are at it, and say which files carry
   none.
2. Ask about everything you are not sure of, in one go rather than file by file.
   A batch of forty documents is normal here; forty questions is not.
3. Ingest the ones that are settled by the procedure above, in one pass, with
   `--backfilled` on every row — they are being written after the event.
4. Leave the rest in `_inbox/` and say what is still waiting and why. A file
   that stays unfiled because nobody knows what it is stays visible, and that
   is the point.

## Email text pasted into the session

The user quotes email text into the chat window — under double quotes — to have
it read, checked against the project, or answered. That is working material,
not project material.

- Use it: read it, cross-check it against the frozen zones, draft the reply.
- Do not file it, and do not offer to.
- Do not write anything it says into `WORKLOG.md`, `PROJECT.md`, a register or
  a dataset context md while a chat message is its only source. If a paste
  changes what the project believes, say so and ask whether it should be
  recorded — the answer decides, not the significance of the content.

What belongs in the record is the user's judgement, and they write the file: a
markdown transcript dropped into `03_exchange/received/<party>/`, or
`issued/<party>/` for one they sent. It surfaces as NEW in the next
session-start scan. **Ingest it by the procedure above without asking** —
context md, log row, extraction, index — since the decision it needed has
already been made. Read the header the file carries rather than re-deriving
direction and party from its contents; if the header and the folder disagree,
the folder is the fact (R1) — raise the disagreement, do not resolve it.

In the log, such a row records `email (transcript)` in `--ref`. A transcribed
email the user sent takes `--dir out` with no document number and no revision;
it is correspondence, not an issued deliverable.

If the user asks *you* to write the transcript, follow the header block in
`README.md` (R3) and ask for whatever the paste does not state — the sent date,
the recipients, the attachments it mentions. Never infer the date: a log row
with a guessed date is worse than no row, because it looks like a fact.

## Procedure: issue a document

Triggered **only** by the user saying so — "issue this", "this is final", "send
this as Rev C". Never inferred from a file looking finished, and never from a
filename containing a date.

Ask for whatever is missing: document number, revision, recipient, transmittal
reference, the issue date — and the PDF. The user exports it; the tools here do
not render documents.

1. Confirm which draft in `04_working/drafts/` is being issued, by path.
2. Move it into `03_exchange/issued/<party>/` under the project's naming
   convention (see `PROJECT.md`). File the issued PDF and its source document
   together at the same revision, under the same stem — R10. The PDF is what
   was sent, so the PDF is what the log row points at.
3. Log it, superseding the previous revision — and closing what it answers —
   in the same command:

   ```bash
   python3 05_tools/log.py add --date <issue date> --dir out --party "<label>" \
       --type <letter|report|boq|po|…> --doc "<document>" --rev <rev> \
       --ref "<transmittal>" --thread <thread> --path <path to the PDF> \
       [--supersedes <id of the previous revision>] [--answers <id it replies to>] \
       [--action open --due <date>]
   ```

   `--action open` if the document itself asks for something back. The
   superseded row and the superseded file both stay where they are. They are
   evidence.
4. Add a dated `WORKLOG.md` entry recording what was issued and why.
5. Update the thread's context md in `00_AI_context/datasets/` with the new
   member row, and the register (R11) if the document belongs to a controlled
   series.
6. Run `05_tools/extract_text.py`, then `05_tools/update_index.py`.
7. Report what moved and what the log now says.

The user decides when a document is finished. Everything after that decision is
clerical, and clerical work is what gets skipped at six o'clock on a Friday —
so it is yours, in full, in one step.

## Working with the log

`03_exchange/LOG.jsonl` is the record; `LOG.md` is a rendered view of it. Add
rows with `log.py add` — never by typing into the markdown, which is
regenerated and will lose the edit.

A row has two states, because they answer two questions. `status` is the
document's: `current`, `superseded by #n`, `withdrawn`. `action` is what is
owed on it: `open`, `answered by #n`, `closed`, or nothing. On an `in` row
`open` means we owe the reply; on an `out` row, they do.

```bash
python3 05_tools/log.py query --action open              # what is owed, either way
python3 05_tools/log.py query --overdue                  # open and past --due
python3 05_tools/log.py query --party "ACME" --dir out   # everything we sent them
python3 05_tools/log.py query --thread delay-claim --paths
python3 05_tools/log.py query --since 2026-01-01 --json  # for further processing
python3 05_tools/log.py set 41 --action "answered by #58"
python3 05_tools/log.py set 41 --note "reply covered items 1–3 only"
python3 05_tools/log.py check                            # gaps, drift, dangling refs
```

`set` changes `status`, `action`, `due` and `note` (appended), and fills the
path of a row logged `--pending` before its file landed. Nothing else on a row
is ever rewritten — a row filed against the wrong file or the wrong party is
corrected by a new row with a note — and every change `set` makes is kept in
the row's `history`. Read `LOG.jsonl` directly when a question needs more than
the filters give; it is one JSON object per line and it is meant to be read by
an agent. What it must not be is *edited* by one.

## Registers

A controlled series with a status — variations, RFIs, purchase orders, payment
applications — has an md in `00_AI_context/registers/` (R11). Keep it current
as part of ingesting or issuing anything that belongs to it, and cite the log
id in the row rather than restating what the log holds.

The value of a register is in its gaps: an RFI with no answer, a variation
instructed and never valued, an application with no certificate against it.
When you update one, say what the gaps now are. Do not create a register
unasked — propose it when a series is large enough to need one.

## Environment notes

- **This session runs locally, on the user's machine.** The project folder is a
  real path with ordinary filesystem access and a real shell. There is no
  upload step and no snapshot to go stale.
- **The folder is inside a synced cloud drive.** Reading a cloud-only
  placeholder triggers a download rather than an error — it works, slowly, and
  not at all offline. If the scan crawls, ask the user to pin the folder (R9).
- **Documents open in Word or Excel are locked.** If a write fails or a
  `~$name.docx` sits beside the file, the user has it open. Ask them to close
  it; do not write to a different name to get around the lock.
- **Python invocation differs by platform**: `python3` on macOS and Linux,
  `py -3` on Windows. PDF extraction needs `pypdf`; Word, Excel and PowerPoint
  need nothing beyond the standard library. A PDF seen while `pypdf` was
  missing is retried on every run until it is read — the gap stays visible.
- **Rights-managed documents cannot be opened** by any tool (R10). Report and
  ask; do not attempt to defeat it.

### The Microsoft 365 connector is a secondary path

If a connector to Microsoft 365 / SharePoint is available, use it only to fetch
inputs that are not on disk — an attachment in Outlook, a file in Teams, a
document in an unsynced SharePoint library. Then ingest what you fetched
through the normal procedure above, on disk.

Do not work on the project through it. It reaches the same files with none of
this repository's machinery: the scan cannot run over it, so nothing notices
what changed, and it can delete, move and overwrite, which R8 forbids by any
route.

## Working style

- Traceability over speed: every figure in a document resolves to a file in a
  frozen zone or a script in `05_tools/`.
- When a working file and a frozen one disagree, the frozen one wins — and the
  conflict is recorded in the dataset's context md, not silently resolved.
- When the contract and anything else disagree, the contract wins. When the
  contract's own documents disagree with each other, its order-of-precedence
  clause decides — `PROJECT.md` says where it is. Cite the clause by number
  either way, and where the contract is silent, say so rather than assume.
- Decisions get a dated WORKLOG entry the moment they are made, including the
  ones the user rules on verbally.
- When the user asks for a change to a draft, change the draft. Do not produce
  a new version alongside it (R6).
