# Why the structure is shaped this way

Each rule in the template exists because something goes wrong without it. This
is the failure mode behind each one.

## R1 — SoT is immutable

**Failure it prevents:** you lose the ability to prove what you were actually
sent.

Six weeks into a project you find that a quantity in the client's schedule is
wrong. The tempting move is to fix it in place — it is obviously wrong, the
corrected file is more useful, and everyone knows what happened. Three months
later, in a claim or a negotiation, "what did they actually send us on the 24th"
becomes the whole question, and the answer no longer exists anywhere.

Keeping `01_SoT/` byte-identical to what arrived, and putting every correction in
`02_derivatives/` with the transformation written down, costs one extra file and
buys a defensible audit trail. It also protects against the subtler version of
the same failure: an agent "helpfully" normalising a spreadsheet, converting a
PDF, or renaming a file to something tidier, and quietly destroying the link
between your analysis and the document the other party will produce in evidence.

The corollary is that generated files never enter SoT either. The moment a
derived figure sits alongside received documents, the boundary stops being
checkable, and "is this ours or theirs?" becomes a judgement call instead of a
lookup.

## R2 — Every input gets context

**Failure it prevents:** the agent re-derives, badly, what you already knew.

A PDF in a folder tells a model almost nothing: not who sent it, not whether it
superseded the previous one, not that page 2's subtotal is known to be wrong,
not that three downstream figures depend on it. Without that, every session
re-reads the raw file and re-forms an opinion — sometimes a different one from
last week's.

The granularity rule matters more than it looks. One md per *logical dataset*,
not per file: a single document gets its own; a homogeneous series gets one file
covering the series with a member table inside. Per-file context files fragment
exactly the comparison you need — "how did this figure move across the five
revisions" is a question about the series, and it should be answerable from one
place.

## R3 — Ingestion

**Failure it prevents:** shadow inputs.

Files arrive through chat uploads, email attachments, someone dropping a folder
on the desktop. If they can be analysed where they land, they will be, and the
project develops a second undocumented source of truth. Making ingestion a
single named step — move to `01_SoT/`, write the context md, regenerate the
index — means there is exactly one way in.

## R4 — Session-start scan

**Failure it prevents:** silent divergence.

This is the rule that does the most work, and the one most often skipped. An AI
session has no memory of the last one; the folder, meanwhile, has been edited by
you, synced by OneDrive, and possibly changed by a colleague. The scan is the
only mechanism that turns "the folder changed" into something the session
notices.

Note the asymmetry in how the three cases are handled. NEW files get ingested
automatically — that is routine. CHANGED and MISSING files get **flagged to the
human, not resolved**. A file that changed under an immutable-SoT regime means
either a rule was broken or the sync client did something; neither is for the
agent to decide.

## R5 — Derivatives vs deliverables

**Failure it prevents:** sending the wrong file, and losing track of which
outputs are disposable.

The distinction is not tidiness, it is a property: everything in
`02_derivatives/` can be deleted and rebuilt from `01_SoT/` + `04_tools/`.
Everything in `03_deliverables/` cannot, because it was *issued* — it exists in
someone else's inbox now, and its identity is its document number and revision.

Once the two are mixed, you can no longer safely purge working outputs, and you
can no longer answer "what exactly did we send them" without opening files.
Internal-only workbooks that live in `03_deliverables/` because they are
controlled — cost models, margin sheets — need their status stated loudly in
`INDEX.md`, since that folder is otherwise the one you send from.

## R6 — Tools vs temp

**Failure it prevents:** unreproducible numbers.

If a figure appears in a deliverable, something produced it, and that something
is either in `04_tools/` where it will still exist next quarter, or it was an
ad-hoc snippet in a chat window that is now gone. The rule that each derivative's
context md *names its script* is what makes the chain walkable backwards from
any number in any document.

`05_temp/` is the pressure valve. Without a place for genuinely disposable work,
scratch files accumulate in the real directories and the reproducibility
guarantee decays.

## R7 — Index and manifest

**Failure it prevents:** search-based exploration, and mtime-blind scanning.

`INDEX.md` is for the agent to read instead of grepping the tree — a single
screen that says what every file is, in your words. The design decision that
makes it work is that hand-written descriptions survive regeneration: the file
is machine-maintained in structure and human-maintained in content, so the
knowledge accumulates rather than being flattened on every rebuild.

`MANIFEST.json` is the machine half — the baseline the scan compares against.
Size and mtime are enough in a local folder. In a synced folder they are not
always: sync clients rewrite modification times when hydrating or resolving
conflicts, which produces CHANGED reports for files nobody touched. That is what
`--hash` is for; it costs a full read of every file and pays for it in a diff
you can trust.

## R8 — No deletion via the bridge

**Failure it prevents:** irreversible action from a process that misreads
context.

An agent working through a file bridge cannot delete, by design. That constraint
is worth keeping even where deletion is technically possible: cleanup means
moving into `_to_delete/` and reporting what was moved, and a human empties it.
The cost is a folder that occasionally needs emptying. The benefit is that no
misread instruction is ever unrecoverable.

## R9 — Sync discipline

**Failure it prevents:** two specific, real, and initially baffling problems.

*Cloud placeholders.* Files-on-demand shows every file in Finder whether or not
its content is on disk. An agent reading through a device bridge gets a hard
error on a dehydrated file — OneDrive surfaces it as `Resource deadlock avoided`
— and the session stops on a file that looks perfectly normal to you. Pinning
the folder for offline availability removes the failure mode entirely.

*Git inside a synced folder.* Git assumes exclusive control of `.git/`; a sync
client assumes it may upload, version and resurrect anything under its root.
Running both over the same directory produces corrupted object stores and
phantom conflicts. Keep version control at the template level and let the sync
client's own version history cover the project instance.

## What the pattern does not do

It does not version project instances. Sync-client history is coarse and
per-file; if a project genuinely needs commits, tags and branches, keep it in a
git repository *outside* the synced drive and accept that you have given up the
sharing model.

It does not enforce anything. Every rule is a convention held up by CLAUDE.md
being read at session start and by you noticing when it is not. The scan is the
only automated check, and it only checks that the folder matches its own
baseline — not that the rules were followed.
