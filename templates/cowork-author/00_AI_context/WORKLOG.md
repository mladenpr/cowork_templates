# WORKLOG — {{PROJECT_NAME}}

Dated decisions, corrections, and open items. One dated entry per decision.
Entries are never rewritten retroactively — later changes get their own entry.

Entry shape: an ISO date and a short title, then what was done, what was
decided (and by whom), and what is still open. Name files and scripts in full
so the entry stays resolvable later.

In this template, **every session that changes a draft ends with an entry**:
which sections were touched, which feedback items (`F-ids`) were addressed,
what was decided, what is next. That entry is the reasoning behind the draft
(R6) and the first thing the next session reads. A freeze (R11), an issue (R5)
and a rollback each get an entry of their own.

---

## {{DATE}} — Repository created

- Structure instantiated from the `cowork-author` template **v{{TEMPLATE_VERSION}}**:
  `00_AI_context/` (PROJECT, INDEX, MANIFEST, TEMPLATE.json, WORKLOG,
  datasets/, documents/), `01_basis/` (reference/, examples/, templates/),
  `02_exchange/` (received/, issued/, LOG.md), `03_revisions/` (LOG.md),
  `04_working/` (drafts/, analysis/, _extracted/), `05_tools/`, `06_temp/`,
  `_inbox/`, `_to_delete/`. Sub-folders by subject under `reference/`, by slug
  under `analysis/`, and `04_working/library/` are made on demand, not now.
- Rules R1–R12 in README.md. `01_basis/`, `02_exchange/` and `03_revisions/`
  are frozen; `04_working/` is mutable. CLAUDE.md points every session at the
  context layer, the session-start scan, and the ingest, instantiate,
  feedback, revise, freeze and issue procedures.
- `05_tools/update_index.py` generates INDEX.md and MANIFEST.json, counts
  `_inbox/` and rolls media folders up; initial baseline generated today.
  `05_tools/extract_text.py` builds the searchable text layer in
  `04_working/_extracted/`; nothing to extract yet. `05_tools/draft_diff.py`
  compares a live draft with a frozen revision.
- PROJECT.md is a stub — nothing ingested yet, all three frozen zones are
  empty, no deliverable has a document md.

Open items:

- Fill in `00_AI_context/PROJECT.md`: the brief, the people, the deliverables
  table, and the naming and revision convention a session must apply when
  issuing (R5).
- File the inputs by role (R3): requests and comments sheets into
  `02_exchange/received/`; drawings, specs, photos, standards into
  `01_basis/reference/` (subject folders as sets arrive); examples and shells
  into their folders — each with its dataset md, a set of media with one md
  for the set; an example's md lists the terms to check for (R12). Drop
  arrivals into `_inbox/`; the scan counts them until filed.
- Instantiate the draft from the shell and write its document md
  (CLAUDE.md, "instantiate a draft").
- Pin the folder for offline availability in the sync client (user action, R9).
- Install `pypdf` if the project will contain PDFs (`pip install pypdf`) —
  without it `extract_text.py` records PDFs as unread rather than reading them.

---
