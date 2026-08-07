# DELIVERABLES REGISTER — {{PROJECT_NAME}}

Every controlled document issued from this project (rule R5). Maintained by
hand — `update_index.py` does not touch it, because the facts that matter here
are not visible in the filesystem: who received it, under what transmittal, and
whether it still stands.

One row per **issue**, not per file. A revision that was superseded keeps its
row; it is not edited, it is marked superseded and a new row is added. That is
what makes "what exactly did we send them, and when" answerable without opening
anything.

| Doc no. | Title | Rev | Date issued | Issued to | Transmittal | Format | Status |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |

Columns:

- **Doc no. / Rev** — your organisation's numbering, not a filename.
- **Issued to** — the named recipient, not just the company.
- **Transmittal** — the covering letter, email or portal submission reference.
  This is what the recipient will cite back at you.
- **Format** — what was actually sent: `PDF`, `PDF + XLSX`, `signed PDF`. The
  issued artefact is normally the PDF; the source document stays beside it at
  the same revision (R10).
- **Status** — `current`, `superseded by Rev n`, `withdrawn`.

## Internal-only documents

Controlled documents that live in `03_deliverables/` because they are
version-managed, but must never be sent — cost models, margin sheets,
negotiation positions. List them here explicitly and mark them in `INDEX.md`
too. `03_deliverables/` is otherwise the folder you send from, so anything in
it that must not leave needs saying twice.

-
