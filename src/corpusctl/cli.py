"""Argparse command-line interface for corpusctl."""

from __future__ import annotations

import argparse
import json
import logging
from collections.abc import Sequence
from pathlib import Path

from .config import ScanConfig
from .errors import CorpusError
from .exporter import encode_record, write_jsonl
from .logging_config import configure_logging
from .scanner import scan_path
from .stats import summarize_result

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser without performing any I/O."""
    parser = argparse.ArgumentParser(
        prog="corpusctl",
        description=(
            "Scan UTF-8 text and Markdown documents for deterministic metadata."
        ),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="increase diagnostic logging (repeat for debug output)",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    def add_scan_arguments(command: argparse.ArgumentParser) -> None:
        command.add_argument("path", type=Path, help="file or directory to scan")
        command.add_argument(
            "--extension",
            dest="extensions",
            action="append",
            metavar="SUFFIX",
            help="file suffix to include; repeat to replace .txt/.md defaults",
        )

    scan_command = commands.add_parser("scan", help="emit one JSON record per file")
    add_scan_arguments(scan_command)

    stats_command = commands.add_parser("stats", help="emit aggregate JSON statistics")
    add_scan_arguments(stats_command)

    export_command = commands.add_parser("export", help="write scan records as JSONL")
    add_scan_arguments(export_command)
    export_command.add_argument(
        "--output",
        "-o",
        required=True,
        type=Path,
        help="destination JSONL file",
    )
    return parser


def _config_from_args(args: argparse.Namespace) -> ScanConfig:
    return ScanConfig.from_extensions(args.extensions)


def _emit_scan(path: Path, config: ScanConfig) -> int:
    result = scan_path(path, config)
    for record in result.records:
        print(encode_record(record))
    LOGGER.info(
        "scanned %d document(s), %d error(s)",
        len(result.documents),
        len(result.errors),
    )
    return 0


def _emit_stats(path: Path, config: ScanConfig) -> int:
    result = scan_path(path, config)
    payload = summarize_result(result).to_dict()
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    LOGGER.info(
        "scanned %d document(s), %d error(s)",
        len(result.documents),
        len(result.errors),
    )
    return 0


def _emit_export(path: Path, output: Path, config: ScanConfig) -> int:
    result = scan_path(path, config)
    write_jsonl(result, output)
    LOGGER.info("exported %d record(s) to %s", len(result.records), output)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a shell-friendly exit status."""
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.verbose)

    try:
        config = _config_from_args(args)
        if args.command == "scan":
            return _emit_scan(args.path, config)
        if args.command == "stats":
            return _emit_stats(args.path, config)
        if args.command == "export":
            return _emit_export(args.path, args.output, config)
    except CorpusError as exc:
        LOGGER.error("%s", exc)
        return 2

    parser.error(f"unknown command: {args.command}")
    return 2
