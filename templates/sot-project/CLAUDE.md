# CLAUDE.md — session bootstrap (read this first, every session)

Project: **{{PROJECT_NAME}}**{{CLIENT_SUFFIX}}

This repository follows a fixed schema and a set of working rules. Before doing
any work in this project:

1. Read `00_AI_context/PROJECT.md` — what this project is and who it is for.
2. Read `README.md` — the repository schema and the working rules (R1–R10).
   The rules are binding; do not improvise around them.
3. Run the session-start scan: `python3 04_tools/update_index.py --diff`
   (`py -3` on Windows).
   - Any NEW raw input file → move it into `01_SoT/`, write/extend its context
     md under `00_AI_context/sot/`, run `04_tools/extract_text.py`, then
     regenerate INDEX and MANIFEST.
   - Any changed or missing file → flag it to the user before proceeding.
   - Any file the scan marks `CONFLICT?` or `BAD NAME` → report it and stop
     touching it. A sync-conflict copy is never ingested on the session's own
     judgement.
4. Check `00_AI_context/WORKLOG.md` for the latest decisions and open items.
5. Consult `00_AI_context/INDEX.md` before searching the tree — every file is
   listed there with a one-line description. To search *inside* the documents,
   grep `02_derivatives/_extracted/`, not the binaries.

Key invariants (full text in README.md):

- `01_SoT/` is **immutable**. Never edit, rename, convert, re-save or "fix" a
  raw input in place. Corrections are new files in `02_derivatives/`, with the
  transformation documented in the dataset's context md.
- **Never delete anything.** Move it to `_to_delete/` and tell the user (R8).
  You have real write access on this machine — this rule is what stands in for
  the protection the filesystem does not give.
- Regenerable outputs go to `02_derivatives/`; issued controlled documents go
  to `03_deliverables/` and into its `REGISTER.md`; kept scripts to
  `04_tools/`; scratch to `05_temp/`.
- After any file operation, regenerate `INDEX.md` and `MANIFEST.json` with
  `04_tools/update_index.py`.

## Environment notes

These are mechanics, not rules — they save a session from re-learning them.

- **This session runs locally, on the user's machine.** The project folder is a
  real path with ordinary filesystem access and a real shell. There is no
  staging step and no snapshot to go stale: what you read is what is on disk.
- **The folder is inside a synced cloud drive.** Reading a cloud-only
  placeholder triggers a download rather than an error, so it works — slowly,
  and not at all when the machine is offline. If the scan crawls, that is why;
  ask the user to pin the folder (R9) rather than working around it.
- **Documents open in Word or Excel are locked.** If a write fails or you see a
  `~$name.docx` beside the file, the user has it open. Ask them to close it;
  do not write to a different name to get around the lock.
- **Python invocation differs by platform.** `python3` on macOS and Linux,
  `py -3` on Windows. PDF extraction needs `pypdf` (`pip install pypdf`);
  Word, Excel and PowerPoint need nothing beyond the standard library.
- **Rights-managed documents cannot be opened** by any tool (R10). Report and
  ask; do not attempt to defeat it.

### The Microsoft 365 connector is a secondary path

If a connector to Microsoft 365 / SharePoint is available, use it only for
inputs that live in Outlook, Teams or a SharePoint library that is *not* synced
to this folder — fetching an emailed attachment, for example. Then ingest that
file into `01_SoT/` through the normal R3 route, on disk.

Do not treat the connector as a way to work on this project's files. It reaches
the same documents by a different path, with none of this repository's
machinery: the manifest scan cannot run over it, so nothing notices what
changed; and it can delete, move and overwrite items, which R8 forbids
regardless of the route taken.

## Working style

- Traceability over speed: every number in a deliverable resolves to a file in
  `01_SoT/` or a script in `04_tools/`.
- When a raw input and a working file disagree, the SoT wins — and the conflict
  is recorded in the dataset's context md, not silently resolved.
- Decisions get a dated WORKLOG entry the moment they are made, including the
  ones the user rules on verbally.
