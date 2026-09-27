"""Safe pathlib discovery and per-file metadata extraction."""

from __future__ import annotations

import logging
from collections.abc import Iterator
from pathlib import Path

from .config import ScanConfig
from .errors import RootPathError
from .metadata import build_document_metadata
from .models import DocumentMetadata, Record, ScanError, ScanResult

LOGGER = logging.getLogger(__name__)


def _relative_path(path: Path, root: Path) -> str:
    """Return a portable relative path for records and errors."""
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name or "."


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def iter_candidate_paths(
    root: Path,
    config: ScanConfig,
) -> Iterator[Path | ScanError]:
    """Yield supported regular files and discovery errors below *root*.

    Symlinks are never followed. A symlink resolving outside the requested
    root is surfaced as a structured error rather than being read.
    """
    pending = [root]
    while pending:
        directory = pending.pop()
        try:
            children = sorted(directory.iterdir(), key=lambda item: item.name)
        except OSError:
            yield ScanError(
                path=_relative_path(directory, root),
                code="directory_unreadable",
                message="could not list directory",
            )
            continue

        directories: list[Path] = []
        for child in children:
            relative = _relative_path(child, root)
            try:
                if child.is_symlink():
                    try:
                        resolved = child.resolve(strict=False)
                    except OSError:
                        yield ScanError(
                            path=relative,
                            code="symlink_error",
                            message="could not resolve symbolic link",
                        )
                        continue
                    if not _is_within(resolved, root):
                        yield ScanError(
                            path=relative,
                            code="path_outside_root",
                            message="path resolves outside requested root",
                        )
                    continue

                if child.is_dir():
                    directories.append(child)
                elif child.is_file() and child.suffix.lower() in config.extensions:
                    resolved = child.resolve(strict=True)
                    if _is_within(resolved, root):
                        yield child
                    else:
                        yield ScanError(
                            path=relative,
                            code="path_outside_root",
                            message="path resolves outside requested root",
                        )
            except OSError:
                yield ScanError(
                    path=relative,
                    code="path_error",
                    message="could not inspect path",
                )

        pending.extend(reversed(directories))


def _validate_root(path: Path) -> Path:
    requested = path.expanduser()
    try:
        root = requested.resolve(strict=True)
    except FileNotFoundError as exc:
        raise RootPathError(f"scan path does not exist: {path}") from exc
    except OSError as exc:
        raise RootPathError(f"scan path cannot be accessed: {path}") from exc

    if not root.is_dir() and not root.is_file():
        raise RootPathError(f"scan path is not a regular file or directory: {path}")
    return root


def _sort_records(records: list[Record]) -> tuple[Record, ...]:
    """Sort paths and keep an error after a document on an equal path."""
    return tuple(
        sorted(
            records,
            key=lambda record: (
                record.path,
                0 if isinstance(record, DocumentMetadata) else 1,
            ),
        )
    )


def scan_path(path: Path, config: ScanConfig | None = None) -> ScanResult:
    """Scan a file or directory and return documents plus structured errors.

    Invalid UTF-8 and ordinary per-file I/O failures do not abort the scan.
    Root validation failures raise :class:`RootPathError` because no useful
    scan could be performed.
    """
    scan_config = config or ScanConfig()
    root = _validate_root(path)
    records: list[Record] = []

    if root.is_file():
        candidates: Iterator[Path | ScanError]
        if root.suffix.lower() in scan_config.extensions:
            candidates = iter((root,))
        else:
            candidates = iter(())
        base = root.parent
    else:
        candidates = iter_candidate_paths(root, scan_config)
        base = root

    for candidate in candidates:
        if isinstance(candidate, ScanError):
            records.append(candidate)
            continue

        relative = _relative_path(candidate, base)
        try:
            document = build_document_metadata(candidate, relative, scan_config)
            records.append(document)
        except UnicodeDecodeError as exc:
            LOGGER.debug("invalid UTF-8 in %s at byte %s", relative, exc.start)
            records.append(
                ScanError(
                    path=relative,
                    code="invalid_utf8",
                    message=f"invalid UTF-8 at byte offset {exc.start}",
                )
            )
        except OSError:
            LOGGER.debug("could not read %s", relative, exc_info=True)
            records.append(
                ScanError(
                    path=relative,
                    code="file_unreadable",
                    message="could not read file",
                )
            )

    return ScanResult(records=_sort_records(records))
