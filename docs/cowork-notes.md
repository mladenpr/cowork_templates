# Running this with Claude Cowork

Practical mechanics of working on a synced project folder through an agent's
device bridge. Written against Claude Cowork; most of it applies to any agent
that reaches your disk through a bridge rather than running on it.

## Where the session actually runs

A Cowork task runs either **in the cloud** (an isolated Linux container) or **on
your computer**, chosen when the task starts. It cannot be moved mid-session.

In cloud mode the session does not have your files. It reaches them through a
bridge: it lists your connected folder, *stages* copies of files into its own
workspace, works on the copies, and writes results back by committing them to an
absolute path on your disk. Two consequences follow, and both bite eventually.

**Staged copies are snapshots.** A file staged twenty minutes ago does not
reflect an edit you made since. Before deriving anything from an older staged
copy, re-check it against the device. This is the source of the "the AI is
working from the wrong version" experience.

**Shell commands run in the container, not on your machine.** Anything that
needs to run *against* your files either operates on staged copies in the cloud
workspace, or runs through the bridge's own shell — which has no network access.
Install-anything work happens in the container; file-in-place work happens on
the device. Do not mix the two filesystems for the same file.

## Cloud placeholders will stop a session dead

OneDrive Files On-Demand, Dropbox Smart Sync and iCloud Optimise Storage all
show a file in Finder whether or not its bytes are on disk. Reading a dehydrated
file through the bridge fails — OneDrive reports it as `Resource deadlock
avoided`, which is accurate and completely unhelpful.

The symptom: the agent says it cannot read a file that you can see, and possibly
that it "is a cloud placeholder (not downloaded)". The fix: right-click the
project folder in Finder → **Always Keep on This Device** (OneDrive), **Make
Available Offline** (Dropbox), **Keep Downloaded** (iCloud), wait for the solid
green checks, and tell the agent to retry.

Do this once, when the project folder is created. It is rule R9 for a reason.

## Getting files back onto your disk

Files the agent produces live in its workspace until they are explicitly
committed to a path on your machine. A file that was only *shown* to you in the
conversation is downloadable from the chat but is not on your disk — it will not
appear in the project folder, and the next session's manifest scan will not see
it.

If something the agent made should be in `02_derivatives/` or
`03_deliverables/`, say so explicitly, and confirm afterwards with a fresh
listing of the folder. Then regenerate the index.

There are size ceilings on the write-back path — on the order of tens of MB per
file and around 100 MB per batch. Large deliverables may need to come down
through the chat download instead, and be filed by hand.

## Deletion

The bridge cannot delete. `rm` on a mounted file fails with `Operation not
permitted`, by design. That is exactly rule R8: cleanup means `mv` into
`_to_delete/` and a report of what moved, and you empty the folder yourself.

Keep `_to_delete/` out of the manifest scan — the template's `update_index.py`
already skips it — otherwise every cleanup produces a wall of NEW entries at the
next session start.

## A session that behaves

Open a task on the project folder and give it one line:

> Read CLAUDE.md and run the session-start scan.

A well-behaved session then, without further prompting: reads `PROJECT.md` and
`README.md`, runs `update_index.py --diff`, reports NEW / CHANGED / MISSING,
ingests any new raw inputs into `01_SoT/` with their context md, regenerates
INDEX and MANIFEST, reads the last few WORKLOG entries, and only then asks what
you want done.

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
