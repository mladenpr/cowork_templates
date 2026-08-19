# Why the structure is shaped this way

Each rule exists because something goes wrong without it. This is the failure
mode behind each one.

## The distinction underneath everything

Documents in a project of this kind fall into two states. Some are **frozen**:
they arrived from outside, or they were sent outside, and either way they are a
record of an exchange that already happened. Nothing about them can change
without changing history. Others are **moving**: drafts, calculations, working
notes, things that are wrong until they are right.

Almost every failure in document-heavy work is one of these being mistaken for
the other — editing a record, or treating a draft as settled. The directory
layout is that distinction made visible, and the rules are what follows.

An earlier version of this template organised the same material by
*reproducibility*: regenerable outputs in one folder, issued documents in
another. That axis does not survive contact with real work. A review memo, a
chronology, an issue matrix — all hand-authored, none regenerable, none
issued — fit nowhere, and the promise that a folder could be safely purged
quietly became false. Frozen-versus-moving has no such gap.

## R1 — Frozen zones, and provenance as a lookup

**Failure it prevents:** losing the ability to prove what was exchanged.

Six weeks in you find that a quantity in the client's schedule is wrong. The
tempting move is to fix it in place — it is obviously wrong, the corrected file
is more useful, everyone knows what happened. Three months later, in a claim or
a negotiation, "what did they actually send us on the 24th" becomes the whole
question, and the answer no longer exists anywhere.

With document formats the rule has a sharper edge than it looks. Opening a
`.docx` in Word and saving it — with no edits at all — rewrites the whole
package and changes its hash. So does accepting a tracked change, resolving a
comment, or "just converting it to PDF". Each is an edit to evidence, and none
of them feels like one at the time.

**What you issued is frozen too**, and this is the half people miss. A document
that has been sent exists in someone else's inbox. It cannot be revised, only
superseded by a new revision, which is a new file. An issued document is
immutable for exactly the same reason a received one is: somebody else has a
copy, and the two must still match years later.

The second half of the rule is about direction. `received/` and `issued/` are
separate folders not for tidiness but because **"is this ours or theirs?" must
be answerable by looking**. In a dispute that question decides things. A
filename convention would not survive; a folder boundary does.

Which gives the corollary that catches everyone once: **your own document,
returned to you marked up, is a received document.** It goes in `received/`
even though most of its bytes are yours. It is theirs now, and their markup is
the content that matters.

None of this is enforced. A session running locally can edit anything in either
zone. The rule holds because it is followed.

## R2 — Every dataset gets context

**Failure it prevents:** the agent re-deriving, badly, what you already knew.

A PDF in a folder tells a model almost nothing: not who sent it, not whether it
superseded the previous one, not that page 2's subtotal is known to be wrong,
not that three downstream figures depend on it. Without that, every session
re-reads the raw file and re-forms an opinion — sometimes a different one from
last week's.

The granularity rule matters more than it looks. One md per *logical dataset*,
not per file. Per-file context fragments exactly the comparison you need: "how
did this figure move across the five revisions" is a question about the series,
and it should be answerable from one place.

**A negotiation thread is the case that proves the rule.** A subcontract
exchanged back and forth — your draft, their comments, your response, their
counter — is one dataset whose members alternate custody. The files live in
their direction folders, where provenance stays unambiguous; the *thread* lives
in the context layer, with a member table carrying date, direction, version,
path and what changed.

That last column is the one that earns the file. Six months later nobody
remembers why clause 12 was reworded, and no folder layout, log or file listing
can tell you. It is only recoverable if somebody wrote it down at the time.

## R3 — Ingestion

**Failure it prevents:** shadow inputs.

Files arrive through chat uploads, email attachments, someone dropping a folder
on the desktop. If they can be analysed where they land, they will be, and the
project develops a second undocumented source of truth. Making ingestion a
single named step means there is exactly one way in.

The zone decision — exchange or basis — is worth pausing on rather than
defaulting. Reference material that everybody has (a standard, a code) is not
part of your conversation with anyone, and filing it under `received/` inflates
the exchange record with things nobody sent you.

**Pasted text is the case the rule has to exclude.** Quoting an email into a
chat window to have it read or answered looks like arrival, and a session
reading R3 literally would file it. It should not, for two reasons that pull in
opposite directions and land in the same place.

The first is that most pasted email is not correspondence anybody needs to
keep. Filing all of it fills `received/` with transcripts of scheduling notes,
and a folder that holds everything that passed through a chat window no longer
means "this is the record". The filter is the value, and the filter is human —
the same seam as R5, where you decide a document is finished and the clerical
work is not yours to remember.

