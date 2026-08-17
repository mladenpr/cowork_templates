# <Register name> — e.g. Variations, RFIs, Purchase orders, Payment applications

> Template for a register (rule R11). Copy it, name it for the series it
> tracks, delete these guidance notes.
>
> A register is a **controlled series read by its gaps**: every variation from
> VO-001 to VO-047, every RFI and whether it was answered, every application
> and whether it was certified. The exchange log answers "what happened, in
> order"; a register answers "where does this series stand, and what is
> missing". Neither substitutes for the other.
>
> Which registers a project keeps is a project decision. Start one when you
> catch yourself asking the same status question twice.

## Identity

- **What this series is:**
- **Numbering:** who allocates the number, and the format (`VO-001`, `RFI-014`)
- **Under which contract:** `01_contract/upstream/` or a downstream package
- **Thread in the log:** the `thread` value these events carry, so the register
  and the log can be read against each other
- **Kept current by:** who updates this file, and at what moment

## Entries

| Ref | Date raised | Party | Subject | Value / effect | Status | Log # | Path |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |

Columns:

- **Status** — the state of *this item*, in the words this series actually
  uses: `raised`, `submitted`, `under review`, `agreed`, `rejected`,
  `certified`, `paid`, `withdrawn`. Whatever the set is, use it consistently;
  a status column with fourteen spellings cannot be counted.
- **Log #** — the id of the corresponding event in `03_exchange/LOG.jsonl`, so
  the register never duplicates what the log already records. One entry may
  cite several ids as it moves through the series.
- **Value / effect** — money, time, or both, in the project's currency and
  units. State clearly whether a figure is claimed, agreed or certified: the
  difference is the whole subject of the register.

## Gaps and anomalies

> The reason the register exists. A number missing from the sequence, an item
> raised and never answered, an application with no certificate against it.
> Dated, so the age of each gap is visible.

-

## Totals

> Only if the series carries money or time worth totalling — and only ever as a
> derived figure. Say what is included, as at what date, and never quote a
> total from here into a document without checking it against the sources.

- **As at:**
- **Claimed / submitted:**
- **Agreed / certified:**
- **Difference, and what it consists of:**
