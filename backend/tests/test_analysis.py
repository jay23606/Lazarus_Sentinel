"""Synthetic graph contracts; no FastAPI runtime is installed or imported."""

import base64
import hashlib
import json
from pathlib import Path

from lazarus_sentinel.analysis import analyze
from lazarus_sentinel.models import SecurityPolicy, Snapshot


def snapshot(files):
    return Snapshot(
        revision="test",
        files={p: base64.b64encode(s.encode()).decode() for p, s in files.items()},
        file_hashes={p: hashlib.sha256(s.encode()).hexdigest() for p, s in files.items()},
        manifest_base64="",
        policy_base64="",
        policy_hash="",
        policy=SecurityPolicy(protected_operations=[]),
    )


def test_fixture_routes_and_calls():
    root = Path(__file__).parents[2] / "fixtures/fastapi_demo"
    graph = analyze(
        snapshot({p.relative_to(root).as_posix(): p.read_text() for p in root.rglob("*.py")})
    )
    endpoints = {n.name: n for n in graph.nodes if n.type == "API_ENDPOINT"}
    oracle = json.loads((root.parent / "expected_results/fastapi_demo.json").read_text())
    assert set(endpoints) == set(oracle["endpoints"])
    assert endpoints["GET /protected"].properties["dependencies"] == [
        "app.controls.authorize_export"
    ]
    assert endpoints["GET /inherited/export"].properties["dependencies"] == [
        "app.controls.authorize_export"
    ]
    assert endpoints["GET /annotated"].properties["dependencies"] == [
        "app.controls.authorize_export"
    ]
    assert all(n.properties["control_scope_supported"] for n in endpoints.values())
    names = {n.id: n.qualified_name for n in graph.nodes}
    assert ("app.services.export_service", "app.repository.export_records") in {
        (names[e.source], names[e.target]) for e in graph.edges if e.type == "CALLS"
    }
    assert any(d.code == "NEEDS_CONTEXT" for d in graph.diagnostics)
    assert graph.evidence and all(n.evidence_ids for n in graph.nodes)
    assert (
        graph.model_dump()
        == analyze(
            snapshot({p.relative_to(root).as_posix(): p.read_text() for p in root.rglob("*.py")})
        ).model_dump()
    )


def test_opaque_scope_and_shadowing_are_not_controls():
    graph = analyze(
        snapshot(
            {
                "main.py": """from fastapi import FastAPI, Depends
app = FastAPI()
def control(): pass
@app.get("/x")
def route(control=Depends()):
    return control()
"""
            }
        )
    )
    endpoint = next(n for n in graph.nodes if n.type == "API_ENDPOINT")
    assert not endpoint.properties["control_scope_supported"]
    assert not [e for e in graph.edges if e.type == "CALLS"]


def test_source_is_never_executed_and_errors_are_reported():
    graph = analyze(
        snapshot(
            {"main.py": "raise RuntimeError('never execute')\ndef x(): pass\n", "bad.py": "def !!!"}
        )
    )
    assert any(n.qualified_name == "main.x" for n in graph.nodes)
    assert any(c.status == "PARSER_ERROR" for c in graph.coverage)


def endpoints_for(source, extra=None):
    files = {"main.py": source}
    files.update(extra or {})
    graph = analyze(snapshot(files))
    return graph, [n for n in graph.nodes if n.type == "API_ENDPOINT"]


