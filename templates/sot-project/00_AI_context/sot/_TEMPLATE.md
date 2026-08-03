# <Dataset reference name>

> Template for SoT context files (rule R2). One file per **logical dataset**:
> a singular document gets its own md; a homogeneous series gets one md with a
> member list and coverage table. Copy this template, fill it in, delete the
> guidance notes. Keep the file next to the SoT structure it mirrors.

## Identity

- **SoT path(s):** `01_SoT/...`
- **Received:** date, from whom, via what channel (email / transfer / chat)
- **File type / format:**
- **Size / member count:** (for a series: list members and coverage below)
- **Status:** draft / issued / superseded — and by what

## Content

What the dataset actually contains, in 3–10 lines. For a series, add a member
table: filename | period covered | notes.

## Known issues / QA findings

Anything wrong, suspicious, or superseded — with evidence, and dated. The raw
file stays untouched in SoT (rule R1); note here where the corrected version
lives in `02_derivatives/` and which script in `04_tools/` produced it.

## Downstream use

Which derivatives, figures, or deliverable sections rely on this dataset, and
which script in `04_tools/` builds each one.
