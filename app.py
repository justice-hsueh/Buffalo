import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import os
import base64
import json

st.set_page_config(page_title="大竹國小兒童樂隊行事曆", layout="wide")

DATA_FILE = "events.json"
CONFIG_FILE = "config.json"

# --- 密碼管理 ---
def load_admin_password():
    MY_PASSWORD = "dccb"
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("admin_password", MY_PASSWORD)
        except: pass
    return MY_PASSWORD

ADMIN_PASSWORD = load_admin_password()

# --- 資料存取 ---
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

# --- 輔助功能 ---
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
            html += f'<div style="margin-bottom: 2px; display: flex; align-items: flex-start; gap: 6px;"><span>{get_smart_icon(line)}</span><span>{line}</span></div>'
    return html

def get_sort_date(date_str):
    try: return datetime.strptime(str(date_str).split("~")[0].strip(), "%Y-%m-%d").date()
    except: return date.max

# --- 樣式設定 ---
st.markdown("""
    <style>
    /* 手機版響應式設定 */
    @media (max-width: 600px) {
        .rainbow-text { font-size: 26px !important; }
        .custom-title-logo { width: 50px !important; }
    }
    .event-card { padding: 12px 15px; border-radius: 8px; margin-bottom: 10px; font-size: 19px !important; }
    .show-style { background-color: #E0F2FE; border-left: 6px solid #0EA5E9; color: #0369A1; }
    .progress-style { background-color: #E2F0D9; border-left: 6px solid #70AD47; color: #385723; }
    .notice-style { background-color: #FCE8E6; border-left: 6px solid #EA4335; color: #A51D12; }
    hr { margin: 6px 0 !important; border: 0; border-top: 1px dashed #A0A0A0; }
    .title-text { font-size: 22px !important; font-weight: bold !important; margin-bottom: 4px; }
    .rainbow-text { font-size: 42px !important; font-weight: bold !important; 
        background: linear-gradient(to right, #E53E3E, #ED8936, #ECC94B, #48BB78, #3182CE, #000080, #9F7AEA);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .custom-title-container { display: flex; align-items: center; gap: 15px; margin-bottom: 20px; }
    .custom-title-logo { width: 80px; height: auto; }
    </style>
""", unsafe_allow_html=True)

if 'events' not in st.session_state: st.session_state.events = load_events()

