"""
智能体基类
定义智能体的通用接口和基础能力
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from config.settings import settings
from src.memory.short_term import ShortTermMemory
from src.memory.long_term import LongTermMemory


class AgentResponse(BaseModel):
    """智能体响应结构"""
    content: str = Field(description="回复内容")
    thinking: Optional[str] = Field(default=None, description="思考过程")
    action: Optional[str] = Field(default=None, description="执行的动作名称")
    action_input: Optional[str] = Field(default=None, description="动作输入")
    need_memory: bool = Field(default=False, description="是否需要存入长期记忆")


class BaseAgent(ABC):
    """智能体抽象基类"""

    def __init__(
            self,
            name: str,
            model: Optional[str] = None,
            short_term: Optional[ShortTermMemory] = None,
            long_term: Optional[LongTermMemory] = None,
    ):
        """
        Args:
            name: 智能体名称
            model: 使用的模型名称，默认从配置读取
            short_term: 短期记忆实例
            long_term: 长期记忆实例
        """
        self.name = name
        self.model = model or settings.ZHIPU_MODEL
        self.short_term = short_term or ShortTermMemory()
        self.long_term = long_term

    @abstractmethod
    def think(self, user_input: str) -> AgentResponse:
        """
        处理用户输入，生成响应（子类必须实现）

        Args:
            user_input: 用户输入文本

        Returns:
            AgentResponse 对象
        """
        pass

    def remember(self, content: str, metadata: Optional[Dict] = None) -> str:
        """
        将内容存入长期记忆

        Args:
            content: 要记忆的内容
            metadata: 附加元数据

        Returns:
            记忆 ID
        """
        if self.long_term is None:
            self.long_term = LongTermMemory()

        return self.long_term.add_memory(content, metadata)

    def recall(self, query: str, n_results: int = 3) -> List[Dict]:
        """
        从长期记忆中检索相关内容

        Args:
            query: 查询文本
            n_results: 返回结果数量

        Returns:
            相关记忆列表
        """
        if self.long_term is None:
            return []

        return self.long_term.search(query, n_results)

    def get_context(self, max_turns: int = 5) -> List[Dict[str, str]]:
        """
        获取对话上下文

        Args:
            max_turns: 最大轮数

        Returns:
            消息列表
        """
        return self.short_term.get_recent(max_turns)

    def add_to_history(self, role: str, content: str) -> None:
        """
        添加消息到对话历史

        Args:
            role: 角色
            content: 内容
        """
        self.short_term.add_message(role, content)

    def clear_memory(self) -> None:
        """清空所有记忆"""
        self.short_term.clear()
        if self.long_term:
            self.long_term.clear()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name='{self.name}' model='{self.model}'>"