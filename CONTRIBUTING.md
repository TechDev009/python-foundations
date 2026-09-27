# Contributing

Thanks for helping improve `corpusctl`.

## Development setup

Use uv and the supported Python version:

```bash
uv sync
```

Make focused changes inside this repository. The project intentionally keeps
runtime dependencies at zero; add a dependency only with a clear justification.

## Checks

Run the full local checks before opening a pull request:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run pyright
```

Add or update tests for behavior changes. Keep CLI stdout machine-readable and
send diagnostics to stderr. Preserve deterministic ordering and stable JSON
field names. Do not include real corpus data in fixtures.

## Pull requests

Describe the behavior change, test coverage, and any compatibility or security
impact. Small, reviewable pull requests are preferred.
