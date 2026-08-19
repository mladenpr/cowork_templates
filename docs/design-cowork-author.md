# Design — `cowork-author`

> Status: **implemented as `cowork-author` 0.1.0 on 2026-08-19**, with every
> recommendation below accepted as written. The template's own
> [`README.md`](../templates/cowork-author/README.md) (R1–R12),
> [`CLAUDE.md`](../templates/cowork-author/CLAUDE.md) and the
> [CHANGELOG entry](../CHANGELOG.md#cowork-author-010--2026-08-19) are now the
> authoritative statement; this file is kept as the design record — why each
> piece is shaped as it is, and what the alternatives were.

## What it is for

A project whose centre is **producing a document** — a proposal, an RFQ
response, a method statement, a report or study, a response to a comments
sheet — through **many internal revisions across many sessions**, and
finishing with a submission. The role is irrelevant: a consultant and a
contractor run the same loop, only the document type differs.

The loop, as you run it:

1. You give the task, and the material the document rests on — an RFQ with a
   scope of works, a comments-resolution sheet, standards, data.
2. Sometimes an **example** — a document that shows what you are aiming for.
3. A **template** — the company's branded document shell, empty or a sample
   from another project — *in which* the agent is to work.
4. Sessions, plural: the agent drafts, you react, it revises; the draft
   matures over days or weeks.
5. At some point **you edit the document by hand.**
6. Eventually it is ready, and it is submitted.

`cowork-consultant` covers steps 1 and 6 well and is silent on 2–5. What
follows keeps every one of its four ideas — frozen/moving, provenance by
lookup, a context layer the agent must read, issuing as an explicit step —
and adds what the middle of that loop needs.

## The three things the consultant template is missing

**1. A frozen record of the document's own history.** R6 says one live draft,
revised in place, history in the sync client, reasoning in the WORKLOG. For a
tender bill that is right. For a document that goes through fifteen internal
revisions it is not: sync history gives you bytes, not a record — no "what
changed and why", no "what did the reviewer see", no answer to "which
revision did we send Jane". The answer is a third frozen zone, **revisions**,
written to only by an explicit step that mirrors issuing.

**2. A context file for the output, not just the inputs.** A dataset md
describes something that arrived. Nothing describes the thing being made:
what it is for, what form it borrows, which requirements it must answer and
where, how far each section has got, what you have said you want, what
feedback is still open, which passages are yours and not to be touched. Every
session re-derives this from the draft and the WORKLOG, and re-derives it
differently. The answer is a **document md** per deliverable, read before the
draft is opened.

**3. Rules for borrowed form and for hands on the draft.** The template and
the example are inputs with a specific hazard — another project's content
leaking into this one — that no existing rule names. And the user editing the
draft by hand is a *normal event* in this workflow that the consultant scan
reports as routine and the consultant rules do not mention. Both need a
sentence that an agent will obey.

## The tree

```
{{PROJECT_FOLDER}}/
├── CLAUDE.md              ← AI session bootstrap (read first, every session)
├── README.md              ← schema + working rules R1–R12
├── 00_AI_context/
│   ├── PROJECT.md         ← the brief, the people, the deliverables table, conventions
│   ├── INDEX.md           ← every file, one line each
│   ├── MANIFEST.json      ← scan baseline
│   ├── TEMPLATE.json      ← template stamp (tooling-maintained)
│   ├── WORKLOG.md         ← dated decisions, never rewritten
│   ├── datasets/          ← one context md per input dataset          (as consultant)
│   └── documents/         ← one context md per DELIVERABLE              ← NEW
├── 01_basis/              ← FROZEN — what the document rests on, by role
│   ├── reference/         ← what it must be correct against            ← NEW sub-folders
│   ├── examples/          ← what good looks like — form, never content
│   └── templates/         ← the branded shell the draft is instantiated from
├── 02_exchange/           ← FROZEN — the conversation with other parties (as consultant; thin here)
│   ├── received/
│   ├── issued/
│   └── LOG.md
├── 03_revisions/          ← FROZEN — the document's own history         ← NEW ZONE
│   ├── LOG.md             ← revision log: every freeze, return and issue, one chronology
│   └── <doc-slug>/
│       ├── R01/           ← the draft as frozen: source, PDF when it left your hands
│       │   ├── <doc-slug>_R01.docx
│       │   ├── <doc-slug>_R01.pdf
│       │   └── returns/   ← what came back ON R01: marked-up copies, review notes, scans
│       ├── R02/
│       └── …
├── 04_working/            ← MUTABLE — nothing here is authoritative
│   ├── drafts/
│   │   └── <doc-slug>/    ← ONE live draft per deliverable (plus its appendices), revised in place
│   ├── analysis/          ← calculations, figures, tables feeding the draft
│   └── _extracted/        ← text layer of the three frozen zones (regenerated)
├── 05_tools/              ← update_index.py, extract_text.py, draft_diff.py
├── 06_temp/               ← disposable scratch
└── _to_delete/            ← cleanup staging (only the human empties it)
```

Numbering follows the repo's rule — frozen first (`01`–`03`), mutable (`04`),
machinery (`05`, `06`). `01_basis/` and `02_exchange/` keep their consultant
numbers so the two templates read alike; the revision zone is *added*, and
working/tools/temp shift by one, landing on the same numbers `cowork-contractor`
uses.

### Why the revision zone is separate from the exchange

`02_exchange/issued/` means "this left the building" — `pattern.md` says that
folder contains *only* things already sent, and that is what lets a session
trust it. An internal revision has not left the building; a colleague's
marked-up return is "theirs", but they are inside it. Filing either into the
exchange would make "did we send this to the client?" a judgement again. A
separate frozen zone keeps the exchange's no-exceptions meaning and gives the
document's history a home with its own log.

### Why the three basis roles are fixed sub-folders

Reference, example and template are all "material the work rests on", all
frozen, and each is *used* in a completely different way:

| Role | Take from it | Never take from it |
|---|---|---|
| `reference/` | Facts, requirements, figures — everything the document must be correct against | — |
| `examples/` | Structure, tone, depth, table layouts — what good looks like | Its content: names, figures, project specifics |
| `templates/` | Styles, headers/footers, numbering, boilerplate that is genuinely standard | Anything left in a sample from another project |

The folder makes the role a lookup, so the agent never has to decide from a
filename whether a document is something to be correct against or something to
imitate. A project with no example simply has an empty folder.

The consultant's zone question still applies first: **the RFQ you are answering
is `received/`, not reference** — it opened the conversation your document will
close — and **the client's comments sheet on your last submission is
`received/`** — it is your own document returned marked up. `reference/` is for
what nobody sent you as part of this conversation: standards, data, your own
source material, a past project's document you are drawing on.

## The document md — `00_AI_context/documents/<doc-slug>.md`

The authoring counterpart of a dataset md. One per deliverable, keyed by the
same slug as `04_working/drafts/<slug>/` and `03_revisions/<slug>/`. Read
**before the draft is opened**, every session; updated whenever anything in it
changes. Current state lives here; history lives in the revision LOG and the
WORKLOG.

```markdown
# <Document title> — <doc-slug>

## Identity
- Type / document number / recipient / purpose (one paragraph)
- Brief: the task as given — by whom, on what date — or a pointer to PROJECT.md

## Form
- Instantiated from `01_basis/templates/<file>` on <date>; what was stripped if it was a sample
- Examples followed: `01_basis/examples/<file>` — taken: structure, tone, depth, table x; not taken: content
- House-style notes that bind: styles to use, numbering, language, length

## Requirements coverage
| Ref | Source (RFQ §, CRS #, brief) | Requirement | Where addressed | Status |
(read by its gaps — an open row before issue is a finding)

## Outline and status
| # | Heading | Status | Notes |
Status ∈ planned · drafted · revised · user-edited · locked
"locked" = finalised by you; not to be changed without an instruction that names it.

## Decisions in force
The current rules for this document: tone, terminology, exclusions, what you
have said you want. Superseded decisions go to the WORKLOG, not deleted here.

## Feedback register
| F-id | Date | Source | Feedback | Status | Where |
Source ∈ "user, session <date>" · "return <path>, comment n, <author>" · "CRS #n"
Status ∈ open · addressed in Rnn · rejected — why · deferred
Written the moment feedback is given, not when it is acted on.

## Revision state
- Live draft: `04_working/drafts/<slug>/<file>`
- Last frozen: R07 on <date> — purpose
- Issued: R05 as Rev A on <date> (exchange LOG row …)
- Next: what the next revision is for
```

The two tables are both "read by their gaps", which is the property the
contractor's registers have: the coverage table answers "have we answered
everything they asked", the feedback register answers "have we done everything
you said". Neither can be reconstructed from the draft.

## The revision log — `03_revisions/LOG.md`

One row per **event** in a document's internal history, all documents in one
chronology, written at the moment of the event (R4's discipline, applied
inward).

| Date | Document | Rev | Event | From / For | What changed · Purpose | Feedback | Path | Status |
|---|---|---|---|---|---|---|---|---|

- **Event** — `frozen` (a revision was cut), `return` (something came back on
  a revision), `issued` (a revision left the building — cross-references the
  exchange LOG row), `restored` (the live draft was rolled back to this
  revision).
- **From / For** — a return: who it came from. A freeze: what it was for —
  "before manual edit", "to JD for review", "end of structure phase",
  "for issue as Rev A".
- **What changed** — against the previous revision, in a sentence; the column
  you reread. `draft_diff.py` writes the raw material for it.
- **Feedback** — the F-ids this revision addresses, or (on a return) the F-ids
  it generated.
- **Rev** — the project's own sequence `R01, R02, …`, never reused, never the
  client's label. The external revision label ("Rev A", "P02") belongs to the
  exchange LOG; the `issued` row carries both so the mapping is written down
  once.

## Rules — what changes against R1–R10, and what is added

Numbering keeps the consultant's where the rule is the same, so the two
READMEs can be read side by side. Changed rules are marked.

- **R1 — Frozen zones, and provenance as a lookup** *(changed)*. Three frozen
  zones: `01_basis/`, `02_exchange/`, `03_revisions/`. Within basis, role is a
  folder. Within a revision, snapshot vs. return is a folder (`returns/`). A
  reviewer's marked-up copy is never cleaned up; the markup is the content —
  the same rule as a received document, for the same reason.
- **R2 — Every dataset gets context; every deliverable gets a document md**
  *(changed)*. The dataset md gains a **Role** line and, for examples and
  templates, a "take / do not take / terms to check for" section. The document
  md is as above.
- **R3 — Ingestion** *(changed)*. The zone decision gains the role decision.
  The paste rule stands — a fact about the world quoted in chat has no
  provenance and is not recorded — with one clarification the authoring loop
  needs: **your instructions about the document are decisions, and you are the
  source.** "Make section 3 shorter", "use the client's term for X" go into the
  feedback register and, where they change the approach, the WORKLOG, dated,
  attributed to you. A figure you quote from an email you have not filed still
  does not.
- **R4 — The exchange log.** Unchanged.
- **R5 — Issuing is an explicit step** *(changed in one mechanic)*. A document
  is issued **from a frozen revision**: if the live draft is ahead of the last
  freeze, issuing freezes it first. The frozen files are **copied** into
  `02_exchange/issued/` under the external naming convention; the revision LOG
  gains an `issued` row; the exchange LOG a row; the WORKLOG an entry; the
  document md its revision state. The live draft **stays** in `04_working/` —
  it is the base of the next revision and R6 keeps it singular. (The consultant
  *moves* the draft out and copies it back for the next revision; here the
  frozen revision already holds exactly what was sent, so the move is ceremony
  — see decision 2.) Before issue, the contamination check of R12 runs.
- **R6 — Working is mutable and singular; the draft on disk is the truth**
  *(changed)*. One live draft per deliverable, in `drafts/<slug>/`, revised in
  place. Its **history is `03_revisions/`**, frozen by you at the moments you
  choose; its **reasoning is the WORKLOG**; sync history is the safety net, not
  the record. A session **reads the draft before it writes it**, never
  regenerates it from a prior understanding, never keeps a parallel master
  (no markdown twin that the `.docx` is rendered from — the moment you edit the
  `.docx` by hand the twin is stale and the project has two truths). Passages
  the outline marks **locked** or **user-edited** are not rewritten without an
  instruction that names them.
- **R7 — Index, manifest and the scan** *(changed: one severity added)*.
  `CHANGED` in `04_working/drafts/` at session start means the draft was edited
  since the last index — in practice, by you, by hand. Not a stop, not routine:
  **read it, diff it against the last frozen revision, report what changed,
  record it.** `CHANGED` elsewhere in working stays routine.
- **R8 — Never delete; stage instead.** Unchanged.
- **R9 — Sync discipline.** Unchanged.
- **R10 — Document handling** *(one addition)*. The live draft is a `.docx`
  edited **in place, as a package**: use the shell's styles, preserve headers,
  footers, numbering and fields, never round-trip it through a converter, never
  rebuild it from scratch unless asked. Comments found in the live draft are
  feedback — register them (F-ids), act, and only then may a resolved comment
  be removed; the live draft is mutable, so that is allowed where it never is
  in a frozen zone.
- **R11 — Revisions are frozen by an explicit step, and are the record**
  *(new — the internal mirror of R5)*. Freezing is something you ask for by
  name — "freeze this as R03", "checkpoint before I edit", "send R03 to JD" —
  and something a session **offers** at the moments that warrant it: before
  you edit by hand, before anyone else sees the draft, at a milestone, before
  issue. On that instruction the live draft folder is copied into
  `03_revisions/<slug>/Rnn/` (source always; PDF when the revision leaves your
  hands), a LOG row is written with what changed and which feedback it
  addresses, the WORKLOG gets a dated entry, the document md its revision
  state, the text layer and index are regenerated. Anything that comes back on
  a revision is filed in its `returns/` as a received document, extracted, and
  its comments become F-ids. Rolling back is a freeze of the current state
  followed by a copy of Rnn over the live draft, and a `restored` row.
- **R12 — Form is borrowed, content is not** *(new)*. The draft is
  instantiated by **copying** the shell; the shell is never edited. A sample
  from another project is stripped to its skeleton at instantiation and what
  was kept as boilerplate is recorded in the document md. Nothing from an
  example's content enters the draft — structure, tone and depth only. The
  context md of every example and sample lists the **terms to check for** (the
  source project's proper nouns, figures, references), and **before issue the
  draft is grepped for them** — the text layer makes that a one-liner. A
  confidential figure from another client's proposal appearing in this one is
  the failure; it is cheap to prevent and impossible to recall.

## Procedures in CLAUDE.md

Session start — as consultant, with two additions: read the document md(s)
before the draft; treat `CHANGED` in `drafts/` as "hands were on it".

1. **Ingest** — zone, then role; context md; LOG row if received; extract;
   reindex. (As consultant.)
2. **Instantiate a draft** *(new)* — copy the shell into `drafts/<slug>/`;
   strip sample content; write the document md (identity, form, outline,
   coverage table from the reference); WORKLOG; reindex.
3. **Record feedback** *(new)* — from your instructions in session (F-id,
   source "user, session <date>"); from a return (ingest into
   `Rnn/returns/`, extract, one F-id per comment with author); from a CRS
   (received document, one F-id per item with its CRS ref); from comments in
   the live draft. Recorded when given, not when done.
4. **Revise** *(new, the daily procedure)* — read the document md; read the
   draft; change what was asked, in the shell's styles; update outline and
   feedback statuses; at session end a WORKLOG entry naming the sections
   touched and the F-ids addressed; reindex. Never a locked section; never a
   user-edited passage without instruction.
5. **Freeze a revision** *(new)* — R11, step by step.
6. **Issue** — R5, from a frozen revision, contamination check first.
7. **Session end** — reindex; WORKLOG entry if the draft moved.

The session-start line stays the same: *"Read CLAUDE.md and run the
session-start scan."*

## Tooling

| Script | Change |
|---|---|
| `05_tools/update_index.py` | `FROZEN_DIRS` gains `03_revisions/`; `REQUIRED_DIRS` reflects the tree (basis roles, `documents/`, revision zone, `04_working/…`); `--diff` reports `CHANGED` under `04_working/drafts/` as its own section — "DRAFT EDITED since last index — read before editing" — between the frozen-zone alarm and the routine list. |
| `05_tools/extract_text.py` | `SOURCE_DIRS` = the three frozen zones; `OUT_DIR` = `04_working/_extracted/`. No other change: it already captures tracked changes and comments with authors, which is exactly what a reviewer's return needs extracted. The live draft is still not mirrored (a stale copy of something that changes hourly — the consultant's reason holds; the agent opens the draft itself). |
| `05_tools/draft_diff.py` *(new, small)* | `draft_diff.py <slug> [--against Rnn] [--between R02 R04]`: extracts the live draft's text to temp with the readers `extract_text.py` already has, diffs it against the frozen revision's extraction, prints changes grouped by heading. Used at session start when the draft is CHANGED (what did you change by hand?) and at freeze time (the "what changed" column). Read-only; encodes no workflow guesses — which is why it can ship in 0.1.0 under the repo's "automate after a live run" principle. |
| `revision.py` (freeze / return / issued rows; `LOG.jsonl` + rendered `LOG.md`, contractor-style) | **Not in 0.1.0.** Freeze is a documented procedure first, the way issue is in the consultant. Scripted once the workflow has run on a real document — the freeze is frequent enough that it will earn it quickly. |

`bin/new_project.py` needs no change (it discovers the tools directory and the
frozen zones by pattern). `bin/upgrade_project.py` applies its existing
scaffolding rule. `tests/test_author_tools.py` mirrors the consultant's tests
plus the new scan section and `draft_diff.py`.

## Seed files the template ships

- `CLAUDE.md`, `README.md` (R1–R12), `VERSION` = `0.1.0`
- `00_AI_context/PROJECT.md` — consultant's, with: a **Brief** section up
  front (the task as given, dated, by whom); a **People** table (owner,
  reviewers with the label used in the revision LOG, recipient party); a
  **Deliverables** table (slug · title · doc no. · recipient · document md ·
  status); conventions gain the internal-vs-external revision convention and a
  terminology line ("the client's term for X is Y").
- `00_AI_context/WORKLOG.md`, `INDEX.md`, `MANIFEST.json` — as consultant.
- `00_AI_context/datasets/_TEMPLATE.md` — consultant's plus Role and the
  example/template section.
- `00_AI_context/documents/_TEMPLATE.md` — new, as sketched above.
- `02_exchange/LOG.md` — as consultant.
- `03_revisions/LOG.md` — new, as sketched above.
- Empty: `01_basis/{reference,examples,templates}/`, `02_exchange/{received,issued}/`,
  `04_working/{drafts,analysis,_extracted}/`, `06_temp/`, `_to_delete/`.

Repo-side: a third row in the README templates table; a section in
`docs/adapting.md` reading the zones against document types (RFQ response,
method statement, report/study, comments-resolution response); `docs/pattern.md`
gains the failure modes behind R11 and R12; CHANGELOG entry `cowork-author
0.1.0`.

## Addendum — 0.2.0: one project, many documents (2026-08-19)

Two constraints arrived after 0.1.0 and changed the reading of the design
without changing its rules. First, the template is for the heavy lifting —
documents developed from the ground up on a real project; a priced quotation
or the revision of a document already issued is ordinarily consultant work.
Second, and structurally the important one: **one author repository per real
project, all of its documents in it**, created once, with years of drops —
photos, drawings, spec sections — and still legible after ten documents.

What 0.1.0 already had for this: the slug level everywhere it matters. What it
lacked: a drop zone; any statement of how `reference/` is sub-foldered; any
home for text reused across documents; and tooling that stays readable at
hundreds of media files. 0.2.0 adds `_inbox/` (the contractor's, counted by
every scan), `04_working/library/` (on demand), sub-folders **by subject,
never by document, made on demand** — the user's ruling: no predefined subject
folders, because a tree of empty folders predicting subjects nobody has
dropped yet is the clutter the template exists to avoid — one dataset md per
media set, and a media roll-up in `INDEX.md`, in `--diff` and in the
extractor's report (ten or more media files in a folder become one line with a
count; the manifest still records every file; the inbox rolls up too — a
batch dropped as a folder is one line and one filing decision).
It also states what the exchange *is* on a real project: the conversation
about the documents — requests, comments sheets, approvals, submissions — and
that drawings, specifications and photos are reference whoever sent them.

