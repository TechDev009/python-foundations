"""JSONL exporter tests."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

from corpusctl.exporter import write_jsonl_stream
from corpusctl.scanner import scan_path


def test_jsonl_stream_has_one_record_per_line(tmp_path: Path) -> None:
    (tmp_path / "doc.txt").write_text("hello", encoding="utf-8")
    stream = StringIO()

    write_jsonl_stream(scan_path(tmp_path), stream)

    assert stream.getvalue().count("\n") == 1
    assert stream.getvalue().endswith("\n")
