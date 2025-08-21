# calculator/evaluator.py
import ast
import operator as op
from typing import Union

Number = Union[int, float]

class EvalError(Exception):
    """Raised on invalid or unsafe math expressions."""

_ALLOWED = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}

def safe_eval(expr: str) -> Number:
    """Safely evaluate a math expression supporting + - * / ^ and parentheses."""
    if not expr or not isinstance(expr, str):
        raise EvalError("Empty or invalid expression.")
    # allow '^' as power
    expr = expr.replace("^", "**")

    def _eval(node: ast.AST) -> Number:
        if isinstance(node, ast.Num):  # py<3.8
            return node.n
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED:
            return _ALLOWED[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED:
            return _ALLOWED[type(node.op)](_eval(node.operand))
        raise EvalError("Unsupported operation or structure.")

    try:
        parsed = ast.parse(expr, mode="eval")
        return _eval(parsed.body)
    except EvalError:
        raise
    except ZeroDivisionError:
        raise EvalError("Division by zero.")
    except Exception as e:
        raise EvalError(f"Invalid expression: {e}")
