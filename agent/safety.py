import ast
import os
from pathlib import Path


# -----------------------------
# Path sandboxing
# -----------------------------
def is_path_safe(path, allowed_paths):
    abs_path = os.path.abspath(path)
    return any(
        abs_path.startswith(os.path.abspath(p))
        for p in allowed_paths
    )


# -----------------------------
# AST-based code safety check
# -----------------------------
class UnsafeCodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.issues = []

    def visit_Call(self, node):
        # Detect dangerous function calls more reliably
        try:
            if isinstance(node.func, ast.Name):
                if node.func.id in {"eval", "exec"}:
                    self.issues.append(f"Use of {node.func.id}() is unsafe")

            if isinstance(node.func, ast.Attribute):
                if node.func.attr in {"system", "popen"}:
                    self.issues.append(f"Use of {node.func.attr}() may be unsafe")

        except Exception:
            pass

        self.generic_visit(node)


# -----------------------------
# Main validation function
# -----------------------------
def validate_code(code: str):
    """
    Returns:
        (bool, message)
    """

    # 1. Basic string-level checks (fast fail)
    banned_patterns = [
        "os.system",
        "subprocess",
        "eval(",
        "exec(",
        "__import__",
    ]

    for pattern in banned_patterns:
        if pattern in code:
            return False, f"Unsafe pattern detected: {pattern}"

    # 2. AST-based deeper inspection
    try:
        tree = ast.parse(code)
        visitor = UnsafeCodeVisitor()
        visitor.visit(tree)

        if visitor.issues:
            return False, "; ".join(visitor.issues)

    except SyntaxError as e:
        return False, f"Syntax error in generated code: {e}"

    except Exception as e:
        return False, f"AST validation failed: {e}"

    return True, "OK"