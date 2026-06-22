import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import os
import base64
import json

st.set_page_config(page_title="大竹國小兒童樂隊行事曆", layout="wide")

DATA_FILE = "events.json"
CONFIG_FILE = "config.json"
QUESTION_FILE = "questions.json"

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

if 'events' not in st.session_state: st.session_state.events = load_json(DATA_FILE)
if 'questions' not in st.session_state: st.session_state.questions = load_json(QUESTION_FILE)

# --- 樣式設定 ---
st.markdown("""
    <style>
    .event-card { padding: 12px 15px; border-radius: 8px; margin-bottom: 10px; font-size: 19px !important; }
    .show-style { background-color: #E0F2FE; border-left: 6px solid #0EA5E9; color: #0369A1; }
    .progress-style { background-color: #E2F0D9; border-left: 6px solid #70AD47; color: #385723; }
    .notice-style { background-color: #FCE8E6; border-left: 6px solid #EA4335; color: #A51D12; }
    .title-text { font-size: 22px !important; font-weight: bold !important; margin-bottom: 4px; }
    .rainbow-text { font-size: 42px !important; font-weight: bold !important; 
        background: linear-gradient(to right, #E53E3E, #ED8936, #ECC94B, #48BB78, #3182CE, #000080, #9F7AEA);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
""", unsafe_allow_html=True)

# --- 標題與 Logo ---
logo_file = next((n for n in ["logo.jpg", "logo.png", "logo.jpeg"] if os.path.exists(n)), None)
if logo_file:
    with open(logo_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(f'<div style="display: flex; align-items: center; gap: 15px;"><img src="data:image/jpeg;base64,{encoded}" width="80"><span class="rainbow-text">大竹國小兒童樂隊行事曆</span></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="rainbow-text">🎵 大竹國小兒童樂隊行事曆</div>', unsafe_allow_html=True)
st.markdown("---")

# --- 主畫面：行事曆顯示 ---
col1, col2, col3 = st.columns(3)

def render_content_items(lines):
    html = ""
    for line in lines:
        if line.strip(): html += f'<div>📌 {line}</div>'
    return html

with col1:
    st.markdown("## ✨ 演出活動")
    for ev in [e for e in st.session_state.events if e["分類"] == "✨ 演出活動"]:
        lines = ev["內容"].split("\n")
        st.markdown(f'<div class="event-card show-style"><div class="title-text">🎵 {lines[0]}</div>📅 {ev["日期"]}<hr>{render_content_items(lines[1:])}</div>', unsafe_allow_html=True)

with col2:
    st.markdown("## 🥁 每日進度")
    for ev in [e for e in st.session_state.events if e["分類"] == "🥁 每日進度"]:
        st.markdown(f'<div class="event-card progress-style"><strong>📅 {ev["日期"]}</strong><hr>{render_content_items(ev["內容"].split("\n"))}</div>', unsafe_allow_html=True)

with col3:
    st.markdown("## 📢 通知事項")
    for ev in [e for e in st.session_state.events if e["分類"] == "📢 通知事項"]:
        lines = ev["內容"].split("\n")
        st.markdown(f'<div class="event-card notice-style"><div class="title-text">📢 {lines[0]}</div>📅 {ev["日期"]}<hr>{render_content_items(lines[1:])}</div>', unsafe_allow_html=True)

# --- 下方：問題牆 ---
st.markdown("---")
st.markdown("## 💭 師生互動問題牆")
with st.expander("📝 點此發表新提問"):
    user_name = st.text_input("您的稱呼")
    q_text = st.text_area("想問老師什麼呢？")
    if st.button("送出提問"):
        st.session_state.questions.append({"name": user_name, "text": q_text, "reply": ""})
        save_json(QUESTION_FILE, st.session_state.questions)
        st.rerun()

for q in reversed(st.session_state.questions):
    st.markdown(f"**{q['name']}**: {q['text']}")
    if q['reply']: st.success(f"🎵 老師回覆：{q['reply']}")
    st.markdown("---")
    
