# Release Manifest Schema Hardening

Sprint 267 strengthens release manifest verification and manifest generation.

- The manifest sprint identifier must be a positive integer (booleans are not
  accepted as integers).
- The file count must be a non-negative integer and must equal the number of
  manifest records.
- Each file size must be a non-negative integer; booleans and floating-point
  values are rejected.
- Manifest paths must use canonical relative POSIX paths and are checked using
  the same path-safety rules as ZIP members.
- Duplicate keys in manifest JSON are rejected rather than silently resolved
  using a parser's last-value-wins behavior.
- The manifest builder refuses symlinks in the input tree to avoid hashing a
  target outside the release root or creating platform-dependent packages.

These checks supplement SHA-256 and ZIP CRC validation. A checksum manifest
supports integrity verification but is not a digital signature and does not
prove who produced a package.
