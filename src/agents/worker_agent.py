"""
Worker 执行智能体
负责具体执行 Planner 分配的子任务
"""

from typing import Optional, List, Dict
from zhipuai import ZhipuAI

from config.settings import settings
from src.agents.base_agent import BaseAgent, AgentResponse
from src.agents.react_agent import ReactAgent


class WorkerAgent(BaseAgent):
    """执行智能体：调用 ReAct 智能体完成具体任务"""

    def __init__(self, name: str = "Worker", **kwargs):
        super().__init__(name=name, **kwargs)
        self.client = ZhipuAI(api_key=settings.ZHIPU_API_KEY)
        # Worker 内部使用 ReactAgent 执行复杂任务
        self.react_agent = ReactAgent(name=f"Worker-ReAct", **kwargs)

    def think(self, task: str, context: Optional[str] = None) -> AgentResponse:
        """
        执行一个子任务

        Args:
            task: 子任务描述
            context: 上下文信息（前置任务的输出）

        Returns:
            AgentResponse 对象
        """
        self.add_to_history("user", task)

        # 构建带有上下文的提示
        full_task = task
        if context:
            full_task = f"""任务：{task}

前置任务的输出供你参考：
{context}

请基于以上上下文完成当前任务。"""

        # 使用 ReactAgent 执行
        response = self.react_agent.think(full_task)

        self.add_to_history("assistant", response.content)
        return response