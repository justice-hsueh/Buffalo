import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import base64
import json

st.set_page_config(page_title="大竹國小兒童樂隊行事曆", layout="wide")

DATA_FILE = "events.json"
CONFIG_FILE = "config.json"

# --- 資料存取 ---
def load_events():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return []
    return []

def save_events(events):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=4)

if 'events' not in st.session_state: st.session_state.events = load_events()

# --- 輔助函式 ---
def get_sort_date(date_str):
    try: return datetime.strptime(str(date_str).split("~")[0].strip(), "%Y-%m-%d").date()
    except: return date.max

def render_content_items(text):
    lines = text.split("\n")
    html = ""
    for line in lines:
        if line.strip():
            html += f'<div style="margin: 3px 0;">📌 {line}</div>'
    return html

# --- 1. 標題區 (使用 HTML 標籤內建樣式，避免 CSS 衝突) ---
logo_file = next((n for n in ["logo.jpg", "logo.JPG", "logo.png", "logo.PNG", "logo.jpeg"] if os.path.exists(n)), None)
if logo_file:
    with open(logo_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(f'<div style="display:flex; align-items:center; gap:15px; margin-bottom:20px;"><img src="data:image/jpeg;base64,{encoded}" style="width:60px;"><h1>大竹國小兒童樂隊行事曆</h1></div>', unsafe_allow_html=True)
else:
    st.title("🎵 大竹國小兒童樂隊行事曆")

# --- 2. 倒數計時區 ---
today = date.today()
upcoming_shows = [e for e in st.session_state.events if e["分類"] == "✨ 演出活動" and get_sort_date(e["日期"]) >= today]
if upcoming_shows:
    next_show = sorted(upcoming_shows, key=lambda x: get_sort_date(x["日期"]))[0]
    days = (get_sort_date(next_show["日期"]) - today).days
    st.info(f"⏳ 下一個演出：{next_show['內容'].splitlines()[0]}，還有 {days} 天！")

# --- 3. 側邊欄 ---
st.sidebar.markdown("## ⚙️ 管理員控制台")
if st.sidebar.text_input("🔑 請輸入密碼", type="password") == "dccb":
    mode = st.sidebar.radio("操作", ["新增", "刪除"])
    if mode == "新增":
        with st.sidebar.form("add"):
            cat = st.selectbox("分類", ["✨ 演出活動", "🥁 每日進度", "📢 通知事項"])
            f_date = str(st.date_input("日期"))
            time_in = st.text_input("時間")
            cont = st.text_area("內容")
            if st.form_submit_button("新增"):
                new_id = max([e["id"] for e in st.session_state.events] + [0]) + 1
                st.session_state.events.append({"id": new_id, "日期": f_date, "分類": cat, "時間": time_in, "內容": cont})
                save_events(st.session_state.events)
                st.rerun()
    elif mode == "刪除":
        selected = st.sidebar.selectbox("刪除行程", [f"{e['日期']} - {e['內容'][:10]}" for e in st.session_state.events])
        if st.sidebar.button("確認刪除"):
            st.session_state.events = [e for e in st.session_state.events if f"{e['日期']} - {e['內容'][:10]}" != selected]
            save_events(st.session_state.events)
            st.rerun()

# --- 4. 主畫面 (卡片樣式) ---
cols = st.columns(3)
categories = ["✨ 演出活動", "🥁 每日進度", "📢 通知事項"]
colors = {"✨ 演出活動": "#E0F2FE", "🥁 每日進度": "#E2F0D9", "📢 通知事項": "#FCE8E6"}

for i, cat in enumerate(categories):
    with cols[i]:
        st.subheader(cat)
        for ev in sorted([e for e in st.session_state.events if e["分類"] == cat], key=lambda x: get_sort_date(x["日期"])):
            st.markdown(f'''
                <div style="background-color:{colors[cat]}; padding:15px; border-radius:10px; margin-bottom:10px; border-left: 6px solid #888;">
                    <strong>{ev['日期']} | {ev['時間']}</strong><br>
                    {render_content_items(ev['內容'])}
                </div>
            ''', unsafe_allow_html=True)