def test_all_declared_dependency_scopes():
    cases = [
        'app = FastAPI(dependencies=[D(permit)])\n@app.get("/x")\ndef route(): pass',
        'app = FastAPI()\n@app.get("/x", dependencies=[D(permit)])\ndef route(): pass',
        'app = FastAPI()\n@app.get("/x")\ndef route(x=D(permit)): pass',
        'app = FastAPI()\n@app.get("/x")\ndef route(x: A[str, S(permit)]): pass',
        'app = FastAPI()\nr = APIRouter(dependencies=[D(permit)])\napp.include_router(r)\n@r.get("/x")\ndef route(): pass',
        'app = FastAPI()\nr = APIRouter()\napp.include_router(r, dependencies=[D(permit)])\n@r.get("/x")\ndef route(): pass',
    ]
    for body in cases:
        graph, endpoints = endpoints_for(
            "from fastapi import FastAPI, APIRouter, Depends as D, Security as S\nfrom typing import Annotated as A\ndef permit(): pass\n"
            + body
        )
        assert len(endpoints) == 1
        assert endpoints[0].properties["dependencies"] == ["main.permit"]
        assert endpoints[0].properties["control_scope_supported"]
        assert any(e.type == "DEPENDS_ON" for e in graph.edges)


def test_unsupported_scopes_cannot_be_treated_as_control_absence():
    cases = [
        'app = FastAPI()\nr = APIRouter()\napp.include_router(r)\napp.include_router(r)\n@r.get("/x")\ndef route(): pass',
        'app = FastAPI()\nr = APIRouter()\ns = APIRouter()\napp.include_router(s)\ns.include_router(r)\n@r.get("/x")\ndef route(): pass',
        'app = FastAPI()\n@app.get("/x")\n@custom\ndef route(): pass',
        'app = FastAPI()\n@app.get("/x")\ndef route(x=D()): pass',
        'app = FastAPI()\n@app.get("/x", dependencies=[D(Permit)] )\ndef route(): pass',
        'app = FastAPI()\n@app.middleware("http")\ndef middleware(request): pass\n@app.get("/x")\ndef route(): pass',
        'app = FastAPI()\n@app.get("/x", dependencies=factory())\ndef route(): pass',
    ]
    for body in cases:
        graph, endpoints = endpoints_for(
            "from fastapi import FastAPI, APIRouter, Depends as D\nclass Permit: pass\n" + body
        )
        assert endpoints, body
        assert all(not n.properties["control_scope_supported"] for n in endpoints), body
        assert any(d.code == "NEEDS_CONTEXT" for d in graph.diagnostics)


def test_rebinding_and_local_shadow_do_not_create_call_edges():
    for suffix in [
        "def route(target):\n    target()\n",
        "target = unknown\ndef route():\n    target()\n",
        "def route():\n    target = unknown\n    target()\n",
    ]:
        graph = analyze(
            snapshot(
                {
                    "main.py": "from service import target\n" + suffix,
                    "service.py": "def target(): pass\n",
                }
            )
        )
        assert not [e for e in graph.edges if e.type == "CALLS"]


def test_cross_file_import_alias_and_exact_encoded_evidence():
    source = (
        "# coding: latin-1\n# café\nfrom service import work as alias\ndef route():\n    alias()\n"
    )
    snap = snapshot({"main.py": source, "service.py": "def work(): pass\n"})
    raw = source.encode("latin-1")
    snap.files["main.py"] = base64.b64encode(raw).decode()
    graph = analyze(snap)
    assert len([e for e in graph.edges if e.type == "CALLS"]) == 1
    ev = next(e for e in graph.evidence if e.file_path == "main.py" and e.start_line == 1)
    assert (
        ev.excerpt_hash == "sha256:" + hashlib.sha256(raw.splitlines(keepends=True)[0]).hexdigest()
    )


def test_opaque_helper_and_unresolved_calls_mark_path_context_unknown():
    graph = analyze(
        snapshot(
            {
                "main.py": """def wrapper(f): return f
@wrapper
def service():
    return missing()
"""
            }
        )
    )
    service = next(n for n in graph.nodes if n.qualified_name == "main.service")
    assert not service.properties["control_scope_supported"]
    assert not [e for e in graph.edges if e.type == "CALLS"]


def test_three_duplicate_symbols_stay_unresolved():
    graph = analyze(
        snapshot(
            {
                "main.py": """def service(): pass
def service(): pass
def service(): pass
def route(): service()
"""
            }
        )
    )
    assert not [e for e in graph.edges if e.type == "CALLS"]
    assert any(d.code == "NEEDS_CONTEXT" for d in graph.diagnostics)


