"""
记忆模块单元测试
"""

import pytest
from src.memory.short_term import ShortTermMemory
from src.memory.long_term import LongTermMemory


class TestShortTermMemory:
    """短期记忆测试"""

    def test_add_message(self):
        mem = ShortTermMemory()
        mem.add_message("user", "你好")
        msgs = mem.get_messages()
        assert len(msgs) == 1
        assert msgs[0]["role"] == "user"

    def test_max_messages(self):
        mem = ShortTermMemory(max_messages=3)
        for i in range(5):
            mem.add_message("user", f"msg_{i}")
        assert len(mem.get_messages()) == 3

    def test_get_recent(self):
        mem = ShortTermMemory()
        mem.add_message("user", "msg1")
        mem.add_message("assistant", "msg2")
        mem.add_message("user", "msg3")
        recent = mem.get_recent(2)
        assert len(recent) == 2
        assert recent[1]["content"] == "msg3"

    def test_clear(self):
        mem = ShortTermMemory()
        mem.add_message("user", "hello")
        mem.clear()
        assert len(mem.get_messages()) == 0

    def test_summary(self):
        mem = ShortTermMemory()
        mem.add_message("user", "你好")
        summary = mem.summary()
        assert "你好" in summary

    def test_empty_summary(self):
        mem = ShortTermMemory()
        assert "暂无" in mem.summary()


class TestLongTermMemory:
    """长期记忆测试"""

    def test_add_and_search(self):
        mem = LongTermMemory()
        mem.add_memory("Python 是动态类型语言", {"role": "user"})
        mem.add_memory("Chroma 是向量数据库", {"role": "assistant"})
        results = mem.search("向量数据库", n_results=1)
        assert len(results) >= 1
        assert "Chroma" in results[0]["content"]
        mem.clear()

    def test_get_all(self):
        mem = LongTermMemory()
        mem.add_memory("测试记忆1")
        mem.add_memory("测试记忆2")
        all_mem = mem.get_all()
        assert len(all_mem) == 2
        mem.clear()

    def test_clear(self):
        mem = LongTermMemory()
        mem.add_memory("test")
        mem.clear()
        assert len(mem.get_all()) == 0

    def test_delete_memory(self):
        mem = LongTermMemory()
        mid = mem.add_memory("要删除的记忆")
        mem.delete_memory(mid)
        assert len(mem.get_all()) == 0