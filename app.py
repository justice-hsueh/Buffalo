import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import base64
import json

st.set_page_config(page_title="大竹國小兒童樂隊行事曆", layout="wide")

DATA_FILE = "events.json"
CONFIG_FILE = "config.json"

# --- CSS 樣式 ---
CSS_STYLE = """
<style>
    .event-card { padding: 12px 15px; border-radius: 8px; margin-bottom: 10px; font-size: 19px !important; }
    .show-style { background-color: #E0F2FE; border-left: 6px solid #0EA5E9; color: #0369A1; }
    .progress-style { background-color: #E2F0D9; border-left: 6px solid #70AD47; color: #385723; }
    .notice-style { background-color: #FCE8E6; border-left: 6px solid #EA4335; color: #A51D12; }
    hr { margin: 6px 0 !important; border: 0; border-top: 1px dashed #A0A0A0; }
    .title-text { font-size: 22px !important; font-weight: bold !important; margin-bottom: 4px; }
    .rainbow-text { font-size: clamp(22px, 6vw, 42px) !important; font-weight: bold !important; white-space: nowrap; background: linear-gradient(to right, #E53E3E, #ED8936, #ECC94B, #48BB78, #3182CE, #000080, #9F7AEA); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .custom-title-container { display: flex; align-items: center; gap: 15px; margin-bottom: 20px; }
    .custom-title-logo { width: 80px; height: auto; }
    @media (max-width: 600px) {
        .custom-title-logo { width: 50px !important; }
        .custom-title-container { gap: 10px !important; margin-bottom: 15px !important; }
    }
</style>
"""
st.markdown(CSS_STYLE, unsafe_allow_html=True)

# --- 函數區 ---
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

if 'events' not in st.session_state: st.session_state.events = load_events()

# --- 標題與倒數 ---
logo_file = next((n for n in ["logo.jpg", "logo.JPG", "logo.png", "logo.PNG", "logo.jpeg"] if os.path.exists(n)), None)
if logo_file:
    with open(logo_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(f'<div class="custom-title-container"><img class="custom-title-logo" src="data:image/jpeg;base64,{encoded}"><span class="rainbow-text">大竹國小兒童樂隊行事曆</span></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="rainbow-text">🎵 大竹國小兒童樂隊行事曆</div>', unsafe_allow_html=True)

today = date.today()
upcoming_shows = [e for e in st.session_state.events if e["分類"] == "✨ 演出活動" and get_sort_date(e["日期"]) >= today]
if upcoming_shows:
    next_show = sorted(upcoming_shows, key=lambda x: get_sort_date(x["日期"]))[0]
    days_left = (get_sort_date(next_show["日期"]) - today).days
    st.markdown(f'''<div style="background-color: #F8F9FA; padding: 10px; border-radius: 8px; border-left: 5px solid #48BB78; margin-bottom: 20px;"><div style="font-size: 18px; color: #2D3748;">⏳ 下一個演出倒數：距離 <b>{next_show['內容'].splitlines()[0]}</b> 還有 <b style="color: #48BB78; font-size: 1.3em;">{days_left}</b> 天</div></div>''', unsafe_allow_html=True)

# --- 管理員控制台與主畫面 (其餘代碼保持一致) ---
# ... (這裡為了篇幅，請確保您將原本的 側邊欄 和 三個欄位的主畫面代碼接在下方即可)