def test_imports_link_after_all_definitions_are_indexed():
    graph = analyze(
        snapshot(
            {
                "a.py": "from z import service\ndef route(): service()\n",
                "z.py": "def service(): pass\n",
            }
        )
    )
    assert len([e for e in graph.edges if e.type == "IMPORTS"]) == 1
    assert len([e for e in graph.edges if e.type == "CALLS"]) == 1


def test_nested_shadowing_and_local_imports_do_not_use_global_target():
    for body in [
        "def route():\n    def service(): pass\n    service()\n",
        "def route():\n    from unknown import service\n    service()\n",
    ]:
        graph = analyze(
            snapshot(
                {
                    "main.py": "from helper import service\n" + body,
                    "helper.py": "def service(): pass\n",
                }
            )
        )
        assert not [e for e in graph.edges if e.type == "CALLS"]


def test_source_execution_sentinel_is_not_created(tmp_path):
    sentinel = tmp_path / "must-not-exist"
    source = f'from pathlib import Path\nPath({str(sentinel)!r}).write_text("executed")\ndef service(): pass\n'
    graph = analyze(snapshot({"main.py": source}))
    assert graph.nodes
    assert not sentinel.exists()


def test_subdependencies_require_context_instead_of_inferred_absence():
    graph, endpoints = endpoints_for("""from fastapi import FastAPI, Depends
app = FastAPI()
def permit(): pass
def authenticate(permission=Depends(permit)): pass
@app.get("/x")
def route(user=Depends(authenticate)): pass
""")
    assert not endpoints[0].properties["control_scope_supported"]
    assert any(d.code == "NEEDS_CONTEXT" for d in graph.diagnostics)


def test_opaque_constructor_hooks_require_context():
    for body in [
        'app=FastAPI(middleware=[UnknownMiddleware])\n@app.get("/x")\ndef route(): pass\n',
        'app=FastAPI()\nr=APIRouter(route_class=CustomRoute)\napp.include_router(r)\n@r.get("/x")\ndef route(): pass\n',
    ]:
        graph, endpoints = endpoints_for("from fastapi import FastAPI, APIRouter\n" + body)
        assert endpoints
        assert not endpoints[0].properties["control_scope_supported"]
        assert any(d.code == "NEEDS_CONTEXT" for d in graph.diagnostics)


def test_destination_reassignment_or_deletion_cannot_resolve_imported_call():
    for tail in ["service = replacement\n", "del service\n"]:
        graph = analyze(
            snapshot(
                {
                    "main.py": "from helper import service\ndef route(): service()\n",
                    "helper.py": "def service(): pass\n" + tail,
                }
            )
        )
        assert not [e for e in graph.edges if e.type == "CALLS"]


def test_router_include_inside_uninvoked_setup_is_not_exposed():
    graph, endpoints = endpoints_for("""from fastapi import FastAPI, APIRouter
app=FastAPI()
r=APIRouter()
def setup():
    app.include_router(r)
@r.get("/x")
def route(): pass
""")
    assert not endpoints
    assert any(d.code == "NEEDS_CONTEXT" for d in graph.diagnostics)


def test_parent_constructor_kwargs_suppress_inherited_scope():
    graph, endpoints = endpoints_for("""from fastapi import FastAPI, APIRouter
app=FastAPI(**opaque)
r=APIRouter()
app.include_router(r)
@r.get("/x")
def route(): pass
""")
    assert not endpoints[0].properties["control_scope_supported"]
    assert any(d.code == "NEEDS_CONTEXT" for d in graph.diagnostics)


def test_deleted_function_identity_is_explicitly_unsupported():
    graph = analyze(
        snapshot(
            {
                "main.py": "def sensitive(): pass\ndel sensitive\ndef authorize(): pass\ndel authorize\n"
            }
        )
    )
    functions = [n for n in graph.nodes if n.type == "FUNCTION"]
    assert len(functions) == 2
    assert all(not n.properties["control_scope_supported"] for n in functions)


