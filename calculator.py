#!/usr/bin/env python3
"""
Advanced CLI calculator with:
- Safe expression evaluation via AST (no eval)
- Variables (x = 2 + 3)
- Memory register (M+, M-, MR, MC)
- Command history (history, clear_history)
- Built-in math functions and constants
"""

from __future__ import annotations

import ast
import math
from dataclasses import dataclass, field
from typing import Any


ALLOWED_FUNCTIONS = {
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "pow": pow,
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "floor": math.floor,
    "ceil": math.ceil,
    "factorial": math.factorial,
    "radians": math.radians,
    "degrees": math.degrees,
}

ALLOWED_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
}


class SafeEvaluator(ast.NodeVisitor):
    """Evaluate a restricted Python expression safely."""

    def __init__(self, symbols: dict[str, Any]) -> None:
        self.symbols = symbols

    def evaluate(self, expression: str) -> float:
        parsed = ast.parse(expression, mode="eval")
        result = self.visit(parsed.body)
        if isinstance(result, bool):
            return float(result)
        if not isinstance(result, (int, float)):
            raise ValueError("Expression did not produce a numeric result.")
        return float(result)

    def visit_Constant(self, node: ast.Constant) -> Any:
        if isinstance(node.value, (int, float, bool)):
            return node.value
        raise ValueError(f"Unsupported constant: {node.value!r}")

    def visit_Name(self, node: ast.Name) -> Any:
        if node.id in self.symbols:
            return self.symbols[node.id]
        raise NameError(f"Unknown symbol: {node.id}")

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op
        if isinstance(op, ast.Add):
            return left + right
        if isinstance(op, ast.Sub):
            return left - right
        if isinstance(op, ast.Mult):
            return left * right
        if isinstance(op, ast.Div):
            return left / right
        if isinstance(op, ast.FloorDiv):
            return left // right
        if isinstance(op, ast.Mod):
            return left % right
        if isinstance(op, ast.Pow):
            return left**right
        raise ValueError(f"Unsupported operator: {type(op).__name__}")

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        operand = self.visit(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand
        raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")

    def visit_Call(self, node: ast.Call) -> Any:
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only direct function calls are allowed.")
        func_name = node.func.id
        if func_name not in ALLOWED_FUNCTIONS:
            raise NameError(f"Unknown function: {func_name}")
        func = ALLOWED_FUNCTIONS[func_name]
        args = [self.visit(arg) for arg in node.args]
        return func(*args)

    def visit_Compare(self, node: ast.Compare) -> Any:
        left = self.visit(node.left)
        for op, comparator in zip(node.ops, node.comparators):
            right = self.visit(comparator)
            if isinstance(op, ast.Eq):
                ok = left == right
            elif isinstance(op, ast.NotEq):
                ok = left != right
            elif isinstance(op, ast.Lt):
                ok = left < right
            elif isinstance(op, ast.LtE):
                ok = left <= right
            elif isinstance(op, ast.Gt):
                ok = left > right
            elif isinstance(op, ast.GtE):
                ok = left >= right
            else:
                raise ValueError(f"Unsupported comparison: {type(op).__name__}")
            if not ok:
                return False
            left = right
        return True

    def visit_BoolOp(self, node: ast.BoolOp) -> Any:
        if isinstance(node.op, ast.And):
            result = True
            for value in node.values:
                result = bool(result and self.visit(value))
                if not result:
                    return False
            return result
        if isinstance(node.op, ast.Or):
            result = False
            for value in node.values:
                result = bool(result or self.visit(value))
                if result:
                    return True
            return result
        raise ValueError(f"Unsupported boolean operator: {type(node.op).__name__}")

    def visit_List(self, node: ast.List) -> Any:
        return [self.visit(elt) for elt in node.elts]

    def visit_Tuple(self, node: ast.Tuple) -> Any:
        return tuple(self.visit(elt) for elt in node.elts)

    def generic_visit(self, node: ast.AST) -> Any:
        raise ValueError(f"Unsupported syntax: {type(node).__name__}")


@dataclass
class Calculator:
    variables: dict[str, float] = field(default_factory=dict)
    memory: float = 0.0
    history: list[str] = field(default_factory=list)
    last_result: float = 0.0

    def __post_init__(self) -> None:
        self.variables.update(ALLOWED_CONSTANTS)
        self.variables["ans"] = self.last_result

    def evaluate(self, expression: str) -> float:
        evaluator = SafeEvaluator(self.variables)
        result = evaluator.evaluate(expression)
        self.last_result = result
        self.variables["ans"] = result
        self.history.append(f"{expression} = {self._format_number(result)}")
        return result

    def assign(self, name: str, expression: str) -> float:
        if not name.isidentifier():
            raise ValueError("Invalid variable name.")
        if name in ALLOWED_FUNCTIONS:
            raise ValueError("Cannot overwrite built-in function names.")
        value = self.evaluate(expression)
        self.variables[name] = value
        return value

    def memory_add(self, value: float) -> None:
        self.memory += value

    def memory_subtract(self, value: float) -> None:
        self.memory -= value

    @staticmethod
    def _format_number(value: float) -> str:
        if value.is_integer():
            return str(int(value))
        return f"{value:.12g}"


HELP_TEXT = """
Commands:
  help                Show this help
  vars                Show user variables
  history             Show expressions history
  clear_history       Clear history
  MR                  Memory recall
  MC                  Memory clear
  M+ <expr>           Add expression result to memory
  M- <expr>           Subtract expression result from memory
  quit / exit         Exit calculator

Expression examples:
  2 + 2 * 5
  sqrt(25) + sin(pi / 2)
  x = 10
  x * 3 + ans
  max([2, 7, 3]) + 1
"""


def run_repl() -> None:
    calc = Calculator()
    print("Advanced Python Calculator")
    print("Type 'help' for commands. Type 'exit' to quit.")

    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not line:
            continue

        lowered = line.lower()
        if lowered in {"exit", "quit"}:
            print("Bye!")
            break
        if lowered == "help":
            print(HELP_TEXT.strip())
            continue
        if lowered == "history":
            if not calc.history:
                print("(history is empty)")
            else:
                for idx, item in enumerate(calc.history, start=1):
                    print(f"{idx}. {item}")
            continue
        if lowered == "clear_history":
            calc.history.clear()
            print("History cleared.")
            continue
        if lowered == "vars":
            user_vars = {
                k: v
                for k, v in calc.variables.items()
                if k not in ALLOWED_CONSTANTS and k != "ans"
            }
            if not user_vars:
                print("(no user variables)")
            else:
                for k in sorted(user_vars):
                    print(f"{k} = {calc._format_number(float(user_vars[k]))}")
            print(f"ans = {calc._format_number(calc.last_result)}")
            continue
        if line == "MR":
            print(calc._format_number(calc.memory))
            continue
        if line == "MC":
            calc.memory = 0.0
            print("Memory cleared.")
            continue
        if line.startswith("M+ "):
            expr = line[3:].strip()
            if not expr:
                print("Usage: M+ <expression>")
                continue
            try:
                value = calc.evaluate(expr)
                calc.memory_add(value)
                print(f"Memory = {calc._format_number(calc.memory)}")
            except Exception as exc:
                print(f"Error: {exc}")
            continue
        if line.startswith("M- "):
            expr = line[3:].strip()
            if not expr:
                print("Usage: M- <expression>")
                continue
            try:
                value = calc.evaluate(expr)
                calc.memory_subtract(value)
                print(f"Memory = {calc._format_number(calc.memory)}")
            except Exception as exc:
                print(f"Error: {exc}")
            continue

        try:
            if "=" in line:
                left, right = line.split("=", 1)
                var_name = left.strip()
                expr = right.strip()
                result = calc.assign(var_name, expr)
                print(f"{var_name} = {calc._format_number(result)}")
            else:
                result = calc.evaluate(line)
                print(calc._format_number(result))
        except Exception as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    run_repl()
