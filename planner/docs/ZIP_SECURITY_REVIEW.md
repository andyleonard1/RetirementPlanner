# ZIP Security Review — Sprint 274

Sprint 274 is a bounded review of the release archive audit after the path portability, metadata resource limits, special-file, collision, Windows filename and local-header hardening work in Sprints 266–273.

## Review finding addressed

The local-header validator checked whether a data descriptor had the expected length, but did not verify the descriptor's CRC-32 and compressed/uncompressed size values against the central directory. A ZIP reader that trusts the descriptor could therefore interpret a malformed archive differently from a reader that trusts central-directory metadata.

The auditor now validates both legal data-descriptor layouts: with the optional `PK\x07\x08` signature and without it. It compares CRC-32 and both sizes against the central directory, supports ZIP64 descriptor widths, and reports truncated or inconsistent descriptors before any payload decompression. The signature-less layout is tested as well; the implementation also avoids assuming the signature is present in every valid archive.

## Validation boundaries

- Existing local-header name, flags, compression method, CRC/size, ZIP64 size, record-boundary and overlap checks remain active.
- Descriptor validation is part of the preflight stage, before `testzip()` or manifest/assumptions payload reads.
- Existing archive path portability, collision, special-file and decompression resource limits remain active.
- This review does not broaden the accepted compression-method set or relax existing path rules.
- No production financial calculation logic, assumptions defaults or golden baseline is changed.

## Regression coverage

`tests/test_sprint274_zip_data_descriptor_integrity.py` covers valid signed, unsigned and ZIP64 descriptors, and rejects descriptor CRC and size mismatches. It also asserts roadmap/status/document traceability.
