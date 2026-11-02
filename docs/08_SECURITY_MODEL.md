# 08 — Security, Privacy, Authorization and Isolation

## Integrated demo status — 2026-11-02

The approved [demo contract](16_DEMO_DELIVERY_CONTRACT.md) is implemented alongside the preserved first-slice analyzer: immutable hash-verified bundles, disabled/mock explanations with a gated Meta adapter, and a fixed React/Vite/TypeScript/Cytoscape viewer. See [capability gates](17_CAPABILITY_AND_RESEARCH_REPORT.md), [finite evaluation](18_DEMO_EVALUATION.md), and [integrated verification](19_INTEGRATED_DEMO_REVIEW.md) for current checks and review disposition. Document 14 remains historical first-slice evidence; its 73-test count is not the integrated total.

Local baseline commit `7797b85` is preserved on `feat/integrated-demo`; no remote, publication, submission or license selection is implied. Only fixed synthetic intake is supported. Live access is BLOCKED by the missing key; zero paid calls were made. Joern setup is blocked and analysis NOT_ATTEMPTED; data/trust rules remain NOT_IMPLEMENTED. OS sandbox launch failed before execution, so broader intake remains blocked.

## Current authorized boundary

The approved product scans only the checked-in synthetic `fixture:fastapi-demo`. It parses exact source bytes without importing/executing target code, installing target dependencies, probing services, exploiting findings or applying fixes. This is a controlled-fixture boundary; arbitrary repositories and archives are not accepted.

## Implemented protections

Manifest-driven fd-relative/no-follow reads reject invalid paths, symlinks and non-regular files. Limits are 100 Python files, 256 KiB per file, 5 MiB total source and 64 KiB each for manifest/policy metadata. Immutable snapshots retain exact bytes for parsing; evidence hashes and line ranges are validated, and source identity is rechecked before publication.

The extraction child uses a sanitized credential-free environment, 30-second coordinator deadline, 25-second CPU limit, 16 MiB output/file-size bound, 8 MiB input bound and 64-file-descriptor limit. Output locations are checked for existing symlink aliases; artifacts use generated scan directories. Public errors do not echo raw exceptions, host paths or source. Reports escape displayed metadata and retain locations/hashes rather than excerpts. The default provider is disabled; explicit mock is offline. The Meta adapter is present but live access is blocked; minimal synthetic context would leave the machine only under explicit live selection and the reviewed budget/privacy gates.

## Explicit limitations

Process/environment limits are not an OS filesystem/network sandbox. The worker can retain ambient OS access even though this pipeline does not intentionally perform network requests or execute targets. Do not claim enforced network isolation, read-only mounts, memory limits, containers or adversarial-repository readiness.

Existing-alias checks do not cover concurrent hostile filesystem replacement. Rename before SQLite commit can leave orphan files; readers use committed references only. Unknown-control suppression reduces false candidates but can miss real issues. Recognized declarations do not establish enforcement; no candidate is automatically confirmed.

## Future security gates — not implemented

Before broader authorized intake, review authorization/scope, read-only isolation, filesystem/network restrictions, credential access, output limits, hostile-input tests and cleanup/recovery. Archive support additionally needs member validation, expanded-size/file-count ceilings, link/device rejection and safe extraction. Container controls must be verified on the actual platform; containerization alone is insufficient.

Before any external model call, approve disclosed provider/model/egress, minimal relevant context, secret/personal-data redaction, no raw prompt logging, output schema/evidence-ID validation and a disabled/static alternative. Treat repository content and provider/tool output as untrusted data. No source instruction can override system/owner rules.

Future API/multi-user/triage work requires authentication, access control, tenant/scan ownership, retention/deletion and actor/rationale provenance. These are prerequisites for that expansion, not features already implemented. Never expose host credentials, SSH agent, Docker socket or broad host mounts to target analyzers.

## References for future design review

- OWASP threat modeling: https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html
- OWASP API Security: https://owasp.org/www-project-api-security/
- NIST SSDF: https://csrc.nist.gov/pubs/sp/800/218/final
- Docker isolation references: https://docs.docker.com/engine/security/

These references are guidance, not certification of the current implementation.
