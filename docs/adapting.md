# Adapting the pattern

The skeleton is deliberately discipline-neutral. What changes between project
types is not the structure but what fills each zone, and how `PROJECT.md`'s
"Conventions that matter" section is written.

Below: the same zones read against five kinds of work.

## Engineering tender / bid (the origin case)

| Zone | Contents |
|---|---|
| `01_basis/` | Standards and codes, site survey data, your rate library, anything the pricing rests on that nobody sent you |
| `02_exchange/received/` | Client BOQ and drawings as issued, specification, addenda, RFI responses, the client's queries on your submission |
| `02_exchange/issued/` | Submitted bills by revision, RFIs you raised, transmittal letters, clarifications |
| `00_AI_context/datasets/` | One md for the BOQ *series* — every revision with its total and status — one per drawing set, and one per negotiation thread |
| `03_working/` | Rate-progression tables, arithmetic verification of every line, cost-vs-selling comparisons, the live draft of the next submission |

The internal cost workbook is the case that tests R5: it is controlled and
version-managed, but it must never be sent. It stays in `03_working/` and is
listed under "Internal-only documents" in `LOG.md`. It does not belong in
`issued/`, because that folder means "this left the building".

Conventions worth writing into `PROJECT.md`: currency and VAT treatment, what is
Excluded vs Rate-Only vs Included, whether preliminaries are priced separately or
blended, which historical offers are superseded and must never be quoted back.

## Litigation / contractual claim

| Zone | Contents |
|---|---|
| `01_basis/` | The contract and its amendments, applicable law and authorities, standard forms |
| `02_exchange/received/` | Correspondence as received, disclosure bundles, the other side's pleadings and expert reports |
| `02_exchange/issued/` | Your pleadings, submissions, witness statements, disclosure given — by version and filing date |
| `03_working/` | Chronologies, issue matrices, quantum calculations, extracts keyed to bundle page references |

R1 stops being hygiene and becomes evidential. Every chronology entry should
carry the path and page it came from, and the frozen zones are what make that
chain defensible rather than merely useful.

This is also where the two-direction split pays for itself most obviously: a
chronology that cannot distinguish what you asserted from what they asserted is
worse than no chronology.

## Due diligence / M&A

| Zone | Contents |
|---|---|
| `01_basis/` | Market data, comparables, your own valuation methodology |
| `02_exchange/received/` | Data-room exports by tranche, management presentations, audited accounts, Q&A responses |
| `02_exchange/issued/` | Information requests, issues lists sent to the counterparty, DD report drafts as delivered |
| `00_AI_context/datasets/` | One md per data-room tranche — date, index, and what was requested but not provided |

The high-value field is "known issues" in each tranche's context md: what was
asked for and *not* delivered is often the finding. `LOG.md`'s outstanding
section carries that directly — an information request with no matching response
row is a finding in itself.

## Research / technical study

| Zone | Contents |
|---|---|
| `01_basis/` | Measurement data as recorded, third-party datasets, papers relied on, instrument calibrations |
| `02_exchange/` | Often nearly empty, or just the submitted manuscript and the reviews that came back |
| `03_working/` | Cleaned datasets, every figure, statistical outputs, the live manuscript draft |
| `04_tools/` | The full processing chain |

The one case where `02_exchange/` may be thin: much research has no
counterparty, and almost everything is basis. That is fine — peer review, when
it comes, is an exchange like any other, and reviewer comments returning on your
own manuscript are a *received* document.

## Design / architecture

| Zone | Contents |
|---|---|
| `01_basis/` | Planning constraints, site survey, applicable standards |
| `02_exchange/received/` | Brief, consultant packages received, authority responses, client comments on issued sets |
| `02_exchange/issued/` | Issued drawing sets by revision, design statements, submissions |
| `03_working/` | Area schedules, option studies, compliance checks |

Consultant packages arrive in revisions constantly; the member table inside a
single thread md is what keeps "which structural set is current" answerable
without opening a drawing.

## Adjustments worth making, and ones that are not

**Worth making**

- Sub-foldering `received/` or `issued/` by party once a project runs to several
  counterparties or a few dozen files. This carries no meaning — the rules, the
  scripts and the LOG read identically either way — so single-party projects
  never need it and multi-party ones can adopt it at any point.
- Sub-foldering `01_basis/` by source or subject on the same terms.
- Extending `PROJECT.md` with a section for the specific thing that keeps going
  wrong on your project type.

**Not worth making**

- Folders per negotiation thread. It sounds right and it is not: putting your
  versions and theirs in one directory reduces the ours/theirs boundary to a
  filename convention, which drifts. The thread belongs in the context layer,
  where the member table also gives you the "what changed" column no folder
  could.
- An `obsolete/` or `archive/` folder inside `issued/`. A superseded revision was
  still issued, and it is evidence — burying it is exactly backwards. Mark it
  superseded in the LOG and leave it where it is.
- Collapsing `received/` and `issued/`. The distinction is the one that decides
  disputes.
- Dropping `00_AI_context/` on a small project. It is the entire reason the
  pattern works; a project small enough not to need it does not need the
  template either.
