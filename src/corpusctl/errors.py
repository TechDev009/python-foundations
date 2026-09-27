"""Exceptions raised by corpusctl's configuration and I/O boundaries."""


class CorpusError(Exception):
    """Base class for expected, user-facing corpusctl failures."""


class ConfigurationError(CorpusError):
    """Raised when a scan configuration is invalid."""


class RootPathError(CorpusError):
    """Raised when the requested scan root cannot be used."""


class ExportError(CorpusError):
    """Raised when an export cannot be written safely."""
