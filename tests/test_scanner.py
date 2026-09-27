"""Scanner and pure statistics tests."""

from __future__ import annotations

import json
from pathlib import Path

from corpusctl.config import ScanConfig
from corpusctl.exporter import encode_record
from corpusctl.scanner import scan_path
from corpusctl.stats import summarize_result


def test_scans_text_and_markdown_with_metadata(tmp_path: Path) -> None:
    (tmp_path / "notes.md").write_text("# Hello\nworld\n", encoding="utf-8")
    (tmp_path / "plain.txt").write_text("one two\n", encoding="utf-8")
    (tmp_path / "ignored.py").write_text("print('ignored')", encoding="utf-8")

    result = scan_path(tmp_path)

    assert [document.path for document in result.documents] == ["notes.md", "plain.txt"]
    assert not result.errors
    assert result.documents[0].sha256
    assert result.documents[0].line_count == 2
    assert result.documents[0].word_count == 3
    assert result.documents[0].encoding == "utf-8"


def test_duplicate_files_are_grouped_by_sha256(tmp_path: Path) -> None:
    content = "same content\n"
    (tmp_path / "a.txt").write_text(content, encoding="utf-8")
    (tmp_path / "b.md").write_text(content, encoding="utf-8")

    result = scan_path(tmp_path)
    stats = summarize_result(result)

    assert stats.duplicate_groups == 1
    assert stats.duplicate_files == 2
    assert stats.extensions == {".md": 1, ".txt": 1}


def test_invalid_utf8_is_a_structured_error(tmp_path: Path) -> None:
    (tmp_path / "broken.txt").write_bytes(b"valid\xff\n")

    result = scan_path(tmp_path)

    assert not result.documents
    assert len(result.errors) == 1
    assert result.errors[0].code == "invalid_utf8"
    assert result.errors[0].path == "broken.txt"


def test_empty_directory_is_successful_and_empty(tmp_path: Path) -> None:
    result = scan_path(tmp_path)

    assert result.records == ()
    assert summarize_result(result).to_dict()["document_count"] == 0


def test_output_order_is_deterministic(tmp_path: Path) -> None:
    (tmp_path / "z.txt").write_text("z", encoding="utf-8")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "a.md").write_text("a", encoding="utf-8")

    first = [encode_record(record) for record in scan_path(tmp_path).records]
    second = [encode_record(record) for record in scan_path(tmp_path).records]

    assert first == second
    assert [json.loads(line)["path"] for line in first] == ["nested/a.md", "z.txt"]


def test_custom_extensions_replace_defaults(tmp_path: Path) -> None:
    (tmp_path / "document.rst").write_text("text", encoding="utf-8")
    (tmp_path / "document.txt").write_text("text", encoding="utf-8")

    result = scan_path(tmp_path, ScanConfig.from_extensions(["rst"]))

    assert [document.path for document in result.documents] == ["document.rst"]
