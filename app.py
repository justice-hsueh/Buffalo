import streamlit as st
import pandas as pd
import os
import base64
import json

st.set_page_config(page_title="大竹國小兒童樂隊行事曆", layout="wide")

DATA_FILE = "events.json"
CONFIG_FILE = "config.json"
QUESTION_FILE = "questions.json"

# --- 資料讀寫 ---
def load_json(file, default=[]):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return default

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if 'events' not in st.session_state: st.session_state.events = load_json(DATA_FILE)
if 'questions' not in st.session_state: st.session_state.questions = load_json(QUESTION_FILE)

# --- 側邊欄 (管理員) ---
st.sidebar.markdown("## ⚙️ 管理員控制台")
if st.sidebar.text_input("🔑 輸入密碼", type="password") == "dccb":
    mode = st.sidebar.radio("操作", ["➕ 新增", "🗑️ 刪除/回覆"])
    # (此處省略新增/刪除邏輯，維持原樣即可)

# --- 標題 ---
st.markdown('<div class="rainbow-text">🎵 大竹國小兒童樂隊行事曆</div>', unsafe_allow_html=True)
st.markdown("---")

# --- 公告欄位與提問整合 (核心修改處) ---
def render_event_with_questions(event):
    # 顯示公告內容
    st.markdown(f'<div class="event-card">{event["內容"]}</div>', unsafe_allow_html=True)
    
    # 該公告專屬的提問區
    with st.expander(f"💬 針對此項目提問"):
        q_list = [q for q in st.session_state.questions if q.get("target_id") == event["id"]]
        for q in q_list:
            st.write(f"**{q['name']}**: {q['text']}")
            if q['reply']: st.success(f"老師回覆: {q['reply']}")
        
        # 發表新提問
        u = st.text_input(f"您的稱呼", key=f"n_{event['id']}")
        t = st.text_area(f"提問內容", key=f"q_{event['id']}")
        if st.button("送出", key=f"b_{event['id']}"):
            st.session_state.questions.append({"target_id": event["id"], "name": u, "text": t, "reply": ""})
            save_json(QUESTION_FILE, st.session_state.questions)
            st.rerun()

# 顯示三欄
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("✨ 演出活動")
    for ev in [e for e in st.session_state.events if e["分類"] == "✨ 演出活動"]:
        render_event_with_questions(ev)

# (col2, col3 依此類推使用 render_event_with_questions 函式)
