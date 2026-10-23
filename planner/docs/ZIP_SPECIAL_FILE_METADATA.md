# ZIP Special-File Metadata Safety

Sprint 270 extends release ZIP auditing to Unix file-type metadata.

- Only ordinary files and directory entries are supported in the release format.
- FIFO, character-device, block-device, and socket entries are rejected.
- Symbolic links remain prohibited.
- Unix directory/file type bits must agree with whether the member name denotes a directory.
- FIFO/device/socket and file-versus-directory consistency checks run before CRC verification or payload decompression, so rejected special entries are not read first. The existing symlink prohibition remains enforced by the archive member scan.
- Archives created by systems that do not provide Unix file-type metadata continue to be evaluated by the existing path, manifest, resource-limit, CRC, and required-file checks.

The auditor does not extract archives. This metadata validation prevents cross-platform extraction tools from interpreting a release member as a special filesystem object.
