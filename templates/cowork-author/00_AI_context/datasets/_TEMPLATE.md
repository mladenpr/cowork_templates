# <Dataset or thread name>

> Template for context files (rule R2). One file per **logical dataset**: a
> singular document gets its own; a series or a negotiation thread gets one
> covering the whole thing, with the member table below. An example and a
> template each get one, with the *Use as example or template* section filled
> in — that section is what R12 is enforced from. Copy this, fill it in,
> delete the guidance notes.
>
> The thing being *written* is not a dataset and does not get one of these; it
> gets a document md in `00_AI_context/documents/` (R2).

## Identity

- **Zone:** `01_basis/` (reference / example / template) or `02_exchange/`
  (conversation)
- **Role (basis only):** `reference` — to be correct against | `example` — to
  imitate in form | `template` — the shell the draft is copied from
- **Path(s):**
- **Party:** who it came from or goes to — omit for basis material
- **Thread:** the LOG thread name, if this is a negotiation or a series
- **First received / first issued:** date, and by what channel
- **Status:** live / concluded / superseded — and by what
- **Document reference:** the sender's own number and revision. This is what
  the other side will call it in correspondence.

## Members

> For a thread or a series. Delete for a single document.
>
> A negotiation is a document whose revisions alternate custody, and the "what
> changed" column is the one you will actually reread. Fill it in at the time —
> it cannot be reconstructed later from the files.

| Date | Dir | Version | Path | What changed |
|---|---|---|---|---|
|  |  |  |  |  |

## Document condition

> What decides whether the file can be used at all, and is expensive to
> rediscover every session (R10). Delete the lines that do not apply.

- **Text layer:** searchable / scanned image — needs OCR / mixed (pages n–m
  have none — the extraction's front matter lists them as `textless_pages`)
- **Tracked changes:** none / present — n insertions, n deletions, by whom
- **Comments:** none / n comments, by whom
- **Protection:** none / rights-managed (Confidential label) / password — and
  what was done about it
- **Extracted to:** `04_working/_extracted/...` — or why it could not be
- **Completeness:** all pages, sheets and appendices present, or what is missing

## Content

What this actually contains, in 3–10 lines.

## Use as example or template

> Only for `01_basis/examples/` and `01_basis/templates/`. Delete otherwise.
> This is the section a session reads before it imitates anything, and the
> one the contamination check (R12) is run from.

- **Take from it:** structure and heading scheme / tone and register / depth
  of treatment / table and figure layouts / boilerplate that is genuinely
  standard (name the passages) / the styles, headers and footers (template)
- **Do not take from it:** its content — every name, figure, date, reference
  and project specific. For a sample used as a shell: what was stripped at
  instantiation, so the draft's document md can say what was kept.
- **Terms to check for before a revision leaves your hands:** the source
  project's client and project names, site names, document numbers, key
  figures, people — one per line. A hit in the draft stops an issue (R12).
  -
- **Where it falls short** as a model, if anywhere, so it is not imitated
  there.

## Known issues / QA findings

Anything wrong, suspicious or superseded — with evidence, and dated. The file
itself stays untouched in its frozen zone (R1); note here where the corrected
version lives in `04_working/` and which script in `05_tools/` produced it.

In a received document the finding is often in the markup: an inserted clause,
a deleted qualification, a reviewer's comment. Record what it says, with the
author and date.

## Downstream use

Which deliverables (by slug), calculations or issued documents rely on this,
and which rows of a document md's requirements coverage table it feeds.
