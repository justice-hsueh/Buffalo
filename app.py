import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import os
import base64
import json

st.set_page_config(page_title="大竹國小兒童樂隊行事曆", layout="wide")

DATA_FILE = "events.json"
CONFIG_FILE = "config.json"
QUESTION_FILE = "questions.json" # 新增問題牆檔案

# --- 讀寫資料函式 ---
def load_json(file, default=[]):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return default

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 初始化 ---
if 'events' not in st.session_state: st.session_state.events = load_json(DATA_FILE)
if 'questions' not in st.session_state: st.session_state.questions = load_json(QUESTION_FILE)

# --- 側邊欄與其他邏輯維持原樣 (包含密碼驗證) ---
# (為了縮短版面，這裡省略重複的密碼驗證邏輯，請沿用您原本的側邊欄設定)

# --- 問題牆功能 ---
st.sidebar.markdown("---")
st.sidebar.markdown("## 💬 師生互動問題牆")
with st.sidebar.expander("📝 發表新提問"):
    user_name = st.text_input("您的稱呼")
    question_text = st.text_area("想問老師什麼呢？")
    if st.button("送出提問"):
        if user_name and question_text:
            new_q = {"id": len(st.session_state.questions)+1, "name": user_name, "text": question_text, "reply": ""}
            st.session_state.questions.append(new_q)
            save_json(QUESTION_FILE, st.session_state.questions)
            st.rerun()

# --- 在主頁面展示問題牆 (建議放在 col1~col3 下方) ---
st.markdown("---")
st.markdown("## 💭 常見問題與師生互動牆")
for q in reversed(st.session_state.questions):
    with st.expander(f"{q['name']}：{q['text'][:20]}..."):
        st.write(f"**提問內容：** {q['text']}")
        if q['reply']:
            st.success(f"🎵 老師回覆：{q['reply']}")
        
        # 簡易管理員回覆邏輯
        if st.text_input(f"回覆此提問 (ID:{q['id']})", key=f"r_{q['id']}"):
            if st.button("發送回覆", key=f"b_{q['id']}"):
                q['reply'] = st.session_state[f"r_{q['id']}"]
                save_json(QUESTION_FILE, st.session_state.questions)
                st.rerun()

# --- 主畫面其餘排版維持原樣 ---
