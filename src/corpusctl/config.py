"""Validated configuration for corpus scans."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Final

from .errors import ConfigurationError

DEFAULT_EXTENSIONS: Final[frozenset[str]] = frozenset({".md", ".txt"})
DEFAULT_CHUNK_SIZE: Final[int] = 1024 * 1024


def normalize_extension(value: str) -> str:
    """Normalize a user extension such as ``md`` or ``.MD``."""
    extension = value.strip().lower()
    if not extension:
        raise ConfigurationError("file extensions cannot be empty")
    if not extension.startswith("."):
        extension = f".{extension}"
    if extension == "." or "/" in extension or "\\" in extension:
        raise ConfigurationError(f"invalid file extension: {value!r}")
    return extension


@dataclass(frozen=True, slots=True)
class ScanConfig:
    """Options that affect discovery and UTF-8 decoding."""

    extensions: frozenset[str] = DEFAULT_EXTENSIONS
    encoding: str = "utf-8"
    chunk_size: int = DEFAULT_CHUNK_SIZE

    def __post_init__(self) -> None:
        normalized = frozenset(normalize_extension(item) for item in self.extensions)
        if not normalized:
            raise ConfigurationError("at least one file extension is required")
        if self.encoding.lower() != "utf-8":
            raise ConfigurationError("corpusctl currently supports UTF-8 only")
        if self.chunk_size < 1:
            raise ConfigurationError("chunk_size must be positive")
        object.__setattr__(self, "extensions", normalized)
        object.__setattr__(self, "encoding", "utf-8")

    @classmethod
    def from_extensions(cls, values: Sequence[str] | None) -> ScanConfig:
        """Build a config from repeated CLI extension options."""
        if not values:
            return cls()
        return cls(extensions=frozenset(values))
