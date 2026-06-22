import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import os
import base64
import json

# 設定網頁標題與整體風格
st.set_page_config(page_title="大竹國小兒童樂隊行事曆", layout="wide")

DATA_FILE = "events.json"
CONFIG_FILE = "config.json"

# --- 密碼管理 ---
def load_admin_password():
    MY_PASSWORD = "dccb" 
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("admin_password", MY_PASSWORD)
        except: pass
    return MY_PASSWORD

def save_admin_password(new_password):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"admin_password": new_password}, f, ensure_ascii=False, indent=4)

ADMIN_PASSWORD = load_admin_password()

def load_events():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return []

def save_events(events):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=4)

# 輔助函式
def get_smart_icon(text):
    text_lower = text.lower()
    if any(k in text_lower for k in ["譜", "歌", "樂譜", "演奏"]): return "🎼"
    if any(k in text_lower for k in ["帶", "拿", "備", "準備", "攜帶"]): return "🎒"
    if any(k in text_lower for k in ["注意", "務必", "記得", "重要", "切記"]): return "⚠️"
    if any(k in text_lower for k in ["服", "穿", "衣", "團服"]): return "👕"
    return "📌"

def render_content_items(lines_list):
    html = ""
    for line in lines_list:
        if line.strip():
            html += f'<div style="margin-bottom: 6px; display: flex; align-items: flex-start; gap: 8px;"><span>{get_smart_icon(line)}</span><span>{line}</span></div>'
    return html

def get_sort_date(date_str):
    try: return datetime.strptime(str(date_str).split("~")[0].strip(), "%Y-%m-%d").date()
    except: return date.max

# CSS
st.markdown("""
    <style>
    .event-card { padding: 15px 20px; border-radius: 8px; margin-bottom: 12px; font-size: 20px !important; }
    .show-style { background-color: #E0F2FE; border-left: 6px solid #0EA5E9; color: #0369A1; }
    .progress-style { background-color: #E2F0D9; border-left: 6px solid #70AD47; color: #385723; }
    .notice-style { background-color: #FCE8E6; border-left: 6px solid #EA4335; color: #A51D12; }
    .title-text { font-size: 24px !important; font-weight: bold !important; margin-bottom: 8px; }
    </style>
""", unsafe_allow_html=True)

# 狀態初始化
if 'events' not in st.session_state: st.session_state.events = load_events()

# --- 側邊欄管理 (強制顯示) ---
st.sidebar.markdown("## ⚙️ 管理員控制台")
password_input = st.sidebar.text_input("🔑 請輸入管理密碼：", type="password")

if password_input == ADMIN_PASSWORD:
    st.sidebar.success("🔓 已解鎖編輯")
    mode = st.sidebar.radio("操作項目：", ["➕ 新增行程", "✏️ 修改行程", "🗑️ 刪除行程"])
    
    # 新增 (包含日期範圍選取)
    if mode == "➕ 新增行程":
        with st.sidebar.form("add_form", clear_on_submit=True):
            date_mode = st.selectbox("日期模式", ["單日", "日期範圍"])
            if date_mode == "單日":
                chosen = st.date_input("選擇日期")
                f_date = str(chosen)
            else:
                rng = st.date_input("選擇範圍", value=[date.today(), date.today()])
                f_date = f"{rng[0]} ~ {rng[1]}" if len(rng)==2 else str(rng[0])
            
            cat = st.selectbox("分類", ["✨ 演出活動", "🥁 每日進度", "📢 通知事項"])
            time_in = st.text_input("時間 (每日進度可留空)")
            loc = st.text_input("地點 (僅限演出)") if cat == "✨ 演出活動" else ""
            cont = st.text_area("內容 (第一行為標題)")
            
            if st.form_submit_button("儲存"):
                new_id = max([e["id"] for e in st.session_state.events] + [0]) + 1
                data = {"id": new_id, "日期": f_date, "分類": cat, "時間": time_in, "內容": cont}
                if cat == "✨ 演出活動": data["地點"] = loc
                st.session_state.events.append(data)
                save_events(st.session_state.events)
                st.rerun()

# --- 主畫面 ---
col1, col2, col3 = st.columns(3)

# 1. 演出
with col1:
    st.markdown("<h2>✨ 演出活動</h2>", unsafe_allow_html=True)
    for ev in sorted([e for e in st.session_state.events if e["分類"] == "✨ 演出活動"], key=lambda x: get_sort_date(x["日期"])):
        lines = ev["內容"].split("\n")
        st.markdown(f"""<div class="event-card show-style">
            <div class="title-text">🎵 {lines[0]}</div>
            📅 {ev["日期"]} | ⏰ {ev["時間"]}<br>🏠 {ev.get("地點", "未定")}
            <hr>{render_content_items(lines[1:])}</div>""", unsafe_allow_html=True)

# 2. 每日進度 (只顯示日期)
with col2:
    st.markdown("<h2>🥁 每日進度</h2>", unsafe_allow_html=True)
    for ev in sorted([e for e in st.session_state.events if e["分類"] == "🥁 每日進度"], key=lambda x: get_sort_date(x["日期"])):
        st.markdown(f"""<div class="event-card progress-style">
            <strong>📅 {ev["日期"]}</strong>
            <hr>{render_content_items(ev["內容"].split("\n"))}</div>""", unsafe_allow_html=True)

# 3. 通知
with col3:
    st.markdown("<h2>📢 通知事項</h2>", unsafe_allow_html=True)
    for ev in sorted([e for e in st.session_state.events if e["分類"] == "📢 通知事項"], key=lambda x: get_sort_date(x["日期"])):
        lines = ev["內容"].split("\n")
        st.markdown(f"""<div class="event-card notice-style">
            <div class="title-text">📢 {lines[0]}</div>
            📅 {ev["日期"]}
            <hr>{render_content_items(lines[1:])}</div>""", unsafe_allow_html=True)
