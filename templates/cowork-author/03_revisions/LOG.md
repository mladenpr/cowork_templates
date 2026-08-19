# REVISION LOG — {{PROJECT_NAME}}

Every revision of every deliverable that was frozen, everything that came back
on one, and every one that was issued — all documents, one chronology (rule
R11). This is the index of the document's own history, the way
`02_exchange/LOG.md` is the index of the conversation and `INDEX.md` the index
of the files.

One row per **event**, not per file. A revision that was superseded keeps its
row — it is not edited, it is marked superseded and a new row is added below.
Rows are written **at the moment of the event**: a freeze writes its row as
the copy is made, a return writes its row as the file is filed. A log
reconstructed afterwards from folder listings is a guess about exactly the
facts you will later need — what changed between R04 and R05, and who saw
which one.

| Date | Document | Rev | Event | From / For | What changed · Purpose | Feedback | Path | Status |
|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |

Columns:

- **Document** — the deliverable's slug, matching `00_AI_context/documents/`,
  `04_working/drafts/` and the folder under `03_revisions/`.
- **Rev** — the project's own sequence `R01, R02, …`, never reused, never the
  recipient's label. The external revision ("Rev A", "P02") lives in the
  exchange LOG; the `issued` row below carries both, once, so the mapping is
  written down.
- **Event** — `frozen` (a revision was cut from the live draft), `return`
  (something came back on a revision), `issued` (a revision left the building
  — the exchange LOG has the matching `out` row), `restored` (the live draft
  was rolled back to this revision).
- **From / For** — a return: who it came from, by the label in PROJECT.md's
  People table. A freeze: what it was for — `before manual edit`, `to JD for
  review`, `end of structure phase`, `for issue as Rev A`.
- **What changed · Purpose** — against the previous revision, in a sentence.
  This is the column you reread. `05_tools/draft_diff.py` writes the raw
  material; the sentence is yours.
- **Feedback** — the `F-ids` this revision addresses (a freeze) or generated
  (a return), as listed in the document md's feedback register.
- **Path** — repo-relative: `03_revisions/<slug>/Rnn/<slug>_Rnn.<ext>` for a
  freeze (the PDF, when one was made, sits beside it under the same stem);
  `03_revisions/<slug>/Rnn/returns/<file>` for a return.
- **Status** — for a freeze: `current`, `superseded by Rnn`, `issued as <label>`
  (which also supersedes); for a return: `open` until every comment in it has
  an F-id, then `registered`.

## Outstanding

Revisions that are out with someone and have not come back, and returns whose
comments are not yet all in the register. Kept here rather than inferred from
the table, because "has Jane sent her comments yet" is the question that gets
asked, and the answer should not require reading the table backwards.

-
