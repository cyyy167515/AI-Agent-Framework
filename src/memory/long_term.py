"""
长期记忆模块
使用 Chroma 向量数据库存储和检索历史对话
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional
from config.settings import settings


class LongTermMemory:
    """长期记忆，使用 Chroma 向量数据库持久化存储"""

    def __init__(self, collection_name: str = "agent_memory", persist_dir: Optional[str] = None):
        """
        Args:
            collection_name: Chroma 集合名称
            persist_dir: 数据库持久化路径，默认使用配置中的 VECTOR_DB_PATH
        """
        if persist_dir is None:
            persist_dir = settings.VECTOR_DB_PATH

        # 初始化 Chroma 客户端（持久化模式）
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},  # 余弦相似度
        )

    def add_memory(self, text: str, metadata: Optional[Dict] = None) -> str:
        """
        添加一条记忆到向量数据库

        Args:
            text: 记忆文本内容
            metadata: 附加元数据，如 {"role": "user", "timestamp": "..."}

        Returns:
            记忆 ID
        """
        # 生成唯一 ID（简单递增）
        count = self.collection.count()
        memory_id = f"mem_{count:06d}"

        add_kwargs = {
            'ids': [memory_id],
            'documents': [text],
        }
        if metadata:
            add_kwargs['metadatas'] = [metadata]
        self.collection.add(**add_kwargs)

        return memory_id

    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        根据查询检索相关记忆

        Args:
            query: 查询文本
            n_results: 返回结果数量

        Returns:
            相关记忆列表
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
        )

        memories = []
        if results["ids"] and results["ids"][0]:
            for i, mem_id in enumerate(results["ids"][0]):
                memories.append({
                    "id": mem_id,
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else None,
                })

        return memories

    def get_all(self, limit: int = 100) -> List[Dict]:
        """
        获取所有记忆（用于调试或导出）

        Args:
            limit: 最大返回数量

        Returns:
            记忆列表
        """
        results = self.collection.get(limit=limit)

        memories = []
        for i, mem_id in enumerate(results["ids"]):
            memories.append({
                "id": mem_id,
                "content": results["documents"][i],
                "metadata": results["metadatas"][i] if results["metadatas"] else {},
            })

        return memories

    def clear(self) -> None:
        """清空所有记忆"""
        all_ids = self.collection.get()["ids"]
        if all_ids:
            self.collection.delete(ids=all_ids)

    def delete_memory(self, memory_id: str) -> None:
        """
        删除指定记忆

        Args:
            memory_id: 记忆 ID
        """
        self.collection.delete(ids=[memory_id])