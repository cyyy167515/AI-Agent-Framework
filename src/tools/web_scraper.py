import httpx
from langchain_core.tools import Tool
from pydantic import BaseModel, Field
from typing import Optional
import re

class WebScraperInput(BaseModel):
    url: str = Field(description='??URL')

class WebScraperInput(BaseModel):
    url: str = Field(description='??URL')

def scrape_webpage(url: str) -> str:
    try:
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            html = response.text
            text = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL)
            text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:5000]
    except Exception as e:
        return f'??: {e}'

web_scraper_tool = Tool(
    name='web_scraper',
    description='???????????URL?????????????HTML????',
    func=scrape_webpage,
    args_schema=WebScraperInput,
)

__all__ = ['web_scraper_tool', 'scrape_webpage']
