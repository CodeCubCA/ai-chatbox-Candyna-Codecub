import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 页面配置
st.set_page_config(
    page_title="音乐顾问 AI",
    page_icon="🎵",
    layout="centered"
)

# 初始化 Groq 客户端
def init_groq_client():
    """初始化 Groq API 客户端"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("❌ 请在 .env 文件中设置 GROQ_API_KEY")
        st.stop()
    return Groq(api_key=api_key)

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []
    # 添加系统提示词，定义 AI 助手的角色
    st.session_state.messages.append({
        "role": "system",
        "content": "你是一位专业的音乐顾问。你对各种音乐类型、艺术家、专辑和音乐历史有深入的了解。你可以根据用户的心情、场景或偏好推荐音乐，分享音乐知识，并提供个性化的音乐建议。请用友好、热情的语气与用户交流。"
    })

# 创建 Groq 客户端
client = init_groq_client()

# 页面标题和描述
st.title("🎵 音乐顾问 AI")
st.markdown("**你的私人音乐推荐助手** - 告诉我你的心情、场景或喜好，我会为你推荐最适合的音乐！")

# 添加侧边栏
with st.sidebar:
    st.header("ℹ️ 关于")
    st.markdown("""
    这是一个基于 AI 的音乐顾问助手，可以帮助你：
    - 🎧 根据心情推荐音乐
    - 🎼 发现新的艺术家和专辑
    - 📚 了解音乐历史和知识
    - 🎹 获取个性化音乐建议
    """)

    st.header("🎯 使用提示")
    st.markdown("""
    试试这些问题：
    - "推荐一些适合工作时听的音乐"
    - "我心情不好，有什么歌可以听？"
    - "介绍一下爵士乐的历史"
    - "有哪些经典的摇滚专辑？"
    """)

    # 清空对话按钮
    if st.button("🗑️ 清空对话历史"):
        # 保留系统提示词
        system_message = st.session_state.messages[0]
        st.session_state.messages = [system_message]
        st.rerun()

# 显示聊天历史（不显示系统提示词）
for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 用户输入
if prompt := st.chat_input("输入你的问题..."):
    # 添加用户消息到历史记录
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)

    # 显示助手响应
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # 调用 Groq API（流式响应）
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages,
                temperature=0.7,
                max_tokens=2048,
                stream=True
            )

            # 逐字显示响应
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")

            # 显示完整响应
            message_placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"❌ 发生错误: {str(e)}")
            full_response = "抱歉，我遇到了一些问题。请稍后再试。"
            message_placeholder.markdown(full_response)

    # 添加助手响应到历史记录
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# 页脚
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "由 Groq API 和 Streamlit 驱动 | 模型: llama-3.3-70b-versatile"
    "</div>",
    unsafe_allow_html=True
)
