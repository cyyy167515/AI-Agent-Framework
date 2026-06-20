"""Streamlit Web 界面 - 支持用户系统"""
import sys
import os

# 确保项目根目录在 Python 路径中
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import streamlit as st
from src.agents.react_agent import ReactAgent
from src.graph.workflow import run_workflow
from src.user.user_manager import UserManager
from src.user.conversation_store import ConversationStore

# 页面配置
st.set_page_config(
    page_title="AI Agent Framework",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 AI Agent Framework")

# 初始化用户管理器
if "user_manager" not in st.session_state:
    st.session_state.user_manager = UserManager()

def login_page():
    """用户登录界面"""
    st.subheader("👤 用户登录")

    users = st.session_state.user_manager.list_users()
    user_names = ["新用户"] + [u.username for u in users]

    choice = st.selectbox("选择用户", user_names, key="login_select")

    if choice == "新用户":
        username = st.text_input("请输入新用户名", key="new_username_input")
        if st.button("创建并登录", key="btn_create_login", type="primary"):
            if username.strip():
                user = st.session_state.user_manager.get_or_create_user(username.strip())
                init_user_session(user)
                st.rerun()
            else:
                st.warning("请输入用户名")
    else:
        if st.button("登录", key="btn_login", type="primary"):
            user = st.session_state.user_manager.get_or_create_user(choice)
            init_user_session(user)
            st.rerun()

def init_user_session(user):
    """初始化用户会话数据"""
    st.session_state.current_user = user
    st.session_state.user_id = user.user_id
    st.session_state.conversation_store = ConversationStore(user.user_id)
    st.session_state.agent = ReactAgent()
    # 加载历史对话
    history = st.session_state.conversation_store.get_history()
    st.session_state.history = [{"role": m["role"], "content": m["content"]} for m in history]

# 检查登录状态
if "current_user" not in st.session_state:
    login_page()
    st.stop()

# === 侧边栏 ===
with st.sidebar:
    st.subheader("👤 用户信息")
    st.write(f"**用户名**: {st.session_state.current_user.username}")
    st.write(f"**用户 ID**: {st.session_state.user_id}")
    st.divider()

    st.subheader(" 对话管理")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("清空对话", use_container_width=True, key="btn_clear"):
            st.session_state.conversation_store.clear()
            st.session_state.history = []
            st.rerun()
    with col2:
        if st.button("导出对话", use_container_width=True, key="btn_export"):
            text = st.session_state.conversation_store.export_text()
            st.download_button(
                label="下载",
                data=text,
                file_name=f"chat_{st.session_state.current_user.username}.txt",
                mime="text/plain",
                key="btn_download"
            )
    st.divider()

    if st.button("切换用户", use_container_width=True, key="btn_switch_user"):
        keys_to_delete = ["current_user", "user_id", "conversation_store", "agent", "history"]
        for k in keys_to_delete:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

    st.divider()
    count = st.session_state.conversation_store.count()
    st.metric("消息数", count)

# === 主内容区 ===
tab1, tab2 = st.tabs(["💬 ReAct 对话", " 多智能体工作流"])

# 1. ReAct 对话选项卡
with tab1:
    st.header("ReAct 智能体")

    # 显示聊天历史
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("thinking"):
                with st.expander("💡 思考过程"):
                    st.text(msg["thinking"])

    # 输入框
    user_input = st.chat_input("请输入你的问题...", key="chat_input")

    if user_input:
        # 保存到持久化存储
        st.session_state.conversation_store.add_message("user", user_input)
        st.session_state.history.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        # 流式输出
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                response_stream = st.session_state.agent.think_stream(user_input)
                response_content = st.write_stream(response_stream)

        # 保存到持久化存储和历史
        st.session_state.conversation_store.add_message("assistant", response_content)
        st.session_state.history.append({
            "role": "assistant",
            "content": response_content,
            "thinking": None
        })

# 2. 多智能体工作流选项卡
with tab2:
    st.header("多智能体协作 (Planner → Worker → Reviewer)")

    task = st.text_area("请输入任务描述", height=100, placeholder="例如：帮我写一篇关于人工智能的报告...", key="workflow_input")

    col1, col2 = st.columns([3, 1])
    with col2:
        iterations = st.number_input("最大迭代次数", min_value=1, max_value=5, value=3, key="wf_iterations")
    with col1:
        run_btn = st.button("🚀 执行工作流", type="primary", key="btn_run_wf")

    if run_btn and task:
        with st.spinner("工作流运行中..."):
            try:
                result = run_workflow(task, max_iterations=iterations)

                st.success("工作流完成")

                # 保存到对话历史
                st.session_state.conversation_store.add_message("user", f"[工作流] {task}")
                st.session_state.conversation_store.add_message("assistant", result["final_answer"])

                st.subheader("最终答案")
                st.markdown(result["final_answer"])

                review = result.get("review_result", {})
                st.subheader("审查结果")
                st.metric("评分", f"{review.get('score', 0)} / 10")
                st.info(review.get("feedback", "无反馈"))

                st.subheader("任务分解")
                subtasks = result.get("subtasks", [])
                for sub in subtasks:
                    st.write(f"- **{sub.get('id')}**: {sub.get('description')}")

            except Exception as e:
                st.error(f"执行失败: {str(e)}")
    elif run_btn:
        st.warning("请输入任务描述")