# WORKLOG — {{PROJECT_NAME}}

Dated decisions, corrections, and open items. One dated entry per decision.
Entries are never rewritten retroactively — later changes get their own entry.

Entry shape: an ISO date and a short title, then what was done, what was
decided (and by whom), and what is still open. Name files and scripts in full
so the entry stays resolvable later.

---

## {{DATE}} — Repository created

- Structure instantiated from the `cowork-contractor` template
  **v{{TEMPLATE_VERSION}}**: `00_AI_context/` (PROJECT, PARTIES, INDEX,
  MANIFEST, WORKLOG, datasets/, registers/), `01_contract/` (upstream/,
  downstream/), `02_basis/`, `03_exchange/` (received/, issued/, LOG.jsonl,
  LOG.md), `04_working/` (drafts/, analysis/, _extracted/), `05_tools/`,
  `06_temp/`, `_inbox/`, `_to_delete/`.
- Rules R1–R11 in README.md. `01_contract/`, `02_basis/` and `03_exchange/` are
  frozen; `04_working/` is mutable; `_inbox/` is unfiled staging and
  authoritative for nothing. CLAUDE.md points every session at the context
  layer, the session-start scan, and the ingest and issue procedures.
- `05_tools/update_index.py` generates INDEX.md and MANIFEST.json; initial
  baseline generated today.
- `05_tools/log.py` maintains `03_exchange/LOG.jsonl`, renders `LOG.md` from
  it and checks it against the tree; no events logged yet.
- `05_tools/extract_text.py` builds the searchable text layer in
  `04_working/_extracted/`; nothing to extract yet.
- PROJECT.md is a stub — nothing ingested yet, all three frozen zones are empty.

Open items:

- File the executed contract into `01_contract/upstream/`, with the documents
  it incorporates, log it (`--type contract`), and fill in the "The contract"
  section of `PROJECT.md` from it — including the order-of-precedence, authority
  and notice clauses.
- List the counterparties in `00_AI_context/PARTIES.md`, with the label each
  will be filed and logged under. Labels are permanent; choose them once.
- Fill in `00_AI_context/PROJECT.md`, including the document numbering and
  revision convention a session must apply when issuing (R5).
- Decide which controlled series need a register (R11) — variations, RFIs,
  purchase orders, payment applications. Start with none and add them when a
  series grows past being answerable from the log.
- Pin the folder for offline availability in the sync client (user action, R9).
- Install `pypdf` if the project will contain PDFs (`pip install pypdf`) —
  without it `extract_text.py` records PDFs as unread rather than reading them.

---
