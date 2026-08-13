# EXCHANGE LOG — {{PROJECT_NAME}}

Every document that entered or left this project, in date order (rule R4). This
is the index of the conversation, the way `INDEX.md` is the index of the files.

One row per **event**, not per file. A revision that was superseded keeps its
row — it is not edited, it is marked superseded and a new row is added below.
That is what makes "what did we send them on the 24th, and what came back"
answerable without opening anything.

Rows are written **at the moment of the event**. A log reconstructed afterwards
from file timestamps is a guess, and it is a guess about exactly the facts
someone will later dispute.

| Date | Dir | Party | Thread | Document | Rev | Ref | Path | Status |
|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |

Columns:

- **Dir** — `in` for received, `out` for issued. The whole point of the table is
  that both directions sit in one chronology.
- **Party** — who it came from or went to, by name. Projects with several
  counterparties are read by filtering this column; projects with one can leave
  it constant.
- **Thread** — the negotiation or topic this belongs to, matching the context md
  in `00_AI_context/datasets/`. A subcontract exchanged back and forth is one
  thread with many rows.
- **Rev** — the sender's own revision, not an internal one. It is what the other
  side will cite.
- **Ref** — outbound: the transmittal, covering letter or portal submission.
  Inbound: how it arrived — email, Teams, portal, hand delivery. An email typed
  up into a markdown file rather than filed as it arrived says `email
  (transcript)`, because what the project holds is a copy and the row should
  not imply otherwise.
- **Status** — `current`, `superseded by Rev n`, `withdrawn`, or for inbound
  items `open` / `answered by …` when a reply is owed.

## Outstanding

Inbound items still awaiting a response, and outbound items awaiting theirs.
Kept here rather than inferred from the table, because "what have they not
answered" is the question that gets asked in a progress meeting.

-

## Internal-only documents

Documents that are controlled and version-managed but must never be sent — cost
models, margin sheets, negotiation positions. They do not belong in
`02_exchange/issued/` at all, since that folder means "this left the building".
Keep them in `03_working/` and list them here so the exclusion is written down
somewhere both you and a session will see it.

-
