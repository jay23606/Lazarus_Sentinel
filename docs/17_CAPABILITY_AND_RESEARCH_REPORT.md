# 17 — Capability and research report

Measured **2026-11-02** against the controlled-fixture profile and approved [demo contract](16_DEMO_DELIVERY_CONTRACT.md). This is a bounded compatibility/research tranche, not approval to implement the roadmap. No new detector, global package, analyzer download, provider call, or target execution was performed.

## Status vocabulary and disposition

`NOT_ATTEMPTED` means the analyzer/probe never ran. `SETUP_BLOCKED` means a prerequisite prevented attempting it; it is not an analyzer failure. `SETUP_FAILED` requires an actual attempted setup that failed. `UNSUPPORTED` requires a known unsupported capability, not merely a missing tool. `UNKNOWN` means no supporting measurement. `NOT_IMPLEMENTED` describes absent product behavior. A documentation source establishes a published capability, not that this application measured or integrated it.

| Gate | Measured result | Disposition |
|---|---|---|
| AST/FastAPI declaration-context slice | Baseline six endpoints; positive/declared/unknown second fixture passes exact path/evidence checks | GO for controlled synthetic subset only |
| Joern setup | No executable; only Oracle Java 26 arm64 installed; pinned release README specifies JDK 21 | SETUP_BLOCKED; analysis NOT_ATTEMPTED; capability UNKNOWN |
| LS-DATA-001 | No measured source/value/sink/control model or flow artifact | NOT_IMPLEMENTED; NO-GO pending capability review |
| LS-TRUST-001 | No reviewed executable boundary/handling policy or transition extractor | NOT_IMPLEMENTED; NO-GO pending policy/capability review |
| OS sandbox | Runner present, trusted no-op blocked before execution | BLOCKED; denial/resource probes NOT_ATTEMPTED |
| Broader repositories/archives | Isolation prerequisite unmet | BLOCKED under N14/N15; fixed CLI allowlist preserved |
| Semgrep/CodeQL baselines | No executable or account/license assessment for this product use | NOT_ATTEMPTED; no ranking or superiority claim |

## N09 — Joern compatibility preflight, stopped before download

The optional setup-plus-measurement budget was **at most two hours**, not a requirement to spend two hours or download an incompatible tool. This tranche stopped at preflight. Source review and local commands establish:

