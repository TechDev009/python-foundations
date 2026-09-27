"""Streaming file hashing helpers."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import BinaryIO

from .config import DEFAULT_CHUNK_SIZE


@dataclass(frozen=True, slots=True)
class HashedContent:
    """Bytes read from a file and their SHA-256 digest."""

    data: bytes
    digest: str


def iter_chunks(
    stream: BinaryIO, chunk_size: int = DEFAULT_CHUNK_SIZE
) -> Iterator[bytes]:
    """Yield non-empty chunks until a binary stream is exhausted.

    This small generator keeps hashing independent from the scanner and makes
    the memory/read trade-off explicit at the file boundary.
    """
    if chunk_size < 1:
        raise ValueError("chunk_size must be positive")
    while chunk := stream.read(chunk_size):
        yield chunk


def read_and_hash(path: Path, chunk_size: int = DEFAULT_CHUNK_SIZE) -> HashedContent:
    """Read *path* once while computing its SHA-256 digest."""
    digest = sha256()
    content = bytearray()
    with path.open("rb") as stream:
        for chunk in iter_chunks(stream, chunk_size):
            digest.update(chunk)
            content.extend(chunk)
    return HashedContent(data=bytes(content), digest=digest.hexdigest())
