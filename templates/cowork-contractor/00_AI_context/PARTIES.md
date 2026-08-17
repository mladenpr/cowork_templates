# PARTIES — {{PROJECT_NAME}}

Everyone this project exchanges documents with, by name, with the label used in
the `Party` field of the exchange log and as the folder name under
`03_exchange/received/` and `03_exchange/issued/`.

The label is the thing that matters. Pick one per party, short and stable, and
never change it — it is written into every log row and every folder path, and a
renamed party is a broken filter across two years of history. It is a folder
name, so keep it sync-legal: letters, digits, `-` and `_`, no spaces, none of
`" * : < > ? / \ |`. `ACME`, not `ACME Infrastructure Ltd` — the full name has
its own column. If a company changes its name, keep the label and record the
change in the Notes column. `log.py` warns when a row names a label that is
not in the table below, and `log.py check` lists every such row.

## Tier

Which contract a party sits on. This is metadata, not a folder: correspondence
is filed by direction first, and the tier is a lookup here.

- **upstream** — the party you are contracted to, and anyone acting for them
  (employer, engineer, project manager, main contractor if you are a sub).
- **downstream** — the parties you have contracted, or are contracting
  (subcontractors, suppliers).
- **external** — everyone else: authorities, insurers, utilities, third-party
  testers, neighbours. Not a party to any contract in this project, but they
  send and receive documents and their letters can matter as much as anyone's.

## Register

| Label | Full name | Tier | Role | Contract | Typical traffic | Notes |
|---|---|---|---|---|---|---|
|  | {{CLIENT}} | upstream | | `01_contract/upstream/` | | |

Columns:

- **Contract** — where the instrument that binds you to them is filed, or
  `none` for an external party. A downstream party with an executed subcontract
  points at `01_contract/downstream/<label>/`; one working under purchase
  orders alone says `POs only`, since a PO is an issued document (R1) and there
  is no instrument in `01_contract/` to point at.
- **Typical traffic** — what they actually send and receive: drawings,
  instructions, invoices, test certificates. Written down, it tells a session
  what is normal and therefore what is odd.

## Who signs, and who may be written to

> Delete this section if it is one company and one contact. Fill it in the
> moment it is not — a letter sent to the wrong person, by the wrong method, at
> the right company can fail to be a valid notice. The contract's notice clause
> says who must be served, how (hand, post, email, portal), where, and when
> service is deemed to have happened; PROJECT.md cites the clause, this table
> holds the particulars.

| Party | Contact | Role | For what | Notices: method and address | Authority limit |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

- **Authority limit** — what this contact may bind their company to: sign the
  contract, issue instructions, agree a variation up to a value, certify.
  Written down, it tells a session whether a received letter is an instruction
  or a suggestion.

## Changes

> A party that changed its name, its contact, or its role, with the date. Never
> rewrite a row above; add a line here and update the row's Notes.

-
