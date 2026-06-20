import os
from pathlib import Path
from typing import Optional
from langchain_core.tools import Tool
from pydantic import BaseModel, Field
import zipfile

class ReadFileInput(BaseModel):
    file_path: str = Field(description='????')

class WriteFileInput(BaseModel):
    file_path: str = Field(description='????')
    content: str = Field(description='????')

class ListFilesInput(BaseModel):
    directory: Optional[str] = Field(default='.', description='????')

def read_file(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        return f'??: ????? {file_path}'
    if not path.is_file():
        return f'??: ?????? {file_path}'
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f'??: {e}'

def write_file(file_path: str, content: str) -> str:
    if not Path(file_path).is_absolute():
        project_root = Path(__file__).resolve().parent.parent.parent
        file_path = str(project_root / file_path)
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f'????: {file_path}'
    except Exception as e:
        return f'??: {e}'

def list_directory(directory: str = '.') -> str:
    dir_path = Path(directory).resolve()
    if not dir_path.exists():
        return f'??: ????? {directory}'
    if not dir_path.is_dir():
        return f'??: ?????? {directory}'
    items = []
    for item in sorted(dir_path.iterdir()):
        if item.is_dir():
            items.append(f'[DIR] {item.name}')
        else:
            size = item.stat().st_size
            items.append(f'[FILE] {item.name} ({size} bytes)')
    return '\n'.join(items) if items else '????'

def extract_zip(zip_path: str, extract_to: str = None) -> str:
    zip_obj = Path(zip_path)
    if not zip_obj.exists() or not zip_obj.suffix == '.zip':
        return f'??: ???ZIP?? {zip_path}'
    extract_dir = Path(extract_to) if extract_to else zip_obj.parent
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(extract_dir)
        return f'?????: {extract_dir}'
    except Exception as e:
        return f'??: {e}'

read_file_tool = Tool(
    name='read_file',
    description='读取文件内容。参数 file_path 是文件路径。示例输入: {"file_path": "test.txt"}',
    func=read_file,
    args_schema=ReadFileInput,
)

write_file_tool = Tool(
    name='write_file',
    description='写入文件。参数 file_path 是文件路径，content 是文件内容。示例输入: {"file_path": "test.txt", "content": "hello"}',
    func=write_file,
    args_schema=WriteFileInput,
)

list_files_tool = Tool(
    name='list_files',
    description='列出目录内容。参数 directory 是目录路径，默认为当前目录。示例输入: {"directory": "."}',
    func=list_directory,
    args_schema=ListFilesInput,
)

extract_zip_tool = Tool(
    name='extract_zip',
    description='??ZIP???',
    func=extract_zip,
)

__all__ = ['read_file_tool', 'write_file_tool', 'list_files_tool', 'extract_zip_tool']
