# utils/math_utils.py
import re

# Detects if user text is likely a pure math query (numbers/operators)
_MATH_CHARS = re.compile(r"[0-9\+\-\*\/\^\(\)\.\s]")

def is_math_question(text: str) -> bool:
    if not text:
        return False
    # Heuristic: contains only math-ish chars and at least a digit+operator
    only_mathish = all(_MATH_CHARS.match(ch) for ch in text)
    has_digit = any(ch.isdigit() for ch in text)
    has_op = any(op in text for op in ("+", "-", "*", "/", "^"))
    return (only_mathish and has_digit and has_op) or bool(re.search(r"\d+\s*[\+\-\*\/\^]\s*\d+", text))

def extract_expression(text: str) -> str | None:
    if not text:
        return None
    # Extract the largest block of math-like expression:
    matches = re.findall(r"[0-9\.\s\+\-\*\/\^\(\)]+", text)
    if not matches:
        return None
    expr = max(matches, key=len).strip()
    # Sanitize multiple spaces
    expr = re.sub(r"\s+", "", expr)
    return expr or None
