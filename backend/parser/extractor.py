import ast
import textwrap

MAX_ATTRIBUTE_CHARS = 100


def extract_module_docstring(source_code: str) -> str:
    """Returns the module-level docstring, or "" if there is none or the file does not parse."""
    try:
        return ast.get_docstring(ast.parse(source_code)) or ""
    except SyntaxError:
        return ""


def _class_header(node: ast.ClassDef, name: str) -> str:
    parents = [ast.unparse(base) for base in node.bases] + [ast.unparse(keyword) for keyword in node.keywords]
    return f"class {name}({', '.join(parents)})" if parents else f"class {name}"


def _class_skeleton(node: ast.ClassDef) -> str:
    """
    The class without its method bodies: header, class-level attributes and method
    signatures. Methods are extracted separately, so repeating their bodies here
    would only duplicate them.
    """
    lines = [_class_header(node, node.name) + ":"]
    for statement in node.body:
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
            prefix = "async def" if isinstance(statement, ast.AsyncFunctionDef) else "def"
            lines.append(f"    {prefix} {statement.name}({ast.unparse(statement.args)}): ...")
        elif isinstance(statement, ast.ClassDef):
            lines.append(f"    class {statement.name}: ...")
        elif isinstance(statement, (ast.Assign, ast.AnnAssign)):
            lines.append("    " + ast.unparse(statement)[:MAX_ATTRIBUTE_CHARS])
    if len(lines) == 1:
        lines.append("    ...")
    return "\n".join(lines)


def extract_definitions(source_code: str, file_path: str) -> list[dict]:
    """
    Parses Python source code and extracts every class, function and method, in
    source order. Each entry carries:

        name            dotted name, e.g. "Inventory.add_item", or "outer.inner" for a
                        function nested in another function
        kind            "function", "method" (directly inside a class) or "class"
        signature       "name(args)" or "class Name(Base)"
        source / code   the function's source, or the class skeleton
        has_docstring, docstring
        lineno          line of the def/class keyword (1-based)
        body_lineno     line of the first statement of the body
        body_col        column of that statement
        loc             number of lines
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return []  # Gracefully skip files with invalid syntax

    results = []

    class DefinitionVisitor(ast.NodeVisitor):
        def __init__(self):
            # (name, is_class) for every enclosing class and function
            self.scope: list[tuple[str, bool]] = []

        def _qualified(self, name: str) -> str:
            return ".".join([*(scope_name for scope_name, _ in self.scope), name])

        def _entry(self, node, name: str, kind: str, signature: str, code: str) -> dict:
            docstring = ast.get_docstring(node)
            end_line = getattr(node, 'end_lineno', node.lineno)
            return {
                "name": name,
                "kind": kind,
                "signature": signature,
                "file": file_path,
                "code": code,
                "source": code,                   # Bridge for frontend docs.py
                "has_docstring": bool(docstring),
                "docstring": docstring or "",     # Bridge for pipeline.py logic
                "lineno": node.lineno,
                "body_lineno": node.body[0].lineno,
                "body_col": node.body[0].col_offset,
                "loc": end_line - node.lineno + 1,
            }

        def visit_ClassDef(self, node):
            name = self._qualified(node.name)
            results.append(self._entry(node, name, "class", _class_header(node, name), _class_skeleton(node)))
            self.scope.append((node.name, True))
            self.generic_visit(node)
            self.scope.pop()

        def visit_FunctionDef(self, node):
            self._process_function(node)
            self.scope.append((node.name, False))
            self.generic_visit(node)
            self.scope.pop()

        visit_AsyncFunctionDef = visit_FunctionDef

        def _process_function(self, node):
            # padded=True keeps the indentation of the def line, so dedenting the whole
            # segment leaves a method looking like a normal top-level function.
            code_segment = ast.get_source_segment(source_code, node, padded=True)
            if not code_segment:
                return
            code_segment = textwrap.dedent(code_segment)
            name = self._qualified(node.name)
            kind = "method" if self.scope and self.scope[-1][1] else "function"
            results.append(self._entry(node, name, kind, f"{name}({ast.unparse(node.args)})", code_segment))

    DefinitionVisitor().visit(tree)
    return results


def extract_functions(source_code: str, file_path: str) -> list[dict]:
    """Functions and methods only (see extract_definitions for classes as well)."""
    return [d for d in extract_definitions(source_code, file_path) if d["kind"] != "class"]
