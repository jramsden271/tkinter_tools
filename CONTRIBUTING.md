# Contributing

Conventions for working in this repo.

## Branching

- `main` is always in a working, releasable state. Don't commit directly to it.
- `dev` is the default branch and integration point for ongoing work. Don't commit directly to it either.
- Two kinds of branches come off `dev`:
  - **Session branches** — when asked to create a feature branch for today's session, name it `session<YYYYMMDD>` (e.g. `session20260721`). This is the default branch to work from during a session.
  - **Feature/fix branches** — for work with a more specific scope, name it `<type>/<short-description>`, e.g. `feat/queue-cancel-all`, `fix/entry-dnd-crash`.
- Open a PR into `dev` when the branch is ready. Merge via PR (squash or regular merge, your call) rather than pushing straight to `dev`.
- Delete the branch after merge.
- `dev` merges into `main` when a set of changes is ready to release.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<optional scope>): <short summary>

<optional body>
```

Types used in this repo:

- `feat` — new functionality (new rowbuilder, new widget behavior, new theme)
- `fix` — bug fix
- `refactor` — code change that doesn't change behavior
- `chore` — tooling, deps, repo housekeeping
- `docs` — documentation only
- `test` — adding or fixing tests

Rules:

- Summary in imperative mood, lowercase, no trailing period: `add drag-and-drop support`, not `Added drag and drop.`
- Keep the summary short (~70 chars). Use the body to explain *why*, not *what* — the diff already shows what changed.
- Scope is optional; use it when a change is isolated to one area, e.g. `feat(rowbuilders): add enum dropdown support`.

Examples from this repo, reworded:

```
feat(rowbuilders): add drag-and-drop entry support

Entries accept dropped files/text via tkinterdnd2 (optional dep).
```

```
fix(styles): match canvas background to active theme
```

```
refactor(rowbuilders): use frames instead of grid for layout
```

## Pull requests

- PR title follows the same Conventional Commits format as commit summaries.
- Description should cover what changed and why; link any relevant context.
- Keep PRs scoped to one logical change — don't bundle unrelated fixes/features.
- Session branches (`session<YYYYMMDD>`) are an exception: they can bundle whatever was worked on that session, since they track a day's work rather than a single change.
