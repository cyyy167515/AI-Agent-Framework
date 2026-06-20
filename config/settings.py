"""
项目配置管理
从 .env 文件读取环境变量，提供统一的配置访问接口
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件（项目根目录）
_project_root = Path(__file__).resolve().parent.parent
load_dotenv(_project_root / ".env")


class Settings:
    """应用配置单例，所有模块从这里读取配置"""

    # 智谱 API
    ZHIPU_API_KEY: str = os.getenv("ZHIPU_API_KEY", "")
    ZHIPU_MODEL: str = os.getenv("ZHIPU_MODEL", "glm-4")

    # 搜索 API
    SEARCH_API_KEY: str = os.getenv("SEARCH_API_KEY", "")
    SEARCH_ENGINE: str = os.getenv("SEARCH_ENGINE", "serpapi")

    # 向量数据库
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "./data/chroma_db")

    # 应用
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls) -> None:
        """启动前校验必要配置是否已填写"""
        missing = []
        if not cls.ZHIPU_API_KEY:
            missing.append("ZHIPU_API_KEY")
        if not cls.SEARCH_API_KEY:
            missing.append("SEARCH_API_KEY")
        if missing:
            raise RuntimeError(
                f"缺少必要的环境变量: {', '.join(missing)}，请检查 .env 文件"
            )


# 全局配置实例
settings = Settings()
