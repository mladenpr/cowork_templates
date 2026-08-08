# <Dataset or thread name>

> Template for context files (rule R2). One file per **logical dataset**: a
> singular document gets its own; a series or a negotiation thread gets one
> covering the whole thing, with the member table below. Copy this, fill it in,
> delete the guidance notes.

## Identity

- **Zone:** `01_basis/` (reference material) or `02_exchange/` (conversation)
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

- **Text layer:** searchable / scanned image — needs OCR / mixed (pages n–m)
- **Tracked changes:** none / present — n insertions, n deletions, by whom
- **Comments:** none / n comments, by whom
- **Protection:** none / rights-managed (Confidential label) / password — and
  what was done about it
- **Extracted to:** `03_working/_extracted/...` — or why it could not be
- **Completeness:** all pages, sheets and appendices present, or what is missing

## Content

What this actually contains, in 3–10 lines.

## Known issues / QA findings

Anything wrong, suspicious or superseded — with evidence, and dated. The file
itself stays untouched in its frozen zone (R1); note here where the corrected
version lives in `03_working/` and which script in `04_tools/` produced it.

In a received document the finding is often in the markup: an inserted clause,
a deleted qualification, a reviewer's comment. Record what it says, with the
author and date.

## Downstream use

Which drafts, calculations or issued documents rely on this, and which script
in `04_tools/` builds each one.
