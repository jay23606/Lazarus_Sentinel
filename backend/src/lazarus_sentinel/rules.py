"""Conservative declaration-only authorization queries and evidence gate."""

from __future__ import annotations

import base64
import hashlib
import itertools
import re
from pathlib import PurePosixPath

import networkx as nx  # type: ignore[import-untyped]

from .models import (
    Diagnostic,
    Edge,
    Finding,
    Graph,
    Node,
    SecurityPolicy,
    Snapshot,
    source_bytes,
    stable_id,
)


def validate_graph(graph: Graph) -> None:
    nodes = {n.id: n for n in graph.nodes}
    edges = {e.id: e for e in graph.edges}
    evidence = {e.id: e for e in graph.evidence}
    if (
        len(nodes) != len(graph.nodes)
        or len(edges) != len(graph.edges)
        or len(evidence) != len(graph.evidence)
    ):
        raise ValueError("DUPLICATE_IDENTIFIERS")
    revision = graph.repository.get("revision")
    if not revision or not nodes:
        raise ValueError("INVALID_GRAPH")
    for ev in graph.evidence:
        path = PurePosixPath(ev.file_path)
        if (
            path.is_absolute()
            or ".." in path.parts
            or "\\" in ev.file_path
            or ev.start_line > ev.end_line
            or ev.repository_revision != revision
            or not re.fullmatch(r"sha256:[0-9a-f]{64}", ev.excerpt_hash)
        ):
            raise ValueError("INVALID_EVIDENCE")
    items: list[Node | Edge] = [*graph.nodes, *graph.edges]
    for item in items:
        if not item.evidence_ids or any(e not in evidence for e in item.evidence_ids):
            raise ValueError("INVALID_EVIDENCE_REFERENCE")
    for edge in graph.edges:
        if edge.source not in nodes or edge.target not in nodes:
            raise ValueError("INVALID_EDGE_REFERENCE")
    for f in graph.findings:
        if (
            f.repository_revision != revision
            or not f.path_node_ids
            or f.entry_node_id != f.path_node_ids[0]
            or len(f.path_edge_ids) != len(f.path_node_ids) - 1
        ):
            raise ValueError("INVALID_FINDING_PATH")
        if any(n not in nodes for n in f.path_node_ids) or any(
            e not in evidence for e in f.evidence_ids
        ):
            raise ValueError("INVALID_FINDING_REFERENCE")
        required = set()
        for n in f.path_node_ids:
            required.update(nodes[n].evidence_ids)
        for index, edge_id in enumerate(f.path_edge_ids):
            path_edge = edges.get(edge_id)
            if (
                path_edge is None
                or path_edge.type != ("HANDLES" if index == 0 else "CALLS")
                or path_edge.source != f.path_node_ids[index]
                or path_edge.target != f.path_node_ids[index + 1]
                or path_edge.fact_status != "OBSERVED"
            ):
                raise ValueError("INVALID_FINDING_PATH")
            required.update(path_edge.evidence_ids)
        if not required.issubset(f.evidence_ids):
            raise ValueError("INCOMPLETE_FINDING_EVIDENCE")


