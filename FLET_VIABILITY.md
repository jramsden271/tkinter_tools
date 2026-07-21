# Flet Frontend Viability Report

Experimental Flet rewrite of the tkinter front end, done for [issue #3](../../issues/3) on branch `feat/flet-frontend`. Flet 0.86.1 (the "1.0 Beta" API line), tested on Windows desktop.

## Summary

**Viable, with caveats.** All functionality from the tkinter app was reproduced and verified working live: dynamic form generation from method signatures, the None/Default/Current value state per field, the serial task queue, unlimited-concurrency async execution, live status/spinner polling, a Tasks dialog (queue + running async list, cancel/clear), a Help dialog (parameter table + docstring summary), right-click context menu (Run/Run Asynchronously/Help), and F-key shortcuts.

One feature (file/path picker with a native OS dialog) had to be dropped to a plain text field — not a design limitation, but a bug in the installed Flet desktop client (see below).

The backend (`core/`, `helpers/task_queue.py`, `helpers/conjugator.py`) was reused **completely unmodified** — zero changes to any existing file. The Flet frontend lives entirely in new files/packages and runs side by side with the tkinter app.

## What ported cleanly

- Dynamic form generation from `inspect.signature` — one row per parameter, driven by the same `MethodCollection`/`ParameterState` metadata.
- The None/Default/Current 3-way state per entry (a `ttk.Combobox` in tkinter → an `ft.Dropdown` in Flet), including the "typing snaps back to Current" and "picking Default fills the field" behaviors.
- The serial task queue (`TaskQueue`) and unlimited-concurrency async execution (`AsyncTaskTracker` + a thread per call) — reused with zero code changes.
- Snapshot-at-click-time argument capture (`create_submit_action`) — works identically, since Flet's `on_click` handlers run on the main/UI thread just like tkinter's `command=`.
- The Help dialog's parameter table is arguably *nicer* in Flet — `ft.DataTable` gives real column headers and borders for free, versus tkinter's manual `grid()`-based approximation.
- Theming: Flet's `page.theme_mode` + `ft.Theme(color_scheme_seed=...)` reused the exact same `LightStyle`/`DarkStyle` color dicts already in `styles/`, with far less code than tkinter's manual `option_add` cascade.

## Real issues hit (and how they were resolved)

1. **`ft.FilePicker` triggers "Unknown control: FilePicker" in the installed `flet-desktop` 0.86.1 client.** Confirmed via an isolated 6-line repro completely independent of this codebase — a genuine client-side gap between the Python SDK (which exposes the class) and the bundled desktop renderer, not a usage mistake. Resolved by dropping `PathEntry` to a plain text field for now (per your call) rather than fighting the client bug.
2. **API drift from what's documented online vs. what's actually installed.** `page.open()`/`page.close()` (referenced in some docs/blog posts) don't exist in 0.86.1 — the real API is `page.show_dialog(dialog)` / `page.pop_dialog()`. Similarly, `ElevatedButton`/`TextButton` are deprecated in favor of `ft.Button`, and neither accepts a `text=` kwarg — content is passed via `content=` (or positionally). Caught these by directly inspecting the installed package rather than trusting documentation.
3. **Threading discipline is real, not optional.** Flet's own docs warn that raw threads calling `.update()` directly can be flaky. This build funnels all worker-thread → UI communication through a single `page.run_task` polling loop (250ms cadence) that reads plain Python state and does the only `page.update()` calls — worker/queue callbacks never touch `ft.Control`s directly. This sidesteps the issue entirely and turned out simpler than tkinter's per-callback `.after(0, ...)` marshaling.
4. **Two logic bugs caught by testing, not by inspection:**
   - `FletEntry.pull_value()` had an early-return guard (`if self.dropdown is None or self.field is None: return`) that skipped pulling the field value entirely whenever a parameter had no default and couldn't be None (so no dropdown was built) — every such field silently submitted `None`. Caught by a headless round-trip test exercising `collect_final_args` end to end.
   - `TasksDialog.refresh()` mutated `ft.Column.controls` without calling `.update()`, so the dialog's *first* render was correct but live updates while already open never reached the client. Fixed with a `_safe_update()` helper (try/except around `.update()`, since Flet raises rather than returning a boolean for "not yet attached to a page").

## What's different from the tkinter version (by design)

- **No independent "Toplevel" windows.** Flet has no first-class multi-window support on desktop; Help and Tasks are `AlertDialog`s within the single window rather than separate windows. Functionally equivalent, visually different.
- **Cut/Copy/Paste context menu is native, not custom.** Flet's `TextField` gets the OS's built-in text-selection menu for free; the tkinter version's hand-rolled "Clear"/"Clear & Paste" items weren't reproduced, since the None/Default dropdown already covers "reset to a known state."
- **Path entry is a plain text field**, not a file/folder picker with a Browse button, due to the `FilePicker` client bug above.

## Recommendation

Flet is viable as a long-term replacement if the visual/UX changes above are acceptable and the `FilePicker` bug either gets fixed upstream or a workaround (older/newer flet-desktop version) is found. The amount of new code needed was modest — a parallel `rowbuilders_flet/` package mirroring the existing `rowbuilders/` shape, plus `flet_builder.py` and `flet_ui/` mirroring `tkinter_builder.py`/`help_window.py`/`tasks_window.py` — and the backend needed zero changes, confirming the original tkinter app's model/view split was already well-suited to a frontend swap.

The main ongoing cost would be Flet's youth as a framework (this is its first post-1.0-beta line) and the gap between its documentation and actual installed behavior, which means verifying against the real installed version rather than trusting docs/tutorials is necessary — as this session did repeatedly.
