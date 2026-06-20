"""
计算器工具
支持基本四则运算和数学函数
"""

import math
import ast
import operator

from langchain_core.tools import Tool
from pydantic import BaseModel, Field


class CalculatorInput(BaseModel):
    """计算器工具的输入参数"""
    expression: str = Field(description="数学表达式，如 '2 + 3 * 4' 或 'sin(0.5)'")


def _safe_eval(expression: str) -> str:
    """
    安全地计算数学表达式，不使用 eval()

    支持：加减乘除、幂运算、括号、常用数学函数
    """
    # 支持的数学函数
    safe_funcs = {
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
        "exp": math.exp, "abs": abs, "round": round,
        "pi": math.pi, "e": math.e,
    }

    # 支持的运算符
    operators_map = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }

    try:
        node = ast.parse(expression, mode="eval").body

        def _eval_node(n):
            if isinstance(n, ast.Constant):
                return n.value
            elif isinstance(n, ast.BinOp):
                left = _eval_node(n.left)
                right = _eval_node(n.right)
                op_func = operators_map[type(n.op)]
                return op_func(left, right)
            elif isinstance(n, ast.UnaryOp):
                operand = _eval_node(n.operand)
                return operators_map[type(n.op)](operand)
            elif isinstance(n, ast.Call):
                func_name = n.func.id if hasattr(n.func, "id") else None
                if func_name not in safe_funcs:
                    raise ValueError(f"不支持的函数: {func_name}")
                args = [_eval_node(arg) for arg in n.args]
                return safe_funcs[func_name](*args)
            elif isinstance(n, ast.Name):
                if n.id in safe_funcs:
                    return safe_funcs[n.id]
                raise ValueError(f"未知变量: {n.id}")
            else:
                raise ValueError(f"不支持的语法: {type(n).__name__}")

        result = _eval_node(node)

        # 处理浮点数精度问题
        if isinstance(result, float) and result == int(result):
            result = int(result)

        return str(result)

    except Exception as e:
        return f"计算错误: {str(e)}"


def calculator(expression: str) -> str:
    """
    计算数学表达式

    Args:
        expression: 数学表达式

    Returns:
        计算结果
    """
    if not expression.strip():
        return "请输入要计算的表达式"

    return _safe_eval(expression)


# 创建 LangChain Tool 实例
calculator_tool = Tool(
    name="calculator",
    description="计算器工具，用于执行数学计算。支持加减乘除、幂运算、括号、以及 sin/cos/tan/sqrt/log 等数学函数。当需要进行数值计算时使用。",
    func=calculator,
    args_schema=CalculatorInput,
)

__all__ = ["calculator_tool", "calculator"]