# ZIP Windows Filename Safety — Sprint 272

The package auditor checks every ZIP path component for Windows portability before CRC checks or payload reads. It rejects:

- reserved DOS device names (`CON`, `NUL`, `COM1`–`COM9`, `LPT1`–`LPT9`, and superscript ¹/²/³ variants), including names with extensions;
- components ending in a dot or space;
- Windows-invalid filename punctuation (`<`, `>`, `:`, `"`, `|`, `?`, `*`), including alternate-data-stream syntax using a colon;
- ASCII control characters.

The checks complement canonical path validation, Unicode/case collision checks, special-file metadata checks, duplicate-entry checks, and decompression resource limits. They intentionally favor portable release archives over names that happen to work on a subset of host filesystems.

No financial calculation code, assumptions defaults, or golden scenario baseline is changed by this hardening.
