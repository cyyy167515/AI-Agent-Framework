"""
ReAct 智能体（推理 + 行动循环）
实现 Thought → Action → Observation → ... → Final Answer 的循环
"""

import re
import json
from src.tools.file_tool import read_file_tool, write_file_tool, list_files_tool
from src.tools.web_scraper import web_scraper_tool
from src.tools.api_call import api_call_tool
from src.tools.image_gen import image_gen_tool
from config.logging_config import get_logger
logger = get_logger("react_agent")
from typing import List, Dict, Optional, Any

from zhipuai import ZhipuAI

from config.settings import settings
from src.agents.base_agent import BaseAgent, AgentResponse
from src.tools.search_tool import search_tool
from src.tools.calculator_tool import calculator_tool
from src.tools.code_interpreter import code_interpreter_tool

# 注册所有可用工具
AVAILABLE_TOOLS = {
    "web_search": search_tool,
    "calculator": calculator_tool,
    "code_interpreter": code_interpreter_tool,
    "read_file": read_file_tool,
    "write_file": write_file_tool,
    "list_files": list_files_tool,
    "web_scraper": web_scraper_tool,
    "call_api": api_call_tool,
    "image_gen": image_gen_tool,
}

# ReAct 系统提示词模板
REACT_SYSTEM_PROMPT = """你是一个智能助手，使用 ReAct（推理+行动）模式来回答问题。

你可以使用以下工具：
{tool_descriptions}

请严格按照以下格式回答：

Thought: 描述你的思考过程
Action: 工具名称（从上面列表中选择，如果需要的话）
Action Input: 工具的输入参数

Observation: 工具返回的结果（由系统自动填充）

...（可以重复 Thought/Action/Observation 多轮）

Thought: 我现在有了足够的信息来回答
Final Answer: 你的最终回答

重要规则：
1. 每次只能执行一个 Action
2. 如果不需要工具，直接输出 Final Answer
3. 工具名称必须完全匹配上面的列表
4. 用中文思考和回答"""


