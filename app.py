import streamlit as st
import pandas as pd
from datetime import datetime, date

# 設定網頁標題與整體風格
st.set_page_config(page_title="大竹國小兒童樂隊行事曆", layout="wide")

# 套用自訂 CSS：全面放大字體與美化卡片風格
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
    /* 三個新分類的精美配色 */
    .show-style { background-color: #E0F2FE; border-left: 6px solid #0EA5E9; color: #0369A1; }
    .progress-style { background-color: #E2F0D9; border-left: 6px solid #70AD47; color: #385723; }
    .notice-style { background-color: #FCE8E6; border-left: 6px solid #EA4335; color: #A51D12; }
    
    div[data-testid="stForm"] { background-color: #F3F4F6; padding: 20px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# 1. 標題修改為「大竹國小兒童樂隊行事曆」
st.title("🪗 大竹國小兒童樂隊行事曆")

# 初始化記憶體資料
if 'events' not in st.session_state:
    st.session_state.events = [
        {"id": 1, "日期": "2026-06-25", "分類": "✨ 演出活動", "時間": "13:30 - 15:30", "內容": "全團總排練（注意：分部樂譜需收齊）"},
        {"id": 2, "日期": "2026-06-26", "分類": "🥁 每日進度", "時間": "晨課時間", "內容": "打擊與鍵盤分部練習基本功"},
        {"id": 3, "日期": "2026-06-27", "分類": "📢 通知事項", "時間": "全天", "內容": "請大家記得帶樂器與個人講義回家複習"},
    ]

if 'target_date' not in st.session_state:
    st.session_state.target_date = date(2026, 7, 10)
if 'target_title' not in st.session_state:
    st.session_state.target_title = "重要樂團活動"

# 3. 重大活動倒數顯示
t_date = datetime.combine(st.session_state.target_date, datetime.min.time())
today = datetime.now()
days_left = (t_date - today).days + 1

if days_left >= 0:
    st.markdown(f
