# <Document title> — `<slug>`

> Template for a **document md** (rule R2): one per deliverable, named for its
> slug, the authoring counterpart of a dataset md. A dataset md describes
> something that arrived; this describes the thing being made. It holds the
> *current* state — history is in `03_revisions/LOG.md` and the WORKLOG — and
> is read **before the draft is opened**, every session. Copy it, name it for
> the slug, delete the guidance notes.
>
> Two of the tables below are read by their gaps. *Requirements coverage*
> answers "have we answered everything they asked"; the *Feedback register*
> answers "have we done everything you said". Neither can be reconstructed
> from the draft, which is why they are kept here and kept current.

## Identity

- **Slug:** `<slug>` — names `04_working/drafts/<slug>/` and
  `03_revisions/<slug>/` as well as this file
- **Type:** proposal / method statement / report / response to comments / …
- **Document number:** per the convention in PROJECT.md — or "none"
- **Recipient / audience:**
- **Purpose:** one paragraph — what this document has to achieve for whom
- **Brief:** the task as given — pointer to PROJECT.md's Brief, or the dated
  instruction if this deliverable was asked for later
- **Owner / lead author:**

## Form

- **Instantiated from:** `01_basis/templates/<file>` on <date>
- **Stripped at instantiation** (if the shell was a sample): what was removed,
  what was kept as boilerplate and why it is genuinely standard
- **Examples followed:** `01_basis/examples/<file>` — taken: structure / tone
  / depth / table layout x; not taken: content (R12). One line per example.
- **House style that binds here:** styles to use for what; numbering; captions;
  length or page limit; language and register — where these differ from or
  add to PROJECT.md

## Inputs this document answers to

> The datasets this deliverable rests on, by path and role. The request it
> answers is in `02_exchange/received/`.

-

## Requirements coverage

> One row per thing the document must answer: a scope item, an RFQ question,
> a comments-sheet item, a brief requirement. Seeded when the request is
> ingested; updated as sections are drafted. An `open` row before issue is a
> finding and is reported, not silently passed (R5).

| Ref | Source | Requirement | Where addressed | Status |
|---|---|---|---|---|
| Q-01 | RFQ §3.2 |  | §4.1 | open |

- **Source** — `RFQ §n`, `Scope item n`, `CRS #n`, `brief` — with the file it
  is in, so the requirement can be reread in the original.
- **Status** — `open` · `drafted` · `done` · `n/a — why`.

## Outline and status

> The agreed structure, one row per section, with how far it has got. This is
> what tells a session what it may and may not touch.

| # | Heading | Status | Notes |
|---|---|---|---|
| 1 |  | planned |  |

- **Status** — `planned` · `drafted` · `revised` · `user-edited` · `locked`.
  `user-edited` is set when the scan reports `DRAFT EDITED` and `draft_diff.py`
  shows the user's hand in that section: the passage is theirs now and is not
  rewritten without an instruction that names it. `locked` is set only by the
  user: finished, do not touch.

## Decisions in force

> The current rules for this document, as the user has stated them: tone,
> terminology, what to include and exclude, how long, what to avoid. A
> decision that is superseded is moved to the WORKLOG with a date, not deleted
> here without trace.

-

## Feedback register

> Every instruction and comment the document must respond to, written the
> moment it is given (CLAUDE.md, "record feedback"). Read by its gaps.

| F-id | Date | Source | Feedback | Status | Where |
|---|---|---|---|---|---|
| F-001 |  | user, session <date> |  | open |  |

- **Source** — `user, session <date>` · `return <path>, comment n, <author>` ·
  `CRS #n` · `live draft comment, <author>`.
- **Status** — `open` · `addressed in Rnn` · `rejected — why` · `deferred`.
- **Where** — the section that answers it.

## Revision state

- **Live draft:** `04_working/drafts/<slug>/<file>`
- **Last frozen:** Rnn on <date> — purpose
- **Issued:** Rnn as <external label> on <date> — exchange LOG row <date>
- **Returns outstanding:** who has Rnn and has not yet come back
- **Next:** what the next revision is for, and what has to be true before it
  is frozen
