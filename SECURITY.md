# Security Policy

VFXLens reads untrusted files: After Effects projects (`.aep`, `.aepx`), presets and videos. Treat parser crashes,
path traversal, code execution from project contents, or writes outside the selected output folder as security issues.

## Reporting

Please report vulnerabilities privately through GitHub's **Report a vulnerability** button on the repository's
Security tab, not in a public issue. Include the file type, steps to reproduce and the impact. You will get an answer
as soon as possible; please allow time for a fix before disclosing publicly.

## Scope and safeguards

- The analyzer never executes scripts, expressions or `.aex` plugins embedded in projects.
- The optional After Effects bridge opens only an isolated temporary copy and closes it without saving.
- Output paths are validated before writing.

Supported version: the latest commit on `master`.
