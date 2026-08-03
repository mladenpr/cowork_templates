# CLAUDE.md — session bootstrap (read this first, every session)

Project: **{{PROJECT_NAME}}**{{CLIENT_SUFFIX}}

This repository follows a fixed schema and a set of working rules. Before doing
any work in this project:

1. Read `00_AI_context/PROJECT.md` — what this project is and who it is for.
2. Read `README.md` — the repository schema and the working rules (R1–R9).
   The rules are binding; do not improvise around them.
3. Run the session-start scan: diff the current repository state against
   `00_AI_context/MANIFEST.json` (use `04_tools/update_index.py --diff`).
   - Any NEW raw input file → move it into `01_SoT/`, write/extend its context
     md under `00_AI_context/sot/`, then regenerate INDEX and MANIFEST.
   - Any changed or missing file → flag it to the user before proceeding.
4. Check `00_AI_context/WORKLOG.md` for the latest decisions and open items.
5. Consult `00_AI_context/INDEX.md` before searching the tree — every file is
   listed there with a one-line description.

Key invariants (full text in README.md):

- `01_SoT/` is **immutable**. Never edit, rename, convert or "fix" a raw input
  in place. Corrections are new files in `02_derivatives/`, with the
  transformation documented in the dataset's context md.
- Regenerable outputs go to `02_derivatives/`; issued controlled documents go
  to `03_deliverables/`; kept scripts to `04_tools/`; scratch to `05_temp/`.
- Files are never deleted through the device bridge — move them to
  `_to_delete/` and tell the user.
- After any file operation, regenerate `INDEX.md` and `MANIFEST.json` with
  `04_tools/update_index.py`.

## Environment notes

These are mechanics, not rules — they save a session from re-learning them.

- **The project folder is on the user's machine, inside a synced cloud drive.**
  A cloud-only placeholder cannot be read: the read fails outright (OneDrive
  surfaces it as `Resource deadlock avoided`). If that happens, stop and ask
  the user to pin the folder for offline availability rather than working
  around it — see R9.
- **Writing back to the user's disk** goes through the file-delivery path
  (deliver the file, then commit it to the device at an absolute path). If a
  direct filesystem tool is available but scoped to other directories, it will
  refuse the synced project path; use the delivery path instead.
- **Staged copies can go stale.** A file staged into the session workspace is a
  point-in-time snapshot. Before deriving anything from a copy staged more than
  a few minutes ago, re-check it against the device.
- **Deletion is not available** through the bridge (R8). `mv` into `_to_delete/`
  and report what was moved.
- **Do not `git init`** inside the project folder (R9).

## Working style

- Traceability over speed: every number in a deliverable resolves to a file in
  `01_SoT/` or a script in `04_tools/`.
- When a raw input and a working file disagree, the SoT wins — and the conflict
  is recorded in the dataset's context md, not silently resolved.
- Decisions get a dated WORKLOG entry the moment they are made, including the
  ones the user rules on verbally.