The second is subtler and is the reason the rule is written at all. A paste can
enter the project's *context layer* without ever becoming a file: a session
reads an email, works from it, and writes a WORKLOG entry or a `PROJECT.md`
line based on what it said. The project now holds a fact whose only source was
a chat message that no longer exists. The frozen zones guarantee provenance by
holding the artefact; nothing guarantees it for a sentence somebody typed. So
the boundary the rule draws is not "in the folder or not" but "has provenance
or not", and the second is the one that can be crossed silently.

What follows from both is a transcript written deliberately, by the person who
decided it mattered, declaring itself a copy — with what it left behind, and
which attachments it names but does not hold. Once written it is a file that
arrived, and R3 applies to it unchanged.

## R4 — The exchange log

**Failure it prevents:** a conversation you can only reconstruct by guessing.

The files tell you what exists. They do not tell you what was answered, what is
outstanding, or what went out under which cover. Directory listings are sorted
by name, correspondence happens in time, and reconstructing a chronology from
file timestamps is a guess about precisely the facts someone will later dispute.

`LOG.md` is one table with both directions in it, because the exchange is one
conversation and splitting it across two folders makes the shape invisible. It
answers "what did we send on the 24th, and what came back", "which revision is
current", and "what have they still not replied to" — the last of which is the
question that gets asked in a progress meeting and cannot be derived from a
folder at all.

The rule that a row is written *at the moment of the event* is the whole thing.
A log written up afterwards is a reconstruction, and a reconstruction of a
record is not a record.

## R5 — Issuing is an explicit step

**Failure it prevents:** a project that cannot say what it sent.

The natural workflow is to finish a draft, rename it, and send it. Every part of
that is invisible: no record of the recipient, the transmittal, the date, or
which draft became which revision. The next session finds a file it has never
seen and no way to know it left the building.

Making "issue this" an instruction rather than a rename splits the work along
the right seam. **The judgement is yours** — whether a document is finished is
not a decision to automate, and should not be inferred from a filename that
happens to contain a date. **The bookkeeping is not yours**: move, rename to the
convention, file the PDF with its source, log row, WORKLOG entry, reindex. Six
steps, all mechanical, all easy to skip at six o'clock on a Friday, and the log
row is the one that matters most and gets skipped first.

This is also the only route into `02_exchange/issued/`, which is what lets that
folder mean something exact: this is what left the building. Nothing else is in
there — not drafts, not internal cost models, not "final_v3". The folder you
send from contains only things already sent.

## R6 — Working is mutable, and singular

**Failure it prevents:** draft sprawl, and a live document nobody can identify.

The instinct when revising is to keep the old one — `report_v2`, `report_v2a`,
`report_final`, `report_final_reviewed`. Within a week nobody can say which is
current, and an agent asked to "update the report" has to guess.

One live draft per deliverable, revised in place. Its history is the sync
client's version history, which is what that feature is for; the *reasoning*
behind each change belongs in the WORKLOG, which is where you would actually
look for it. Neither is served by a folder of near-identical files.

This is only safe because of R1: the draft is not evidence and never was. The
version that matters was frozen the moment it was issued.

## R7 — Index, manifest, and the zone-aware scan

**Failure it prevents:** search-based exploration, silent divergence, and a scan
you have learned to ignore.

`INDEX.md` is for the agent to read instead of grepping the tree. The design
decision that makes it work is that hand-written descriptions survive
regeneration: machine-maintained in structure, human-maintained in content, so
the knowledge accumulates rather than being flattened on every rebuild.

`MANIFEST.json` is the machine half. Size and mtime are enough in a local
folder; in a synced one they are not, because sync clients rewrite modification
times when hydrating a file or resolving a conflict, producing CHANGED reports
for files nobody touched. That is what content hashing is for, and two details
make it usable rather than merely correct. It is **sticky** — a flag you must
remember every time is a flag that will eventually be forgotten, and forgetting
it silently returns you to the noisy mode. And hashes are **reused** when size
and mtime both match, so a project of PDFs is not re-read in full every session.

**The zone-awareness is what keeps the scan readable.** Under R6 your live draft
changes constantly. A scan that reports it as CHANGED with the same urgency as a
moved file in `02_exchange/` trains you to skim past both, and then the one that
mattered goes past unread. So frozen-zone movement is reported first, separately,
and named as something to stop for; everything else is routine.

## R8 — Never delete; stage instead

**Failure it prevents:** irreversible action from a process that misreads
context.

This rule began as a description. An agent working through a cloud file bridge
could not delete — `rm` failed with `Operation not permitted` — so R8 merely
wrote down what the environment already guaranteed.

Running locally, the environment guarantees nothing. Delete works, overwrite
works, rename works. The rule survives the change but its status does not: it
has gone from describing a constraint to being the constraint, and it is now the
only thing between a misread instruction and a loss you cannot undo.

