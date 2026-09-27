"""Command-line behavior tests."""

from __future__ import annotations

import json
from pathlib import Path

from corpusctl.cli import main


def test_scan_command_emits_jsonl_and_returns_zero(
    tmp_path: Path, capsys: object
) -> None:
    (tmp_path / "README.md").write_text("hello", encoding="utf-8")

    assert main(["scan", str(tmp_path)]) == 0
    captured = capsys.readouterr()  # type: ignore[attr-defined]

    payload = json.loads(captured.out.strip())
    assert payload["path"] == "README.md"
    assert captured.err == ""


def test_missing_root_returns_nonzero(tmp_path: Path, capsys: object) -> None:
    missing = tmp_path / "does-not-exist"

    assert main(["scan", str(missing)]) == 2
    captured = capsys.readouterr()  # type: ignore[attr-defined]

    assert captured.out == ""
    assert "does not exist" in captured.err


def test_export_command_writes_deterministic_jsonl(tmp_path: Path) -> None:
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    output = tmp_path / "metadata.jsonl"

    assert main(["export", str(tmp_path), "--output", str(output)]) == 0
    lines = output.read_text(encoding="utf-8").splitlines()

    assert [json.loads(line)["path"] for line in lines] == ["a.txt", "b.txt"]
