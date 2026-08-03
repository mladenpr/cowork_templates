# Changelog

All notable changes to the templates in this repository.

## [1.0.0] — 2026-08-03

Initial release.

### Added

- `templates/sot-project/` — the immutable-SoT project skeleton: `CLAUDE.md`
  session bootstrap, `README.md` with working rules R1–R9, a `00_AI_context/`
  layer (PROJECT / INDEX / MANIFEST / WORKLOG / per-dataset context files), and
  the `01_SoT` → `02_derivatives` → `03_deliverables` → `04_tools` → `05_temp`
  pipeline directories.
- `templates/sot-project/04_tools/update_index.py` — regenerates `INDEX.md` and
  `MANIFEST.json`, preserving hand-written descriptions; `--diff` implements the
  session-start scan.
- `bin/new_project.py` — instantiates the template into a new folder, fills the
  placeholders, and writes the first index baseline.
- `docs/pattern.md`, `docs/adapting.md`, `docs/cowork-notes.md`.

### Changed from the source project

The template was extracted from a live engineering-tender repository. Relative
to that original:

- All project, client and discipline specifics removed; replaced with
  `{{PLACEHOLDER}}` substitution.
- `update_index.py` no longer hard-codes the project name in the `INDEX.md`
  title — it resolves it from `--name`, else the `PROJECT.md` heading, else the
  folder name.
- `update_index.py` gained `--hash`: compares sha256 rather than size+mtime, for
  synced folders where the sync client rewrites modification times. Manifests
  written with and without it remain mutually diffable.
- `update_index.py` now skips non-regular files defensively.
- R9 generalised from OneDrive to any sync client, with the placeholder-read
  failure spelled out.
- `PROJECT.md` and `WORKLOG.md` converted from filled-in project documents into
  prompted templates.
