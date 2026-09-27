"""Pure conversion of one UTF-8 file into document metadata."""

from __future__ import annotations

from pathlib import Path

from .config import ScanConfig
from .hashing import read_and_hash
from .models import DocumentMetadata


def build_document_metadata(
    path: Path,
    relative_path: str,
    config: ScanConfig,
) -> DocumentMetadata:
    """Read, decode, hash, and measure one candidate file.

    ``UnicodeDecodeError`` and ``OSError`` intentionally propagate to the
    scanner, which turns them into structured per-file errors.
    """
    content = read_and_hash(path, config.chunk_size)
    text = content.data.decode(config.encoding)
    file_stat = path.stat()
    return DocumentMetadata(
        path=relative_path,
        extension=path.suffix.lower(),
        size_bytes=len(content.data),
        sha256=content.digest,
        modified_ns=file_stat.st_mtime_ns,
        encoding=config.encoding,
        line_count=len(text.splitlines()),
        word_count=len(text.split()),
        character_count=len(text),
    )
