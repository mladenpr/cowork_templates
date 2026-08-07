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

With document formats the rule has a sharper edge than it looks. Opening a
`.docx` in Word and saving it — with no edits at all — rewrites the whole
package and changes its hash. So does accepting a tracked change, resolving a
comment, or "just converting it to PDF". Each of those is an edit to evidence,
and none of them feels like one at the time.

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
Size and mtime are enough in a local folder. In a synced folder they are not:
sync clients rewrite modification times when hydrating a file or resolving a
conflict, which produces CHANGED reports for files nobody touched. A scan that
cries wolf every session stops being read, and R4 quietly dies.

That is what `--hash` is for. Two details make it usable rather than merely
correct. It is **sticky** — once a manifest carries hashes, later regenerations
keep them, because a flag you have to remember every time is a flag that will
eventually be forgotten, and forgetting it silently returns you to the noisy
mode. And hashes are **reused** when size and mtime both match the baseline, so
a scan only reads the bytes of files that look touched; a project of PDFs is
not re-read in full every session. The residue is that content edited in place
with its mtime preserved slips through, which `--rehash` exists to catch.

## R8 — Never delete; stage instead

**Failure it prevents:** irreversible action from a process that misreads
context.

This rule started life as a description. An agent working through a cloud file
bridge could not delete — `rm` failed with `Operation not permitted` — so R8
merely wrote down what the environment already guaranteed.

Running locally, the environment guarantees nothing. Delete works, overwrite
works, rename works. The rule survives the change but its status does not: it
has gone from a description of a constraint to the constraint itself, and it is
now the only thing standing between a misread instruction and a loss you cannot
undo.

That is worth being explicit about, because rules phrased as facts about the
world get dropped silently when the world changes. Cleanup means moving into
`_to_delete/` and reporting what was moved; a human empties it. The cost is a
folder that occasionally needs emptying. The benefit is that no misread
instruction is ever unrecoverable.

The same reasoning applies to R1. Neither rule is enforced by anything. Both
hold because CLAUDE.md is read at session start and because you notice when it
is not.

## R9 — Sync discipline

**Failure it prevents:** several specific, real, and initially baffling
problems.

*Cloud placeholders.* Files-on-demand shows every file whether or not its
content is on disk. Through a cloud bridge, reading a dehydrated file is a hard
error — OneDrive surfaces it as `Resource deadlock avoided` — and the session
stops on a file that looks perfectly normal to you. Locally it degrades instead
of failing: the read triggers a download and eventually succeeds. That is
better, but a session-start scan across an unpinned project now stalls while
gigabytes hydrate one file at a time, and offline it fails outright. Pinning
costs nothing and removes both.

*Sync-conflict copies.* When the same file is edited in two places, OneDrive
does not merge and does not ask — it writes a second file named
`<name>-<YourComputerName>.<ext>` and syncs both. In `01_SoT/` that is a quiet
catastrophe: an immutable-input folder now holds two versions of the same
received document, and the scan reports the copy as NEW, which under R3 means
"ingest it". The scan therefore names conflict copies specifically and refuses
to treat them as routine — like CHANGED and MISSING, they are for the human.

*Names that stop syncing.* SharePoint and OneDrive reject `" * : < > ? / \ |`,
leading and trailing spaces, trailing dots, the reserved DOS device names, and
any item whose URL exceeds 400 characters. Engineering document names run long
and often carry a colon after the discipline. A file that fails to sync is
worse than one that never arrived, because it is present on your machine and
absent everywhere else — so the scan warns rather than waiting for you to find
out.

*Office locks.* Word and Excel hold a lock on an open document. A write to a
locked file fails, and the tempting workaround — write to a slightly different
name — leaves you with two versions of a deliverable and no way to tell which
is current.

*Git inside a synced folder.* Git assumes exclusive control of `.git/`; a sync
client assumes it may upload, version and resurrect anything under its root.
Running both over the same directory produces corrupted object stores and
phantom conflicts. Keep version control at the template level and let the sync
client's own version history cover the project instance.

## R10 — Document handling

**Failure it prevents:** a project whose contents cannot be searched, and
documents whose condition has to be rediscovered every session.

A folder of PDFs and Word files is opaque in a way a folder of text files is
not. `INDEX.md` says what each file is in one line; the context md says what
the dataset is in a paragraph. Neither can answer "which document says X", and
nothing in the tree can be grepped. So every session that needs a figure opens
a binary, reparses it, spends its context doing so, and forgets the result.

`02_derivatives/_extracted/` fixes this by construction: one markdown file per
document, mirroring SoT, rebuilt from SoT by a script in `04_tools/`. It is a
derivative in the full R5 sense — nothing is lost if it is deleted, and the
rebuild is one command. The point is not that extraction is clever; it is that
the searchable form of the project should be a *file*, not something an agent
reconstructs from scratch on every session.

The second half of the rule is about condition. Three properties decide whether
a document can be used at all, and each is expensive to rediscover and cheap to
write down once:

- **Does the PDF have a text layer**, or is it a scan needing OCR? A scanned
  drawing looks identical to a born-digital one in a file listing.
- **Does the Word file carry tracked changes or comments?** In a received
  document that markup is frequently the actual content — an inserted clause or
  a reviewer's comment is the finding, not noise around it. It also means the
  document must never be "cleaned up": accepting the changes destroys the
  record, and it is the kind of tidying that feels helpful.
- **Is the file rights-managed?** An Office document carrying an encrypting
  sensitivity label is not a readable package at all; it is an OLE container
  only authenticated Office can open. No library and no agent can read it. In a
  Microsoft 365 tenant this is the most common reason a document cannot be
  processed, and it produces baffling errors when it is not named. The right
  response is to record it and ask for a decrypted copy in `02_derivatives/` —
  not to work around it.

## What the pattern does not do

It does not version project instances. Sync-client history is coarse and
per-file; if a project genuinely needs commits, tags and branches, keep it in a
git repository *outside* the synced drive and accept that you have given up the
sharing model.

It does not enforce anything. Every rule is a convention held up by CLAUDE.md
being read at session start and by you noticing when it is not. The scan is the
only automated check, and it only checks that the folder matches its own
baseline — not that the rules were followed.