- `command -v joern`: absent. `uname -m`: `arm64`.
- `java -version`: Oracle Java **26**, build `26+35-2893`.
- `/usr/libexec/java_home -V`: one installed runtime, Java 26; no JDK 21 observed.
- Inspected official release **v4.0.666**, commit prefix `346d3e6`, dated 2026-10-27. Its macOS arm64 archive is approximately **1.64 GB**. The listed archive SHA256 is `d4a45bd07b670bf70aefb99c9203173874804d0811ef72ea6d6b87f88f54743e`; these are release metadata, not a locally verified download. [Official release assets](https://github.com/joernio/joern/releases/tag/v4.0.666).
- The **release-pinned README requires JDK 21**, and says other versions are untested. The installation website still says JDK 19 and illustrates an older version. Use the pinned release requirement for a future experiment; Java 26 compatibility was neither assumed nor disproven. [Pinned requirements](https://github.com/joernio/joern/blob/v4.0.666/README.md#requirements), [installation page](https://docs.joern.io/installation/).
- Joern's pinned license is Apache 2.0 with bundled-component notices; any redistribution needs its actual distribution notices reviewed. No product license decision follows from this source check. [Pinned license](https://github.com/joernio/joern/blob/v4.0.666/LICENSE).
- Official documentation describes a Python frontend and data-flow query steps. This does not establish FastAPI routing, dependency semantics, exact source mapping, or useful Python interprocedural coverage for this fixture. [Python frontend](https://docs.joern.io/frontends/python/), [data-flow steps](https://docs.joern.io/cpgql/data-flow-steps/).

No `.tools` directory, JDK installation, release archive, parse run, graph output, or benchmark was created. Consequently there is no analyzer runtime/resource measurement, no installed CLI-help verification, and no failed Python-analysis claim. Reconsider only with a pinned compatible local runtime, reviewed disk/time bounds and a concrete capability experiment; preserve this result rather than silently retrying.

A future predeclared Joern experiment must independently measure functions/source ranges, direct and cross-file calls, same-function value flow, cross-function argument/return flow, known handling controls, unknown external calls, and repeatability. Each must retain exact commands, pinned binary/hash, exit status, graph sample, elapsed/peak resources and source-byte references. Parsing success alone passes none of the flow/control gates.

## N14 — OS runner preflight, original failure preserved

The only executable probe was a trusted host no-op; no target or external network was contacted:

```text
command -v sandbox-exec
/usr/bin/sandbox-exec

/usr/bin/sandbox-exec -p '(version 1)(allow default)' /usr/bin/true
sandbox-exec: sandbox_apply: Operation not permitted
exit status: 71
```

The containing execution environment denied sandbox setup. This is **not** evidence that an application policy denied file or network access. No escalation/bypass was attempted. No canary data, host secrets or listener was needed after this prerequisite failed.

| Required isolation measurement | Result |
|---|---|
| Runner can launch harmless trusted executable | FAILED to launch; original error above |
| Read-only source / prohibited host filesystem reads and writes / output confinement | NOT_ATTEMPTED |
| Symlink races / descriptor replacement / hostile concurrent mutation | NOT_ATTEMPTED |
| OS-enforced outbound and loopback network restriction | NOT_ATTEMPTED |
| CPU, resident-memory and process-count enforcement | NOT_ATTEMPTED |
| Bounded output, timeout, cancellation and descendant cleanup under the OS policy | NOT_ATTEMPTED |
| Crash behavior and escaped-child containment under the OS policy | NOT_ATTEMPTED |

Existing AST-worker deadlines, bounded input/output, environment stripping and path checks remain useful controls, but do not satisfy this matrix. N14 is BLOCKED and N15 is BLOCKED. Do not expand the current fixture-only allowlist based on these tests.

## N10/N18 — LS-DATA-001 prerequisites and experiment contract

A source-to-sensitive-sink candidate requires an actual **value/taint-flow model**, distinct from control/call reachability. Local versus global flow and value-preserving versus taint-derived relationships must remain explicit. [CodeQL's data-flow model](https://codeql.github.com/docs/writing-codeql-queries/about-data-flow-analysis/) illustrates those distinctions. Joern documents conservative external-call propagation when custom semantics are missing; unexplained propagation must therefore remain unknown or low precision, never proof of a vulnerability. [Joern external-call semantics](https://docs.joern.io/dataflow-semantics/).

| Required capability | Positive / controlled comparison / unknown experiment | Current gate |
|---|---|---|
| Source identity and classification | Declared request field vs constant/public value vs unclassified origin | No implemented source model |
| Intraprocedural value propagation | Assignment/return/branch path vs overwritten constant vs unsupported alias/dynamic dispatch | No measured analyzer flow |
| Interprocedural propagation | Exact positional/keyword parameter and return identity vs unrelated argument vs unresolved import/native call | No measured analyzer flow |
| Sink identity and meaning | Policy-declared operation/argument/context vs ordinary output vs unknown wrapper | No reviewed sink policy |
| Context-appropriate handling | Appropriate encoding/parameterization/redaction for one context vs a different-context operation vs external custom transform | No reviewed semantics; names alone insufficient |
| Path-specific handling | Handling applies to this value on this path vs alternate unhandled branch vs condition/control ambiguity | No path-sensitive proof |
| Traceability and stability | Each semantic edge/source/sink has query version, exact revision/range/hash vs tampered/missing edge | Source evidence infrastructure exists; semantic edges absent |
| Uncertainty and evaluation | Predeclared positive/controlled/unknown denominator, false-candidate inspection, unsupported coverage, repeated identity | Not yet run for DATA |

**NO-GO for implementation now.** A minimum future proposal should select one language/framework and one source/sink/handling context, predeclare at least one case in each column, and obtain Astra approval of semantics and false-positive treatment before implementation. Unknown controls are not absent controls. No CALLS edge may be renamed FLOWS_TO. No general sanitizer, confidentiality, exploitability or production-accuracy claim follows from a handful of fixtures.

## N10/N18 — LS-TRUST-001 prerequisites and experiment contract

A trust boundary is a policy/context assertion. Crossing it is normal application behavior. A candidate needs an explicit expected treatment, observed transition and evidence that the applicable treatment relationship is missing in a fully supported scope; otherwise report context uncertainty. This is consistent with treating assumptions, mitigations and verification as explicit threat-model inputs. [OWASP threat-modeling guidance](https://owasp.org/www-community/Threat_Modeling).

| Required capability | Positive / controlled comparison / unknown experiment | Current gate |
|---|---|---|
| Boundary identity | Versioned source/destination zones and actor/tenant/data class vs same-zone call vs unclassified zone | No boundary policy |
| Expected treatment | Actor/time-approved requirement for that transition/context vs intentional permitted public transition vs unspecified expectation | No executable policy |
| Observed transition | Resolved API-to-storage/external operation with source identity vs internal helper vs dynamic client wrapper | Current CALLS graph does not establish boundary transition |
| Relevant treatment scope | Exact declared control/value/identity binding vs unrelated authentication/encoding vs gateway/middleware/external policy | No boundary control semantics |
| Tenant/ownership applicability | Policy-bound tenant/resource equality vs permitted cross-tenant administration vs unresolved identity | Not implemented |
| Evidence and evaluation | Ordered transition evidence and policy provenance; predeclared positive/controlled/unknown examples, repeatability | Infrastructure partly reusable; rule/corpus absent |

**NO-GO for implementation now.** Data-flow capability and trust-policy approval are independent gates. A future source-independent boundary rule still needs observed transition semantics and explicit policy. OWASP categories are classification aids, not evidence. No boundary detector or runtime validation was added here.

## Complete finite research catalog from document 15

All rows below are research/deferred gates unless an implemented subset is expressly named. The catalog covers every N18 topic and the enabling N01–N17 concerns; it does not authorize blanket expansion.

| Topic | Minimum evidence / gate | Disposition |
|---|---|---|
| Event acceptance, rules, deadlines, required provider use, repository/video/submission receipt | Owner portal evidence; public date is insufficient | Owner/external gate N01/N13 |
| Meta access, region/quota, Standard-mode privacy, spend, explanation factuality | Authorized synthetic request, reviewed egress, shared ledger, explicit recorded provenance | Integration workstream; access not established by this QA tranche |
| Versioned baseline, project license, dependency/distribution notices | Reviewed source inventory/lockfiles and owner license decision | Coordinator N03; no publication by QA |
| Controlled fixture evaluation and reproducibility | Separate oracle, exact paths/hashes, repeat and timing, honest denominators | New three-case variant measured; see doc 18 |
| Fixed artifact viewer, schema validation, accessibility | Frozen schemas, corrupted/mismatched bundle rejection, keyboard/table/mobile/zoom checks | Independent frontend/integration N05/N06/N12 |
| Optional read-only API / pagination / selected graph neighborhoods | Concrete viewer need, committed refs, local access/origin policy, caps | API deferred N11; no listener added |
| Authorization declarations and route variants | Exact function/control scopes and separately asserted policy | Controlled subset implemented; stronger semantic rules deferred |
| Ownership and tenant relationships | Actor/resource/tenant binding; explicit exceptions and branch evidence | Research only; declarations do not prove ownership checks |
| Alternate route/control inconsistency | Same policy operation with exact per-route scope and unsupported distinctions | Existing comparison can show declarations; no runtime-inconsistency detector |
| Dependency advisories, usage and reachability | Pinned dependency/advisory identity, actual import/use edges, database freshness | Deferred; advisory match is not reachable exploitation |
| Safe configuration metadata | Resolved config precedence/environment scope with value redaction | Deferred; no secret/config file discovery |
| Secret metadata | Type/location/hash only, bounded local retention and no secret value output | Deferred; never use credential scanning as setup discovery |
| API inventory, deprecated/debug/undocumented routes | Exact route/version registration and explicit approved inventory policy | Literal FastAPI subset only; dynamic registration unknown |
| SSRF destination policy | Value provenance to network operation plus reviewed destination/redirect/DNS policy | Deferred; no network probing or exploit payloads |
| Unsafe deserialization | Exact input provenance, API/mode semantics and trust classification | Deferred; API name alone insufficient |
| Logging and data disclosure | Data classification/value propagation to sink plus context-appropriate redaction evidence | Deferred with DATA gate |
| Additional Python frameworks and richer FastAPI constructs | One predeclared positive/declared/unknown subset, independent source identity tests | Current unsupported patterns remain unknown |
| JavaScript/TypeScript adapters | Pinned parser/module/framework semantics, source maps, dynamic dispatch unknowns | Research only; frontend TypeScript is not an analyzer adapter |
| C/C++ adapters / memory safety | Compilation/configuration identity, bounds/lifetime/alias semantics and controlled corpus | Research only; no compiler/build execution on targets |
| Infrastructure-as-code and cloud IAM | Versioned provider/schema/policy evaluation, resource/identity/permission evidence | Research only; no cloud account access |
| Authorized runtime telemetry | Explicit environment/allowlist/owner approval; provenance and retention/data-egress review | Deferred; never substitute unapproved active testing |
| Business-logic annotations and classification | Actor/time/versioned assertions, uncertainty and contradictions visible | Policy provenance exists; broad annotation/classifier not implemented |
| Human false-positive feedback and learning loop | Immutable original evidence, triage provenance, held-out evaluation and bias checks | Deferred; feedback cannot silently relabel candidates confirmed |
| Policy/data classification and coverage metrics | Explicit denominators by file/construct/rule; unknown/out-of-scope preserved | Current controlled coverage only; no universal coverage score |
| Isolation and expanded local/archive intake | All N14 probes pass before N15; bounded traversal/symlinks/device/expansion tests | BLOCKED as measured above |
| Semgrep baseline | Engine/rule license and mode-specific cross-file capability, fixture-only experiment | NOT_ATTEMPTED; no CE-to-Pro equivalence |
| CodeQL baseline | Exact CLI terms/account/use authorization plus pinned query/database | NOT_ATTEMPTED; query MIT license does not license CLI use |
| Orphan/crash/corruption inspection and retention | Read-only ledger verification, no retry/delete, separate future retention decision | Inspector implemented; repair/retention deferred |
| Human triage/history, incremental/diff, SARIF | Provenance-preserving migration/tests; actual consumer/analyst need | Deferred; no schema/API added here |
| CI, packaging, clean setup, backups/restore, performance | Pinned local deps, offline checks; measured restore/clean-host/performance separately | CI/check scripts added; hosted CI/restore not claimed |
| LangGraph/orchestration | Demonstrated linear-pipeline recovery/concurrency need and comparison | Deferred; no workflow framework added |
| Graph database, microservices, multi-language architecture | Measured capacity/use case, migration and operations/security evidence | Deferred; modular monolith retained |
| Remote deployment / multi-user auth / tenancy / quotas / queues | Separate access/storage/exposure threat model, isolation and resource gates | Deferred; no remote service/publication |
| Automatic exploitation and remediation | Outside defensive read-only product boundary | Out of scope |

License/mode sources were checked separately: [Semgrep CE engine and rule-license distinction](https://semgrep.dev/blog/2024/important-updates-to-semgrep-oss/), [Semgrep cross-function/cross-file modes](https://semgrep.dev/docs/semgrep-code/semgrep-pro-engine-intro), [CodeQL CLI terms](https://github.com/github/codeql-cli-binaries/blob/main/LICENSE.md), [GitHub CLI availability](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-cli). No legal eligibility or paid account access was inferred. [OWASP API Security](https://owasp.org/www-project-api-security/) supplies topic taxonomy, not automatic vulnerability confirmation.

## Handoff and stop conditions

Astra must review any new security semantics, capability acceptance or risk exception. Sol may implement only the resulting frozen bounded subset. Stop on incompatible/missing runtime, unavailable isolation, license uncertainty, absent owner scope, unresolved policy, unknown controls or exhausted declared budget. Keep the original error/status and require a new explicit experiment identity after repair; never silently retry or redefine a failed gate.
