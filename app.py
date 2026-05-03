import streamlit as st
from huggingface_hub import InferenceClient

st.set_page_config(page_title="Qwen2.5 API Chatbot", layout="centered")
st.title("🤖 Qwen2.5 Chatbot (via HF Hub)")

# รับ Token จาก Sidebar
HF_TOKEN = st.sidebar.text_input("ใส่ Hugging Face Token", type="password")

# กำหนดชื่อโมเดล (แนะนำ 72B-Instruct หรือ 7B-Instruct เพราะ HF มักจะเปิดให้ใช้ฟรี)
MODEL_ID = "Qwen/Qwen2.5-72B-Instruct" 

if "messages" not in st.session_state:
    st.session_state.messages = []

# แสดงประวัติการสนทนา
for message in st.session_state.messages:
    # ข้าม system prompt ไม่ต้องแสดงบนหน้าจอ
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("พิมพ์ข้อความที่นี่..."):
    if not HF_TOKEN:
        st.error("กรุณาใส่ Hugging Face Token ที่แถบด้านซ้ายก่อนครับ")
    else:
        # เก็บข้อความผู้ใช้
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("กำลังคิด..."):
                try:
                    # เรียกใช้ InferenceClient แทน requests
                    client = InferenceClient(model=MODEL_ID, token=HF_TOKEN.strip())
                    
                    # เตรียมข้อมูลสนทนา (ใส่ System Prompt ไว้เป็นบริบท)
                    chat_history = [{"role": "system", "content": "You are a helpful assistant."}]
                    # นำประวัติใน session มาต่อท้าย (กรองเอาเฉพาะ role ที่ถูกต้อง)
                    chat_history.extend([msg for msg in st.session_state.messages if msg["role"] in ["user", "assistant"]])
                    
                    # เรียกใช้งาน Chat API
                    response = client.chat_completion(
                        messages=chat_history,
                        max_tokens=512
                    )
                    
                    # ดึงข้อความตอบกลับ
                    output_text = response.choices[0].message.content
                    
                    st.markdown(output_text)
                    st.session_state.messages.append({"role": "assistant", "content": output_text})
                    
                except Exception as e:
                    st.error(f"❌ เกิดข้อผิดพลาดจาก API: {str(e)}")
                    # ลบข้อความ user ล่าสุดออกถ้า API พัง จะได้พิมพ์ใหม่ได้
                    st.session_state.messages.pop()
