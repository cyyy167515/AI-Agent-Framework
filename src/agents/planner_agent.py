"""
Planner 规划智能体
负责将复杂任务分解为可执行的子任务列表
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from zhipuai import ZhipuAI

from config.settings import settings
from src.agents.base_agent import BaseAgent, AgentResponse


class SubTask(BaseModel):
    """子任务结构"""
    id: int = Field(description="任务编号")
    description: str = Field(description="任务描述")
    depends_on: List[int] = Field(default=[], description="依赖的前置任务编号")
    assigned_to: str = Field(default="worker", description="分配给的角色")


class PlannerOutput(BaseModel):
    """Planner 的输出结构"""
    subtasks: List[SubTask] = Field(description="子任务列表")
    total_count: int = Field(description="子任务总数")


# Planner 系统提示词
PLANNER_SYSTEM_PROMPT = """你是一个任务规划专家。你的职责是将用户的复杂任务分解为一系列可执行的子任务。

规划原则：
1. 将大任务拆解为小的、可独立执行的步骤
2. 标明任务之间的依赖关系
3. 保持任务描述简洁明确
4. 如果任务简单，不需要分解，直接返回单一任务

输出格式要求：
你必须严格按照以下 JSON 格式输出，不要包含任何其他文字：

{
  "subtasks": [
    {
      "id": 1,
      "description": "任务描述",
      "depends_on": [],
      "assigned_to": "worker"
    }
  ],
  "total_count": 1
}

注意：
- id 从 1 开始递增
- depends_on 是依赖的任务 id 列表（数字数组）
- 如果任务很简单（一句话就能完成），total_count 设为 1
- 如果任务复杂需要多步，合理拆分"""


class PlannerAgent(BaseAgent):
    """规划智能体：任务分解"""

    def __init__(self, name: str = "Planner", **kwargs):
        super().__init__(name=name, **kwargs)
        self.client = ZhipuAI(api_key=settings.ZHIPU_API_KEY)

    def think(self, user_input: str) -> PlannerOutput:
        """
        接收用户任务，分解为子任务列表

        Args:
            user_input: 用户输入的任务描述

        Returns:
            PlannerOutput 对象
        """
        self.add_to_history("user", user_input)

        messages = [
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": f"请分解以下任务：\n{user_input}"}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,  # 规划需要确定性
            max_tokens=1024,
        )

        content = response.choices[0].message.content

        # 解析 JSON 输出
        import json
        try:
            # 尝试提取 JSON 块（处理可能包含的代码块标记）
            json_str = content.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()

            data = json.loads(json_str)
            result = PlannerOutput(**data)
        except (json.JSONDecodeError, Exception) as e:
            # 降级处理：如果 JSON 解析失败，创建一个默认任务
            result = PlannerOutput(
                subtasks=[SubTask(id=1, description=user_input, depends_on=[], assigned_to="worker")],
                total_count=1,
            )

        self.add_to_history("assistant", str(result))
        return result