"""FastAPI ????
?? HTTP API ??????????????
"""

import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn

from config.logging_config import get_logger
logger = get_logger("api")

from src.agents.react_agent import ReactAgent
from src.graph.workflow import run_workflow
from src.user.user_manager import UserManager
from src.user.conversation_store import ConversationStore

# ?????
user_manager = UserManager()

# ??????????
agents_cache = {}

# ?? FastAPI ??
app = FastAPI(
    title="AI-Agent-Framework API",
    description="???????? HTTP ?????????",
    version="1.0.1",
)


class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    use_memory: bool = True


class WorkflowRequest(BaseModel):
    task: str
    user_id: Optional[str] = None
    max_iterations: int = 3


class ChatResponse(BaseModel):
    reply: str
    thinking: Optional[str] = None
    action_used: Optional[str] = None
    user_id: Optional[str] = None


class WorkflowResponse(BaseModel):
    final_answer: str
    subtasks_count: int
    iteration: int
    approved: bool
    review_feedback: Optional[str] = None


class UserResponse(BaseModel):
    user_id: str
    username: str
    created_at: str
    message_count: int


class CreateUserRequest(BaseModel):
    username: str


@app.get("/")
async def root():
    return {"message": "AI-Agent-Framework API", "version": "1.0.1", "features": ["user_system", "conversation_persistence"]}


@app.post("/users/create", response_model=UserResponse)
async def create_user(request: CreateUserRequest):
    """????"""
    user = user_manager.get_or_create_user(request.username)
    store = ConversationStore(user.user_id)
    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        created_at=user.created_at,
        message_count=store.count(),
    )


@app.get("/users/list")
async def list_users():
    """??????"""
    users = user_manager.list_users()
    return [{"user_id": u.user_id, "username": u.username} for u in users]


@app.get("/users/{user_id}/conversations")
async def get_conversations(user_id: str):
    """????????"""
    user = user_manager.get_user(user_id)
    if not user:
        raise HTTPException(404, "?????")
    store = ConversationStore(user_id)
    return store.get_history()


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """????"""
    logger.info(f"[api] /chat user={request.user_id} msg={request.message[:30]}...")
    
    # ????????
    if request.user_id:
        if request.user_id not in agents_cache:
            agents_cache[request.user_id] = ReactAgent()
        agent = agents_cache[request.user_id]
        store = ConversationStore(request.user_id)
        store.add_message("user", request.message)
    else:
        agent = ReactAgent()
    
    try:
        response = agent.think(request.message)
        if request.user_id:
            store = ConversationStore(request.user_id)
            store.add_message("assistant", response.content)
        return ChatResponse(
            reply=response.content,
            thinking=response.thinking,
            action_used=response.action,
            user_id=request.user_id,
        )
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/workflow", response_model=WorkflowResponse)
async def workflow(request: WorkflowRequest):
    """?????"""
    try:
        result = run_workflow(request.task, request.max_iterations)
        if request.user_id:
            store = ConversationStore(request.user_id)
            store.add_message("user", f"[???] {request.task}")
            store.add_message("assistant", result.get("final_answer", ""))
        return WorkflowResponse(
            final_answer=result.get("final_answer", ""),
            subtasks_count=len(result.get("subtasks", [])),
            iteration=result.get("iteration", 0),
            approved=result.get("review_result", {}).get("approved", False),
            review_feedback=result.get("review_result", {}).get("feedback"),
        )
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """??????"""
    if request.user_id:
        if request.user_id not in agents_cache:
            agents_cache[request.user_id] = ReactAgent()
        agent = agents_cache[request.user_id]
        store = ConversationStore(request.user_id)
        store.add_message("user", request.message)
    else:
        agent = ReactAgent()
    
    async def generate():
        full_response = ""
        for chunk in agent.think_stream(request.message):
            full_response += chunk
            data = {"content": chunk}
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        if request.user_id:
            store = ConversationStore(request.user_id)
            store.add_message("assistant", full_response)
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


def start_server(host: str = "0.0.0.0", port: int = 8000):
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
