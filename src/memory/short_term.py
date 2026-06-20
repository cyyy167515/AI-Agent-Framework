"""
短期记忆模块
维护对话历史列表，限制最大长度以防止上下文过长
"""

from typing import List, Dict, Any
from collections import deque


class ShortTermMemory:
    """短期记忆，使用 deque 维护固定长度的对话历史"""

    def __init__(self, max_messages: int = 20):
        """
        Args:
            max_messages: 最大保留消息条数
        """
        self.max_messages = max_messages
        self.history: deque = deque(maxlen=max_messages)

    def add_message(self, role: str, content: str) -> None:
        """
        添加一条消息到历史

        Args:
            role: 角色名称，如 'user', 'assistant', 'system'
            content: 消息内容
        """
        self.history.append({"role": role, "content": content})

    def get_messages(self) -> List[Dict[str, str]]:
        """
        获取完整的消息历史列表

        Returns:
            消息列表，格式为 [{"role": ..., "content": ...}]
        """
        return list(self.history)

    def get_recent(self, n: int = 5) -> List[Dict[str, str]]:
        """
        获取最近 n 条消息

        Args:
            n: 要获取的消息条数

        Returns:
            最近的消息列表
        """
        return list(self.history)[-n:]

    def clear(self) -> None:
        """清空短期记忆"""
        self.history.clear()

    def summary(self) -> str:
        """
        返回记忆的文本摘要

        Returns:
            格式化后的对话文本
        """
        if not self.history:
            return "暂无记忆"

        lines = [f"[{msg['role']}]: {msg['content']}" for msg in self.history]
        return "\n".join(lines)