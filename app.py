import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import os
import base64
import json

# 設定網頁標題與整體風格
st.set_page_config(page_title="大竹國小兒童樂隊行事曆", layout="wide")

# 設定資料儲存的檔案路徑
DATA_FILE = "events.json"
CONFIG_FILE = "config.json"

# --- 密碼與設定檔管理機制 ---
def load_admin_password():
    MY_PASSWORD = "dccb" 
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                file_pwd = config.get("admin_password", MY_PASSWORD)
                if file_pwd == "dzor" and MY_PASSWORD != "dzor":
                    return MY_PASSWORD
                return file_pwd
        except:
            pass
    default_config = {"admin_password": MY_PASSWORD}
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)
    except:
        pass
    return MY_PASSWORD

def save_admin_password(new_password):
    config = {"admin_password": new_password}
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

# 載入當前鎖定的密碼
ADMIN_PASSWORD = load_admin_password()

# 讀取行程檔案資料的函式
def load_events():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return [
        {"id": 1, "日期": "2026-06-25", "分類": "✨ 演出活動", "時間": "13:30 - 15:30", "地點": "學校活動中心", "內容": "年度期末發表會\n注意：各分部樂譜需收齊\n請記得攜帶個人講義"},
        {"id": 2, "日期": "2026-06-26", "分類": "🥁 每日進度", "時間": "全天", "內容": "打擊與鍵盤分部練習基本功\n加強弱奏節段的穩定度"},
        {"id": 3, "日期": "2026-06-29 ~ 2026-07-03", "分類": "📢 通知事項", "時間": "全天", "內容": "暑假自主複習週\n放學請大家把樂器和講義帶回家練習\n注意開學後的團練時間"},
    ]

# 儲存資料到檔案的函式
def save_events(events):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=4)

# 關鍵輔助函式：根據文字內容自動分配最適合的圖示
def get_smart_icon(text):
    text_lower = text.lower()
    if any(keyword in text_lower for keyword in ["譜", "歌", "樂譜", "演奏"]):
        return "🎼"
    elif any(keyword in text_lower for keyword in ["帶", "拿", "備", "準備", "攜帶"]):
        return "🎒"
    elif any(keyword in text_lower for keyword in ["注意", "務必", "記得", "重要", "切記"]):
        return "⚠️"
    elif any(keyword in text_lower for keyword in ["服", "穿", "衣", "團服"]):
        return "👕"
    else:
        return "📌"

# 關鍵輔助函式：將純文字清單渲染成精美的多項目 HTML 清單
def render_content_items(lines_list):
    html_output = ""
    for line in lines_list:
        if line.strip():
            icon = get_smart_icon(line)
            html_output += f'<div style="margin-bottom: 6px; display: flex; align-items: flex-start; gap: 8px;"><span>{icon}</span><span>{line}</span></div>'
    return html_output

# 排序輔助函式
def get_sort_date(date_str):
    if not date_str:
        return date.max
    try:
        first_part = str(date_str).split("~")[0].strip()
        return datetime.strptime(first_part, "%Y-%m-%d").date()
    except:
        return date.today()

# 套用自訂 CSS
st.markdown("""
    <style>
    html, body, [data-testid="stWidgetLabel"] p, .stSelectbox, .stDateInput {
        font-size: 20px !important; font-weight: 500 !important;
    }
    h2 { font-size: 32px !important; font-weight: bold !important; color: #0D9488; }
    .event-card { padding: 15px 20px; border-radius: 8px; margin-bottom: 12px; font-size: 22px !important; }
    .show-style { background-color: #E0F2FE; border-left: 6px solid #0EA5E9; color: #0369A1; }
    .progress-style { background-color: #E2F0D9; border-left: 6px solid #70AD47; color: #385723; }
    .notice-style { background-color: #FCE8E6; border-left: 6px solid #EA4335; color: #A51D12; }
    .show-title-text { font-size: 24px !important; font-weight: bold !important; color: #1E40AF; margin-bottom: 8px; }
    .notice-title-text { font-size: 24px !important; font-weight: bold !important; color: #B91C1C; margin-bottom: 8px; }
    .show-meta-text { font-size: 19px !important; color: #475569; line-height: 1.5; }
    </style>
""", unsafe_allow_html=True)

# 載入最新行程
if 'events' not in st.session_state:
    st.session_state.events = load_events()

# --- 主畫面呈現 ---
col1, col2, col3 = st.columns([1, 1, 1])

# --- 1. 演出活動 ---
with col1:
    st.markdown("<h2>✨ 演出活動</h2>", unsafe_allow_html=True)
    show_events = [e for e in st.session_state.events if e["分類"] == "✨ 演出活動"]
    for ev in sorted(show_events, key=lambda x: get_sort_date(x["日期"])):
        lines = [line.strip() for line in ev["內容"].split("\n") if line.strip()]
        act_name = lines[0] if lines else "未命名活動"
        desc_lines = lines[1:] if len(lines) > 1 else []
        items_html = render_content_items(desc_lines)
        st.markdown(f"""
            <div class="event-card show-style">
                <div class="show-title-text">🎵 {act_name}</div>
                <div class="show-meta-text">📅 <b>日期：</b>{ev["日期"]}<br>⏰ <b>時間：</b>{ev["時間"]}<br>🏠 <b>地點：</b>{ev.get("地點", "未定")}</div>
                <hr style="margin: 12px 0; border: 0; border-top: 1px dashed #0EA5E9;">
                <div>{items_html}</div>
            </div>
        """, unsafe_allow_html=True)

# --- 2. 每日進度（已隱藏時間顯示） ---
with col2:
    st.markdown("<h2>🥁 每日進度</h2>", unsafe_allow_html=True)
    prog_events = [e for e in st.session_state.events if e["分類"] == "🥁 每日進度"]
    for ev in sorted(prog_events, key=lambda x: get_sort_date(x["日期"])):
        lines = [line.strip() for line in ev["內容"].split("\n") if line.strip()]
        items_html = render_content_items(lines)
        st.markdown(f'<div class="event-card progress-style"><strong>📅 【{ev["日期"]}】</strong><hr style="margin: 8px 0; border: 0; border-top: 1px dashed #70AD47;">{items_html}</div>', unsafe_allow_html=True)

# --- 3. 通知事項 ---
with col3:
    st.markdown("<h2>📢 通知事項</h2>", unsafe_allow_html=True)
    notice_events = [e for e in st.session_state.events if e["分類"] == "📢 通知事項"]
    for ev in sorted(notice_events, key=lambda x: get_sort_date(x["日期"])):
        lines = [line.strip() for line in ev["內容"].split("\n") if line.strip()]
        notice_title = lines[0] if lines else "未命名通知"
        desc_lines = lines[1:] if len(lines) > 1 else []
        items_html = render_content_items(desc_lines)
        st.markdown(f"""
            <div class="event-card notice-style">
                <div class="notice-title-text">📢 {notice_title}</div>
                <div class="show-meta-text">📅 <b>日期：</b>{ev["日期"]}<br>⏰ <b>時間：</b>{ev["時間"]}</div>
                <hr style="margin: 12px 0; border: 0; border-top: 1px dashed #EA4335;">
                <div>{items_html}</div>
            </div>
        """, unsafe_allow_html=True)
