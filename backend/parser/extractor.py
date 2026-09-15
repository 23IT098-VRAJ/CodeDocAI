import ast

def extract_functions(source_code: str, file_path: str) -> list[dict]:
    """
    Parses Python source code and extracts all standalone functions and class methods.
    Matches A.4 data contract and safely extends it for frontend compatibility.
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return []  # Gracefully skip files with invalid syntax

    results = []

    class FunctionVisitor(ast.NodeVisitor):
        def __init__(self):
            self.class_stack = []

        def visit_ClassDef(self, node):
            self.class_stack.append(node.name)
            self.generic_visit(node)
            self.class_stack.pop()

        def visit_FunctionDef(self, node):
            self._process_function(node)
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node):
            self._process_function(node)
            self.generic_visit(node)

        def _process_function(self, node):
            name = node.name
            if self.class_stack:
                class_prefix = ".".join(self.class_stack)
                name = f"{class_prefix}.{name}"

            # Capture the actual docstring string to pass to the pipeline
            docstring = ast.get_docstring(node)
            has_docstring = bool(docstring)

            start_line = node.lineno
            end_line = getattr(node, 'end_lineno', start_line)
            loc = end_line - start_line + 1

            code_segment = ast.get_source_segment(source_code, node)
            if not code_segment:
                return

            results.append({
                "name": name,
                "file": file_path,
                "code": code_segment,
                "source": code_segment,           # Bridge for frontend docs.py
                "has_docstring": has_docstring,
                "docstring": docstring or "",     # Bridge for pipeline.py logic
                "loc": loc
            })

    visitor = FunctionVisitor()
    visitor.visit(tree)
    return results