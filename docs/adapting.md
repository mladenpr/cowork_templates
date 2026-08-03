# Adapting the pattern

The skeleton is deliberately discipline-neutral. What changes between project
types is not the structure but what fills each drawer, and how `PROJECT.md`'s
"Conventions that matter" section is written.

Below: the same seven directories read against five different kinds of work.

## Engineering tender / bid (the origin case)

| Directory | Contents |
|---|---|
| `01_SoT/` | Client BOQ and drawings as issued, specification, addenda, RFI responses, your own submitted bills as PDFs |
| `00_AI_context/sot/` | One md for the BOQ *series* — every revision in one member table with its total and status — plus one per drawing set |
| `02_derivatives/` | Rate-progression tables, arithmetic verification of every line, cost-vs-selling comparisons, review memos |
| `03_deliverables/` | Issued bills by revision, transmittal letters, the internal cost workbook (marked never-send) |
| `04_tools/` | Transcription and verification scripts, workbook builders |

Conventions that earn their place in `PROJECT.md`: currency and VAT treatment,
what is Excluded vs Rate-Only vs Included, whether preliminaries are priced
separately or blended into rates, which historical offers are superseded and
must never be quoted back to the client.

## Litigation / contractual claim

| Directory | Contents |
|---|---|
| `01_SoT/` | Correspondence as received, the contract and its amendments, site records, expert reports, disclosure bundles |
| `00_AI_context/sot/` | One md per bundle or correspondence series, with the date range and what is known missing from it |
| `02_derivatives/` | Chronologies, issue matrices, quantum calculations, extracts keyed to bundle page references |
| `03_deliverables/` | Pleadings, submissions, witness statements — by version and filing date |

R1 stops being hygiene and becomes evidential. Every derived chronology entry
should carry the SoT path and page it came from; the immutability of `01_SoT/`
is what makes the chronology defensible rather than merely useful.

## Due diligence / M&A

| Directory | Contents |
|---|---|
| `01_SoT/` | Data-room exports by tranche, management presentations, audited accounts, Q&A responses |
| `00_AI_context/sot/` | One md per data-room tranche — date, index, what was requested but not provided |
| `02_derivatives/` | Normalised financials, adjustment bridges, red-flag registers |
| `03_deliverables/` | DD report drafts by revision, issues lists sent to the counterparty |

The high-value field here is "known issues" in each tranche's context md: what
was asked for and *not* delivered is often the finding.

## Research / technical study

| Directory | Contents |
|---|---|
| `01_SoT/` | Measurement data as recorded, third-party datasets, papers relied on |
| `00_AI_context/sot/` | Provenance, instrument and units, sampling gaps, licence terms |
| `02_derivatives/` | Cleaned datasets, every figure, statistical outputs |
| `03_deliverables/` | Report revisions, conference material, submitted manuscripts |
| `04_tools/` | The full processing chain — here R6 is simply reproducibility |

If the work will be published, `02_derivatives/` plus `04_tools/` is close to a
replication package already; keep the scripts runnable from `01_SoT/` alone.

## Design / architecture

| Directory | Contents |
|---|---|
| `01_SoT/` | Brief, site survey, planning constraints, consultant drawings received |
| `00_AI_context/sot/` | One md per consultant package, with revision and issue date |
| `02_derivatives/` | Area schedules, option studies, compliance checks |
| `03_deliverables/` | Issued drawing sets by revision, design statements |

Consultant packages arrive in revisions constantly; the member table inside a
single series md is what keeps "which structural set is current" answerable
without opening a drawing.

## Adjustments worth making, and ones that are not

**Worth making**

- Sub-foldering `01_SoT/` by source or tranche when inputs run past a few dozen
  files. Mirror it in `00_AI_context/sot/` — R2 asks the context layer to
  mirror SoT's structure precisely so this stays navigable.
- Adding a `06_correspondence/` if the project's email volume is itself the
  work product. Keep it out of `01_SoT/` only if it is *your* correspondence;
  what the other side sent you is a raw input and belongs in SoT.
- Extending `PROJECT.md` with a section for the specific thing that keeps going
  wrong on your project type.

**Not worth making**

- Renumbering the directories. The numbers are pipeline order, and CLAUDE.md,
  README.md and `update_index.py` all reference them by name.
- Collapsing `02_derivatives/` and `03_deliverables/`. The distinction is the
  rebuild-vs-issued property, not a folder-count problem.
- Dropping `00_AI_context/` on a small project. It is the entire reason the
  pattern works; a project small enough not to need it does not need the
  template either.
