# Running this with Claude Cowork

Practical mechanics of working on a synced project folder with an agent.
Written against Claude Cowork running **locally**, which is what the template
now assumes; the cloud/bridge mode is covered at the end, because its
constraints are different in ways that matter.

## Where the session runs

A Cowork task runs either **on your computer** or **in the cloud**, chosen when
the task starts. It cannot be moved mid-session.

Running locally, the session has your actual filesystem. The project folder is
a real path, the shell is a real shell on your machine, and `04_tools/` scripts
run against the real tree rather than against copies. There is no staging step,
so there is no snapshot to go stale — the thing the session reads is the thing
on disk.

This is the right mode for this template. The session-start scan (R7) is the
mechanism the whole pattern rests on, and it only works when the agent can
actually run `update_index.py` over the actual folder.

## What you give up by running locally

The bridge used to be a safety property, not just a limitation. It could not
delete, could not overwrite in place, and could not touch anything outside the
folder you connected. Locally, none of that is true: `rm` works, overwrite
works, and R1's immutability and R8's no-deletion rule are conventions the
session follows because CLAUDE.md tells it to.

So the rules stop being descriptions of the environment and become the actual
control. That is worth saying out loud, because a rule that reads like a
statement of fact gets quietly dropped the moment the fact changes. R8 is now
the only thing between a misread instruction and an unrecoverable loss.

Two things reduce the blast radius without getting in the way:

- **OneDrive keeps version history and a recycle bin.** Both have retention
  limits, and neither is a substitute for not deleting things. Know how to
  reach them before you need them: right-click a file → Version History.
- **`_to_delete/` is cheap.** Emptying it takes ten seconds a month. That is
  the whole cost of the rule.

## Cloud placeholders

OneDrive Files On-Demand, Dropbox Smart Sync and iCloud Optimise Storage all
show a file in Finder or Explorer whether or not its bytes are on disk.

Locally this is no longer the hard failure it was through the bridge — a normal
process reading a dehydrated file triggers a download and gets the content. But
it is still worth pinning the folder ("Always Keep on This Device"), for two
reasons: a session-start scan across an unpinned project stalls while gigabytes
hydrate one file at a time, and offline the reads fail outright.

Do it once, when the project folder is created. It is rule R9.

## Documents open in Word or Excel

Office holds a lock on an open document and drops a `~$name.docx` beside it.
A locked file cannot be rewritten, and on Windows the error is unhelpful.

If a write fails, check whether you have the file open. The failure mode to
watch for is an agent working around the lock by writing to a slightly
different filename — that is how you end up with two versions of a deliverable
and no idea which is current. `update_index.py` skips `~$` files so they never
reach the manifest.

## The Microsoft 365 connector

If you have the Microsoft 365 connector enabled, the same OneDrive and
SharePoint content is reachable a second way — without your machine being
awake, which is genuinely useful.

It is not a way to work on this project. The connector has no shell, so
`update_index.py` cannot run, so the session-start scan does not happen and
nothing notices what changed. Worse, it *can* delete, move, rename and
overwrite items, which R8 forbids by whatever route.

Where it earns its place is fetching inputs that are not on your disk in the
first place: an attachment sitting in Outlook, a document in a SharePoint
library you have not synced, a file someone dropped in Teams. Pull it down,
then ingest it into `02_exchange/received/` through the normal R3 route,
locally, with its context md, its LOG row and an index regeneration. The
connector gets it to the door; the repository rules take over there.

## Getting documents into the project

Anything that arrives — chat upload, email attachment, a folder someone shared
— goes through R3: into `02_exchange/received/` if it is part of the
conversation or `01_basis/` if it is reference material, context md written, a
LOG row appended, `extract_text.py` run, INDEX and MANIFEST regenerated. The
point of making it a single named step is that otherwise files get analysed
where they landed and the project grows a second, undocumented record.

Files an agent produces are written directly to the path you name. Drafts go to
`03_working/drafts/`. Anything *leaving* the project goes through the issue
step (R5) — you ask for it by name, and the move, the naming, the LOG row and
the WORKLOG entry happen together. Confirm afterwards with a fresh listing.

## The text layer is what makes documents searchable

`03_working/_extracted/` holds one markdown file per document in the frozen
zones, built by `04_tools/extract_text.py`. Without it, "which document says X" is
unanswerable without opening every file, and every session that needs a figure
reparses a binary to get it.

Run `extract_text.py --report` when you want to know what state the frozen
zones are in: what has been extracted, what is stale, what is a scan needing OCR, what is
rights-managed and unreadable. It is the fastest way to find out that the
document you were about to rely on cannot actually be read.

PDFs need `pip install pypdf`. Word, Excel and PowerPoint need nothing.

## A session that behaves

Open a task on the project folder and give it one line:

> Read CLAUDE.md and run the session-start scan.

A well-behaved session then, without further prompting: reads `PROJECT.md` and
`README.md`, runs `update_index.py --diff`, reports NEW / CHANGED / MISSING and
any conflict or bad-name warnings, ingests new raw inputs into their zone with
their context md and LOG row, runs `extract_text.py`, regenerates INDEX and
MANIFEST, reads `LOG.md` and the last few WORKLOG entries, and only then asks
what you want done.

If it starts working before it has scanned, stop it. The scan is the only thing
standing between the session and a stale picture of the project.

## Persistent memory is not a substitute for the context layer

Cowork can carry project memory across sessions. It is genuinely useful for the
things the folder cannot express — your preferences, the reasoning behind a
decision, the state of a negotiation.

It is not a substitute for `00_AI_context/`. Memory is invisible to you unless
you ask for it, invisible to colleagues entirely, and lost if the project moves
to a different tool or a different person. The folder is the durable record.
Anything that would matter to a stranger picking the project up belongs in
`PROJECT.md`, a context md, or the WORKLOG — memory holds the rest.

## If you run in the cloud instead

Cloud mode reaches your disk through a bridge: it lists the connected folder,
*stages* copies into its own workspace, works on the copies, and writes results
back to an absolute path on your machine. Three consequences, all of which the
local mode removes:

- **Staged copies are snapshots.** A file staged twenty minutes ago does not
  reflect an edit you made since. This is the source of the "the AI is working
  from the wrong version" experience.
- **Shell commands run in the container, not on your machine**, so
  `update_index.py` does not straightforwardly run against the real folder.
- **Write-back has size ceilings** — on the order of tens of MB per file and
  around 100 MB per batch. Large deliverables may need to come down through the
  chat download and be filed by hand. A file that was only *shown* to you in
  conversation is not on your disk and the next scan will not see it.

Cloud mode also cannot delete: `rm` on a mounted file fails with `Operation not
permitted`. And a dehydrated placeholder is a hard error rather than a slow
read — OneDrive surfaces it as `Resource deadlock avoided`, which is accurate
and completely unhelpful. Pinning the folder removes that failure entirely.
