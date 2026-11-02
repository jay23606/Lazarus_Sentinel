# Security policy

Lazarus Sentinel is a defensive, read-only analysis tool. It currently analyses only the fixed synthetic fixture `fixture:fastapi-demo`.

## Reporting a vulnerability

Report privately through [GitHub security advisories](https://github.com/sumitjadhav1703/Lazarus_Sentinel/security/advisories/new). Do not open a public issue and do not include working exploit payloads or real secrets. Expect an acknowledgement within a few days; this is a volunteer project without an SLA.

## In scope

- Path traversal, symlink or reparse-point escape in intake and bundle handling.
- Secrets reaching the frontend bundle, logs, reports or explanation sidecars.
- Injection or XSS in generated Markdown/JSON reports or the viewer.
- Bypass of the explanation budget or provider gates.

## Out of scope

- Findings produced for the synthetic fixture: they are intentional test data.
- Analysing third-party systems. Only analyse repositories you own or are authorised to assess.
