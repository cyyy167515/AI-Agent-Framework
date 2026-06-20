"""
智能体模块单元测试
"""

import pytest
from src.agents.base_agent import BaseAgent, AgentResponse
from src.agents.planner_agent import PlannerAgent, PlannerOutput
from src.agents.reviewer_agent import ReviewerAgent, ReviewResult


class TestAgentResponse:
    """AgentResponse 结构测试"""

    def test_default_values(self):
        resp = AgentResponse(content="hello")
        assert resp.content == "hello"
        assert resp.thinking is None
        assert resp.need_memory is False

    def test_with_thinking(self):
        resp = AgentResponse(content="answer", thinking="思考过程")
        assert resp.thinking == "思考过程"


class TestBaseAgent:
    """基类测试"""

    def test_repr(self):
        # BaseAgent 是抽象类，用 ReactAgent 测试 repr
        from src.agents.react_agent import ReactAgent
        agent = ReactAgent()
        assert "ReactAgent" in repr(agent)
        assert "glm-4" in repr(agent)


class TestPlannerAgent:
    """Planner 智能体测试"""

    def test_simple_task(self):
        planner = PlannerAgent()
        result = planner.think("计算 1+1")
        assert result.total_count >= 1
        assert len(result.subtasks) >= 1


class TestReviewerAgent:
    """Reviewer 智能体测试"""

    def test_review_format(self):
        reviewer = ReviewerAgent()
        result = reviewer.think(
            task="测试任务",
            output="这是一个简单但完整的回答。"
        )
        assert isinstance(result.score, int)
        assert 1 <= result.score <= 10
        assert isinstance(result.approved, bool)
        assert isinstance(result.feedback, str)