## Decisions taken

All seven as recommended (first option in each), 2026-08-19. Ordered by how
much they changed the build.

1. **Name.** `cowork-author` — names the user's role in the loop, like the
   other two. Alternative: `cowork-document`.
2. **Issue copies; the live draft stays.** The consultant moves the draft out
   and copies it back. Here the frozen revision already is the record and the
   live draft is the base of the next revision. Alternative: keep the
   consultant's move for strict parity.
3. **The `.docx` is the single live draft — no markdown master.** Better for
   your manual edits and for the branded shell; worse for diffing and for the
   agent's ease of revision (`draft_diff.py` is the mitigation). Alternative:
   a markdown master rendered into the shell, which breaks the moment you edit
   the `.docx` by hand.
4. **Three fixed basis sub-folders** (`reference/`, `examples/`,
   `templates/`). Alternative: only `examples/` and `templates/`, with plain
   reference at the zone root — one level flatter, role by negative lookup.
5. **0.1.0 ships the freeze as a procedure and a markdown revision LOG**, plus
   `draft_diff.py`; `revision.py` and a JSONL log follow after one live
   document. Alternative: build `revision.py` on `cowork-contractor`'s `log.py`
   from the start.
6. **PDF only when a revision leaves your hands** (review, issue), source at
   every freeze. Alternative: PDF at every freeze — tidier record, a render
   step every time.
7. **The RFQ you answer is `received/`** — consultant rule, unchanged. Confirm
   you are happy with the LOG row and the "outstanding" entry that brings; the
   alternative is to treat the whole input set as reference and leave
   `02_exchange/` for the submission only.
