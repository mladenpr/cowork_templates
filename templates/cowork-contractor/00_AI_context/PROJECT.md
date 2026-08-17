# PROJECT.md — {{PROJECT_NAME}}

> The project brief. Fill this in at first ingestion and keep it current — it is
> the first thing an AI session reads. Aim for one screen: enough that someone
> with no history can act correctly, no more. Detail belongs in the dataset
> context files, the registers and the WORKLOG. Delete these guidance notes as
> you fill each section.

## What the project is

> One paragraph. What is being built or supplied, for whom, under what contract,
> and what role this repository plays. Cite where the statement comes from: a
> file in a frozen zone, or a dated user statement.

- **Principal party:** {{CLIENT}}
- **Owner:** {{OWNER}}
- **Started:** {{DATE}}

Parties are listed in `00_AI_context/PARTIES.md`, with the label each one is
filed and logged under. Add a party there before filing anything from them.

## The contract

> The four or five facts a session must not get wrong, each pointing at the
> instrument in `01_contract/upstream/` that says so. Everything else about the
> contract is in the document; this is the part that gets misremembered.

- **Our position:** subcontractor to … / main contractor to … / supplier to …
- **Contract and date:** what was executed, when, and where it is filed
- **Form and amendments:** the standard form if any, its edition, and the fact
  that the particular conditions amend it — with the amendments that matter
- **Scope in one line:** what we are obliged to deliver
- **Key dates:** commencement, completion, sectional dates if any
- **Amendments since:** each executed amendment, dated, with what it changed
- **Order of precedence:** the clause that says which contract document
  governs when they disagree, and the order it sets. Cited whenever two
  documents in `01_contract/` conflict.
- **Authority to instruct and vary:** who may issue an instruction that binds,
  under which clause, and what an instruction must look like to count — so a
  session can tell an instruction from a suggestion in a received letter.
- **Notices:** the clause that governs formal notices — form, method, address
  and deemed receipt — and the time-bars that hang off it. Recording it here
  is not tracking it; a project that needs a notice register keeps one under
  R11.

## Scope and history

> Numbered, chronological. How the scope arrived at its present shape —
> variations, changes of instruction, superseded positions. Each step with its
> date and its headline figure or outcome. This is what stops a later session
> from quoting a superseded position back to the other side.

1.

## Conventions that matter

> The non-obvious rules a session must respect to avoid producing something
> wrong. Anything you have had to correct twice belongs here.

- **Document numbering and revisions:** how our documents are numbered, how
  revisions are lettered or numbered, and what "issued" means here. A session
  applies this when it files into `03_exchange/issued/` (R5), so write it down
  precisely enough to be followed without asking.
- **Their numbering:** how the other side numbers letters, instructions and
  drawings, so their references can be recognised in correspondence.
- **Units and unit system:** which units for each quantity; where mixed units
  appear in received documents and which one governs.
- **Standards and codes:** which apply, in which edition and national annex.
  Work checked against the wrong edition is wrong in a way that looks right.
- **Rounding and significant figures:** what is reported to what precision, and
  where rounding happens — at the line, at the subtotal, or only at the total.
- **Sign and coordinate conventions:** datum, chainage direction, what counts
  as positive, which coordinate system.
- **Commercial terms:** currency, tax treatment, retention, what is Included vs
  Excluded vs Rate-Only, how measurement and remeasurement work here.
- **Payment cycle:** when applications go in, what they must contain, and what
  the response dates are.
- **Language:** the language documents are issued in, and whether received
  documents are in another one.

## Registers kept

> Which controlled series this project tracks (R11), and where each one lives.
> Delete the line for any series small enough not to need one.

- `registers/variations.md` — …
- `registers/rfis.md` — …
- `registers/purchase-orders.md` — …

## Internal position — not for external release

> Delete this section if the project has no internal/external split.
>
> Cost basis, margin, reserves, target prices, negotiation floors, our own view
> of a claim's strength. Mark it clearly so no session pastes it into a
> document that goes out. The whole folder is internal (R5); this section is
> the part that is internal even within it.
>
> List the internal-only documents here — cost models, margin sheets,
> negotiation positions, internal programmes. They live in `04_working/`,
> never in `03_exchange/issued/`, and this list is where a session learns
> that before it drafts.

- `04_working/analysis/…` — …

## Current objective

> What the next piece of work is, with its target and its constraints. Rewritten
> as the objective changes; the superseded version stays in the WORKLOG.

## Open questions

> Unresolved items, each phrased so it is obvious who must answer it and what
> unblocks when they do.

-