def evaluate_authorization(graph: Graph, policy: SecurityPolicy) -> list[Finding]:
    validate_graph(graph)
    network = nx.MultiDiGraph()
    nodes = {node.id: node for node in graph.nodes}
    for node in graph.nodes:
        network.add_node(node.id)
    for edge in graph.edges:
        if edge.type in {"HANDLES", "CALLS"} and edge.fact_status == "OBSERVED":
            network.add_edge(edge.source, edge.target, key=edge.id, edge=edge)
    findings = []
    for endpoint in sorted(graph.nodes, key=lambda n: n.id):
        if endpoint.type != "API_ENDPOINT":
            continue
        for assertion in policy.protected_operations:
            controls = [
                n
                for n in graph.nodes
                if n.type == "FUNCTION"
                and n.qualified_name == assertion.required_authorization
                and n.fact_status == "OBSERVED"
                and n.properties.get("control_scope_supported", False) is True
            ]
            if len(controls) != 1:
                graph.diagnostics.append(
                    Diagnostic(
                        code="NEEDS_CONTEXT",
                        message="Required authorization identity is unresolved; no candidate emitted.",
                    )
                )
                continue
            for operation in sorted(graph.nodes, key=lambda n: n.id):
                if operation.type != "FUNCTION" or operation.qualified_name != assertion.operation:
                    continue
                try:
                    path = nx.shortest_path(network, endpoint.id, operation.id)
                except nx.NetworkXNoPath:
                    continue
                path_edges = []
                for left, right in itertools.pairwise(path):
                    selected = min(network[left][right].values(), key=lambda x: x["edge"].id)[
                        "edge"
                    ]
                    path_edges.append(selected)
                if (
                    not path_edges
                    or path_edges[0].type != "HANDLES"
                    or any(e.type != "CALLS" for e in path_edges[1:])
                ):
                    continue
                if not endpoint.properties.get("control_scope_supported", False) or any(
                    nodes[n].fact_status != "OBSERVED"
                    or nodes[n].properties.get("control_scope_supported", False) is not True
                    for n in path
                ):
                    graph.diagnostics.append(
                        Diagnostic(
                            code="NEEDS_CONTEXT",
                            message="Authorization scope is unsupported; no candidate emitted.",
                        )
                    )
                    continue
                dependencies = endpoint.properties.get("dependencies", [])
                if assertion.required_authorization in dependencies:
                    graph.diagnostics.append(
                        Diagnostic(
                            code="AUTHORIZATION_DECLARATION_RECOGNIZED",
                            message="Expected authorization declaration recognized; effectiveness unverified.",
                        )
                    )
                    continue
                evidence_ids = sorted(
                    {ev for n in path for ev in nodes[n].evidence_ids}
                    | {ev for e in path_edges for ev in e.evidence_ids}
                )
                findings.append(
                    Finding(
                        id=stable_id(
                            "finding",
                            graph.repository["revision"],
                            endpoint.id,
                            assertion.model_dump(),
                            [e.id for e in path_edges],
                        ),
                        title="Potential authorization declaration gap",
                        severity=assertion.severity,
                        confidence="LOW",
                        repository_revision=graph.repository["revision"],
                        entry_node_id=endpoint.id,
                        path_node_ids=path,
                        path_edge_ids=[e.id for e in path_edges],
                        evidence_ids=evidence_ids,
                        impact_hypothesis=assertion.impact,
                        why_flagged="A policy-protected operation is reachable through supported calls without its expected authorization declaration.",
                        missing_or_uncertain_controls=[assertion.required_authorization],
                        assumptions=[
                            "Human policy assertion defines protected operation sensitivity."
                        ],
                        unknowns=[
                            "Declaration effectiveness and runtime enforcement are unverified."
                        ],
                        false_positive_considerations=[
                            "Authorization may exist outside this supported static model."
                        ],
                        human_review_steps=[
                            "Review the pinned source path and policy assertion before accepting the candidate."
                        ],
                        coverage_context={
                            "policy_assertion": assertion.model_dump(),
                            "profile": "reduced-static-auth",
                        },
                    )
                )
    graph.findings = sorted(findings, key=lambda f: f.id)
    validate_graph(graph)
    return graph.findings


def validate_evidence_snapshot(graph: Graph, snapshot: Snapshot) -> None:
    validate_graph(graph)
    if graph.repository["revision"] != snapshot.revision:
        raise ValueError("REVISION_MISMATCH")
    for evidence in graph.evidence:
        if evidence.file_path == "policy.json":
            data = base64.b64decode(snapshot.policy_base64, validate=True)
        elif evidence.file_path in snapshot.files:
            data = source_bytes(snapshot, evidence.file_path)
        else:
            raise ValueError("EVIDENCE_OUTSIDE_SNAPSHOT")
        lines = data.splitlines(keepends=True)
        if evidence.end_line > len(lines):
            raise ValueError("EVIDENCE_RANGE_OUTSIDE_SOURCE")
        excerpt = b"".join(lines[evidence.start_line - 1 : evidence.end_line])
        if evidence.excerpt_hash != "sha256:" + hashlib.sha256(excerpt).hexdigest():
            raise ValueError("EVIDENCE_HASH_MISMATCH")
