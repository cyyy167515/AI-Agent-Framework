import os
from pathlib import Path
from zhipuai import ZhipuAI
from config.settings import settings
from langchain_core.tools import Tool
from pydantic import BaseModel, Field
from config.logging_config import get_logger

logger = get_logger('image_gen')

class ImageGenInput(BaseModel):
    prompt: str = Field(description='???????')

def generate_image(prompt: str) -> str:
    try:
        client = ZhipuAI(api_key=settings.ZHIPU_API_KEY)
        response = client.images.generations(
            model='cogview-3-plus',
            prompt=prompt,
        )
        
        if response.data and len(response.data) > 0:
            image_url = response.data[0].url
            
            output_dir = Path(__file__).resolve().parent.parent.parent / 'data' / 'images'
            output_dir.mkdir(parents=True, exist_ok=True)
            
            import httpx
            with httpx.Client(timeout=30.0) as http_client:
                img_response = http_client.get(image_url)
                img_response.raise_for_status()
                
                filename = f'gen_{hash(prompt) % 100000}.png'
                filepath = output_dir / filename
                with open(filepath, 'wb') as f:
                    f.write(img_response.content)
            
            logger.info(f'??????: {filepath}')
            return f'?????????: {filepath}\n???: {prompt}'
        else:
            return '??: ?????????'
    except Exception as e:
        logger.error(f'??????: {e}')
        return f'??: ?????? - {e}'

image_gen_tool = Tool(
    name='image_gen',
    description='???????????????????CogView??????????',
    func=generate_image,
    args_schema=ImageGenInput,
)

__all__ = ['image_gen_tool', 'generate_image']
