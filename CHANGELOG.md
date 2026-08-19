# Changelog

All notable changes to the templates in this repository.

Templates are versioned independently, each in its own
`templates/<template>/VERSION`. Every project stamps the template and version it
was created from into its own `README.md` footer and its first WORKLOG entry —
a project is a copy, not a link, so that stamp is the only record of which
rules and tooling it actually has. Releases are git tags on this repository.

Entries name their template in the heading from `cowork-consultant 2.0.2`
onwards. Everything below that point describes the single template this
repository started with — the one now called `cowork-consultant`, under the
names it carried at the time: `sot-project` through 1.x, `cowork-project` at
2.0.0 and 2.0.1. Those entries are left as they were written.

Semantic versioning, read for a template rather than a library:

- **major** — the schema or a rule changes such that an existing project cannot
  simply adopt it; upgrading means migrating a live project by hand.
- **minor** — new tooling, new rules or new template files that an existing
  project can take or leave.
- **patch** — fixes to the scripts or the documentation, with no change to the
  structure or the rules.

## cowork-author 0.1.0 — 2026-08-19

A third template, for the projects where the document *is* the project. The
consultant template covers the two ends of a document's life — the inputs
arriving, the document leaving — and is silent on the middle, where most of
the work is: the draft going round between the user and the agent across
sessions, from a brief, reference material, an example and a branded shell,
with the user's own hand edits in between, to submission. The loop is the same
whether the user is a consultant or a contractor; only the document type
differs. Derived from `cowork-consultant` 2.1.0 the way `cowork-contractor`
was, keeping the four ideas and the first two zones unchanged. Below 1.0.0
until it has run on a live document. The design it implements is
`docs/design-cowork-author.md`.

### Added — `03_revisions/`, a third frozen zone, and R11

The document's own history. A revision is frozen only by an explicit step —
the internal mirror of issuing: the user asks for it by name, the session
**offers** it at the moments that warrant it (before the user edits by hand,
before anyone else sees the draft, at a milestone, before issue) and never
performs it unasked. `03_revisions/<slug>/Rnn/` holds the draft as frozen,
source always and PDF when the revision leaves the user's hands, and in
`returns/` whatever came back on it — a colleague's marked-up copy, an
annotated print — filed as a received document would be. `03_revisions/LOG.md`
records every `frozen`, `return`, `issued` and `restored` event in one
chronology, with the "what changed" column that sync history cannot supply;
the `issued` row is where the internal `Rnn` and the external label ("Rev A")
are written against each other, once. Kept out of `02_exchange/` so that "left
the building" remains a lookup with no exceptions. `R01, R02, …` is the
project's own sequence, never the recipient's.

### Added — a document md per deliverable (R2 extended)

`00_AI_context/documents/<slug>.md`, the authoring counterpart of a dataset
md: identity and brief, form (which shell, which examples, what was stripped),
a requirements-coverage table seeded from the request, an outline with a
status per section — `planned · drafted · revised · user-edited · locked` —
the decisions in force, a feedback register with `F-ids`, and where the
revisions stand. Read before the draft is opened, every session. Two of its
tables are read by their gaps. `documents/_TEMPLATE.md` is scaffolding.

One slug ties a deliverable together across `00_AI_context/documents/`,
`04_working/drafts/` and `03_revisions/`; the level exists from day one.

### Added — `01_basis/` by role, and R12

`reference/` (to be correct against), `examples/` (form, never content),
`templates/` (the branded shell the draft is instantiated from). Each is used
differently and carries a different hazard, so the role is a folder rather
than a judgement; the scan treats all three as schema. **R12 — form is
borrowed, content is not:** the shell is copied, never edited; a sample from
another project is stripped to its skeleton at instantiation and the document
md records what was kept; an example's context md lists the **terms to check
for**, and the draft is grepped for them before a revision leaves the user's
hands and always before issue. The failure is another client's content in
this client's document — fluent, plausible, found by the recipient.

The consultant's zone rule is unchanged and stated for this case: the RFQ
being answered is `received/`, not reference; the client's comments sheet is
`received/` — the user's own document returned marked up.

### Changed — R6, the draft on disk is the truth; R7, `DRAFT EDITED`

The user editing the draft by hand is step five of the loop, not an exception.
R6 now says: one live `.docx` per deliverable in `04_working/drafts/<slug>/`,
read before it is written, never regenerated from memory or from the document
md, **no markdown master beside it** — the moment the `.docx` is edited by
hand a twin is stale and the project has two truths. The draft's history is
`03_revisions/`, its reasoning the WORKLOG, sync history the safety net.
Passages the outline marks `locked` or `user-edited` are not rewritten without
an instruction that names them.

`update_index.py --diff` reports a change under `04_working/drafts/` in its
own section — `DRAFT EDITED since last index` — between the frozen-zone alarm
and the routine list, because the session reindexes after every operation, so
a change visible at session start happened outside a session. Not a stop, not
routine: read it, diff it, record it, then edit. `CHANGED` elsewhere in
working stays routine; the two `LOG.md` files are exempt from the frozen alarm
when they change (appending is the ordinary case) and not when they go
missing, as in the contractor; `06_temp/` is not scanned, as in the
contractor.

### Changed — R3 and R5, and R10

R3 keeps the paste rule — a fact about the world quoted in chat has no
provenance — and states the clarification the authoring loop needs: **the
user's instructions about the document are decisions, and the user is their
source.** They go into the feedback register the moment they are given, dated
and attributed, and into the WORKLOG where they change the approach.

R5 issues **from a frozen revision** — issuing freezes first if the live
draft is ahead — and **copies** the frozen files into `02_exchange/issued/`
under the external convention; the live draft stays, as the base of the next
revision. The consultant moves the draft out and copies it back; here the
frozen revision already is the record of what was sent, so the move is
ceremony. The contamination check of R12 runs before any issue.

R10 adds: edit the live draft in place, as a package — the shell's styles,
headers, footers, numbering and fields preserved; never round-tripped through
a converter; never rebuilt unless asked. Comments found in the live draft are
feedback: registered first, acted on, and only then removable — the live
draft is mutable, so that is allowed where it never is in a frozen zone.

