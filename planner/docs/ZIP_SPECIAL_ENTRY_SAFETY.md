# ZIP Special-Entry Safety

Sprint 268 hardens release-package auditing against ZIP entries that can be
interpreted differently by extraction tools or operating systems.

- ZIP members with Unix symbolic-link file-type metadata are rejected, even if
their names match required release files.
- Directory-entry names are checked for unsafe absolute, traversal, NUL, and
  non-canonical separator forms instead of being ignored by path validation.
- Duplicate archive member detection uses a single pass over the directory
  entries, avoiding quadratic counting behavior on large packages.
- Existing manifest path-set, byte-size, SHA-256, required-file, assumptions
  JSON, transient-file and ZIP CRC checks remain in force.

The auditor does not extract the archive. The symlink check inspects ZIP
metadata and is independent of whether the host OS can create filesystem
symlinks. The separate manifest-builder check continues to reject symlinks in
release input directories.