That is worth being explicit about, because rules phrased as facts about the
world get dropped silently when the world changes.

## R9 — Sync discipline

**Failure it prevents:** several specific, real, and initially baffling
problems.

*Cloud placeholders.* Files-on-demand shows every file whether or not its
content is on disk. Locally a read triggers a download and eventually succeeds —
better than the hard error a cloud bridge gets, but a session-start scan across
an unpinned project stalls while gigabytes hydrate one file at a time, and
offline it fails outright.

*Sync-conflict copies.* When the same file is edited in two places, OneDrive
does not merge and does not ask — it writes `<name>-<YourComputerName>.<ext>`
and syncs both. In a frozen zone that is a quiet catastrophe: two versions of
the same received document, and the scan reports the copy as NEW, which under R3
means "ingest it". The scan therefore names conflict copies specifically and
refuses to treat them as routine.

*Names that stop syncing.* SharePoint and OneDrive reject `" * : < > ? / \ |`,
leading and trailing spaces, trailing dots, the reserved DOS device names, and
any item whose URL exceeds 400 characters. Engineering document names run long
and often carry a colon after the discipline. A file that fails to sync is worse
than one that never arrived, because it is present on your machine and absent
everywhere else.

*Office locks.* Word and Excel hold a lock on an open document. A write fails,
and the tempting workaround — write to a slightly different name — leaves you
with two versions and no way to tell which is current.

*Git inside a synced folder.* Git assumes exclusive control of `.git/`; a sync
client assumes it may upload, version and resurrect anything under its root.
Running both over one directory produces corrupted object stores and phantom
conflicts.

## R10 — Document handling

**Failure it prevents:** a project whose contents cannot be searched, and
documents whose condition has to be rediscovered every session.

A folder of PDFs and Word files is opaque in a way a folder of text files is
not. `INDEX.md` says what each file is in one line; the context md says what the
dataset is in a paragraph. Neither can answer "which document says X", and
nothing in the tree can be grepped. So every session that needs a figure opens a
binary, reparses it, spends its context doing so, and forgets the result.

`03_working/_extracted/` fixes this by construction: one markdown file per
document, mirroring the frozen zones, rebuilt by one command. The point is not
that extraction is clever; it is that the searchable form of the project should
be a *file*, not something an agent reconstructs from scratch every session.

### The failure the text layer introduces

Every index risks being mistaken for the thing it indexes, and here the risk is
real: a session that greps the extraction and quotes what it finds has silently
substituted a lossy copy for the document. So the rule has a second half —
**find it in the extraction, read it in the source** — and the extracted files
each open with a banner saying so, because that banner is what the agent
actually reads.

What extraction cannot carry, none of which announces itself in the output:

- **Layout and pagination.** Page numbers are gone, so a citation of the form
  "page 12" cannot be resolved. Multi-column PDFs interleave. Tables in PDFs
  come out as prose.
- **Anything that is not text.** Drawings, figures, stamps, signatures,
  annotations. A drawing sheet extracts to its title block and nothing that
  matters.
- **Reconstructed values.** Word stores a list's *scheme*, not its numbers, and
  Excel stores a date as a serial with a display format. Both are rebuilt —
  correctly for the ordinary case, wrongly for restarts, numbering overrides and
  unusual format codes. A reconstructed clause number is exactly the kind of
  error that looks authoritative, which is why documents using it are flagged.
- **Fidelity of the PDF reader.** Word, Excel and PowerPoint are parsed from
  their own XML and are near-exact. PDFs go through `pypdf`, whose text output
  is adequate for search and unreliable for structure.

### Condition

Three properties decide whether a document can be used at all, and each is
expensive to rediscover and cheap to write down once:

- **Does the PDF have a text layer**, or is it a scan needing OCR? A scanned
  drawing looks identical to a born-digital one in a file listing.
- **Does the Word file carry tracked changes or comments?** In a received
  document that markup is frequently the finding itself. It also means the
  document must never be "cleaned up" — accepting the changes destroys the
  record, and it is the kind of tidying that feels helpful.
- **Is the file rights-managed?** An Office document with an encrypting
  sensitivity label is not a readable package; it is an OLE container only
  authenticated Office can open. In a Microsoft 365 tenant this is the most
  common reason a document cannot be processed, and it produces baffling errors
  when it is not named.

## The authoring variant — R11 and R12, and what changes in R2, R6 and R7

`cowork-author` exists because the consultant pattern is silent on the middle
of a document's life. Its rules are the consultant's, with three changed and
two added, and each addition has a failure behind it.

### R2 — a document md, not just dataset mds

**Failure it prevents:** every session re-deriving what the document is
supposed to be, and re-deriving it differently.

