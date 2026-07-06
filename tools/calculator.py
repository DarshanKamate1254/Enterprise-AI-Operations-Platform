import ast
import operator as op
from typing import Union


class CalculatorTool:
    """
    Mathematical Calculator Tool that evaluates basic math expressions safely.
    Uses AST (Abstract Syntax Tree) parsing instead of raw eval() to prevent security risks.
    """
    # Supported operators mapping to standard python math operations
    SUPPORTED_OPERATORS = {
        ast.Add: op.add,
        ast.Sub: op.sub,
        ast.Mult: op.mul,
        ast.Div: op.truediv,
        ast.Pow: op.pow,
        ast.USub: op.neg,
        ast.UAdd: op.pos
    }

    def _eval(self, node: ast.AST) -> Union[int, float]:
        if isinstance(node, ast.Constant):  # Python >= 3.8
            if not isinstance(node.value, (int, float)):
                raise TypeError(f"Unsupported constant type: {type(node.value)}")
            return node.value
        elif hasattr(ast, "Num") and isinstance(node, getattr(ast, "Num")):  # Fallback for older python configurations
            return node.n
        elif isinstance(node, ast.BinOp):
            left_val = self._eval(node.left)
            right_val = self._eval(node.right)
            op_type = type(node.op)
            if op_type not in self.SUPPORTED_OPERATORS:
                raise TypeError(f"Unsupported mathematical operator: {op_type}")
            return self.SUPPORTED_OPERATORS[op_type](left_val, right_val)
        elif isinstance(node, ast.UnaryOp):
            val = self._eval(node.operand)
            op_type = type(node.op)
            if op_type not in self.SUPPORTED_OPERATORS:
                raise TypeError(f"Unsupported unary operator: {op_type}")
            return self.SUPPORTED_OPERATORS[op_type](val)
        else:
            raise TypeError(f"Unsupported syntax construct: {type(node)}")

    def calculate(self, expression: str) -> Union[int, float]:
        """
        Parses and evaluates a mathematical string expression.
        Supported operators: +, -, *, /, **, (, )
        """
        # Remove spaces
        cleaned = expression.replace(" ", "")
        if not cleaned:
            raise ValueError("Expression is empty.")

        try:
            tree = ast.parse(cleaned, mode="eval")
            return self._eval(tree.body)
        except Exception as e:
            raise ValueError(f"Failed to evaluate mathematical expression '{expression}': {str(e)}")
