# Security policy

## Scope

`corpusctl` reads files from a path explicitly supplied by its caller and
writes an explicitly supplied JSONL destination. It does not execute corpus
content or make network requests. Symlinks are not followed during directory
traversal, and resolved candidates are checked against the requested root.

## Reporting a vulnerability

Please do not disclose security-sensitive details in a public issue. Report the
issue privately to the repository maintainers with a description, reproduction
steps, affected version, and a suggested mitigation if available. Maintainers
will acknowledge reports as soon as practical and coordinate a fix and release.

Do not include confidential corpus contents in a report; a minimal synthetic
fixture is preferred.