### Added — `05_tools/draft_diff.py`

Read-only. Compares the live draft with a frozen revision (the latest, or
`--against Rnn`), or two frozen revisions (`--between`), by section: only
sections that differ are printed, as added, removed or changed, and a
paragraph that was reworded rather than replaced is shown once with the
removed words marked `[-so-]` and the added `{+so+}`. The extractor's own
sections (header/footer, comments, footnotes, sheets) stay top-level rather
than nesting under the last document heading. Reads both sides through the
readers `extract_text.py` already has — `extract_file()` is new there for the
purpose — so the two compare like with like, and says when the live draft
carries comments or tracked changes, which are feedback. Several files in a
draft folder are paired strictly: same stem (ignoring `_Rnn`) and extension,
or the one case the freeze step creates — the main document renamed
`<slug>_Rnn` — and otherwise `--file` / `--rev-file`, because a diff of the
wrong pair reads exactly like a diff of the right one. Exit 0 identical,
1 differs, 2 usage.

It ships in 0.1.0 because it encodes no workflow guesses; the freeze step
itself is a documented procedure, not a script, on the same principle the
consultant applied to issue and ingest. A `revision.py` — freeze, return and
issue rows into a JSONL log with a rendered view, on the contractor's `log.py`
model — follows once the workflow has run on a real document; the freeze is
frequent enough that it will earn it quickly.

### Not done, deliberately

