"""
工具模块单元测试
"""

import pytest
from src.tools.calculator_tool import calculator_tool, calculator
from src.tools.code_interpreter import code_interpreter_tool, code_interpreter


class TestCalculator:
    """计算器工具测试"""

    def test_addition(self):
        result = calculator("2 + 3")
        assert result == "5"

    def test_multiplication(self):
        result = calculator("2 + 3 * 4")
        assert result == "14"

    def test_division(self):
        result = calculator("10 / 2")
        assert result == "5"

    def test_power(self):
        result = calculator("2 ** 3")
        assert result == "8"

    def test_negative(self):
        result = calculator("-5 + 3")
        assert result == "-2"

    def test_float_result(self):
        result = calculator("1 / 3")
        assert "0.33" in result or "0." in result

    def test_empty_input(self):
        result = calculator("")
        assert "请输入" in result

    def test_invalid_expression(self):
        result = calculator("abc")
        assert "计算错误" in result

    def test_tool_run(self):
        result = calculator_tool.run("1 + 1")
        assert result == "2"


class TestCodeInterpreter:
    """代码解释器工具测试"""

    def test_print_output(self):
        result = code_interpreter("print('hello')")
        assert "hello" in result

    def test_list_comprehension(self):
        result = code_interpreter("print([x**2 for x in range(5)])")
        assert "[0, 1, 4, 9, 16]" in result

    def test_variable(self):
        result = code_interpreter("x = 42\nprint(x)")
        assert "42" in result

    def test_empty_input(self):
        result = code_interpreter("")
        assert "请输入" in result

    def test_forbidden_import(self):
        result = code_interpreter("import os")
        assert "禁止" in result

    def test_forbidden_open(self):
        result = code_interpreter("open('file.txt')")
        assert "禁止" in result

    def test_math_operation(self):
        result = code_interpreter("print(sum([1, 2, 3, 4, 5]))")
        assert "15" in result