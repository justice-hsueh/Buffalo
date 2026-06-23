import streamlit as st
import json
import os
from datetime import datetime, date

# 頁面設定
st.set_page_config(page_title="大竹國小兒童樂隊行事曆", layout="wide")

# --- 資料讀取與自動清理 ---
def load_and_clean_events():
    if not os.path.exists("events.json"):
        return []
    
    with open("events.json", "r", encoding="utf-8") as f:
        events = json.load(f)
    
    today = date.today()
    # 自動清理邏輯：只保留「今天」或「未來」的行程
    # 注意：如果演出活動有時效性，這裡會自動刪除昨天的紀錄
    new_events = [e for e in events if datetime.strptime(e["日期"], "%Y-%m-%d").date() >= today]
    
    # 如果有被刪除的資料，更新 JSON 檔案
    if len(new_events) != len(events):
        with open("events.json", "w", encoding="utf-8") as f:
            json.dump(new_events, f, ensure_ascii=False, indent=4)
            
    return new_events

if 'events' not in st.session_state:
    st.session_state.events = load_and_clean_events()

# --- 標題 ---
st.title("🎵 大竹國小兒童樂隊行事曆")

# --- 倒數計時 ---
today = date.today()
shows = [e for e in st.session_state.events if e["分類"] == "✨ 演出活動"]
if shows:
    # 因為已經過濾掉過期資料，shows 裡的都是今天或未來的
    next_show = sorted(shows, key=lambda x: x["日期"])[0]
    days = (datetime.strptime(next_show["日期"], "%Y-%m-%d").date() - today).days
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
        events = sorted([e for e in st.session_state.events if e["分類"] == category], key=lambda x: x["日期"])
        for ev in events:
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

# --- 側邊欄 ---
st.sidebar.markdown("### ⚙️ 管理員控制台")
if st.sidebar.text_input("🔑 請輸入管理密碼", type="password") == "dccb":
    if st.sidebar.button("手動更新畫面"):
        st.rerun()
