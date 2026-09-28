# Security policy

## Scope

`corpusctl` reads files from a path explicitly supplied by its caller and
writes an explicitly supplied JSONL destination. It does not execute corpus
content or make network requests. Symlinks are not followed during directory
traversal, and resolved candidates are checked against the requested root.

## Reporting a vulnerability

Do not disclose security-sensitive details in a public issue. Once this repository is
published, use its GitHub **Security** tab and **Report a vulnerability** form. If
private reporting is not enabled yet, contact the repository maintainer through
their GitHub profile before sharing details. Include a description, reproduction
steps, affected version, and suggested mitigation when available.

Do not include confidential corpus contents in a report; a minimal synthetic
fixture is preferred.
