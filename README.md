# AI-Agent-Framework

基于 LangChain + LangGraph 的多智能体协作框架，集成 ReAct 推理模式与 Planner-Worker-Reviewer 工作流，支持工具调用、短期/长期记忆、用户系统和 Web 交互界面。

## 功能特性

- **ReAct 智能体** - 推理 + 行动循环（Thought -> Action -> Observation -> Final Answer）
- **多智能体协作** - Planner 分解任务 -> Worker 执行 -> Reviewer 审查，支持迭代优化
- **9 个工具链** - 搜索、计算器、代码解释器、文件读写、网页抓取、API 调用、图片生成
- **记忆系统** - 短期记忆（对话历史）+ 长期记忆（Chroma 向量数据库）
- **用户系统** - 多用户支持、对话持久化、历史导出
- **流式输出** - SSE 流式响应，实时显示生成内容
- **Web 界面** - Streamlit 交互界面，支持对话和工作流两种模式
- **HTTP API** - FastAPI 提供完整的 RESTful 接口

## 技术栈

| 组件 | 技术 |
|------|------|
| 智能体框架 | LangChain, LangGraph |
| LLM | 智谱 GLM-4 (zhipuai) |
| Web 框架 | FastAPI + Uvicorn |
| 前端界面 | Streamlit |
| 向量数据库 | ChromaDB |
| 图片生成 | 智谱 CogView |
| 配置管理 | python-dotenv |

## 项目结构

```text
AI-Agent-Framework/
├── src/
│   ├── agents/
│   │   ├── base_agent.py          # 智能体基类
│   │   ├── react_agent.py         # ReAct 智能体（支持流式）
│   │   ├── planner_agent.py       # 任务规划
│   │   ├── worker_agent.py        # 任务执行
│   │   └── reviewer_agent.py      # 质量审查
│   ├── tools/
│   │   ├── search_tool.py         # SerpApi 搜索引擎
│   │   ├── calculator_tool.py     # 安全计算器
│   │   ├── code_interpreter.py    # 代码解释器
│   │   ├── file_tool.py           # 文件读写工具
│   │   ├── web_scraper.py         # 网页抓取工具
│   │   ├── api_call.py            # RESTful API 调用
│   │   └── image_gen.py           # 图片生成工具
│   ├── memory/
│   │   ├── short_term.py          # 短期记忆（对话历史）
│   │   └── long_term.py           # 长期记忆（向量数据库）
│   ├── graph/
│   │   └── workflow.py            # LangGraph 工作流
│   ├── user/
│   │   ├── user_manager.py        # 用户管理
│   │   └── conversation_store.py  # 对话持久化
│   ├── api/
│   │   └── routes.py              # FastAPI 路由
│   └── ui/
│       └── streamlit_app.py       # Streamlit 界面
├── config/
│   ├── settings.py                # 配置管理
│   └── logging_config.py          # 日志配置
├── tests/                         # 单元测试
├── data/                          # 数据存储（gitignore）
├── .env.example                   # 环境变量模板
├── requirements.txt
└── README.md


## 安装

### 1. 环境要求
- Python 3.10+

### 2. 克隆项目
`ash
git clone https://github.com/cyyy167515/AI-Agent-Framework.git
cd AI-Agent-Framework
`

### 3. 安装依赖
`ash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
`

### 4. 配置环境变量
复制 .env.example 为 .env，填入你的 API 密钥。

## 使用方法

### Streamlit 界面
`ash
streamlit run src/ui/streamlit_app.py
`
浏览器打开 http://localhost:8501

### FastAPI 服务
`ash
python -m uvicorn src.api.routes:app --host 0.0.0.0 --port 8000
`

## 工具链

| 工具 | 功能 |
|------|------|
| web_search | 网络搜索 |
| calculator | 数学计算 |
| code_interpreter | 执行代码 |
| read_file | 读取文件 |
| write_file | 写入文件 |
| list_files | 列出目录 |
| web_scraper | 抓取网页 |
| call_api | API 调用 |
| image_gen | 图片生成 |

## API 文档

### 对话接口
`
POST /chat
POST /chat/stream (流式)
`
参数示例: message=hello, user_id=user_0001

### 用户接口
`
POST /users/create
GET /users/list
GET /users/{id}/conversations
`

## 许可证

MIT License
