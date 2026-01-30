import os
import streamlit as st
import google.generativeai as genai

# 1. 强制代理配置（针对你的 15236 端口）
# 这样你以后直接在 VS Code 点运行，不再需要手动 export 变量
os.environ["http_proxy"] = "http://127.0.0.1:15236"
os.environ["https_proxy"] = "http://127.0.0.1:15236"

# 2. 配置 Gemini API Key
# 建议将 'YOUR_API_KEY' 替换为你真实的 Key
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# 3. Streamlit 页面设置
st.set_page_config(page_title="Gemini 助手", page_icon="🤖")
st.title("🐱 我的 AI 伙伴 (Git版!)")
st.caption("基于 Google Gemini 2.5 Flash")

# 4. 初始化聊天历史（Streamlit 会话状态）
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. 展示之前的对话历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. 聊天输入框
if prompt := st.chat_input("请输入你的问题..."):
    # 用户显示自己的问题
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 7. 调用 Gemini 接口
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # 初始化模型 (注意：这里必须和 try 保持一级缩进)
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            
            # 流式传输回答 (和 model 这一行完全左对齐)
            response = model.generate_content(prompt, stream=True)
            
            # 处理流式响应 (和 model 这一行完全左对齐)
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            
            # 显示完整回答 (和 model 这一行完全左对齐)
            message_placeholder.markdown(full_response)
            
            # 保存 AI 的回答 (和 model 这一行完全左对齐)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            # 错误处理 (和 try 保持一级缩进)
            error_msg = f"连接失败，请检查代理。错误详情: {str(e)}"
            st.error(error_msg)
            # 如果报错，提供诊断建议
            if "403" in str(e):
                st.info("💡 提示：可能是 API Key 无效或所在地区被封锁。")
            elif "404" in str(e):
                st.info("💡 提示：找不到模型，请检查代码里的模型名称是否正确。")