# CLAUDE.md — session bootstrap (read this first, every session)

Project: **{{PROJECT_NAME}}**{{CLIENT_SUFFIX}}

This repository follows a fixed schema and a set of working rules. Before doing
any work in this project:

1. Read `00_AI_context/PROJECT.md` — what this project is and who it is for.
2. Read `README.md` — the schema and the working rules (R1–R10). The rules are
   binding; do not improvise around them.
3. Run the session-start scan: `python3 04_tools/update_index.py --diff`
   (`py -3` on Windows), and read the result by zone:
   - **NEW** → ingest it (procedure below), or ask where it belongs.
   - **CHANGED or MISSING in `01_basis/` or `02_exchange/`** → stop and raise
     it with the user. Something frozen moved.
   - **CHANGED in `03_working/`** → expected. Do not raise it.
   - **`CONFLICT?` or `BAD NAME`** → report and do not touch the file.
4. Read `02_exchange/LOG.md` — the state of the conversation, and what is
   outstanding.
5. Check `00_AI_context/WORKLOG.md` for the latest decisions and open items.
6. Consult `00_AI_context/INDEX.md` before searching the tree. To search
   *inside* documents, grep `03_working/_extracted/`; then open the source in
   the frozen zone to read anything you intend to rely on (R10).

## Invariants

- **`01_basis/` and `02_exchange/` are frozen.** Never edit, rename, convert,
  re-save or "fix" a file in either. That includes documents this project
  issued — once sent, they cannot be revised, only superseded.
- **Direction is provenance.** `received/` is theirs, `issued/` is ours. A copy
  of our own document returned to us marked up is *received*.
- **Never delete anything.** Move it to `_to_delete/` and tell the user (R8).
  You have real write access on this machine; this rule is what stands in for
  the protection the filesystem does not give.
- **Nothing enters `02_exchange/issued/` except through the issue procedure.**
- **`03_working/` holds one live draft per deliverable**, revised in place —
  not a new file per revision.
- After any file operation, regenerate `INDEX.md` and `MANIFEST.json` with
  `04_tools/update_index.py`.

## Procedure: ingest a document that arrived

Triggered whenever anything reaches the project from outside — chat upload,
email attachment, a file the user dropped in, a scan the session found.

1. Decide the zone, and ask if it is not obvious: `02_exchange/received/` if it
   is part of the conversation with another party, `01_basis/` if it is
   reference material the work rests on.
2. Move the file in unchanged. Do not rename it, do not convert it, do not
   "tidy" the filename — R1. If the name is useless, that is what the context
   md is for.
3. Write or extend its context md in `00_AI_context/datasets/`. If it belongs
   to a series or a negotiation thread, add a member-table row to that thread's
   md rather than creating a new one.
4. Append a row to `02_exchange/LOG.md` for anything filed under `received/`:
   date, direction `in`, party, thread, document, revision, path.
5. Run `04_tools/extract_text.py`, then `04_tools/update_index.py`.
6. Report what was filed, and anything the extraction flagged — a scan needing
   OCR, a rights-managed file, tracked changes — since those belong in the
   context md.

## Procedure: issue a document

Triggered **only** by the user saying so — "issue this", "this is final", "send
this as Rev C". Never inferred from a file looking finished, and never from a
filename containing a date.

Ask for whatever is missing: document number, revision, recipient, transmittal
reference, and the issue date.

1. Confirm which draft in `03_working/drafts/` is being issued, by path.
2. Move it into `02_exchange/issued/` under the project's naming convention
   (see `PROJECT.md`). File the issued PDF and its source document together at
   the same revision — R10.
3. Append a row to `02_exchange/LOG.md`: date, direction `out`, party, thread,
   document number, revision, transmittal, status `current`. Mark the previous
   revision of the same document `superseded by Rev n` — the superseded row and
   the superseded file both stay where they are. They are evidence.
4. Add a dated `WORKLOG.md` entry recording what was issued and why.
5. Update the thread's context md in `00_AI_context/datasets/` with the new
   member row.
6. Run `04_tools/extract_text.py`, then `04_tools/update_index.py`.
7. Report what moved and what the LOG now says.

The user decides when a document is finished. Everything after that decision is
clerical, and clerical work is what gets skipped at six o'clock on a Friday —
so it is yours, in full, in one step.

## Environment notes

- **This session runs locally, on the user's machine.** The project folder is a
  real path with ordinary filesystem access and a real shell. There is no
  staging step and no snapshot to go stale.
- **The folder is inside a synced cloud drive.** Reading a cloud-only
  placeholder triggers a download rather than an error — it works, slowly, and
  not at all offline. If the scan crawls, ask the user to pin the folder (R9).
- **Documents open in Word or Excel are locked.** If a write fails or a
  `~$name.docx` sits beside the file, the user has it open. Ask them to close
  it; do not write to a different name to get around the lock.
- **Python invocation differs by platform**: `python3` on macOS and Linux,
  `py -3` on Windows. PDF extraction needs `pypdf`; Word, Excel and PowerPoint
  need nothing beyond the standard library.
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
  frozen zone or a script in `04_tools/`.
- When a working file and a frozen one disagree, the frozen one wins — and the
  conflict is recorded in the dataset's context md, not silently resolved.
- Decisions get a dated WORKLOG entry the moment they are made, including the
  ones the user rules on verbally.
- When the user asks for a change to a draft, change the draft. Do not produce
  a new version alongside it (R6).
