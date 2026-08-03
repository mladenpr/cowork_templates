# WORKLOG — {{PROJECT_NAME}}

Dated decisions, corrections, and open items. One dated entry per decision.
Entries are never rewritten retroactively — later changes get their own entry.

Entry shape: an ISO date and a short title, then what was done, what was
decided (and by whom), and what is still open. Name files and scripts in full
so the entry stays resolvable later.

---

## {{DATE}} — Repository created

- Structure instantiated from the `sot-project` template:
  `00_AI_context/` (PROJECT, INDEX, MANIFEST, WORKLOG, sot/), `01_SoT/`,
  `02_derivatives/`, `03_deliverables/`, `04_tools/`, `05_temp/`, `_to_delete/`.
- Rules R1–R9 in README.md; CLAUDE.md points every session at the context layer
  and the session-start manifest scan.
- `04_tools/update_index.py` generates INDEX.md and MANIFEST.json; initial
  baseline generated today.
- PROJECT.md is a stub — no project inputs ingested yet. `01_SoT/` is empty.

Open items:

- Fill in `00_AI_context/PROJECT.md` at first ingestion.
- Pin the folder for offline availability in the sync client (user action, R9).

---
