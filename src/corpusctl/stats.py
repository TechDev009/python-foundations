"""Pure aggregate statistics for scan records."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

from .models import DocumentMetadata, Record, ScanResult


@dataclass(frozen=True, slots=True)
class CorpusStats:
    """Aggregate counts derived from documents and structured scan errors."""

    document_count: int
    error_count: int
    total_bytes: int
    total_lines: int
    total_words: int
    total_characters: int
    duplicate_groups: int
    duplicate_files: int
    extensions: dict[str, int]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-friendly, deterministically ordered mapping."""
        return {
            "document_count": self.document_count,
            "error_count": self.error_count,
            "total_bytes": self.total_bytes,
            "total_lines": self.total_lines,
            "total_words": self.total_words,
            "total_characters": self.total_characters,
            "duplicate_groups": self.duplicate_groups,
            "duplicate_files": self.duplicate_files,
            "extensions": dict(sorted(self.extensions.items())),
        }


def find_duplicate_groups(
    documents: Iterable[DocumentMetadata],
) -> dict[str, tuple[str, ...]]:
    """Group document paths by digest, retaining only duplicate digests."""
    paths_by_digest: defaultdict[str, list[str]] = defaultdict(list)
    for document in documents:
        paths_by_digest[document.sha256].append(document.path)
    return {
        digest: tuple(sorted(paths))
        for digest, paths in sorted(paths_by_digest.items())
        if len(paths) > 1
    }


def summarize(records: Iterable[Record]) -> CorpusStats:
    """Compute stable aggregate statistics without performing I/O."""
    documents: list[DocumentMetadata] = []
    error_count = 0
    extension_counts: Counter[str] = Counter()
    for record in records:
        if isinstance(record, DocumentMetadata):
            documents.append(record)
            extension_counts[record.extension] += 1
        else:
            error_count += 1

    duplicates = find_duplicate_groups(documents)
    return CorpusStats(
        document_count=len(documents),
        error_count=error_count,
        total_bytes=sum(document.size_bytes for document in documents),
        total_lines=sum(document.line_count for document in documents),
        total_words=sum(document.word_count for document in documents),
        total_characters=sum(document.character_count for document in documents),
        duplicate_groups=len(duplicates),
        duplicate_files=sum(len(paths) for paths in duplicates.values()),
        extensions=dict(extension_counts),
    )


def summarize_result(result: ScanResult) -> CorpusStats:
    """Convenience wrapper for a completed scan."""
    return summarize(result.records)
