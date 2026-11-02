"""Hash-only report: labels are rendered as escaped Markdown text."""

import html
import re

from .models import Graph


def escape(value: str) -> str:
    return (
        re.sub(r"([\\`*_{}\[\]()#+.!|>~-])", r"\\\1", html.escape(value, quote=True))
        .replace("\n", " ")
        .replace("\r", " ")
    )


def render_report(graph: Graph, status: str) -> str:
    lines = [
        "# Lazarus Sentinel static assessment",
        "",
        f"Status: {escape(status)}",
        f"Revision: {escape(graph.repository['revision'])}",
        "",
        "Findings are candidates for human review. Authorization declaration effectiveness is unverified.",
        "No data-flow, trust-boundary or exploitability claim is made.",
        "LLM explanations disabled; no external model egress.",
        "",
    ]
    nodes = {node.id: node for node in graph.nodes}
    for finding in graph.findings:
        lines += [
            f"## {escape(finding.id)}",
            escape(finding.title),
            f"Entry endpoint: {escape(nodes[finding.entry_node_id].name)}",
            "Ordered path: "
            + " → ".join(escape(nodes[node_id].name) for node_id in finding.path_node_ids),
            f"Severity: {finding.severity}; confidence: {finding.confidence}; CANDIDATE / NEEDS_REVIEW",
            escape(finding.why_flagged),
            escape(finding.impact_hypothesis),
            "",
        ]
        for evidence in graph.evidence:
            if evidence.id in finding.evidence_ids:
                lines.append(
                    f"- {escape(evidence.file_path)}:{evidence.start_line}–{evidence.end_line}; hash {escape(evidence.excerpt_hash)}"
                )
    lines += ["", "## Declared dependencies (effectiveness unverified)", ""]
    for endpoint in sorted(graph.nodes, key=lambda node: node.id):
        if endpoint.type == "API_ENDPOINT":
            dependencies = endpoint.properties.get("dependencies", [])
            labels = (
                ", ".join(escape(str(dependency)) for dependency in dependencies) or "None observed"
            )
            lines.append(f"- {escape(endpoint.name)}: {labels}")
    lines += ["", "## Coverage", ""]
    lines += [f"- {escape(c.file_path)}: {c.status}; {escape(c.reason)}" for c in graph.coverage]
    lines += ["", "## Diagnostics", ""]
    lines += [f"- {escape(d.code)}: {escape(d.message)}" for d in graph.diagnostics]
    return "\n".join(lines) + "\n"
