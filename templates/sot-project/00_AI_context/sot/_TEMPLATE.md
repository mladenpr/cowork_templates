# <Dataset reference name>

> Template for SoT context files (rule R2). One file per **logical dataset**:
> a singular document gets its own md; a homogeneous series gets one md with a
> member list and coverage table. Copy this template, fill it in, delete the
> guidance notes. Keep the file next to the SoT structure it mirrors.

## Identity

- **SoT path(s):** `01_SoT/...`
- **Received:** date, from whom, via what channel (email / Teams / transfer /
  chat upload). Name the person, not just the company.
- **File type / format:**
- **Size / member count:** (for a series: list members and coverage below)
- **Status:** draft / issued / superseded — and by what
- **Document reference:** the sender's own number and revision, if it has one.
  This is what the other side will call it in correspondence.

## Document condition

> The properties that decide whether the file can be used at all, and that are
> expensive to rediscover every session (R10). Delete the lines that do not
> apply to this file type.

- **Text layer:** searchable / scanned image — needs OCR / mixed (pages n–m are
  scans)
- **Tracked changes:** none / present — n insertions, n deletions, by whom
- **Comments:** none / n comments, by whom
- **Protection:** none / rights-managed (Confidential label) / password —
  if protected, say what was done about it
- **Extracted to:** `02_derivatives/_extracted/...` — or why it could not be
- **Completeness:** all pages/sheets/appendices present, or what is missing

## Content

What the dataset actually contains, in 3–10 lines. For a series, add a member
table: filename | reference & revision | date | period covered | notes.

## Known issues / QA findings

Anything wrong, suspicious, or superseded — with evidence, and dated. The raw
file stays untouched in SoT (rule R1); note here where the corrected version
lives in `02_derivatives/` and which script in `04_tools/` produced it.

For a received document, the markup is often where the finding is: an inserted
clause, a deleted qualification, a reviewer's comment. Record what it says,
with the author and date.

## Downstream use

Which derivatives, figures, or deliverable sections rely on this dataset, and
which script in `04_tools/` builds each one.
