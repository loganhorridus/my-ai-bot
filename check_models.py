import os
import google.generativeai as genai

# 1. 配置代理 (沿用你成功的 15236 端口)
os.environ["http_proxy"] = "http://127.0.0.1:15236"
os.environ["https_proxy"] = "http://127.0.0.1:15236"

# 2. 配置 Key (请替换为你自己的 Key !!!)
genai.configure(api_key="AIzaSyAk_Hfc7OivRatOiI9letwrLy1f6_9GYWs")

print("🔍 正在连接 Google 服务器查询可用模型...")

try:
    # 列出所有可用模型
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ 发现可用模型: {m.name}")
            available_models.append(m.name)
            
    if not available_models:
        print("❌ 连接成功，但没有发现可用模型。可能是 API Key 权限问题。")
    else:
        print(f"\n🎉 成功！请复制上面任意一个模型名字（例如 {available_models[0].replace('models/', '')}）到你的 ai_app.py 中使用！")
        
except Exception as e:
    print(f"❌ 查询失败，错误详情:\n{e}")