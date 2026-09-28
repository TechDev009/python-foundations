# corpusctl

`corpusctl` is a small, production-minded Python CLI for scanning UTF-8 text
and Markdown corpora. It emits deterministic JSONL metadata that is easy to
pipe into data-quality checks, duplicate detection, or later indexing jobs.
The first independent repository in this learning series focuses on Python
foundations without runtime dependencies outside the standard library.

## Install

Python 3.12 or newer is required. The project uses [uv](https://docs.astral.sh/uv/)
for environments, dependency locking, and command execution:

```bash
uv sync
```

The application has no runtime dependencies. Development dependencies are in
the `dev` dependency group.

## Run

By default, only `.txt` and `.md` files are included. Paths in output are
POSIX-style paths relative to the requested directory, so exports are portable
and stable across machines.

```bash
uv run corpusctl scan ./documents
uv run corpusctl stats ./documents
uv run corpusctl export ./documents --output ./metadata.jsonl
```

A single file may be scanned too. Repeat `--extension` to replace the defaults,
for example `--extension .rst --extension .adoc`. Use `-v` (or repeat it) for
stderr diagnostics; stdout remains machine-readable JSON.

```bash
uv run corpusctl scan ./documents --extension .rst
uv run corpusctl --verbose scan ./documents
```

### JSONL schema

`scan` and `export` emit one compact JSON object per line. Document records have
`type: "document"`, a relative `path`, lower-case `extension`, byte size,
SHA-256 digest, filesystem `modified_ns`, UTF-8 encoding, and line/word/
character counts. A file that cannot be decoded or read becomes an
`type: "error"` record with a relative path, stable error code, and message;
other files continue to be processed. `stats` emits one JSON object containing
aggregate counts, extension counts, and duplicate groups/files.

Output ordering is lexicographic by relative path. JSON object keys are sorted,
and exports are written atomically after the complete payload is flushed.

## Architecture

The `src/corpusctl` package separates boundaries from pure transformations:

- `models.py` contains immutable, typed dataclasses and JSON-friendly records.
- `config.py` validates extensions and UTF-8 scan settings.
- `scanner.py` uses `pathlib` discovery, deterministic ordering, and root
  containment checks; symlinks are never followed.
- `hashing.py` provides a chunk generator and SHA-256 file reads.
- `metadata.py` converts decoded bytes into file metadata and text counts.
- `stats.py` computes duplicate and aggregate statistics without I/O.
- `exporter.py` serializes JSONL and atomically replaces an output file.
- `cli.py` owns `argparse`, exit codes, and stdout/stderr behavior.

## Concepts covered

The example demonstrates `pathlib`, `dataclass(frozen=True, slots=True)`, type
aliases and annotations, generators, context managers (`with` for file and
atomic temporary-file lifetimes), exception translation, `argparse`, logging,
SHA-256 hashing, deterministic serialization, pytest fixtures, and a `src`
package layout.

## Test and quality checks

```bash
uv run pytest
uv run pytest --cov=corpusctl --cov-report=term-missing
uv run ruff check .
uv run ruff format --check .
uv run pyright
```

## Limitations

- Only text-like files selected by suffix are scanned; binary formats and
  archives are intentionally out of scope.
- Input is UTF-8 only. Invalid files are reported as structured errors rather
  than decoded with replacement characters.
- Symlinks are skipped to prevent escaping the requested root. Files can still
  change during a scan, as with any filesystem crawler.
- Contents are held in memory once per file to calculate text counts and a
  digest. Very large documents may need a streaming text implementation.
- File modification time is filesystem metadata and can differ when a corpus
  is copied, even if content is identical.

## License and security

This project is released under the MIT License. See [LICENSE](LICENSE).
Please read [SECURITY.md](SECURITY.md) before reporting a vulnerability.

## Public release / status

- **Local quickstart:** Run `uv sync --locked`, then use the commands in [Run](#run) to scan, summarize, or export a local corpus.
- **CI/tests:** GitHub Actions runs pytest with coverage, Ruff checks and formatting validation, and Pyright; the same checks are listed in [Test and quality checks](#test-and-quality-checks).
- **Limitations:** This release handles bounded UTF-8 text-like files and intentionally excludes binary formats, archives, and symlink traversal; see [Limitations](#limitations).
- **Production:** This is a local CLI, not a hosted deployment. Real production use requires operator-managed credentials and cloud/deployment infrastructure where applicable; none are included here.
