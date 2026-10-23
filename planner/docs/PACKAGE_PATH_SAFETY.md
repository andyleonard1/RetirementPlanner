# Cross-Platform Release ZIP Path Safety

Sprint 266 hardens `scripts/package_audit.py` against archive paths that can be
interpreted differently by POSIX and Windows extraction tools.

The audit accepts canonical relative paths with POSIX `/` separators only. It
rejects absolute POSIX paths, drive-qualified Windows paths, UNC paths, all
backslash separators, NUL characters, and any path containing a `..` segment.
The audit does not extract archive members; consumers should still use a
trusted extraction library and destination directory when unpacking a ZIP.

A release manifest also cannot legitimize an unsafe archive member: every ZIP
member is checked independently of its manifest record. Duplicate member names
are rejected because different ZIP readers may choose different copies.

Run the package audit before sharing a checkpoint:

```bash
python scripts/package_audit.py path/to/checkpoint.zip
```
