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

# --- 初始化 ---
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
    # 這裡加上簡單的檢查，避免內容為空導致的錯誤
    content_text = next_show.get('內容', '無內容')
    title_text = content_text.splitlines()[0] if content_text else "無標題"
    st.info(f"⏳ 下一個演出：{title_text}，距離現在還有 {days} 天！")

# --- 主畫面 ---
col1, col2, col3 = st.columns(3)
colors = {"✨ 演出活動": "#E0F2FE", "🥁 每日進度": "#E2F0D9", "📢 通知事項": "#FCE8E6"}

for col, cat in zip([col1, col2, col3], ["✨ 演出活動", "🥁 每日進度", "📢 通知事項"]):
    with col:
        st.subheader(cat)
        # 顯示時只過濾過期的，不刪除檔案
        events = sorted([e for e in st.session_state.events if e["分類"] == cat and datetime.strptime(e["日期"], "%Y-%m-%d").date() >= today], key=lambda x: x["日期"])
        for ev in events:
            # 確保內容顯示完整
            raw_content = ev.get('內容', '')
            # 使用 <pre> 或直接用 st.write 顯示完整內容
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
    st.sidebar.success("已登入")
    if st.sidebar.button("清理過期資料並存檔"):
        # 真正執行篩選存檔
        valid_events = [e for e in st.session_state.events if datetime.strptime(e["日期"], "%Y-%m-%d").date() >= today]
        with open("events.json", "w", encoding="utf-8") as f:
            json.dump(valid_events, f, ensure_ascii=False, indent=4)
        st.sidebar.write("已刪除所有過期資料！")
        st.rerun()
