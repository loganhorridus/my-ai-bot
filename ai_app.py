import os
import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. 基础配置 (记得把 Key 改成你自己的，或者用 st.secrets)
# ==========================================
# 强制代理 (你的 15236 端口)
os.environ["http_proxy"] = "http://127.0.0.1:15236"
os.environ["https_proxy"] = "http://127.0.0.1:15236"

# 读取 Key (这里假设你已经配好了 secrets.toml，如果没有，暂时把下面这行改成你的 'AIzaSy...')
# 直接填入你的 API Key (注意保留引号)
genai.configure(api_key="AIzaSyDb8Na3JA88ukXL86ztgcPpHF4uZrsB0ZQ")

st.set_page_config(page_title="超级 AI 助手 2.0", page_icon="📂", layout="wide")

# ==========================================
# 2. 侧边栏：控制台 & 文件上传
# ==========================================
with st.sidebar:
    st.title("🎛️ 投喂区")
    
    # 🌟 新功能：文件上传器
    uploaded_file = st.file_uploader("上传一个文本文件 (.txt/.md/.py)", type=["txt", "md", "py"])
    
    # 如果用户上传了文件，读取内容
    file_content = ""
    if uploaded_file is not None:
        # 读取文件内容并解码为中文
        try:
            file_content = uploaded_file.read().decode("utf-8")
            st.success(f"✅ 已读取文件: {uploaded_file.name}")
            with st.expander("查看文件内容预览"):
                st.text(file_content[:500] + "...") # 只显示前500字预览
        except Exception as e:
            st.error("文件读取失败，请确保是纯文本文件。")

    st.divider()
    
    # 角色选择
    role = st.selectbox("选择 AI 角色", ["小说续写助手", "代码审查员", "通用助手"])
    
    # 创造力调节
    temperature = st.slider("脑洞程度", 0.0, 2.0, 0.7)
    
    # 清空按钮
    if st.button("🗑️ 清空对话"):
        st.session_state.messages = []
        st.rerun()

# ==========================================
# 3. 聊天主逻辑
# ==========================================
st.title(f"📂 我的 AI 助手 - {role}")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 处理用户输入
if prompt := st.chat_input("请输入你的指令..."):
    
    # 🌟 关键修改：如果有文件，把文件内容“偷偷”塞给 AI
    final_prompt = prompt
    if file_content:
        # 这是一个“提示词工程”技巧：把资料包装好喂给 AI
        final_prompt = f"""
        【背景资料】：
        {file_content}
        
        【用户指令】：
        {prompt}
        """
    
    # 1. 显示用户的问题 (界面上只显示简洁的问题)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. 调用 AI
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # 实例化模型
            model = genai.GenerativeModel(
                'models/gemini-2.5-flash',
                # 系统指令：告诉 AI 它的身份
                system_instruction=f"你现在的身份是：{role}。请根据用户提供的背景资料（如果有）来回答问题。",
                generation_config=genai.types.GenerationConfig(temperature=temperature)
            )
            
            # 发送拼接后的 prompt (包含文件内容)
            response = model.generate_content(final_prompt, stream=True)
            
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"出错啦: {str(e)}")