A markdown master for the draft (see R6). Automatic freezes at session end
(revision sprawl by another name — R6 exists to prevent it). A per-session
text baseline of the live draft for diffing (the frozen revision is the
honest baseline, and the session offers to freeze before the user edits by
hand, which is when it matters). A PDF at every freeze (a render step every
time; the PDF is required when the revision leaves the user's hands).

### Repository

- `README.md` gains the template's row and a "What `cowork-author` changes"
  section; `docs/adapting.md` a reading by document type; `docs/pattern.md`
  the failure modes behind the document md, R6, R7, R11 and R12.
- `tests/test_author_tools.py` — instantiation, the scan's draft section and
  log exemption, the extractor across three zones and `extract_file()`, and
  `draft_diff.py` end to end including the pairing rules. `test_upgrade.py`
  pins the author scaffolding set: `CLAUDE.md`, `README.md`, the three
  scripts, the two `_TEMPLATE.md` stubs. `bin/new_project.py` and
  `bin/upgrade_project.py` needed no change — they discover zones by pattern.

## cowork-consultant 2.1.0 — 2026-08-19

Projects can now be upgraded. The README has always said what an upgrade means
— copy the scripts over, mind the docs, update the footer — and left every
step of it to the person, along with the two questions the person cannot
actually answer months later: *which of these files did I edit?* and *what
values did the placeholders get?* This release records both at creation and
adds the tool that uses the record.

### Added — a machine-readable stamp: `00_AI_context/TEMPLATE.json`

`new_project.py` now writes down what it did: which template, which version,
the placeholder values it substituted, and a sha256 of every scaffolding file
as instantiated. Scaffolding means the files the template owns and a project
merely carries — `CLAUDE.md`, `README.md`, the `04_tools/` scripts, the
`_TEMPLATE.md` stubs. Everything else the template ships is seed material that
becomes project state the moment the project exists, and is deliberately not
in the stamp.

The prose footer stays, for people. The stamp is for tools: it is the
difference between guessing whether a file was edited and knowing.

### Added — `bin/upgrade_project.py`

Brings a project's scaffolding up to the toolbox's template version, under one
constraint that the tool holds by construction rather than by care: **nothing
a project produced is ever an upgrade candidate.** Documents, frozen zones,
context files, logs, drafts — never rewritten, never moved. Within the
scaffolding, the recorded hash decides per file: unmodified is replaced (with
placeholders re-substituted), locally edited is left alone with the new
version written into `05_temp/template-upgrade-v<version>/` for review,
no-longer-shipped goes to `_to_delete/` if unmodified (R8 — nothing is
deleted) and stays put if edited, missing is restored. The failure mode
everywhere is a review copy, never an overwrite.

An applied upgrade adds a dated line under the README footer, appends a
WORKLOG entry naming what changed, and records itself in `TEMPLATE.json` —
so the stamp keeps meaning what it claims: which rules and which tooling this
project actually has. The session-start scan is deliberately *not* run
afterwards: rebaselining would silently absorb whatever else happened to be
pending in the project, including a change in a frozen zone. Run
`update_index.py --diff` yourself, read it, then rebuild.

Two refusals are policy, not limitation. Across a major version the tool
refuses — a major bump means an existing project cannot simply adopt the new
rules, and that migration stays a hand job. And a toolbox older than the
project is told to `git pull`, not to "upgrade" backwards.

Projects created before the stamp existed are adopted on the first run:
template and version are read from the README footer (the old names
`cowork-project` and `sot-project` are recognised), and the toolbox's git
history stands in for the missing hashes — a project file that matches any
historical version of itself, after substitution, is provably unmodified.
What cannot be proven is proposed, not replaced.

### Changed — the docs know about the stamp

The schema block, the README footer and the WORKLOG seed name
`TEMPLATE.json`, and CLAUDE.md gains an invariant: the stamp is
tooling-maintained, and a session never edits it — not even to "fix" it.

## cowork-contractor 0.4.0 — 2026-08-19

The same release as cowork-consultant 2.1.0, read through this template's
numbering: the stamp records `05_tools/` scripts and both `_TEMPLATE.md` stubs
(datasets and registers), proposals land in `06_temp/`, and the same docs gain
the same lines.

One thing is stricter here, and it is this template's own history that makes
it so: below 1.0.0, `upgrade_project.py` treats the *minor* as the
compatibility boundary. 0.2.0 → 0.3.0 changed the log's schema — exactly what
pre-1.0 minors are allowed to do — so a 0.3.0 project is not auto-upgraded to
0.4.0; the CHANGELOG and a hand migration are. Patch releases upgrade
normally. Since 0.3.0 has not run on a live project, this strands nobody, and
from 1.0.0 the boundary widens to the major like everywhere else.

## cowork-contractor 0.3.0 — 2026-08-18

The log made a record. 0.2.0 introduced `LOG.jsonl` and called it the record;
two outside reviews of that version, cross-checked, agreed on the weakness:
`log.py` accepted whatever it was given — `2026-99-99`, a status of `banana`,
a row saying `in` for a file under `issued/`, a path that escaped the
repository — and a failed `--supersedes` left the new row written and the old
one untouched. This version closes that, adds what the schema was missing to
answer "what is owed" honestly, and brings the rules into line with what the
tools now do. Still below 1.0.0: it has not run on a live project.

### Changed — `log.py add` refuses what it cannot stand behind

Refused, with nothing written: a date that is not a real calendar date
(`--date` is now required — a default of today was a guessed date by another
name); a status or action outside the vocabulary; a path that is absolute or
escapes the repository; a path under `03_exchange/` whose `received/`/`issued/`
folder contradicts `--dir`, or whose party folder contradicts `--party` —
direction and party are lookups (R1), and the row and the tree now agree by
construction; a path that points at nothing, unless `--pending` says the file
is genuinely still on its way; a `--supersedes` or `--answers` id that does not
exist. Everything is checked before anything is written, and the new row and
the rows it changes go down in one atomic replacement (`os.replace`) — a failed
add, or a crash mid-write, leaves the log exactly as it was.

Flagged, and written: a type outside the usual list; a party label not in
PARTIES.md's Register table; superseding a row already superseded, or of a
different party; answering a row that is not open. Warnings are for the human.

### Changed — a row has two states, not one

`status` is the document's — `current`, `superseded by #n`, `withdrawn` — and
`action` is what is owed on it — `open`, `answered by #n`, `closed`, or nothing.
An issued letter that asks a question is `current` and `open` at once; the old
single column could hold one or the other, and the Outstanding list was wrong
whenever it mattered. `--due` records when the action is due; the Outstanding
section of `LOG.md` now splits "we owe" from "they owe" and shows the date.

Two more fields for honesty rather than function: `recorded` (when the row was
written, set by the script) and `backfilled` (`--backfilled`, for rows written
from the documents after the event — a batch off an old drive). R4 used to say
rows are never reconstructed; they sometimes must be, and the honest form is a
reconstruction that says so. A `†` marks them in the rendered table.

`set` changes `status`, `action`, `due` and `note` (appended, never replaced),
and fills the path of a `--pending` row once. Every change is kept in the row's
`history` — field, from, to, when. Nothing else on a row is ever rewritten.

### Added — `log.py check`, `--answers`, and a few conveniences

`check` reads the log against the tree and against itself: files in
`03_exchange/received/`, `03_exchange/issued/` or `01_contract/` that no row
mentions; rows whose path points at nothing; duplicate ids; dangling `#n`
references; rows whose direction or party disagrees with their folder; party
labels not in PARTIES.md; open actions past their due date. It is part of the
session-start scan (CLAUDE.md step 4). A row whose path is a folder covers
everything under it — a transmittal that brought thirty drawings can be one
event.

`--answers ID` mirrors `--supersedes ID`; `query --action open`, `--overdue`;
`query` exits 0 on an empty result, which for `--action open` is the healthy
state; the type vocabulary gains `contract`, `amendment`, `notice`, `rfi`,
`application`, `certificate`, `claim`.

### Changed — what gets a log row, in the rules

R3 said every arrival gets a row; the tool requires a direction and a party;
`02_basis/` material has neither. Now: exchange is always logged; an executed
instrument is logged (`--type contract`, dated the day it became executed);
basis material gets its context md and its INDEX line and no row. The date on
a row is the date on the document — letter date, title block, sent line — never
a file timestamp; a batch filed after the event is backfill, marked as such.

### Changed — the scan, and the rules about it

- `06_temp/` is not walked: disposable scratch was reported NEW on every scan,
  and the rules told a session to ingest it.
- The schema's directories are checked by name (`MISSING DIR`, exit 1), as in
  cowork-consultant 2.0.3 — a manifest of files cannot see an empty zone go.
- R7 and CLAUDE.md now say what the tool always did: `LOG.jsonl` and `LOG.md`
  changing is the ordinary case, never the frozen-zone alarm; MISSING still is.
  And NEW/CHANGED in `04_working/` and `00_AI_context/` is expected — the old
  wording had NEW anywhere calling for ingestion.
- `extract_text.py` and `update_index.py` carry the cowork-consultant 2.0.3
  fixes: a failed extraction is retried rather than cached as current, sheets
  keep Excel row numbers and column letters, `date1904` is honoured, PDFs
  report their textless pages, orphaned extractions are listed.

### Changed — the rules where they over-claimed or under-said

- R1: where a file is filed asserts nothing about its legal effect — a
  purchase order may form a contract; the folder records who sent it and
  whether it created an instrument or acted under one, and no more. And the
  documents an instrument incorporates at award (drawings, specification,
  pricing document) are contract, filed beside it; a later revision of one,
  sent under the contract, is exchange.
- R5: the project folder is internal — both sides' contracts, every party's
  correspondence, the internal position — and nothing in it is shared with a
  counterparty; what they receive left through `issued/`. R9 no longer
  describes the synced drive as "for sharing". The user exports the PDF; the
  tools do not render documents, and the row's path names the PDF.
- CLAUDE.md: "the contract wins" now continues "and when the contract's own
  documents disagree, its order-of-precedence clause decides". PROJECT.md's
  contract section gains the order-of-precedence clause, who may instruct and
  vary, and the notice clause — recorded, not tracked; a project that needs a
  notice register keeps one under R11.
- PARTIES.md: `{{CLIENT}}` is the client's *full name*, not its label — the
  label is chosen once, short and sync-legal, and the template no longer
  pre-fills it with `_TBC_` or a company name with spaces. The "who may be
  written to" table gains the notice method and address, and an authority
  limit, so a session can tell an instruction from a suggestion.
- The "Internal-only documents" list moves from `LOG.md` — a generated view in
  a frozen zone — to PROJECT.md's internal-position section, where it belongs.
- Email transcripts: if the header and the folder disagree, the folder is the
  fact; the disagreement is raised, not resolved. Backlog dates come off the
  documents' faces; only a document with no date waits for the user.
- `INDEX.md` ships with descriptions for the files the template ships with,
  so a new project's index is not twelve blank lines. Wording: "no staging
  step" → "no upload step" (the inbox *is* staging); "SoT files" gone.

### Added — `tests/test_contractor_tools.py`

27 stdlib-only tests that instantiate the template into a temporary directory
and drive the real scripts: every refusal above with proof that nothing was
written, the open/answered/superseded chain and its history, `set`'s limits,
`check`'s findings including hand-damaged JSONL, atomic writes, the inbox
count, the log exemption, the temp skip, `MISSING DIR`. Run with
`python3 -m unittest discover tests`; 46 with the consultant's.

### Not done, deliberately

- **Structured registers.** One review argued that an 80-row markdown register
  has the problem the log had. Not yet: 80 rows is still readable, totals are
  already declared derived-only, and the moment a live project needs sorting
  or summing, CSV plus a generated view is a small change — the log tooling is
  the pattern. Deferred until a live project shows the pain.
- **Locking, UUIDs, event-sourced status.** Integer `#12` is cited in
  registers, context mds and WORKLOG entries by design; two machines writing
  the same file at once produce a sync-conflict copy the scan reports and a
  duplicate id `check` reports. A stated single-writer rule and `history` on
  every mutation cover what a locking scheme would, without the machinery.
- **Time-bar tracking**, still — see 0.2.0. Recording the notice clause is a
  fact; tracking deadlines against it is a system, and a project builds one
  under R11 when it needs it.
- **The consultant's `05_temp/` is still scanned.** 2.0.3 shipped alongside
  this; the temp skip is a one-line change for its next patch.

## cowork-consultant 2.0.3 — 2026-08-18

Fixes to the two scripts, prompted by an outside review of the template, and
the tests that should have caught them. No schema change, no new rule number.
An existing 2.0.x project takes it by copying `04_tools/*.py` over its own; the
first run after that redoes every extraction once, and says so.

### Fixed — a failed extraction was "current" forever

`extract_text.py` decided an extraction was up to date by comparing the
source's size and mtime with what the output recorded. That is the right test
for "did the document change" and the wrong test for "is this output any
good": a stub written because `pypdf` was missing matched its source perfectly,
so the next run reported it as *already current* — and kept doing so after
`pypdf` was installed. The same held for an output that recorded an extraction
error, and for output made by an older version of the script.

Freshness now has four reasons, and `--report` names the one that applies:
**source changed**; **previous attempt failed** (a `not-extracted` or
`extract-error` result is retried on every run until it succeeds — a missing
library and a bug are things that get fixed, unlike a scan or a password);
**extractor updated** (every extraction records the `EXTRACTOR_VERSION` it was
made with, and a bump redoes it); and **row limit changed** (a sheet that was
truncated is re-rendered when `--max-rows` differs). The run summary counts
what it retried and why it redid anything, so a stub is never mistaken for a
success and an upgrade never looks like a mystery.

### Fixed — spreadsheets lost their row numbers and one of their epochs

The sheet renderer appended only populated rows and used the first as the
table header. A value from row 100 sat directly under row 1, the blank rows
that separate one table from the next on a real sheet vanished, and the header
was whatever happened to be first, which on a real sheet is rarely the header.
Every row now carries its Excel number in a leading `#` column and the columns
are headed by their letters, so a cell in the text layer can be named the way
the sheet names it — the same coordinates the formulas list already used.
Blank rows are still dropped; the number carries the gap.

Dates were always read in Excel's 1900 system. A workbook saved in the 1904
system — legacy Excel for Mac, some exporters — puts the same serial 1,462 days
later, so every date came out four years early and looked entirely plausible.
`workbookPr/@date1904` is now honoured, and a 1904 workbook says
`date_system: 1904` in its front matter.

### Fixed — a mixed PDF was not called one

Scan detection averaged text length over the whole document, so a report with
a typed cover page and forty scanned pages could pass as text. It is now judged
page by page: `textless_pages: 2-3, 5` in the front matter, and a flag that
distinguishes `likely-scanned-needs-ocr` (every page) from
`mixed-text-and-scanned` (some) — which is what the dataset template's "mixed
(pages n–m)" line was asking for and had no way to fill.

### Added — orphaned extractions are reported

An extraction whose source has gone — moved to `_to_delete/`, renamed, filed
elsewhere — stayed in `03_working/_extracted/` and went on answering greps
about a document the project no longer held. Both `--report` and the normal
run now list them. Per R8 they are reported, not deleted.

### Added — the scan notices a missing directory

`update_index.py` records files, and an empty directory holds none, so a
schema directory that vanished left no trace in the manifest: removing
`05_temp/` from a project and running `--diff` said *Clean*. The schema's
directories are now checked by name; a missing one prints `MISSING DIR`, makes
`--diff` exit 1, and is a bullet in the session-start scan (`CLAUDE.md`, R7):
recreate it empty and say so — anything it held shows as MISSING alongside,
and that is the real event.

### Clarified — two things the LOG did not say

- **Backfill.** R4 says a row is written at the moment of the event, never
  reconstructed later, and had no answer for a repository started for an
  engagement already under way — which is most of them. It backfills once, and
  every backfilled row says so in **Ref** (`backfilled YYYY-MM-DD from …`),
  with **Date** staying the date of the event. A reconstruction marked as one is
  a record; an unmarked one is a guess that looks like a fact.
- **Path for an issued pair.** R5 files the issued PDF and its source together,
  and the LOG has one **Path** column. That is one event and one row: Path
  names the PDF, since the PDF is what was sent, and the source sits beside it
  under the same stem.

### Added — tests

`tests/test_consultant_tools.py`, standard library only, run with
`python3 -m unittest discover tests` from the repository root. The Office
fixtures are built in code from the minimal OOXML that Excel writes, so there
are no binary files in the repository and every fixture states which behaviour
it exists to pin: both date systems, a sheet with a row gap, a hidden sheet, a
formula, truncation; each freshness reason; page ranges and the mixed-PDF flag;
orphans; the missing-directory scan; and an end-to-end instantiation with
`bin/new_project.py` that runs the real scripts twice with `pypdf` hidden, the
way the original bug was found. Run against the 2.0.2 scripts, eighteen of the
nineteen fail.

### Not done, deliberately

The review also proposed transactional `ingest.py`/`issue.py` commands, an
`_inbox/` arrival zone, a schema validator, and an agent-neutral `AGENTS.md`.
The steps a script could take over are not the ones that fail — the context md
and the WORKLOG entry need judgement, and every mechanical step is visible to
the next scan — and an arrival zone invites files to sit unclassified, which is
what the frozen/mutable split exists to prevent. The one fragile mechanical
step, appending to a markdown table, is what `cowork-contractor`'s `log.py`
already replaces; the consultant template inherits that once it has proved
itself there, as a minor release, along with a recorded-at timestamp per row.
`AGENTS.md` is a new template file and waits for the same release.

## cowork-contractor 0.2.0 — 2026-08-18

The contracting structure, decided. 0.1.0 was a copy of `cowork-consultant`
with a different name in two lines; this is the first version that is actually
a template for work performed under a contract, from award onwards, on either
side of it — a subcontractor with no packages let and a main contractor with
thirty of them run the same schema, and the difference shows up as an empty
folder rather than a different structure.

It stays below 1.0.0 until it has been run on a live project. Nothing here is
expected to change again, but "expected" is not the same as "proved".

### Added — `01_contract/`, and the boundary that makes it decidable

A zone for the instruments that bind: `upstream/` for the contract performed
under and its executed amendments, `downstream/<party>/` for subcontracts let.
The contract is what every question resolves against, it is small, and it is
stable; mixed into general reference material it has to be searched for rather
than known.

The boundary is a rule, not a judgement: **`01_contract/` holds instruments
that create or amend a contract. Everything that flows under one is
`03_exchange/`, by direction.** An instrument came into existence, or a party
acted under one that already existed — a signed variation addendum is contract,
a variation instruction is exchange.

A purchase order is therefore an issued document, not a contract instrument. A
project runs to tens or hundreds of them, for things as small as bolts, and
filing those among the contracts would bury the four documents that govern the
work. The consequence worth stating plainly: **direction now has no exception
for any document type**, which is what keeps R1 a lookup.

### Added — party sub-folders, mandatory from day one

`03_exchange/received/<party>/` and `issued/<party>/`, with the label fixed in
the new `00_AI_context/PARTIES.md`. `cowork-consultant` offers this as an
optional adjustment once a project outgrows a flat folder; a works contract
outgrows it in month two, and adopting the split later means restructuring
mid-project. Party sits *inside* direction rather than above it, so the
ours/theirs boundary stays the top-level fact R1 needs it to be.

Labels are permanent and chosen once, because they are written into every path
and every log row. A renamed party is a broken filter across the whole history.

### Changed — the exchange log is JSONL, with markdown as a view

`03_exchange/LOG.jsonl` is the record: one JSON object per line, one line per
event. `03_exchange/LOG.md` is generated from it by the new `05_tools/log.py`.

This is a concession to length and only to length. A markdown table cannot be
filtered, counted or sorted, and every hand-edit risks mangling a column —
tolerable for the fifty rows a consulting engagement produces, useless for the
thousands a two-year contract produces. JSONL is queryable in one pass, stays
diffable, and can be read directly by an agent; the markdown view survives so
the log is still legible with no tools at all.

Rows are append-only with one exception: `status` may be updated in place, via
`log.py set`, because status is the one field that legitimately changes — an
open query gets answered, a revision gets superseded. A row that was wrong is
corrected by a new row, not by a rewrite.

`log.py` covers `add` (with `--supersedes`, which closes out the previous
revision in the same command), `set`, `query` and `render`.

### Added — `_inbox/`, and `05_tools/log.py`

`_inbox/` is staging for what has arrived and not been filed: a batch off an
old drive, an attachment not yet decided about. It is not a zone — nothing in
it is authoritative, no figure is read from it — and the session-start scan
counts what is sitting there on every run until it is empty. The alternative to
a staging area is not tidiness; it is documents left on a desktop.

### Added — R11, registers

`00_AI_context/registers/` holds one md per controlled series: variations,
RFIs, purchase orders, payment applications. Not a second log. The log answers
"what happened, in what order"; a register answers "where does this series
stand, and what is missing" — an RFI with no answer, a variation instructed and
never valued, an application with no certificate against it. **A register is
read by its gaps**, so each row cites the log id rather than restating it.

Which registers a project keeps is a project decision, made when the same
status question gets asked twice. The template ships the mechanism and one
worked template, and prescribes nothing.

### Changed — zones renumbered, and the scan taught two new things

Inserting `01_contract/` shifts everything after it: `02_basis/`,
`03_exchange/`, `04_working/`, `05_tools/`, `06_temp/`. Contractor projects and
consultant projects therefore number their zones differently, which is the cost
of each template being shaped for its own work.

`update_index.py` follows: three frozen zones instead of two, a count of what
is waiting in `_inbox/` on every run, and one exemption. The log files change
on every ingestion and every issue, so a plain reading of R1 would fire the
frozen-zone alarm on the most ordinary event in the project — and an alarm that
fires routinely stops being read. `LOG.jsonl` and `LOG.md` are exempt from the
alarm when they **change**, and deliberately not exempt when they go
**missing**: growth is expected, disappearance never is.

`extract_text.py` mirrors all three frozen zones and classifies `.jsonl` as
text, so the log reports as "already text" rather than as an unreadable format.

### Changed — `bin/new_project.py` discovers the tools directory

It looked for `04_tools/` by name, which this template no longer has.
Now it matches `NN_tools`, so a template that renumbers its zones needs no
change here — and a template with no tools directory fails with a sentence
rather than a traceback over a half-written folder.

### Not done, deliberately

- **No notice or time-bar machinery.** Deadline tracking shaped to one contract
  form would be wrong for every other, and this template is for working with
  the documents — reports, letters, BoQs, drawings — not for administering a
  particular set of clauses. A project that needs a notice register builds one
  under R11.
- **No zone for daily site records.** Site diaries, labour returns and progress
  photos were considered and rejected: they are rarely the material this
  structure is for, and one that matters is filed as any other document is. A
  zone that is usually empty teaches people to ignore zones.
- **The two templates still keep their own copy of the tooling.** Same reason
  as at 0.1.0, and stronger now that the contractor scripts have diverged: a
  shared script is much harder to split later than two near-identical ones are
  to merge.

## cowork-contractor 0.1.0 — 2026-08-13

A starting point, not yet a template. `templates/cowork-contractor/` is an
unmodified copy of `cowork-consultant` 2.0.2, carrying its own name in the two
stamp lines and nothing else of its own, placed here so the contracting
structure can be developed in the open rather than in a branch.

It is deliberately numbered below 1.0.0 and marked **not ready** in the README.
Nothing in it has been adapted to contracting work yet, so a project started
from it today would carry a stamp naming a template that does not really exist.

### Not done, deliberately

- No structural change, no rule change, no guess at what contracting needs. The
  zones, R1–R10 and both procedures are consultant's, unexamined.
- The two templates each keep their own copy of `04_tools/*.py` rather than
  sharing one. Factoring out a script the moment a second copy exists is the
  wrong instinct here: the contractor tooling may need to diverge, and a shared
  script is much harder to split later than two identical ones are to merge.

## cowork-consultant 2.0.2 — 2026-08-13

Renames the template and moves its version number inside it. No schema change
and no rule change — an existing 2.0.x project is already current, apart from
one line in its README footer.

### Changed — the template is now `cowork-consultant`

`templates/cowork-project/` → `templates/cowork-consultant/`. This repository is
about to hold more than one template, and "project" says nothing about which
kind of work a template is shaped for; the consulting and the contracting sides
run differently enough to want different structures. Earlier changelog entries
keep the old paths, because that is what they were called at the time.

The stamp in a new project's README footer and first WORKLOG entry names the
template it came from, so it now reads `cowork-consultant`. Projects created
before this release say `cowork-project` and are not wrong — that was the name.

### Changed — each template carries its own `VERSION`

`templates/<template>/VERSION` is what `new_project.py` now stamps, falling back
to the repository's root `VERSION` for a template that has none.

**Why.** The stamp is a claim about which rules and which tooling a given
project has. With one template, that claim and the repository's release number
were the same number by accident. With two they are not: a patch to the
contractor template would have renumbered every consultant project created after
it, and the stamp would have quietly stopped meaning what the README promises it
means — while still looking exactly as authoritative.

`VERSION` is dropped on instantiation, alongside the `.gitkeep` markers. Both
are scaffolding for this repository — one so git tracks empty folders, the other
so this script knows what to stamp — and a project has no use for either once
the two places that matter already record it.

### Added — `--template`

`new_project.py --template cowork-contractor` picks a sibling directory under
`templates/`. It defaults to `cowork-consultant`, so every command documented
before this release still does what it did. An unknown name exits with the list
of what is actually available rather than a traceback or a half-written folder.

## [2.0.1] — 2026-08-12

Closes an ambiguity in R3 about email text pasted into a chat window. No
schema change, no new rule number, nothing an existing v2.0.0 project has to
adopt — copy the three template files over if you want it.

### Clarified — R3 does not cover pasted text

R3 says ingestion is triggered by "anything arriving from outside", and
`CLAUDE.md` listed chat uploads among the triggers. An email quoted into a
session reads as arrival, so a session applying the rule literally would file
it — inventing a filename inside a frozen zone, which R1 has no vocabulary for,
since every other file there enters already formed and is never renamed.

Pasting email to have it reviewed or answered is now stated to be working
material. A session may use it and draft from it; it does not file it, and it
does not write what the paste said into `WORKLOG.md`, `PROJECT.md` or a dataset
context md while a chat message is the only source.

**Why the second half matters more than the first.** Losing the text is not the
risk — the risk is a fact entering the context layer with no provenance, which
happens without any file being created and is invisible afterwards. The frozen
zones guarantee provenance by holding the artefact; nothing guarantees it for a
sentence somebody typed into a window.

### Added — the correspondence transcript

Deciding an email belongs in the record stays with the user, on the same seam as
R5: they write a markdown transcript and drop it in, the scan sees it as NEW,
and the session ingests it without asking, since the judgement it needed has
already been made.

- A header block in R3 the transcript carries: direction and party, sent date,
  from/to, thread, **transcribed by** (so a copy is never read as an original),
  **attachments named** but not held, and **not captured**. Filename
  `YYYY-MM-DD_<party>_<subject-slug>.md`, dated when the email was sent.
- `LOG.md` gains `email (transcript)` as a **Ref** value, so a row cannot imply
  the project holds the original.
- The `issued/` invariant in `CLAUDE.md` now names a second door: a transcript
  of correspondence already sent. It is a record being written down, not a
  document being released, and it takes no document number or revision — the
  issue procedure remains the only route for anything leaving
  `03_working/drafts/`.
- `docs/pattern.md` and `docs/cowork-notes.md` carry the reasoning and the
  day-to-day version.

### Fixed — searching would have missed transcripts

`extract_text.py` skips files that are already text, correctly: mirroring a
markdown file into `03_working/_extracted/` produces a copy of the original.
But `CLAUDE.md` told sessions to search inside documents by grepping the
extraction, and an email transcript is never in it — so a session searching
exactly as instructed would find no email at all. The search instruction in
`CLAUDE.md` and the text-layer bullet in R10 now say to cover `_extracted/` and
the frozen zones both. No script change.

Sessions asked to write a transcript must request the sent date, recipients and
attachments rather than infer them. A LOG row with a guessed date is worse than
no row, because it reads as a fact.

### Not done, deliberately

No automatic filing of pasted email, and no prompt offering it. Most pasted
correspondence is not worth keeping, and a `received/` folder holding
everything that passed through a chat window stops meaning "this is the
record". The filter is the value of the frozen zone, and the filter is human.

## [2.0.0] — 2026-08-07

Restructures the template around the distinction between documents that are
**frozen** and documents that are **moving**, and treats the flow of documents
to and from another party as a conversation rather than as inputs and outputs.

Projects created from v1.x keep the v1.x layout. There is no migration and none
is planned — a live project should not have its rules changed under it
mid-engagement. Finish those as they are; start new ones on v2.

### Changed — the schema

The template directory is renamed `templates/sot-project/` →
`templates/cowork-project/`. It was named for the concept it was built around,
and that concept is gone: SoT is now one zone among three rather than the
organising idea. Earlier changelog entries keep the old path, because that is
what it was called at the time.

```
01_SoT/            →  01_basis/              reference material only
02_derivatives/    →  03_working/            drafts/, analysis/, _extracted/
03_deliverables/   →  02_exchange/issued/
                   +  02_exchange/received/  (new)
00_AI_context/sot/ →  00_AI_context/datasets/
REGISTER.md        →  02_exchange/LOG.md     both directions, one chronology
```

The numbers no longer mean pipeline order — `02_exchange/` holds both inputs
and outputs, so no pipeline reading is possible. They now order by status:
frozen first, then mutable, then machinery.

**Why.** The old axis was *reproducibility*: regenerable outputs in one folder,
issued documents in another. That axis never survived contact with real work —
`docs/adapting.md` filed review memos, chronologies and issue matrices under
derivatives, none of which any script can regenerate, so the promise that the
folder could be safely purged was already false. Drafts made the gap visible
rather than creating it. Frozen-versus-moving has no such hole and needs no
exceptions.

**And why received/issued rather than SoT/deliverables.** What you receive and
what you issue carry equal weight and are two halves of one exchange; naming one
"Source of Truth" and the other "deliverables" hid that. `SoT` was the right
name only for the third thing — reference material the work rests on, from
sources that are not party to the conversation — which is now `01_basis/`.

### Added

- **`02_exchange/LOG.md`** — one row per document in or out, in date order, with
  direction, party, thread, revision, transmittal and status, plus an
  outstanding-items section. The index of the conversation, the way `INDEX.md`
  is the index of the files. Rows are written at the moment of the event.
- **R5, the issue step.** A document leaves the project only when the user asks
  for it by name. On that instruction the file moves from `03_working/drafts/`
  into `02_exchange/issued/` under its number and revision, the PDF is filed
  with its source, the LOG gains a row, the WORKLOG a dated entry, the thread's
  context md a member row, and the index is regenerated. Silently renaming a
  draft leaves the project unable to say what was sent, to whom, or under what
  cover. `CLAUDE.md` carries this and the ingest procedure as explicit steps.
- **R6, one live draft per deliverable**, revised in place rather than copied to
  a new file per revision.
- **Negotiation threads** as a first-class case of R2: a document whose
  revisions alternate custody is one dataset with a member table carrying date,
  direction, version, path and *what changed*. The files stay in their direction
  folders; the thread lives in the context layer. Folders per thread were
  considered and rejected — they reduce the ours/theirs boundary to a filename
  convention.
- **Zone-aware scan severity** in `update_index.py`: movement inside a frozen
  zone is reported first and separately as something to stop for, while CHANGED
  in `03_working/` is routine. Without this, a live draft would report CHANGED
  every session and train you to skim past the reports that matter.
- **Multi-party support at no cost to single-party projects.** Party is a LOG
  column, not a folder level. Sub-foldering `received/` or `issued/` by party is
  available when volume justifies it and carries no semantics — the rules, the
  scripts and the LOG read identically either way.
- `VERSION` at the repository root as the single source of truth, and a
  `{{TEMPLATE_VERSION}}` placeholder stamped into each new project's README
  footer and first WORKLOG entry; `new_project.py --version`. (Merged before
  this release; the version stamp is what distinguishes a v1 project from a v2
  one on disk.)
- `PROJECT.md` gains a Parties table for multi-party projects.

### Changed — the rules

R1–R10 rewritten around the frozen/moving distinction:

- **R1** now covers both frozen zones and makes direction the provenance
  boundary. Two consequences are stated explicitly because both catch people
  out: what you issued is frozen too, and your own document returned to you
  marked up is a *received* document.
- **R2** extended to threads. **R3** ingestion now decides a zone and writes a
  LOG row. **R4** is the exchange log. **R5** is issuing. **R6** is working.
  **R7** merges the old index/manifest and session-start-scan rules and adds
  zone-aware severity. **R8** (never delete), **R9** (sync discipline) and
  **R10** (document handling) carry over.
- `extract_text.py` now walks both frozen zones and writes to
  `03_working/_extracted/`, keeping the full zone-relative path so the two
  cannot collide. `03_working/` is not extracted — extracting a live draft would
  only produce a stale copy of something that changes hourly.

### Not done, deliberately

No `issue.py` or `ingest.py`. Both steps are clerical enough to script, but the
workflow has not been run once, so the arguments would be guesswork and the LOG
row is the part that must not be wrong. They are documented as procedures the
agent performs on your instruction; automate whatever proves stable after a real
project.

## [1.1.0] — 2026-08-07

Retargets the template at document work (Word, PDF, Excel) on a synced
OneDrive folder, with sessions running locally rather than through a cloud
file bridge.

### Added

- `templates/sot-project/04_tools/extract_text.py` — mirrors `01_SoT/` into
  `02_derivatives/_extracted/` as one markdown file per document, so the
  project can be searched instead of reparsed. Word, Excel and PowerPoint are
  handled with the standard library alone (they are ZIP archives of XML);
  captures tracked insertions and deletions, comments with their authors,
  tables, hidden sheets, formulas and speaker notes. PDFs use `pypdf` when it
  is installed and are recorded as unread when it is not; a PDF with no text
  layer is flagged as needing OCR. Rights-managed Office files are detected by
  their OLE signature and named as such — in a Microsoft 365 tenant that is the
  most common reason a document cannot be read.
- `templates/sot-project/03_deliverables/REGISTER.md` — one row per issue:
  document number, revision, date, recipient, transmittal, format, status.
  R5 required deliverables to be organised by number and revision but nothing
  recorded the facts that are not visible in the filesystem.
- **R10 — Document handling**: never re-save or clean up a source document;
  keep the extracted text layer current; record document condition (text layer
  vs scan, tracked changes, comments, protection) in the context md; issue PDFs
  and keep sources beside them. The text layer is explicitly **an index, not a
  substitute** — find things in the extraction, read them in the source, and
  never let a figure reach a deliverable without checking it against the
  document. Every extracted file opens with a banner saying so, since that is
  what an agent actually reads.
- `sot/_TEMPLATE.md` gains a "Document condition" section covering those
  properties, plus the sender's own document reference and revision.
- `update_index.py` now warns about suspected sync-conflict copies (keyed on
  the machine name OneDrive appends) and about names SharePoint refuses to
  sync — illegal characters, reserved device names, trailing dots, over-long
  paths. Warnings never affect the exit code.

### Fixed

- `update_index.py`: `--hash` was honoured by `--diff` but not by regeneration,
  so the first regeneration that omitted the flag silently dropped every
  sha256 and returned the project to mtime comparison — the exact mode a sync
  client breaks. Hashing is now sticky, with `--no-hash` to opt out and
  `--rehash` to force a full recompute.
- `update_index.py`: hashes are reused when size and mtime both match the
  baseline, so a scan no longer re-reads every byte of every PDF each session.
- `update_index.py`: Office save-temps (`~WRL0001.tmp`), LibreOffice locks and
  `.tmp` files are skipped. Only `~$` owner files were skipped before, so the
  rest were reported NEW and would have been ingested into `01_SoT/`.
- `extract_text.py`: six extraction losses found by testing against a document
  with the features a real specification has —
  - **Word list numbering was dropped entirely.** Word stores the scheme, not
    the numbers, so `1.` / `2.` / `2.1` simply vanished. In a specification
    that is how the document is referenced. Numbering is now reconstructed from
    `numbering.xml` for the ordinary case and the document is flagged
    `list-numbering-reconstructed`, since restarts and overrides will be wrong.
  - **Headers and footers were not read at all** — which is where a controlled
    document carries its number, revision and confidentiality marking.
  - **Footnotes and endnotes were not read at all**, and their reference marks
    were invisible in the body. Both are now extracted, with `[^n]` markers
    inline.
  - **Nested tables were flattened** into the containing cell, merging the
    inner table's values into one run-on string.
  - **Excel dates stayed as serial numbers.** Number formats are now resolved
    from `styles.xml` (built-in and custom) and serials converted to ISO dates,
    including Excel's fictional 1900-02-29.
  - **Merged cell ranges were unreported**, leaving header rows looking
    misaligned against the source.
- `extract_text.py`: paragraphs inside `w:sdt` content controls were invisible.
  Templates and forms wrap blocks in them, so whole sections could be missing.

### Changed

- **R8** is restated as a policy rather than a description of the environment.
  Through a cloud bridge deletion was impossible; running locally it is not, so
  the rule is now the only thing preventing an unrecoverable loss. R1 is marked
  the same way.
- **R9** covers sync-conflict copies, sync-legal filenames and Office file
  locks, and downgrades the cloud-placeholder failure from a hard error to a
  slow read — which is what it is on a local run.
- `CLAUDE.md` environment notes rewritten for local execution: no staging, no
  stale snapshots, no file-delivery write-back path, real shell, real write
  access. Adds the Windows `py -3` invocation and positions the Microsoft 365
  connector as a way to fetch inputs that are not on disk, never as a way to
  work on the project — it cannot run the scan, and it can delete.
- `PROJECT.md`'s conventions section is reframed for engineering work — units,
  standards and editions, rounding, sign and coordinate conventions, document
  numbering, language — with commercial terms as one item rather than the
  premise. The internal-position section is now explicitly optional.
- `new_project.py` seeds the first manifest with `--hash` and makes both tools
  executable.
- `docs/cowork-notes.md` rewritten around local sessions, with the bridge
  constraints kept as a closing section; `docs/pattern.md` gains R10 and the
  reasoning behind the R8 and R9 changes.

## [1.0.0] — 2026-08-03

Initial release.

### Added

- `templates/sot-project/` — the immutable-SoT project skeleton: `CLAUDE.md`
  session bootstrap, `README.md` with working rules R1–R9, a `00_AI_context/`
  layer (PROJECT / INDEX / MANIFEST / WORKLOG / per-dataset context files), and
  the `01_SoT` → `02_derivatives` → `03_deliverables` → `04_tools` → `05_temp`
  pipeline directories.
- `templates/sot-project/04_tools/update_index.py` — regenerates `INDEX.md` and
  `MANIFEST.json`, preserving hand-written descriptions; `--diff` implements the
  session-start scan.
- `bin/new_project.py` — instantiates the template into a new folder, fills the
  placeholders, and writes the first index baseline.
- `docs/pattern.md`, `docs/adapting.md`, `docs/cowork-notes.md`.

### Changed from the source project

The template was extracted from a live engineering-tender repository. Relative
to that original:

- All project, client and discipline specifics removed; replaced with
  `{{PLACEHOLDER}}` substitution.
- `update_index.py` no longer hard-codes the project name in the `INDEX.md`
  title — it resolves it from `--name`, else the `PROJECT.md` heading, else the
  folder name.
- `update_index.py` gained `--hash`: compares sha256 rather than size+mtime, for
  synced folders where the sync client rewrites modification times. Manifests
  written with and without it remain mutually diffable.
- `update_index.py` now skips non-regular files defensively.
- R9 generalised from OneDrive to any sync client, with the placeholder-read
  failure spelled out.
- `PROJECT.md` and `WORKLOG.md` converted from filled-in project documents into
  prompted templates.
