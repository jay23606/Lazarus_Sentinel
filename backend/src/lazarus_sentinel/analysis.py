"""Conservative Python AST / literal FastAPI adapter. Never imports target code."""

from __future__ import annotations

import ast
import hashlib
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from .models import (
    Coverage,
    Diagnostic,
    Edge,
    Evidence,
    Graph,
    Node,
    Snapshot,
    source_bytes,
    stable_id,
)


@dataclass
class Module:
    path: str
    name: str
    tree: ast.Module
    raw: bytes
    bindings: dict[str, str] = field(default_factory=dict)
    counts: Counter[str] = field(default_factory=Counter)
    definitions: dict[str, ast.AST] = field(default_factory=dict)
    opaque: bool = False
    control_unknown: bool = False


def dotted(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = dotted(node.value)
        return f"{base}.{node.attr}" if base else None
    return None


def module_name(path: str) -> str:
    name = path[:-3].replace("/", ".")
    return name.removesuffix(".__init__")


def analyze(snapshot: Snapshot) -> Graph:
    item: ast.AST
    target: str | None
    graph = Graph(repository={"revision": snapshot.revision, "root_label": snapshot.root_label})
    modules: dict[str, Module] = {}
    symbols: dict[str, Node] = {}
    ambiguous_symbols: set[str] = set()
    routers: dict[str, tuple[ast.Call, Module, str]] = {}
    hidden_routers: set[str] = set()
    includes: dict[str, list[tuple[str, ast.Call, Module]]] = {}
    evidence_seen: set[str] = set()
    edges_seen: set[str] = set()

    def diagnostic(mod: Module, message: str) -> None:
        graph.diagnostics.append(
            Diagnostic(code="NEEDS_CONTEXT", message=message, file_path=mod.path)
        )

    def evidence(mod: Module, item: ast.AST, query: str) -> str:
        start = getattr(item, "lineno", 1)
        end = getattr(item, "end_lineno", start) or start
        lines = mod.raw.splitlines(keepends=True)
        excerpt = b"".join(lines[start - 1 : end])
        ident = stable_id("evidence", snapshot.revision, mod.path, start, end, query)
        if ident not in evidence_seen:
            evidence_seen.add(ident)
            graph.evidence.append(
                Evidence(
                    id=ident,
                    repository_revision=snapshot.revision,
                    file_path=mod.path,
                    start_line=start,
                    end_line=end,
                    excerpt_hash="sha256:" + hashlib.sha256(excerpt).hexdigest(),
                    rule_or_query_id=query,
                    evidence_kind="AST",
                )
            )
        return ident

    def node(
        mod: Module,
        item: ast.AST,
        kind: str,
        qualified: str,
        properties: dict[str, Any] | None = None,
        display: str | None = None,
    ) -> Node:
        result = Node(
            id=stable_id(
                "node", snapshot.revision, kind, mod.path, qualified, getattr(item, "lineno", 1)
            ),
            type=kind,
            layer="APP" if kind == "API_ENDPOINT" else "CODE",
            name=display or qualified.rsplit(".", 1)[-1],
            qualified_name=qualified,
            properties=properties or {},
            evidence_ids=[evidence(mod, item, "python_ast.structure.v1")],
        )
        graph.nodes.append(result)
        return result

    def edge(mod: Module, item: ast.AST, kind: str, source: Node, target: Node) -> None:
        ev = evidence(
            mod,
            item,
            "fastapi.scope.v1"
            if kind in {"HANDLES", "DEPENDS_ON"}
            else "python_ast.relationship.v1",
        )
        ident = stable_id("edge", snapshot.revision, kind, source.id, target.id, ev)
        if ident not in edges_seen:
            edges_seen.add(ident)
            graph.edges.append(
                Edge(
                    id=ident,
                    source=source.id,
                    target=target.id,
                    type=kind,
                    layer="APP" if kind in {"HANDLES", "DEPENDS_ON"} else "CODE",
                    evidence_ids=[ev],
                    analyzer={"name": "python_ast", "version": "0.1.0"},
                )
            )

    normalized_counts = Counter(
        module_name(path) for path in snapshot.files if path.endswith(".py")
    )
    for path in sorted(snapshot.files):
        if not path.endswith(".py"):
            continue
        if normalized_counts[module_name(path)] > 1:
            graph.coverage.append(
                Coverage(
                    file_path=path,
                    status="PARTIALLY_ANALYZED",
                    reason="Ambiguous normalized module name; extraction withheld.",
                )
            )
            graph.diagnostics.append(
                Diagnostic(
                    code="NEEDS_CONTEXT",
                    message="Multiple source files normalize to one module; identity unresolved.",
                    file_path=path,
                )
            )
            continue
        raw = source_bytes(snapshot, path)
        try:
            tree = ast.parse(raw, filename=path)
        except (SyntaxError, ValueError, UnicodeError, RecursionError):
            graph.coverage.append(
                Coverage(
                    file_path=path,
                    status="PARSER_ERROR",
                    reason="Python AST parsing failed; source text omitted.",
                )
            )
            graph.diagnostics.append(
                Diagnostic(
                    code="PARSER_ERROR", message="Source could not be parsed.", file_path=path
                )
            )
            continue
        mod = Module(path, module_name(path), tree, raw)
        modules[mod.name] = mod
        for item in tree.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                mod.counts[item.name] += 1
                mod.bindings[item.name] = f"{mod.name}.{item.name}"
            elif isinstance(item, ast.Import):
                for alias in item.names:
                    local = alias.asname or alias.name.split(".")[0]
                    mod.counts[local] += 1
                    mod.bindings[local] = alias.name if alias.asname else local
            elif isinstance(item, ast.ImportFrom):
                import_base = item.module or ""
                if item.level:
                    package = (
                        mod.name.split(".")
                        if path.endswith("/__init__.py")
                        else mod.name.split(".")[:-1]
                    )
                    import_base = ".".join(
                        package[: len(package) - item.level + 1]
                        + ([import_base] if import_base else [])
                    )
                for alias in item.names:
                    if alias.name == "*":
                        mod.opaque = True
                        diagnostic(mod, "Wildcard import prevents reliable binding resolution.")
                    else:
                        local = alias.asname or alias.name
                        mod.counts[local] += 1
                        mod.bindings[local] = f"{import_base}.{alias.name}"
            elif isinstance(item, ast.Delete):
                for deleted in item.targets:
                    for deleted_name in ast.walk(deleted):
                        if isinstance(deleted_name, ast.Name):
                            mod.counts[deleted_name.id] += 1
            elif isinstance(item, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                targets = item.targets if isinstance(item, ast.Assign) else [item.target]
                for assignment_target in targets:
                    for part in ast.walk(assignment_target):
                        if isinstance(part, ast.Name):
                            mod.counts[part.id] += 1
                            mod.bindings[part.id] = f"{mod.name}.{part.id}"
        # Conditional writes/imports can change module bindings at runtime.
        direct = {id(x) for x in tree.body}
        for item in ast.walk(tree):
            if (
                isinstance(item, (ast.If, ast.Try, ast.For, ast.While, ast.With, ast.Match))
                and id(item) in direct
            ):
                mod.opaque = True
                diagnostic(mod, "Conditional module bindings are outside the supported subset.")

    def resolve(mod: Module, item: ast.AST, blocked: set[str] | None = None) -> str | None:
        name = dotted(item)
        if not name or mod.opaque:
            return None
        head, *tail = name.split(".")
        if head in (blocked or set()) or mod.counts[head] != 1:
            return None
        base = mod.bindings.get(head)
        return ".".join([base, *tail]) if base else None

    for mod in modules.values():
        module_node = node(mod, mod.tree, "MODULE", mod.name)
        symbols[mod.name] = module_node

        def definitions(body: list[ast.stmt], prefix: str, parent: Node, mod: Module) -> None:
            for item in body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    qualified = f"{prefix}.{item.name}"
                    result = node(
                        mod,
                        item,
                        "CLASS" if isinstance(item, ast.ClassDef) else "FUNCTION",
                        qualified,
                    )
                    if qualified in symbols or qualified in ambiguous_symbols:
                        diagnostic(mod, "Duplicate symbol prevents unambiguous resolution.")
                        symbols.pop(qualified, None)
                        ambiguous_symbols.add(qualified)
                    else:
                        symbols[qualified] = result
                        mod.definitions[qualified] = item
                    edge(mod, item, "CONTAINS", parent, result)
                    definitions(item.body, qualified, result, mod)

        definitions(mod.tree.body, mod.name, module_node, mod)
        for item in mod.tree.body:
            if isinstance(item, (ast.Assign, ast.AnnAssign)) and isinstance(item.value, ast.Call):
                targets = item.targets if isinstance(item, ast.Assign) else [item.target]
                if len(targets) == 1 and isinstance(targets[0], ast.Name):
                    ctor = resolve(mod, item.value.func)
                    if ctor in {"fastapi.FastAPI", "fastapi.APIRouter"}:
                        routers[f"{mod.name}.{targets[0].id}"] = (item.value, mod, ctor)
    # Imports are linked only after all modules and definitions have been indexed.
    for mod in modules.values():
        for import_item in mod.tree.body:
            if isinstance(import_item, (ast.Import, ast.ImportFrom)):
                for alias in import_item.names:
                    if alias.name == "*":
                        continue
                    local = alias.asname or alias.name.split(".")[0]
                    import_target = mod.bindings.get(local, "")
                    if import_target in symbols and mod.counts[local] == 1:
                        edge(mod, import_item, "IMPORTS", symbols[mod.name], symbols[import_target])

    for mod in modules.values():
        direct_calls = {
            id(statement.value) for statement in mod.tree.body if isinstance(statement, ast.Expr)
        }
        for item in ast.walk(mod.tree):
            if not isinstance(item, ast.Call) or not isinstance(item.func, ast.Attribute):
                continue
            base = resolve(mod, item.func.value)
            if item.func.attr == "include_router":
                target = resolve(mod, item.args[0]) if item.args else None
                if base in routers and target in routers and id(item) not in direct_calls:
                    hidden_routers.add(target)
                    diagnostic(mod, "Non-module-level router inclusion has unknown exposure.")
                elif base in routers and target in routers:
                    includes.setdefault(target, []).append((base, item, mod))
                else:
                    diagnostic(mod, "Unresolved router inclusion; scope cannot be established.")
                    mod.control_unknown = True
            elif base in routers and item.func.attr in {"add_api_route", "add_route", "mount"}:
                diagnostic(mod, "Dynamic route registration is not extracted.")
            elif base in routers and item.func.attr in {
                "middleware",
                "add_middleware",
                "exception_handler",
            }:
                diagnostic(
                    mod, "Middleware or application wrappers require external control context."
                )
                # Middleware can cover routes imported from other modules.
                for affected in modules.values():
                    affected.control_unknown = True

    def annotation_supported(mod: Module, annotation: ast.AST) -> bool:
        if isinstance(annotation, ast.Name):
            return (
                annotation.id
                in {
                    "str",
                    "int",
                    "float",
                    "bool",
                    "bytes",
                    "list",
                    "dict",
                    "tuple",
                    "set",
                    "object",
                }
                and mod.counts[annotation.id] == 0
            )
        if isinstance(annotation, ast.Constant) and annotation.value is None:
            return True
        if isinstance(annotation, ast.Subscript) and resolve(mod, annotation.value) in {
            "typing.Annotated",
            "typing_extensions.Annotated",
        }:
            parts = annotation.slice.elts if isinstance(annotation.slice, ast.Tuple) else []
            return (
                bool(parts)
                and annotation_supported(mod, parts[0])
                and all(
                    isinstance(meta, ast.Call)
                    and resolve(mod, meta.func) in {"fastapi.Depends", "fastapi.Security"}
                    for meta in parts[1:]
                )
            )
        return False

    def default_supported(mod: Module, default: ast.AST) -> bool:
        if isinstance(default, ast.Constant):
            return default.value is None or isinstance(
                default.value, (str, bytes, bool, int, float)
            )
        if isinstance(default, ast.UnaryOp) and isinstance(default.op, (ast.UAdd, ast.USub)):
            return isinstance(default.operand, ast.Constant) and type(default.operand.value) in {
                int,
                float,
            }
        return isinstance(default, ast.Call) and resolve(mod, default.func) in {
            "fastapi.Depends",
            "fastapi.Security",
        }

    methods = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}
    for mod in modules.values():
        for qualified, definition in mod.definitions.items():
            if qualified not in symbols or not isinstance(
                definition, (ast.FunctionDef, ast.AsyncFunctionDef)
            ):
                continue
            supported_decorators = all(
                isinstance(d, ast.Call)
                and isinstance(d.func, ast.Attribute)
                and d.func.attr in methods
                and resolve(mod, d.func.value) in routers
                for d in definition.decorator_list
            )
            supported_defaults = all(
                default_supported(mod, default)
                for default in [
                    *definition.args.defaults,
                    *(x for x in definition.args.kw_defaults if x is not None),
                ]
            )
            supported_annotations = all(
                argument.annotation is None or annotation_supported(mod, argument.annotation)
                for argument in definition.args.posonlyargs
                + definition.args.args
                + definition.args.kwonlyargs
            )
            symbols[qualified].properties["control_scope_supported"] = (
                supported_decorators
                and supported_annotations
                and supported_defaults
                and not mod.opaque
                and not mod.control_unknown
                and mod.counts[definition.name] == 1
                and mod.bindings.get(definition.name) == qualified
            )
            if mod.counts[definition.name] != 1 or mod.bindings.get(definition.name) != qualified:
                diagnostic(mod, "Function binding is not a unique stable module identity.")
            if not supported_defaults:
                diagnostic(
                    mod,
                    "Unresolved parameter default may carry dependencies; control context requires review.",
                )
            if not supported_annotations:
                diagnostic(
                    mod,
                    "Unresolved parameter annotation may carry dependencies; control context requires review.",
                )
            if not supported_decorators:
                diagnostic(mod, "Opaque function decorator; control context requires review.")

    def function_target(name: str | None) -> bool:
        if name is None or name not in symbols or symbols[name].type != "FUNCTION":
            return False
        owner_name, _, local = name.rpartition(".")
        destination = modules.get(owner_name)
        return (
            destination is not None
            and not destination.opaque
            and destination.counts[local] == 1
            and destination.bindings.get(local) == name
        )

    def has_dependency_parameters(mod: Module, definition: ast.AST) -> bool:
        if not isinstance(definition, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return False
        return any(
            isinstance(part, ast.Call)
            and resolve(mod, part.func) in {"fastapi.Depends", "fastapi.Security"}
            for argument in [
                *definition.args.defaults,
                *(x for x in definition.args.kw_defaults if x is not None),
                *(
                    a.annotation
                    for a in definition.args.posonlyargs
                    + definition.args.args
                    + definition.args.kwonlyargs
                    if a.annotation
                ),
            ]
            for part in ast.walk(argument)
        )

    def dependencies(
        mod: Module, value: ast.AST | None
    ) -> tuple[list[tuple[str, ast.AST, Module]], bool]:
        if value is None:
            return [], True
        if not isinstance(value, (ast.List, ast.Tuple)):
            return [], False
        found: list[tuple[str, ast.AST, Module]] = []
        supported = True
        for part in value.elts:
            if isinstance(part, ast.Call) and resolve(mod, part.func) in {
                "fastapi.Depends",
                "fastapi.Security",
            }:
                target = resolve(mod, part.args[0]) if part.args else None
                if function_target(target):
                    assert target is not None
                    found.append((target, part, mod))
                    destination = modules[target.rpartition(".")[0]]
                    definition = destination.definitions[target]
                    if has_dependency_parameters(destination, definition):
                        supported = False
                        diagnostic(
                            mod, "Dependency subdependencies require external control context."
                        )
                    supported = supported and symbols[target].properties.get(
                        "control_scope_supported", False
                    )
                else:
                    supported = False
            else:
                supported = False
        return found, supported

    def keyword(call: ast.Call, name: str) -> ast.AST | None:
        return next((k.value for k in call.keywords if k.arg == name), None)

    def literal_prefix(call: ast.Call) -> tuple[str, bool]:
        value = keyword(call, "prefix")
        return (
            ("", True)
            if value is None
            else (value.value, True)
            if isinstance(value, ast.Constant) and isinstance(value.value, str)
            else ("", False)
        )

    def constructor_supported(call: ast.Call) -> bool:
        return not any(
            k.arg is None or k.arg in {"middleware", "route_class"} for k in call.keywords
        )

    def scope(name: str) -> tuple[str, list[tuple[str, ast.AST, Module]], bool]:
        call, mod, ctor = routers[name]
        prefix, supported = literal_prefix(call)
        deps, ok = dependencies(mod, keyword(call, "dependencies"))
        supported = (
            supported
            and ok
            and not mod.opaque
            and not mod.control_unknown
            and constructor_supported(call)
        )
        if ctor == "fastapi.FastAPI":
            return prefix, deps, supported and name not in includes
        contexts = includes.get(name, [])
        if len(contexts) != 1:
            diagnostic(mod, "Router is not included exactly once; endpoint exposure unknown.")
            return prefix, deps, False
        parent, include, include_mod = contexts[0]
        parent_call, parent_mod, parent_ctor = routers[parent]
        if parent_ctor != "fastapi.FastAPI":
            diagnostic(mod, "Nested router inclusion is unsupported.")
            return prefix, deps, False
        parent_deps, parent_ok = dependencies(parent_mod, keyword(parent_call, "dependencies"))
        include_deps, include_ok = dependencies(include_mod, keyword(include, "dependencies"))
        include_prefix, prefix_ok = literal_prefix(include)
        return (
            include_prefix + prefix,
            parent_deps + include_deps + deps,
            supported
            and parent_ok
            and constructor_supported(parent_call)
            and include_ok
            and prefix_ok
            and not parent_mod.opaque
            and not include_mod.opaque
            and not parent_mod.control_unknown
            and not include_mod.control_unknown
            and not any(k.arg is None for k in include.keywords),
        )

    methods = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}
    for mod in modules.values():
        for qualified, item in mod.definitions.items():
            if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            function = symbols.get(qualified)
            if function is None:
                continue
            args = item.args
            blocked = {a.arg for a in args.posonlyargs + args.args + args.kwonlyargs}
            if args.vararg:
                blocked.add(args.vararg.arg)
            if args.kwarg:
                blocked.add(args.kwarg.arg)
            # Nested scopes and local writes prevent lexical alias assumptions.
            for part in ast.walk(item):
                if isinstance(part, ast.Name) and isinstance(part.ctx, (ast.Store, ast.Del)):
                    blocked.add(part.id)
                if (
                    isinstance(part, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                    and part is not item
                ):
                    blocked.add(part.name)
                if isinstance(part, (ast.Import, ast.ImportFrom)):
                    blocked.update(a.asname or a.name.split(".")[0] for a in part.names)
            body_nodes: list[ast.AST] = []
            pending: list[ast.AST] = list(item.body)
            while pending:
                part = pending.pop()
                if isinstance(
                    part, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)
                ):
                    continue
                body_nodes.append(part)
                pending.extend(ast.iter_child_nodes(part))
            for part in body_nodes:
                if isinstance(part, ast.Call):
                    target = resolve(mod, part.func, blocked)
                    if function_target(target):
                        assert target is not None
                        edge(mod, part, "CALLS", function, symbols[target])
                    else:
                        diagnostic(mod, "Unresolved call; no call edge asserted.")
                        function.properties["control_scope_supported"] = False
            route_decorators = [
                d
                for d in item.decorator_list
                if isinstance(d, ast.Call)
                and isinstance(d.func, ast.Attribute)
                and d.func.attr in methods
                and resolve(mod, d.func.value) in routers
            ]
            if not route_decorators:
                if any(
                    isinstance(d, ast.Call)
                    and isinstance(d.func, ast.Attribute)
                    and d.func.attr in methods
                    for d in item.decorator_list
                ):
                    diagnostic(mod, "Unresolved route receiver; endpoint exposure unknown.")
                continue
            for dec in route_decorators:
                assert isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute)
                owner = resolve(mod, dec.func.value)
                assert owner is not None
                if owner in hidden_routers:
                    diagnostic(mod, "Endpoint exposure depends on unsupported router inclusion.")
                    continue
                prefix, dep, supported = scope(owner)
                supported = (
                    supported
                    and len(route_decorators) == len(item.decorator_list)
                    and qualified == f"{mod.name}.{item.name}"
                )
                literal = dec.args[0] if dec.args else keyword(dec, "path")
                if not isinstance(literal, ast.Constant) or not isinstance(literal.value, str):
                    diagnostic(mod, "Nonliteral route path is not extracted.")
                    continue
                extra, ok = dependencies(mod, keyword(dec, "dependencies"))
                dep += extra
                supported = supported and ok and not any(k.arg is None for k in dec.keywords)
                defaults = list(args.defaults) + [x for x in args.kw_defaults if x is not None]
                for default in defaults:
                    if isinstance(default, ast.Call) and resolve(mod, default.func) in {
                        "fastapi.Depends",
                        "fastapi.Security",
                    }:
                        extra, ok = dependencies(mod, ast.List(elts=[default], ctx=ast.Load()))
                        dep += extra
                        supported = supported and ok
                    elif isinstance(default, ast.Call):
                        supported = False
                for arg in args.posonlyargs + args.args + args.kwonlyargs:
                    ann = arg.annotation
                    if isinstance(ann, ast.Subscript) and resolve(mod, ann.value) in {
                        "typing.Annotated",
                        "typing_extensions.Annotated",
                    }:
                        parts = ann.slice.elts if isinstance(ann.slice, ast.Tuple) else []
                        for meta in parts[1:]:
                            if isinstance(meta, ast.Call) and resolve(mod, meta.func) in {
                                "fastapi.Depends",
                                "fastapi.Security",
                            }:
                                extra, ok = dependencies(mod, ast.List(elts=[meta], ctx=ast.Load()))
                                dep += extra
                                supported = supported and ok
                            else:
                                supported = False
                supported = supported and function.properties.get("control_scope_supported", False)
                if not supported:
                    diagnostic(
                        mod,
                        "Endpoint control scope unsupported; authorization assessment requires context.",
                    )
                path = prefix + literal.value
                display = f"{dec.func.attr.upper()} {path}"
                endpoint = node(
                    mod,
                    dec,
                    "API_ENDPOINT",
                    f"{qualified}:{display}",
                    properties={
                        "handler_id": function.id,
                        "method": dec.func.attr.upper(),
                        "path": path,
                        "dependencies": sorted({x[0] for x in dep}),
                        "control_scope_supported": supported,
                    },
                    display=display,
                )
                edge(mod, dec, "HANDLES", endpoint, function)
                for target, declaration, declaration_mod in dep:
                    edge(declaration_mod, declaration, "DEPENDS_ON", endpoint, symbols[target])
    for mod in modules.values():
        partial = any(d.file_path == mod.path for d in graph.diagnostics)
        graph.coverage.append(
            Coverage(
                file_path=mod.path,
                status="PARTIALLY_ANALYZED" if partial else "ANALYZED",
                reason="Static subset only; no dataflow or runtime execution.",
                affected_concepts=["CALLS", "API_ENDPOINT", "DEPENDS_ON"],
            )
        )
    return graph
