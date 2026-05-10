#!/usr/bin/env python3
import ast
import tkinter as tk
from tkinter import font


class ExpressionEvaluator(ast.NodeVisitor):
    def evaluate(self, expression: str) -> float:
        parsed = ast.parse(expression, mode="eval")
        value = self.visit(parsed.body)
        if not isinstance(value, (int, float)):
            raise ValueError("Invalid expression")
        return float(value)

    def visit_Constant(self, node: ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Unsupported constant")

    def visit_UnaryOp(self, node: ast.UnaryOp):
        operand = self.visit(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand
        raise ValueError("Unsupported unary operator")

    def visit_BinOp(self, node: ast.BinOp):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        raise ValueError("Unsupported operation")

    def generic_visit(self, node):
        raise ValueError("Unsupported expression")


class WindowsStyleCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.geometry("360x540")
        self.minsize(320, 500)
        self.configure(bg="#1f1f1f")

        self.evaluator = ExpressionEvaluator()
        self.expression = "0"
        self.error_state = False

        self._build_ui()
        self._bind_keys()
        self._refresh_display()

    def _build_ui(self):
        self.display_var = tk.StringVar(value="0")
        self.small_var = tk.StringVar(value="")

        display_frame = tk.Frame(self, bg="#1f1f1f")
        display_frame.pack(fill="x", padx=12, pady=(12, 8))

        small_font = font.Font(family="Segoe UI", size=12)
        large_font = font.Font(family="Segoe UI", size=34, weight="bold")

        small_label = tk.Label(
            display_frame,
            textvariable=self.small_var,
            anchor="e",
            bg="#1f1f1f",
            fg="#b0b0b0",
            font=small_font,
            height=2,
        )
        small_label.pack(fill="x")

        main_label = tk.Label(
            display_frame,
            textvariable=self.display_var,
            anchor="e",
            bg="#1f1f1f",
            fg="#ffffff",
            font=large_font,
            height=2,
        )
        main_label.pack(fill="x")

        buttons_frame = tk.Frame(self, bg="#1f1f1f")
        buttons_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        for i in range(6):
            buttons_frame.grid_rowconfigure(i, weight=1, uniform="row")
        for j in range(4):
            buttons_frame.grid_columnconfigure(j, weight=1, uniform="col")

        layout = [
            [("%", self._percent), ("CE", self._clear_entry), ("C", self._clear_all), ("⌫", self._backspace)],
            [("1/x", self._not_implemented), ("x²", self._square), ("√x", self._sqrt), ("÷", lambda: self._append_operator("/"))],
            [("7", lambda: self._append_digit("7")), ("8", lambda: self._append_digit("8")), ("9", lambda: self._append_digit("9")), ("×", lambda: self._append_operator("*"))],
            [("4", lambda: self._append_digit("4")), ("5", lambda: self._append_digit("5")), ("6", lambda: self._append_digit("6")), ("−", lambda: self._append_operator("-"))],
            [("1", lambda: self._append_digit("1")), ("2", lambda: self._append_digit("2")), ("3", lambda: self._append_digit("3")), ("+", lambda: self._append_operator("+"))],
            [("+/-", self._toggle_sign), ("0", lambda: self._append_digit("0")), (",", self._append_decimal), ("=", self._calculate)],
        ]

        for r, row in enumerate(layout):
            for c, (label, action) in enumerate(row):
                is_op = c == 3 or label == "="
                is_top = r == 0 or (r == 1 and c < 3)
                bg = "#4c4c4c" if is_op else ("#2a2a2a" if is_top else "#333333")
                fg = "#ffffff"
                btn = tk.Button(
                    buttons_frame,
                    text=label,
                    command=action,
                    bg=bg,
                    fg=fg,
                    activebackground="#5a5a5a",
                    activeforeground="#ffffff",
                    relief="flat",
                    borderwidth=0,
                    font=("Segoe UI", 16),
                )
                btn.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)

    def _bind_keys(self):
        for key in "0123456789":
            self.bind(key, lambda event, d=key: self._append_digit(d))
        for key in "+-*/":
            self.bind(key, lambda event, op=key: self._append_operator(op))
        self.bind("<Return>", lambda event: self._calculate())
        self.bind("<KP_Enter>", lambda event: self._calculate())
        self.bind("<BackSpace>", lambda event: self._backspace())
        self.bind("<Escape>", lambda event: self._clear_all())
        self.bind(".", lambda event: self._append_decimal())
        self.bind(",", lambda event: self._append_decimal())

    def _clear_error_if_needed(self):
        if self.error_state:
            self.expression = "0"
            self.error_state = False

    def _append_digit(self, digit: str):
        self._clear_error_if_needed()
        if self.expression == "0":
            self.expression = digit
        else:
            self.expression += digit
        self._refresh_display()

    def _append_decimal(self):
        self._clear_error_if_needed()
        tokens = self._tokenize(self.expression)
        current = tokens[-1] if tokens else ""
        if "." in current and self._is_number_token(current):
            return
        if not current or current in {"+", "-", "*", "/"}:
            self.expression += "0."
        else:
            self.expression += "."
        self._refresh_display()

    def _append_operator(self, operator: str):
        self._clear_error_if_needed()
        if self.expression.endswith((" + ", " - ", " * ", " / ")):
            self.expression = self.expression[:-3] + f" {operator} "
        else:
            self.expression += f" {operator} "
        self._refresh_display()

    def _clear_entry(self):
        self._clear_error_if_needed()
        tokens = self._tokenize(self.expression)
        if not tokens:
            self.expression = "0"
        elif len(tokens) == 1:
            self.expression = "0"
        else:
            if tokens[-1] in {"+", "-", "*", "/"}:
                self.expression = " ".join(tokens[:-1]).strip() or "0"
            else:
                tokens[-1] = "0"
                self.expression = " ".join(tokens)
        self._refresh_display()

    def _clear_all(self):
        self.expression = "0"
        self.small_var.set("")
        self.error_state = False
        self._refresh_display()

    def _backspace(self):
        self._clear_error_if_needed()
        if self.expression == "0":
            return
        if self.expression.endswith(" "):
            self.expression = self.expression[:-3]
        else:
            self.expression = self.expression[:-1]
        if not self.expression:
            self.expression = "0"
        self._refresh_display()

    def _toggle_sign(self):
        self._clear_error_if_needed()
        tokens = self._tokenize(self.expression)
        if not tokens:
            return
        last = tokens[-1]
        if not self._is_number_token(last):
            return
        number = float(last)
        number = -number
        tokens[-1] = self._format_number(number)
        self.expression = " ".join(tokens)
        self._refresh_display()

    def _percent(self):
        self._clear_error_if_needed()
        tokens = self._tokenize(self.expression)
        if not tokens:
            return
        if not self._is_number_token(tokens[-1]):
            return
        value = float(tokens[-1]) / 100.0
        tokens[-1] = self._format_number(value)
        self.expression = " ".join(tokens)
        self._refresh_display()

    def _square(self):
        self._clear_error_if_needed()
        tokens = self._tokenize(self.expression)
        if not tokens or not self._is_number_token(tokens[-1]):
            return
        value = float(tokens[-1])
        tokens[-1] = self._format_number(value * value)
        self.expression = " ".join(tokens)
        self._refresh_display()

    def _sqrt(self):
        self._clear_error_if_needed()
        tokens = self._tokenize(self.expression)
        if not tokens or not self._is_number_token(tokens[-1]):
            return
        value = float(tokens[-1])
        if value < 0:
            self._show_error()
            return
        tokens[-1] = self._format_number(value**0.5)
        self.expression = " ".join(tokens)
        self._refresh_display()

    def _not_implemented(self):
        self.small_var.set("Feature is not implemented in this demo")

    def _calculate(self):
        self._clear_error_if_needed()
        expr = self.expression.strip()
        if expr.endswith(("+", "-", "*", "/")):
            expr = expr[:-1].strip()
        if not expr:
            return
        try:
            result = self.evaluator.evaluate(expr)
            self.small_var.set(expr + " =")
            self.expression = self._format_number(result)
            self._refresh_display()
        except Exception:
            self._show_error()

    def _show_error(self):
        self.display_var.set("Error")
        self.error_state = True

    def _refresh_display(self):
        pretty = self.expression.replace("*", "×").replace("/", "÷").replace("-", "−")
        self.display_var.set(pretty if pretty else "0")

    @staticmethod
    def _tokenize(expression: str) -> list[str]:
        return expression.strip().split()

    @staticmethod
    def _is_number_token(token: str) -> bool:
        try:
            float(token)
            return True
        except ValueError:
            return False

    @staticmethod
    def _format_number(value: float) -> str:
        if value.is_integer():
            return str(int(value))
        return f"{value:.12g}"


if __name__ == "__main__":
    app = WindowsStyleCalculator()
    app.mainloop()
