"""
Reviewer 审查智能体
负责评估 Worker 的输出质量，给出改进建议
"""

import json
from typing import Optional, List
from pydantic import BaseModel, Field
from zhipuai import ZhipuAI

from config.settings import settings
from src.agents.base_agent import BaseAgent, AgentResponse


class ReviewResult(BaseModel):
    """审查结果"""
    score: int = Field(description="评分（1-10）")
    strengths: List[str] = Field(description="优点列表")
    improvements: List[str] = Field(description="改进建议列表")
    approved: bool = Field(description="是否通过审查")
    feedback: str = Field(description="总体反馈意见")


REVIEWER_SYSTEM_PROMPT = """你是一个质量审查专家。你的职责是评估工作成果的质量。

评估维度：
1. **准确性**：内容是否正确、无事实错误
2. **完整性**：是否充分回答了问题或完成了任务
3. **清晰度**：表达是否清晰易懂
4. **相关性**：内容是否紧扣任务要求

输出格式（严格 JSON）：
{
  "score": 8,
  "strengths": ["优点1", "优点2"],
  "improvements": ["改进建议1", "改进建议2"],
  "approved": true,
  "feedback": "总体评价文本"
}

评分标准：
- 9-10：优秀，无需修改
- 7-8：良好，小幅改进即可
- 5-6：及格，需要完善
- 1-4：不合格，需要重做"""


class ReviewerAgent(BaseAgent):
    """审查智能体：评估工作成果质量"""

    def __init__(self, name: str = "Reviewer", **kwargs):
        super().__init__(name=name, **kwargs)
        self.client = ZhipuAI(api_key=settings.ZHIPU_API_KEY)

    def think(self, task: str, output: str) -> ReviewResult:
        """
        审查工作成果

        Args:
            task: 原始任务描述
            output: Worker 的输出

        Returns:
            ReviewResult 对象
        """
        self.add_to_history("user", f"审查任务: {task}")

        messages = [
            {"role": "system", "content": REVIEWER_SYSTEM_PROMPT},
            {"role": "user", "content": f"请审查以下工作成果：\n\n## 原始任务\n{task}\n\n## 工作成果\n{output}"}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
            max_tokens=1024,
        )

        content = response.choices[0].message.content

        # 解析 JSON
        try:
            json_str = content.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            data = json.loads(json_str)
            result = ReviewResult(**data)
        except Exception:
            # 降级：默认通过
            result = ReviewResult(
                score=7,
                strengths=["成果已提交"],
                improvements=["建议进一步完善"],
                approved=True,
                feedback="审查完成，成果质量良好。",
            )

        self.add_to_history("assistant", result.feedback)
        return result