class ReactAgent(BaseAgent):
    """ReAct 智能体：推理 + 行动循环"""

    def __init__(self, name: str = "ReAct", max_iterations: int = 5, **kwargs):
        """
        Args:
            name: 智能体名称
            max_iterations: 最大思考-行动循环次数，防止无限循环
            **kwargs: 传递给 BaseAgent 的参数
        """
        super().__init__(name=name, **kwargs)
        self.max_iterations = max_iterations

        # 初始化智谱 API 客户端
        self.client = ZhipuAI(api_key=settings.ZHIPU_API_KEY)

        # 构建工具描述文本
        self.tool_descriptions = self._build_tool_descriptions()

        # 构建完整系统提示词
        self.system_prompt = REACT_SYSTEM_PROMPT.format(
            tool_descriptions=self.tool_descriptions
        )

    def _build_tool_descriptions(self) -> str:
        """构建工具描述文本，注入到系统提示词中"""
        lines = []
        for tool_name, tool in AVAILABLE_TOOLS.items():
            lines.append(f"- {tool_name}: {tool.description}")
        return "\n".join(lines)

    def think(self, user_input: str) -> AgentResponse:
        """
        处理用户输入，执行 ReAct 循环

        Args:
            user_input: 用户输入

        Returns:
            AgentResponse 对象
        """
        logger.info(f"[{self.name}] 收到用户输入: {user_input[:50]}...")
        # 1. 将用户输入加入短期记忆
        self.add_to_history("user", user_input)

        # 2. 从长期记忆中检索相关内容
        recalled = self.recall(user_input, n_results=3)
        context_extra = ""
        if recalled:
            context_parts = [f"- {m['content']}" for m in recalled]
            context_extra = "\n\n以下是你可能相关的历史记忆：\n" + "\n".join(context_parts)

        # 3. 构建消息列表
        messages = [{"role": "system", "content": self.system_prompt + context_extra}]

        # 添加对话历史
        for msg in self.get_context(max_turns=10):
            messages.append({"role": msg["role"], "content": msg["content"]})

        # 4. ReAct 循环
        thinking_steps = []
        final_answer = None

        for iteration in range(self.max_iterations):
            # 调用 LLM
            response = self._call_llm(messages)

            # 解析响应
            thought = self._extract_thought(response)
            action, action_input = self._extract_action(response)
            final_answer = self._extract_final_answer(response)

            if thought:
                thinking_steps.append(f"[思考 {iteration + 1}] {thought}")

            # 如果有最终答案，结束循环
            if final_answer:
                break

            # 如果需要执行动作
            if action and action_input:
                observation = self._execute_action(action, action_input)
                thinking_steps.append(f"[动作 {iteration + 1}] {action}({action_input}) → {observation[:200]}")

                # 将观察结果加入消息历史
                messages.append({"role": "assistant", "content": response})
                messages.append({"role": "user", "content": f"Observation: {observation}"})
            else:
                # 没有动作也没有最终答案，强制结束
                final_answer = response
                break

        # 5. 保存助手回复到短期记忆
        answer = final_answer or "抱歉，我未能找到答案。"
        self.add_to_history("assistant", answer)

        # 6. 构建响应
        return AgentResponse(
            content=answer,
            thinking="\n".join(thinking_steps) if thinking_steps else None,
            action=action if action and not final_answer else None,
            action_input=action_input if action_input and not final_answer else None,
        )

    def think_stream(self, user_input: str):
        """
        流式处理用户输入，逐字返回响应

        Args:
            user_input: 用户输入

        Yields:
            字符串片段
        """
        # 将用户输入加入短期记忆
        self.add_to_history("user", user_input)

        # 从长期记忆中检索相关内容
        recalled = self.recall(user_input, n_results=3)
        context_extra = ""
        if recalled:
            context_parts = [f"- {m['content']}" for m in recalled]
            context_extra = "\n\n以下是你可能相关的历史记忆：\n" + "\n".join(context_parts)

        # 构建消息列表
        messages = [{"role": "system", "content": self.system_prompt + context_extra}]

        for msg in self.get_context(max_turns=10):
            messages.append({"role": msg["role"], "content": msg["content"]})

        # 流式调用 LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
            stream=True,  # 启用流式
        )

        # 逐字返回
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def _call_llm(self, messages: List[Dict[str, str]]) -> str:
        """
        调用智谱 API

        Args:
            messages: 消息列表

        Returns:
            模型回复文本
        """
        logger.debug(f"[{self.name}] 调用 LLM，消息数: {len(messages)}")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
        )

        return response.choices[0].message.content

    def _extract_thought(self, text: str) -> Optional[str]:

        """从响应中提取 Thought 内容"""
        match = re.search(r"Thought:\s*(.+?)(?=Action:|Final Answer:|$)", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def _extract_action(self, text: str) -> tuple:

        """
        从响应中提取 Action 和 Action Input

        Returns:
            (action_name, action_input) 或 (None, None)
        """

        action_match = re.search(r"Action:\s*(.+?)\s*$", text, re.MULTILINE)
        input_match = re.search(r"Action Input:\s*(.+?)\s*$", text, re.MULTILINE)

        if action_match:
            action_name = action_match.group(1).strip()
            action_input = input_match.group(1).strip() if input_match else ""
            return action_name, action_input

        return None, None

    def _extract_final_answer(self, text: str) -> Optional[str]:
        """从响应中提取 Final Answer"""
        match = re.search(r"Final Answer:\s*(.+)", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def _execute_action(self, action_name: str, action_input: str) -> str:
        """
        执行工具动作

        Args:
            action_name: 工具名称
            action_input: 工具输入（JSON 字符串或纯文本）

        Returns:
            工具执行结果
        """
        if action_name not in AVAILABLE_TOOLS:
            return f"未知工具: {action_name}。可用工具: {list(AVAILABLE_TOOLS.keys())}"

        tool = AVAILABLE_TOOLS[action_name]
        try:
            # 尝试解析 JSON 输入
            import json
            try:
                parsed_input = json.loads(action_input)
                # 如果是 dict，直接传给工具的 func
                if isinstance(parsed_input, dict):
                    result = tool.func(**parsed_input)
                else:
                    result = tool.run(action_input)
            except (json.JSONDecodeError, TypeError):
                # 如果不是 JSON，当作纯文本传给工具
                result = tool.run(action_input)
            return str(result)
        except Exception as e:
            return f"工具执行出错: {str(e)}"