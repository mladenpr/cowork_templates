# WORKLOG — {{PROJECT_NAME}}

Dated decisions, corrections, and open items. One dated entry per decision.
Entries are never rewritten retroactively — later changes get their own entry.

Entry shape: an ISO date and a short title, then what was done, what was
decided (and by whom), and what is still open. Name files and scripts in full
so the entry stays resolvable later.

---

## {{DATE}} — Repository created

- Structure instantiated from the `sot-project` template **v{{TEMPLATE_VERSION}}**:
  `00_AI_context/` (PROJECT, INDEX, MANIFEST, WORKLOG, datasets/), `01_basis/`,
  `02_exchange/` (received/, issued/, LOG.md), `03_working/` (drafts/,
  analysis/, _extracted/), `04_tools/`, `05_temp/`, `_to_delete/`.
- Rules R1–R10 in README.md. `01_basis/` and `02_exchange/` are frozen;
  `03_working/` is mutable. CLAUDE.md points every session at the context
  layer, the session-start scan, and the ingest and issue procedures.
- `04_tools/update_index.py` generates INDEX.md and MANIFEST.json; initial
  baseline generated today.
- `04_tools/extract_text.py` builds the searchable text layer in
  `03_working/_extracted/`; nothing to extract yet.
- PROJECT.md is a stub — nothing ingested yet, both frozen zones are empty.

Open items:

- Fill in `00_AI_context/PROJECT.md` at first ingestion, including the naming
  and revision convention a session must apply when issuing (R5).
- Pin the folder for offline availability in the sync client (user action, R9).
- Install `pypdf` if the project will contain PDFs (`pip install pypdf`) —
  without it `extract_text.py` records PDFs as unread rather than reading them.

---
