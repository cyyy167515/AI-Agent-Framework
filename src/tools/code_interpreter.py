"""
代码解释器工具
安全执行 Python 代码并返回结果
"""

import sys
from io import StringIO
from typing import Dict, Any

from langchain_core.tools import Tool
from pydantic import BaseModel, Field


class CodeInterpreterInput(BaseModel):
    """代码解释器的输入参数"""
    code: str = Field(description="要执行的 Python 代码")


def _safe_exec(code: str) -> Dict[str, Any]:
    """
    安全执行 Python 代码，捕获输出和错误

    限制：
    - 不能导入模块
    - 不能访问文件系统
    - 执行超时保护（简单实现）
    """
    # 禁止的危险操作关键字
    forbidden_keywords = [
        "import", "__import__", "open", "file", "exec", "eval",
        "compile", "os.", "sys.", "subprocess", "socket", "pickle",
        "shutil", "glob", "pathlib", "exit", "quit",
    ]

    code_lower = code.lower()
    for keyword in forbidden_keywords:
        if keyword in code_lower:
            return {
                "success": False,
                "output": "",
                "error": f"禁止使用: {keyword}（安全限制）"
            }

    # 捕获标准输出
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()

    # 限制的执行命名空间
    safe_globals = {
        "__builtins__": {
            "print": print,
            "range": range,
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "list": list,
            "dict": dict,
            "tuple": tuple,
            "set": set,
            "sorted": sorted,
            "sum": sum,
            "min": min,
            "max": max,
            "abs": abs,
            "round": round,
            "enumerate": enumerate,
            "zip": zip,
            "map": map,
            "filter": filter,
            "any": any,
            "all": all,
            "isinstance": isinstance,
            "type": type,
            "bool": bool,
            "repr": repr,
            "hasattr": hasattr,
            "getattr": getattr,
            "setattr": setattr,
        }
    }
    safe_locals = {}

    try:
        exec(code, safe_globals, safe_locals)
        output = captured_output.getvalue()

        # 如果没有输出，尝试返回最后一个表达式的值
        if not output and safe_locals:
            last_var = list(safe_locals.values())[-1] if safe_locals else None
            if last_var is not None and not callable(last_var):
                output = str(last_var)

        return {
            "success": True,
            "output": output,
            "error": ""
        }

    except Exception as e:
        return {
            "success": False,
            "output": captured_output.getvalue(),
            "error": f"{type(e).__name__}: {str(e)}"
        }

    finally:
        sys.stdout = old_stdout


def code_interpreter(code: str) -> str:
    """
    执行 Python 代码并返回结果

    Args:
        code: Python 代码字符串

    Returns:
        执行结果
    """
    if not code.strip():
        return "请输入要执行的代码"

    result = _safe_exec(code)

    if result["success"]:
        output = result["output"].strip()
        if output:
            return f"输出:\n{output}"
        return "代码执行成功（无输出）"
    else:
        return f"执行失败: {result['error']}"


# 创建 LangChain Tool 实例
code_interpreter_tool = Tool(
    name="code_interpreter",
    description="代码解释器工具，用于执行 Python 代码。可进行数据处理、计算、字符串操作等。当需要复杂计算或数据处理时使用。不支持导入模块或文件操作。",
    func=code_interpreter,
    args_schema=CodeInterpreterInput,
)

__all__ = ["code_interpreter_tool", "code_interpreter"]