# --- 標題與 Logo 渲染 ---
logo_file = next((n for n in ["logo.jpg", "logo.JPG", "logo.png", "logo.PNG", "logo.jpeg"] if os.path.exists(n)), None)
if logo_file:
    with open(logo_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(f'''<div class="custom-title-container"><img class="custom-title-logo" src="data:image/jpeg;base64,{encoded}"><span class="rainbow-text">大竹國小兒童樂隊行事曆</span></div>''', unsafe_allow_html=True)
else:
    st.markdown('<div class="rainbow-text">🎵 大竹國小兒童樂隊行事曆</div>', unsafe_allow_html=True)

# --- 簡潔版倒數計時 ---
today = date.today()
upcoming_shows = [e for e in st.session_state.events if e["分類"] == "✨ 演出活動" and get_sort_date(e["日期"]) >= today]

if upcoming_shows:
    next_show = sorted(upcoming_shows, key=lambda x: get_sort_date(x["日期"]))[0]
    days_left = (get_sort_date(next_show["日期"]) - today).days
    st.markdown(f'''
        <div style="background-color: #F8F9FA; padding: 10px; border-radius: 8px; border-left: 5px solid #48BB78; margin-bottom: 20px;">
            <div style="font-size: 18px; color: #2D3748;">
                ⏳ 下一個演出倒數：距離 <b>{next_show['內容'].splitlines()[0]}</b> 還有 <b style="color: #48BB78; font-size: 1.3em;">{days_left}</b> 天
            </div>
        </div>
    ''', unsafe_allow_html=True)
else:
    st.info("目前沒有即將到來的演出活動，繼續努力練習喔!")

# --- 側邊欄控制台 ---
st.sidebar.markdown("## ⚙️ 管理員控制台")
if st.sidebar.text_input("🔑 請輸入管理密碼：", type="password") == ADMIN_PASSWORD:
    st.sidebar.success("🔓 已解鎖編輯")
    mode = st.sidebar.radio("操作項目：", ["➕ 新增行程", "✏️ 修改行程", "🗑️ 刪除行程"])
    if mode == "➕ 新增行程":
        with st.sidebar.form("add_form", clear_on_submit=True):
            cat = st.selectbox("分類", ["✨ 演出活動", "🥁 每日進度", "📢 通知事項"])
            f_date = str(st.date_input("選擇日期"))
            time_in = st.text_input("時間")
            loc = st.text_input("地點 (僅演出用)") if cat == "✨ 演出活動" else ""
            cont = st.text_area("內容 (第一行為標題)")
            if st.form_submit_button("新增"):
                new_id = max([e["id"] for e in st.session_state.events] + [0]) + 1
                data = {"id": new_id, "日期": f_date, "分類": cat, "時間": time_in, "內容": cont}
                if cat == "✨ 演出活動": data["地點"] = loc
                st.session_state.events.append(data)
                save_events(st.session_state.events)
                st.rerun()
    elif mode == "✏️ 修改行程":
        event_list = {f"{e['分類']} - {e['內容'][:10]} ({e['日期']})": e for e in st.session_state.events}
        selected = st.sidebar.selectbox("選擇要修改的行程", list(event_list.keys()))
        ev = event_list[selected]
        with st.sidebar.form("edit_form"):
            new_cont = st.text_area("修改內容", ev["內容"])
            if st.form_submit_button("儲存修改"):
                ev["內容"] = new_cont
                save_events(st.session_state.events)
                st.rerun()
    elif mode == "🗑️ 刪除行程":
        event_list = {f"{e['分類']} - {e['內容'][:10]} ({e['日期']})": e for e in st.session_state.events}
        selected = st.sidebar.selectbox("選擇要刪除的行程", list(event_list.keys()))
        if st.sidebar.button("確認刪除"):
            st.session_state.events = [e for e in st.session_state.events if e["id"] != event_list[selected]["id"]]
            save_events(st.session_state.events)
            st.rerun()

# --- 主畫面 ---
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("<h2>✨ 演出活動</h2>", unsafe_allow_html=True)
    for ev in sorted([e for e in st.session_state.events if e["分類"] == "✨ 演出活動"], key=lambda x: get_sort_date(x["日期"])):
        lines = ev["內容"].split("\n")
        st.markdown(f'''<div class="event-card show-style"><div class="title-text">🎵 {lines[0]}</div>📅 {ev["日期"]} | ⏰ {ev["時間"]}<br>🏠 {ev.get("地點", "未定")}<hr>{render_content_items(lines[1:])}</div>''', unsafe_allow_html=True)
with col2:
    st.markdown("<h2>🥁 每日進度</h2>", unsafe_allow_html=True)
    for ev in sorted([e for e in st.session_state.events if e["分類"] == "🥁 每日進度"], key=lambda x: get_sort_date(x["日期"])):
        st.markdown(f'''<div class="event-card progress-style"><strong>📅 {ev["日期"]}</strong><hr>{render_content_items(ev["內容"].split("\n"))}</div>''', unsafe_allow_html=True)
with col3:
    st.markdown("<h2>📢 通知事項</h2>", unsafe_allow_html=True)
    for ev in sorted([e for e in st.session_state.events if e["分類"] == "📢 通知事項"], key=lambda x: get_sort_date(x["日期"])):
        lines = ev["內容"].split("\n")
        st.markdown(f'''<div class="event-card notice-style"><div class="title-text">📢 {lines[0]}</div>📅 {ev["日期"]}<hr>{render_content_items(lines[1:])}</div>''', unsafe_allow_html=True)