A dataset md describes something that arrived. Nothing in the consultant
pattern describes the thing being *made*: what it is for, whose form it
borrows, which requirements it must answer and where, how far each section has
got, what you have said you want, what feedback is still open, which passages
are yours and must not be touched. Without that file, a session reads the
draft and the WORKLOG and forms an opinion — a different opinion from last
week's — and the document drifts in tone and structure from session to
session. The document md is read before the draft is opened, and two of its
tables are read by their gaps: a coverage row still `open` before issue is a
finding, and a feedback item still `open` is a thing you said that has not been
done.

### R6 — the draft on disk is the truth

**Failure it prevents:** the agent overwriting your hand edits with its own
memory of the document.

The user editing the draft by hand is not an exception in this workflow; it is
step five of six. Two things go wrong when a session does not expect it. The
first is that the session regenerates the draft — from what it remembers, from
the document md, from a markdown master it kept for its own convenience — and
your edits are gone. The second is that it reads a stale copy: an extraction of
the draft made last session, which is why the live draft is never mirrored into
the text layer. Both are prevented by the same sentence: read the draft before
you write it, and never keep a second copy of its text that could be mistaken
for it.

The markdown-master temptation deserves naming, because it is the reasonable
engineering choice — easier to revise, easier to diff — and it is wrong here
for one reason: it lasts until your first hand edit of the `.docx`, and from
then on there are two truths and the agent will trust the wrong one.

### R7 — `DRAFT EDITED` as its own category

**Failure it prevents:** the one `CHANGED` that matters being skimmed past
with the ones that do not.

The consultant scan reports a change in the working zone as routine, which is
right there: a draft being drafted. In the authoring loop a change to the live
draft *at session start* cannot be routine, because the session reindexes
after every operation — so a change visible at the start happened since the
last index, which means outside a session, which means you. The scan says so in
its own section, and the session's first act is `draft_diff.py`: what did you
change, by section, so that it can record it, mark those passages
`user-edited`, and work around them.

### R11 — revisions are frozen by an explicit step, and are the record

**Failure it prevents:** a document with fifteen revisions and no history.

The consultant's R6 says the draft's history is the sync client's version
history. For a bill of quantities that is adequate. For a document that goes
round fifteen times it is not: sync history gives you bytes with timestamps —
no "what changed and why", no "what did the reviewer see", no "which revision
did we send Jane and has she come back". The record needs a frozen snapshot
per revision, a log row saying what it was for and what changed, and a place
for what came back on it.

The rule has the same shape as R5 because it solves the same problem one
level in. **The judgement is yours** — when a state of the draft is worth
keeping is not a decision to automate, and a session that froze a revision
every time it finished editing would rebuild the `report_v2_final_reviewed`
sprawl that R6 exists to prevent. **The bookkeeping is not yours**: copy,
rename, log row, WORKLOG entry, status updates, reindex. What the session
*does* do on its own initiative is offer: before you edit by hand (so the diff
afterwards is clean), before anyone else sees the draft (so a return has a
revision to be on), before issue.

Returns go in `Rnn/returns/` and not in `02_exchange/received/`, even though a
colleague's marked-up copy is "theirs" in every sense the consultant's R1 uses,
because "they" are inside the building. `02_exchange/issued/` means "this left
the building" and is trusted because it has no exceptions; putting internal
review traffic through the exchange would make "did we send this to the
client?" a judgement again.

### R12 — form is borrowed, content is not

**Failure it prevents:** another client's confidential content appearing in
this client's document.

An example and a template are the two inputs that make the authoring loop
work and the two that carry a hazard no other input does. A sample from a
past project used as the shell still has the past project in it — a client
name in the footer, a figure in a table, a paragraph of scope that was never
rewritten. An example proposal is imitated for its structure and tone, and a
model that is good at imitation will, without a rule, imitate a sentence. The
failure is invisible in review because the offending text is fluent and
plausible; it is found by the recipient, or by the other client.

The rule makes the boundary mechanical. The shell is copied, never edited; a
sample is stripped to its skeleton at instantiation and the document md
records what was kept. An example's context md lists its **terms to check
for** — names, figures, references — and the draft is grepped for them before
a revision leaves your hands and always before issue. With the examples in the
text layer that is one command, and it is the difference between catching the
leak and recalling it.

## What the pattern does not do

It does not version project instances. Sync-client history is coarse and
per-file; if a project genuinely needs commits, tags and branches, keep it in a
git repository *outside* the synced drive and accept that you have given up the
sharing model.

It does not enforce anything. Every rule is a convention held up by CLAUDE.md
being read at session start and by you noticing when it is not. The scan is the
only automated check, and it only checks that the folder matches its own
baseline — not that the rules were followed.
