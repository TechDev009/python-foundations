"""Logging setup kept separate from the pure scanning and export logic."""

from __future__ import annotations

import logging
import sys


def configure_logging(verbosity: int) -> None:
    """Configure stderr logging for the command-line entry point.

    JSON records are written to stdout, so diagnostics deliberately stay on
    stderr. Reconfiguring is safe for repeated calls from tests or embedding
    applications that invoke :func:`corpusctl.cli.main` more than once.
    """
    if verbosity <= 0:
        level = logging.WARNING
    elif verbosity == 1:
        level = logging.INFO
    else:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
        force=True,
    )
