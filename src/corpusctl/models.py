"""Immutable domain models used by the scanner, stats, and exporter."""

from __future__ import annotations

from dataclasses import dataclass

type JsonScalar = str | int | float | bool | None
type JsonValue = JsonScalar | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]


@dataclass(frozen=True, slots=True)
class DocumentMetadata:
    """Metadata and text-derived counts for one successfully decoded file."""

    path: str
    extension: str
    size_bytes: int
    sha256: str
    modified_ns: int
    encoding: str
    line_count: int
    word_count: int
    character_count: int

    def to_dict(self) -> JsonObject:
        """Return the stable JSON representation for this document."""
        return {
            "type": "document",
            "path": self.path,
            "extension": self.extension,
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
            "modified_ns": self.modified_ns,
            "encoding": self.encoding,
            "line_count": self.line_count,
            "word_count": self.word_count,
            "character_count": self.character_count,
        }


@dataclass(frozen=True, slots=True)
class ScanError:
    """A structured, non-fatal error encountered while discovering a file."""

    path: str
    code: str
    message: str

    def to_dict(self) -> JsonObject:
        """Return the stable JSON representation for this scan error."""
        return {
            "type": "error",
            "path": self.path,
            "code": self.code,
            "message": self.message,
        }


type Record = DocumentMetadata | ScanError


@dataclass(frozen=True, slots=True)
class ScanResult:
    """Ordered records produced by one scan."""

    records: tuple[Record, ...]

    @property
    def documents(self) -> tuple[DocumentMetadata, ...]:
        """Return only successfully scanned documents."""
        return tuple(
            record for record in self.records if isinstance(record, DocumentMetadata)
        )

    @property
    def errors(self) -> tuple[ScanError, ...]:
        """Return only structured scan errors."""
        return tuple(record for record in self.records if isinstance(record, ScanError))
