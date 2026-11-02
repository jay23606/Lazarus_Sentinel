import pytest

from lazarus_sentinel.models import Edge, Evidence, Graph, Node
from lazarus_sentinel.rules import validate_graph


def test_evidence_gate_rejects_missing_reference():
    graph = Graph(
        repository={"revision": "r"},
        nodes=[Node(id="n", type="FUNCTION", layer="CODE", name="f", evidence_ids=["missing"])],
    )
    with pytest.raises(ValueError):
        validate_graph(graph)


def test_evidence_gate_rejects_reversed_range():
    with pytest.raises(ValueError):
        Evidence(
            id="e",
            repository_revision="r",
            file_path="a.py",
            start_line=2,
            end_line=1,
            excerpt_hash="sha256:" + "a" * 64,
            rule_or_query_id="q",
            evidence_kind="AST",
        )


def authorization_graph(dependencies=(), supported=True):
    ev = Evidence(
        id="ev",
        repository_revision="r",
        file_path="app.py",
        start_line=1,
        end_line=1,
        excerpt_hash="sha256:" + "a" * 64,
        rule_or_query_id="q",
        evidence_kind="AST",
    )
    nodes = [
        Node(
            id="route",
            type="API_ENDPOINT",
            layer="APP",
            name="route",
            properties={"dependencies": list(dependencies), "control_scope_supported": supported},
            evidence_ids=["ev"],
        ),
        Node(id="handler", type="FUNCTION", layer="CODE", name="handler", evidence_ids=["ev"]),
        Node(
            id="op",
            type="FUNCTION",
            layer="CODE",
            name="op",
            qualified_name="app.export",
            evidence_ids=["ev"],
        ),
    ]
    nodes.append(
        Node(
            id="auth",
            type="FUNCTION",
            layer="CODE",
            name="authorize",
            qualified_name="app.authorize",
            evidence_ids=["ev"],
        )
    )
    for node in nodes:
        if node.type == "FUNCTION":
            node.properties["control_scope_supported"] = True
    return Graph(
        repository={"revision": "r"},
        nodes=nodes,
        edges=[
            Edge(
                id="handles", source="route", target="handler", type="HANDLES", evidence_ids=["ev"]
            ),
            Edge(id="calls", source="handler", target="op", type="CALLS", evidence_ids=["ev"]),
        ],
        evidence=[ev],
    )


def policy():
    from lazarus_sentinel.models import ProtectedOperation, SecurityPolicy

    return SecurityPolicy(
        protected_operations=[
            ProtectedOperation(
                operation="app.export",
                required_authorization="app.authorize",
                severity="HIGH",
                impact="Synthetic records disclosure",
                author="fixture-owner",
                created_at="2026-11-01",
            )
        ]
    )


@pytest.mark.parametrize(
    "dependencies,supported,count",
    [
        ((), True, 1),
        (("app.authenticate",), True, 1),
        (("app.authorize",), True, 0),
        ((), False, 0),
    ],
)
def test_authorization_is_exact_declaration(dependencies, supported, count):
    from lazarus_sentinel.rules import evaluate_authorization

    graph = authorization_graph(dependencies, supported)
    findings = evaluate_authorization(graph, policy())
    assert len(findings) == count
    if count:
        assert findings[0].confidence == "LOW"
        assert findings[0].path_edge_ids == ["handles", "calls"]
        assert findings[0].coverage_context["policy_assertion"]["author"] == "fixture-owner"


def test_no_policy_no_sensitivity_guesses():
    from lazarus_sentinel.models import SecurityPolicy
    from lazarus_sentinel.rules import evaluate_authorization

    assert (
        evaluate_authorization(authorization_graph(), SecurityPolicy(protected_operations=[])) == []
    )


def test_invalid_ordered_finding_path_rejected():
    from lazarus_sentinel.rules import evaluate_authorization

    graph = authorization_graph()
    evaluate_authorization(graph, policy())
    graph.findings[0].path_edge_ids.reverse()
    with pytest.raises(ValueError):
        validate_graph(graph)


def test_unresolved_authorization_identity_needs_context():
    from lazarus_sentinel.rules import evaluate_authorization

    graph = authorization_graph()
    graph.nodes = [n for n in graph.nodes if n.id != "auth"]
    assert evaluate_authorization(graph, policy()) == []
    assert any(d.code == "NEEDS_CONTEXT" for d in graph.diagnostics)


def test_snapshot_gate_checks_actual_hash_and_range():
    import base64
    import hashlib

    from lazarus_sentinel.models import SecurityPolicy, Snapshot
    from lazarus_sentinel.rules import validate_evidence_snapshot

    graph = authorization_graph()
    data = b'print("synthetic")\n'
    snapshot = Snapshot(
        revision="r",
        files={"app.py": base64.b64encode(data).decode()},
        file_hashes={"app.py": hashlib.sha256(data).hexdigest()},
        manifest_base64="",
        policy_base64="",
        policy_hash="",
        policy=SecurityPolicy(protected_operations=[]),
    )
    with pytest.raises(ValueError, match="HASH_MISMATCH"):
        validate_evidence_snapshot(graph, snapshot)
    graph.evidence[0].excerpt_hash = "sha256:" + hashlib.sha256(data).hexdigest()
    validate_evidence_snapshot(graph, snapshot)
    graph.evidence[0].end_line = 2
    with pytest.raises(ValueError, match="RANGE_OUTSIDE"):
        validate_evidence_snapshot(graph, snapshot)


@pytest.mark.parametrize("identity", ["handler", "op", "auth"])
def test_opaque_function_scope_emits_context_only(identity):
    from lazarus_sentinel.rules import evaluate_authorization

    graph = authorization_graph()
    for node in graph.nodes:
        if node.id == identity:
            node.properties["control_scope_supported"] = False
    assert evaluate_authorization(graph, policy()) == []
    assert any(d.code == "NEEDS_CONTEXT" for d in graph.diagnostics)