def test_colliding_module_names_cover_both_files_without_resolution():
    graph = analyze(
        snapshot(
            {
                "svc.py": "def sensitive(): pass\n",
                "svc/__init__.py": "def sensitive(): pass\n",
                "main.py": "from svc import sensitive\ndef route(): sensitive()\n",
            }
        )
    )
    covered = {c.file_path: c.status for c in graph.coverage}
    assert covered["svc.py"] == "PARTIALLY_ANALYZED"
    assert covered["svc/__init__.py"] == "PARTIALLY_ANALYZED"
    assert not [e for e in graph.edges if e.type == "CALLS"]
    assert not [n for n in graph.nodes if n.qualified_name == "svc.sensitive"]


def test_aliased_or_forward_annotations_require_context():
    prefix = "from fastapi import FastAPI, Depends\nfrom typing import Annotated\napp=FastAPI()\ndef authorize(): pass\nAuth=Annotated[str,Depends(authorize)]\n"
    for annotation in ["Auth", '"Annotated[str, Depends(authorize)]"', "UnknownType", "list[Auth]"]:
        graph, endpoints = endpoints_for(
            prefix + f'@app.get("/x")\ndef route(permission: {annotation}): pass\n'
        )
        assert not endpoints[0].properties["control_scope_supported"]
        assert any(d.code == "NEEDS_CONTEXT" for d in graph.diagnostics)
    for annotation in ["str", "int", "bool", "float", "bytes"]:
        _, endpoints = endpoints_for(
            prefix + f'@app.get("/x")\ndef route(value: {annotation}): pass\n'
        )
        assert endpoints[0].properties["control_scope_supported"]


def test_aliased_dependency_parameter_annotation_requires_context():
    graph, endpoints = endpoints_for("""from fastapi import FastAPI, Depends
from typing import Annotated
app=FastAPI()
def authorize(): pass
Auth=Annotated[str,Depends(authorize)]
def authenticate(permission: Auth): pass
@app.get("/x")
def route(user=Depends(authenticate)): pass
""")
    assert not endpoints[0].properties["control_scope_supported"]
    assert any(d.code == "NEEDS_CONTEXT" for d in graph.diagnostics)


def test_unsupported_framework_route_decorators_have_coverage_diagnostic():
    for decorator in ["api_route", "websocket", "websocket_route"]:
        graph, endpoints = endpoints_for(
            f'from fastapi import FastAPI\napp=FastAPI()\n@app.{decorator}("/x")\ndef route(): pass\n'
        )
        assert not endpoints
        assert any(d.code == "NEEDS_CONTEXT" for d in graph.diagnostics)
        assert graph.coverage[0].status == "PARTIALLY_ANALYZED"


def test_aliased_defaults_require_context_on_route_and_dependency_function():
    prefix = "from fastapi import FastAPI, Depends\napp=FastAPI()\ndef authorize(): pass\nauth_default=Depends(authorize)\n"
    for body in [
        '@app.get("/x")\ndef route(permission=auth_default): pass\n',
        'def authenticate(permission=auth_default): pass\n@app.get("/x")\ndef route(user=Depends(authenticate)): pass\n',
    ]:
        graph, endpoints = endpoints_for(prefix + body)
        assert not endpoints[0].properties["control_scope_supported"]
        assert any(d.code == "NEEDS_CONTEXT" for d in graph.diagnostics)


def test_literal_parameter_defaults_keep_supported_scope():
    for value in ["None", "1", "1.5", "True", '"synthetic"', 'b"synthetic"']:
        _, endpoints = endpoints_for(
            f'from fastapi import FastAPI\napp=FastAPI()\n@app.get("/x")\ndef route(value={value}): pass\n'
        )
        assert endpoints[0].properties["control_scope_supported"]
