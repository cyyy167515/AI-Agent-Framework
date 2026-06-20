import httpx
import json
from langchain_core.tools import Tool
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ApiCallInput(BaseModel):
    method: str = Field(description='HTTP??: GET, POST, PUT, DELETE')
    url: str = Field(description='API URL')
    headers: Optional[str] = Field(default='{}', description='JSON???headers')
    body: Optional[str] = Field(default='{}', description='JSON??????')

def call_api(method: str, url: str, headers: str = '{}', body: str = '{}') -> str:
    try:
        headers_dict = json.loads(headers) if headers else {}
        body_dict = json.loads(body) if body else {}
        
        with httpx.Client(timeout=15.0) as client:
            if method.upper() == 'GET':
                response = client.get(url, headers=headers_dict, params=body_dict)
            elif method.upper() == 'POST':
                response = client.post(url, headers=headers_dict, json=body_dict)
            elif method.upper() == 'PUT':
                response = client.put(url, headers=headers_dict, json=body_dict)
            elif method.upper() == 'DELETE':
                response = client.delete(url, headers=headers_dict)
            else:
                return f'??: ????HTTP?? {method}'
            
            result = {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'body': response.text[:2000]
            }
            return json.dumps(result, ensure_ascii=False, indent=2)
    except json.JSONDecodeError as e:
        return f'??: JSON???? - {e}'
    except Exception as e:
        return f'??: {e}'

api_call_tool = Tool(
    name='call_api',
    description='??RESTful API???HTTP???URL?headers?body?JSON?????????',
    func=call_api,
    args_schema=ApiCallInput,
)

__all__ = ['api_call_tool', 'call_api']
