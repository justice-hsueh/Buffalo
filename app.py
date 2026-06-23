import streamlit as st
import json
import os
from datetime import datetime, date

st.set_page_config(page_title="大竹國小兒童樂隊行事曆", layout="wide")

# --- 資料載入 ---
def load_events():
    if os.path.exists("events.json"):
        try:
            with open("events.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return []

# --- 強力日期轉換函數 (解決 ValueError) ---
def parse_date(date_str):
    try:
        # 先去除前後空格，只取前10個字元 (YYYY-MM-DD)
        clean_date = str(date_str).strip()[:10]
        return datetime.strptime(clean_date, "%Y-%m-%d").date()
    except:
        # 如果格式真的毀損，就回傳一個遠古日期，讓它被篩選掉
        return date(1900, 1, 1)

if 'events' not in st.session_state:
    st.session_state.events = load_events()

# --- 標題 ---
st.title("🎵 大竹國小兒童樂隊行事曆")

# --- 倒數計時 ---
today = date.today()
shows = [e for e in st.session_state.events if e["分類"] == "✨ 演出活動"]
# 使用新的 parse_date 函數來過濾
upcoming = [e for e in shows if parse_date(e["日期"]) >= today]

if upcoming:
    next_show = sorted(upcoming, key=lambda x: x["日期"])[0]
    days = (parse_date(next_show["日期"]) - today).days
    st.info(f"⏳ 下一個演出：{next_show['內容'].splitlines()[0]}，距離現在還有 {days} 天！")

# --- 主畫面 ---
col1, col2, col3 = st.columns(3)
colors = {"✨ 演出活動": "#E0F2FE", "🥁 每日進度": "#E2F0D9", "📢 通知事項": "#FCE8E6"}

for col, cat in zip([col1, col2, col3], ["✨ 演出活動", "🥁 每日進度", "📢 通知事項"]):
    with col:
        st.subheader(cat)
        # 篩選並排序，同樣使用 parse_date
        events = sorted(
            [e for e in st.session_state.events if e["分類"] == cat and parse_date(e["日期"]) >= today], 
            key=lambda x: x["日期"]
        )
        for ev in events:
            raw_content = ev.get('內容', '')
            st.markdown(f"""
                <div style="background-color: {colors.get(cat, '#f0f0f0')}; 
                            padding: 15px; border-radius: 10px; margin-bottom: 15px; 
                            border-left: 6px solid #555; color: #000000;">
                    <div style="font-size: 18px; font-weight: bold;">{raw_content.replace('\n', '<br>')}</div>
                    <div style="font-size: 14px; margin-top: 8px;">📅 {ev['日期']} | ⏰ {ev['時間']}</div>
                </div>
            """, unsafe_allow_html=True)

# --- 側邊欄 ---
st.sidebar.markdown("### ⚙️ 管理員控制台")
if st.sidebar.text_input("🔑 請輸入管理密碼", type="password") == "dccb":
    if st.sidebar.button("清理過期資料並存檔"):
        valid_events = [e for e in st.session_state.events if parse_date(e["日期"]) >= today]
        with open("events.json", "w", encoding="utf-8") as f:
            json.dump(valid_events, f, ensure_ascii=False, indent=4)
        st.sidebar.write("已清理完成！")
        st.rerun()
