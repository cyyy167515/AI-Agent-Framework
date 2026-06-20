"""日志配置模块"""

import logging
import logging.handlers
from pathlib import Path

# 日志目录
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"


def setup_logging(log_level: str = "INFO"):
    """配置全局日志系统"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台输出
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)

    # 文件输出（按大小轮转，10MB，保留7个）
    file = logging.handlers.RotatingFileHandler(
        filename=LOG_DIR / "app.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=7,
        encoding="utf-8",
    )
    file.setLevel(logging.DEBUG)
    file.setFormatter(formatter)

    # 配置根 Logger
    root = logging.getLogger()
    root.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    root.handlers.clear()
    root.addHandler(console)
    root.addHandler(file)

    return root


def get_logger(name: str):
    """获取指定名称的 Logger"""
    return logging.getLogger(name)


# 初始化
logger = setup_logging()