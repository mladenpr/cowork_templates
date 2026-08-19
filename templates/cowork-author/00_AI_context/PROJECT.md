# PROJECT.md — {{PROJECT_NAME}}

> The project brief. Fill this in when the task is given and keep it current —
> it is the first thing an AI session reads. Aim for one screen: enough that
> someone with no history can act correctly, no more. Detail about each
> deliverable belongs in its document md; detail about each input in its
> dataset md; history in the WORKLOG. Delete these guidance notes as you fill
> each section.

## Brief

> The task as it was given — by whom, on what date, in their words if they
> were short. This is the user's decision and the user is its source, so it
> may be written here from the conversation in which it was given (R3). What
> it rests on — the RFQ, the scope, the comments sheet — is filed and listed
> under *Inputs* below.

- **Given by:** {{OWNER}}, {{DATE}}
- **Task:**
- **Deadline / submission date:**

## What the project is

> One paragraph. What is being produced, for whom, by whom, and what role this
> repository plays.

- **Recipient / principal party:** {{CLIENT}}
- **Owner:** {{OWNER}}
- **Started:** {{DATE}}

### People

> Everyone who will see or mark up the document, by name, with the label used
> in the `From / For` column of `03_revisions/LOG.md` and the `Party` column of
> `02_exchange/LOG.md`. One line each.

| Name | Role (author · reviewer · recipient) | Label in the logs |
|---|---|---|
| {{OWNER}} | author / owner | |
| {{CLIENT}} | recipient | |

## Deliverables

> One row per document this project produces. The slug is the key that ties
> `00_AI_context/documents/<slug>.md`, `04_working/drafts/<slug>/` and
> `03_revisions/<slug>/` together; choose it once.

| Slug | Title | Doc number | Recipient | Document md | Status |
|---|---|---|---|---|---|
|  |  |  |  | `00_AI_context/documents/<slug>.md` | not started |

## Inputs

> What the document rests on, by role, with the path each was filed under and
> the dataset md that describes it. The request being answered is in
> `02_exchange/received/`, not here (R1).

- **Reference** (`01_basis/reference/`):
- **Examples** (`01_basis/examples/`): — and what each is an example *of*
- **Template / shell** (`01_basis/templates/`):
- **Received** (`02_exchange/received/`): the RFQ, scope, comments sheet

## Conventions that matter

> The non-obvious rules a session must respect to avoid producing something
> wrong. Anything you have had to correct twice belongs here.

- **Naming and revision conventions:** internal revisions are `R01, R02, …` in
  `03_revisions/` and are the project's own. The **external** revision label
  the recipient will see ("Rev A", "P01", "Issue 2") and the document-number
  format follow the convention written here — a session applies it when it
  issues (R5), so write it precisely enough to be followed without asking.
- **Language and register:** the language deliverables are written in; formal
  or plain; first or third person; British or American spelling.
- **Terminology:** the recipient's own terms, where they differ from yours —
  "the client calls it the *jetty*; never *pier*." Anything a reviewer has
  corrected once.
- **House style:** which styles in the shell are to be used for what; numbering
  depth; how figures and tables are captioned; length limits or page limits
  from the request.
- **Units and unit system:** which units for each quantity; where mixed units
  appear in received documents and which one governs.
- **Standards and codes:** which apply, in which edition.
- **Rounding and significant figures:** what is reported to what precision.
- **Commercial terms**, where the document carries any: currency, tax
  treatment, what is Included vs Excluded vs Rate-Only.

## Internal position — not for external release

> Delete this section if the project has no internal/external split.
>
> Cost basis, margin, reserves, negotiation floors, anything said about the
> recipient that must not reach them. Mark it clearly so no session pastes it
> into the draft, and keep the documents themselves out of anything issued.

## Current objective

> What the next piece of work on the document is, with its target and its
> constraints — "get R03 ready for technical review by Friday". Rewritten as
> the objective changes; the superseded version stays in the WORKLOG.

## Open questions

> Unresolved items, each phrased so it is obvious who must answer it and what
> unblocks when they do.

-
