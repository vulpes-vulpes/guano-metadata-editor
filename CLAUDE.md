# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A desktop GUI tool for wildlife biologists to read, add, and edit GUANO metadata (an open standard for bat acoustic monitoring) embedded in WAV file recordings. Built on the `guano-py` library, distributed as PyInstaller standalone executables.

## Commands

```bash
# Activate the project virtualenv (contains guano and its bundled scripts)
source .venv/bin/activate

# Run the application
python guano_gui.py

# Command-line usage examples (alternative to the GUI)
python example_usage.py

# Diagnostic scripts for inspecting WAV internals
python inspect_wav_chunks.py <file.wav>   # list all RIFF chunks in a file
python parse_list_chunk.py <file.wav>     # decode LIST/INFO chunk contents

# Build the standalone app locally
pip install pyinstaller && pyinstaller --clean guano_editor.spec
```

There is no test suite and no linter configured. Releases are built automatically by GitHub Actions (`.github/workflows/build-release.yml`) for macOS/Windows/Linux when a `v*` tag is pushed; update `CHANGELOG.md` when releasing.

Note (macOS): if Python crashes on launch, it is usually tkinter missing from the Python build — use python.org Python or Homebrew's `python-tk`.

## Architecture

Three layers, top to bottom:

- **`guano_gui.py`** — tkinter GUI. `GuanoGUI` is the main window. Edits are not applied immediately: the three dialogs — `EditDialog` (common fields), `EditVariableFieldsDialog` (standardize variable fields to one value), and `AddFieldDialog` (add standard/custom fields) — each push entries onto a **pending changes queue** (`self.pending_changes`, tuples of `(field, value, change_type)` where change_type is `[C]`, `[V→C]`, or `[NEW]`). Nothing is written until the user clicks "▶ Apply All Changes", which applies the whole queue in a single pass through all files with a progress bar.
- **`guano_metadata_manager.py`** — `GuanoMetadataManager` holds the loaded file set and classifies every metadata field as *common* (identical value in all files) or *variable* (differs per file); the GUI's two tabs mirror this split. Loading and updating are parallelized with `ThreadPoolExecutor` (adaptive worker count, batches of 100) and deliberately memory-optimized for 10,000+ file datasets: only plain metadata dicts are kept, never `GuanoFile` objects. Also holds the GUANO spec constants used by the add-field dialog: `GUANO_STANDARD_FIELDS` (all 23 spec fields with types/descriptions), `GUANO_RESERVED_NAMESPACES`, and `GUANO_PROTECTED_FIELDS` (fields like `GUANO|Version` that require explicit confirmation before modification). `_coerce_field_value()` converts entry text to the spec type before writing.
- **`wav_chunk_preserver.py`** — low-level RIFF chunk reader/writer. Exists because guano-py's own `write()` drops non-GUANO chunks (e.g. LIST/INFO). `safe_guano_write()` is the only write path: it copies the file to a temp file, lets guano-py write metadata there, extracts just the updated `guan` chunk, splices it into the original file's full chunk list, then atomically replaces the original. All edits must go through this function — never call `GuanoFile.write()` directly on user files.

## Conventions and Constraints

- Deletion has two forms: a "Delete field" checkbox in the edit dialogs (shown as `<delete>` in the queue) or an emptied value; both reach the manager as `None`/empty meaning "delete this field".
- Field names must not contain `:` or newlines (would corrupt the GUANO text format); custom user fields should use the `User|` namespace.
- The manager reads guano-py's private `_md` dict to enumerate namespaced fields — be careful if upgrading the `guano` dependency.
- There is deliberately **no built-in backup feature** (removed in 1.2.0 in favor of a prominent warning telling users to keep their own backups) — don't reintroduce one without discussion.
- Safety is a core product value: symlink-containment checks during directory load, macOS `._` AppleDouble files filtered out, a 256 MB chunk-size cap, and multi-step confirmations before writing. Preserve these behaviors when changing write paths.
- Users are field biologists, not developers — error messages and dialogs should stay non-technical.

## Workflow Notes

- The maintainer works from multiple machines: **check `git fetch`/status early** — local `main` has previously been many commits behind `origin/main`, and the app they run may be built from newer code than the checkout.
