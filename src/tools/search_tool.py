"""
搜索引擎工具
使用 SerpApi 进行网络搜索，返回搜索结果
"""

from langchain_core.tools import Tool
from pydantic import BaseModel, Field
import httpx
from config.settings import settings


class SearchInput(BaseModel):
    """搜索工具的输入参数"""
    query: str = Field(description="搜索关键词或问题")


def search_serpapi(query: str) -> str:
    """
    调用 SerpApi 执行搜索，返回摘要结果

    Args:
        query: 搜索关键词

    Returns:
        搜索结果摘要字符串
    """
    api_key = settings.SEARCH_API_KEY
    if not api_key:
        return "错误：未配置 SEARCH_API_KEY，请检查 .env 文件"

    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": api_key,
        "hl": "zh-cn",
        "gl": "cn",
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        results = []
        organic = data.get("organic_results", [])
        for item in organic[:5]:
            title = item.get("title", "无标题")
            snippet = item.get("snippet", "无摘要")
            link = item.get("link", "")
            results.append(f"- {title}\n  {snippet}\n  链接: {link}")

        if not results:
            return "未找到相关搜索结果"

        return "\n\n".join(results)

    except httpx.HTTPStatusError as e:
        return f"搜索请求失败: HTTP {e.response.status_code}"
    except httpx.TimeoutException:
        return "搜索超时，请稍后重试"
    except Exception as e:
        return f"搜索出错: {str(e)}"


search_tool = Tool(
    name="web_search",
    description="搜索引擎工具，用于查询网络信息。输入一个搜索关键词，返回相关的网页结果摘要。当需要查找实时信息、新闻、百科知识时使用。",
    func=search_serpapi,
    args_schema=SearchInput,
)

__all__ = ["search_tool", "search_serpapi"]