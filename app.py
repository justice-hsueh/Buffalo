import streamlit as st
import pandas as pd
from datetime import datetime

# 設定網頁標題與整體風格
st.set_page_config(page_title="我的專屬大字體行事曆", layout="wide")

# 套用自訂 CSS：全面放大字體
st.markdown("""
    <style>
    html, body, [data-testid="stWidgetLabel"] p, .stSelectbox, .stDateInput {
        font-size: 20px !important;
        font-weight: 500 !important;
    }
    h1 { font-size: 42px !important; font-weight: bold !important; color: #1E3A8A; }
    h2 { font-size: 32px !important; font-weight: bold !important; color: #0D9488; }
    h3 { font-size: 26px !important; font-weight: bold !important; }
    .stButton>button {
        font-size: 22px !important;
        padding: 10px 24px !important;
        background-color: #1E3A8A !important;
        color: white !important;
    }
    .countdown-box {
        background-color: #FEF3C7;
        padding: 20px;
        border-radius: 12px;
        border-left: 8px solid #F59E0B;
        font-size: 28px !important;
        font-weight: bold;
        margin-bottom: 25px;
    }
    .event-card {
        padding: 15px 20px;
        border-radius: 8px;
        margin-bottom: 12px;
        font-size: 22px !important;
    }
    .band-style { background-color: #E0F2FE; border-left: 6px solid #0EA5E9; color: #0369A1; }
    .personal-style { background-color: #FFEDD5; border-left: 6px solid #F97316; color: #C2410C; }
    </style>
""", unsafe_allow_html=True)

st.title("📅 我的專屬大字體行事曆")

# 倒數計時（可自行修改目標日期）
target_date = datetime(2026, 7, 10)
today = datetime.now()
days_left = (target_date - today).days

if days_left >= 0:
    st.markdown(f"""
        <div class="countdown-box">
            ⏰ 距離 重要活動（2026/07/10） 還有 <span style="font-size: 36px; color: #DC2626;">{days_left}</span> 天
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown('<div class="countdown-box">🎉 活動已圓滿完成！</div>', unsafe_allow_html=True)

if 'events' not in st.session_state:
    st.session_state.events = [
        {"日期": "2026-06-25", "分類": "🎵 樂團事務", "時間": "13:30 - 15:30", "內容": "全團總排練（注意：分部樂譜需收齊）"},
        {"日期": "2026-06-25", "分類": "🏡 個人生活", "時間": "18:00", "內容": "與家人聚餐"},
    ]

# 左側表單
st.sidebar.markdown("<h2>➕ 新增新行程</h2>", unsafe_allow_html=True)
with st.sidebar.form("event_form", clear_on_submit=True):
    new_date = st.date_input("選擇日期")
    new_category = st.selectbox("選擇分類", ["🎵 樂團事務", "🏡 個人生活"])
    new_time = st.text_input("輸入時間")
    new_content = st.text_area("行程備忘 / 準備事項")
    submit_button = st.form_submit_button("確認加入行事曆")
    
    if submit_button and new_content:
        st.session_state.events.append({
            "日期": str(new_date),
            "分類": new_category,
            "時間": new_time,
            "內容": new_content
        })

# 右側顯示
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("<h2>🎵 樂團事務行程</h2>", unsafe_allow_html=True)
    for ev in sorted([e for e in st.session_state.events if e["分類"] == "🎵 樂團事務"], key=lambda x: x["日期"]):
        st.markdown(f'<div class="event-card band-style"><strong>【{ev["日期"]}】 {ev["時間"]}</strong><br>📌 {ev["內容"]}</div>', unsafe_allow_html=True)

with col2:
    st.markdown("<h2>🏡 個人生活行程</h2>", unsafe_allow_html=True)
    for ev in sorted([e for e in st.session_state.events if e["分類"] == "🏡 個人生活"], key=lambda x: x["日期"]):
        st.markdown(f'<div class="event-card personal-style"><strong>【{ev["日期"]}】 {ev["時間"]}</strong><br>📌 {ev["內容"]}</div>', unsafe_allow_html=True)
