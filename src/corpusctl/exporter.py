"""Deterministic JSONL serialization and atomic file export."""

from __future__ import annotations

import contextlib
import json
import os
import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import Protocol

from .errors import ExportError
from .models import Record, ScanResult


class TextWriter(Protocol):
    """Minimal write interface shared by files and in-memory streams."""

    def write(self, text: str, /) -> int: ...


def encode_record(record: Record) -> str:
    """Encode one record as compact, UTF-8-safe, sorted-key JSON."""
    return json.dumps(
        record.to_dict(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def iter_jsonl(result: ScanResult) -> Iterator[str]:
    """Yield JSONL lines in the scan result's deterministic order."""
    for record in result.records:
        yield encode_record(record)


def write_jsonl_stream(result: ScanResult, stream: TextWriter) -> None:
    """Write records to an already-open text stream."""
    for line in iter_jsonl(result):
        stream.write(line)
        stream.write("\n")


def write_jsonl(result: ScanResult, output: Path) -> None:
    """Atomically write a scan result to *output*.

    The temporary file is created next to the destination so ``os.replace`` is
    atomic on the same filesystem. Existing output is replaced only after the
    complete JSONL payload has been flushed.
    """
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=output.parent,
            prefix=f".{output.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary_path = Path(stream.name)
            write_jsonl_stream(result, stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, output)
        temporary_path = None
    except OSError as exc:
        raise ExportError(f"could not write export file {output}") from exc
    finally:
        if temporary_path is not None:
            with contextlib.suppress(OSError):
                temporary_path.unlink(missing_ok=True)
