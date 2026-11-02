from test_rules import authorization_graph, policy

from lazarus_sentinel.models import Node
from lazarus_sentinel.report import render_report
from lazarus_sentinel.rules import evaluate_authorization


def test_report_names_ordered_path_and_declared_dependencies():
    graph = authorization_graph()
    graph.nodes[0].name = "GET /weak"
    graph.nodes.extend(
        [
            Node(
                id="protected",
                type="API_ENDPOINT",
                layer="APP",
                name="GET /protected",
                properties={"dependencies": ["app.authorize"]},
                evidence_ids=["ev"],
            ),
            Node(
                id="injection",
                type="API_ENDPOINT",
                layer="APP",
                name="<script>[click](evil)",
                properties={"dependencies": ["<bad>*dependency*"]},
                evidence_ids=["ev"],
            ),
        ]
    )
    evaluate_authorization(graph, policy())
    report = render_report(graph, "PARTIAL")
    assert "Entry endpoint: GET /weak" in report
    assert "Ordered path: GET /weak → handler → op" in report
    assert "GET /protected" in report and "app\\.authorize" in report
    assert "Declared dependencies (effectiveness unverified)" in report
    assert "<script>" not in report and "&lt;script&gt;" in report
    assert "[click](evil)" not in report
    assert "def " not in report
