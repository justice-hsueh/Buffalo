import streamlit as st
import json
import os
from datetime import datetime, date

# 頁面設定
st.set_page_config(page_title="大竹國小兒童樂隊行事曆", layout="wide")

# --- 載入資料 ---
def load_events():
    if os.path.exists("events.json"):
        with open("events.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

if 'events' not in st.session_state:
    st.session_state.events = load_events()

# --- 標題 ---
st.title("🎵 大竹國小兒童樂隊行事曆")

# --- 倒數計時 ---
today = date.today()
shows = [e for e in st.session_state.events if e["分類"] == "✨ 演出活動"]
upcoming = [e for e in shows if datetime.strptime(e["日期"], "%Y-%m-%d").date() >= today]

if upcoming:
    next_show = sorted(upcoming, key=lambda x: x["日期"])[0]
    days = (datetime.strptime(next_show["日期"], "%Y-%m-%d").date() - today).days
    # 使用 st.info 顯示，確保顏色明亮且文字清晰
    st.info(f"⏳ 下一個演出：{next_show['內容'].splitlines()[0]}，距離現在還有 {days} 天！")

# --- 顏色定義 ---
colors = {
    "✨ 演出活動": "#E0F2FE", 
    "🥁 每日進度": "#E2F0D9", 
    "📢 通知事項": "#FCE8E6"
}

# --- 主畫面 ---
col1, col2, col3 = st.columns(3)

def render_column(column, title, category):
    with column:
        st.subheader(title)
        # 篩選並排序行程
        events = sorted([e for e in st.session_state.events if e["分類"] == category], key=lambda x: x["日期"])
        for ev in events:
            # 使用 inline 樣式定義卡片，確保字體顏色為黑色 (color: #000000)
            st.markdown(f"""
                <div style="background-color: {colors.get(category, '#f0f0f0')}; 
                            padding: 15px; 
                            border-radius: 10px; 
                            margin-bottom: 15px; 
                            border-left: 6px solid #555;
                            color: #000000;">
                    <div style="font-size: 18px; font-weight: bold;">{ev['內容'].splitlines()[0]}</div>
                    <div style="font-size: 14px; margin-top: 5px;">📅 {ev['日期']} | ⏰ {ev['時間']}</div>
                </div>
            """, unsafe_allow_html=True)

render_column(col1, "✨ 演出活動", "✨ 演出活動")
render_column(col2, "🥁 每日進度", "🥁 每日進度")
render_column(col3, "📢 通知事項", "📢 通知事項")

# --- 側邊欄 (管理員功能) ---
st.sidebar.markdown("### ⚙️ 管理員控制台")
if st.sidebar.text_input("🔑 請輸入管理密碼", type="password") == "dccb":
    if st.sidebar.button("重新整理頁面"):
        st.rerun()
    st.sidebar.write("（若要新增或刪除，請使用原本的邏輯）")
