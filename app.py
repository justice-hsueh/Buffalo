import streamlit as st
import json
import os
from datetime import datetime, date

# 頁面設定
st.set_page_config(page_title="大竹國小兒童樂隊行事曆", layout="wide")

# --- 核心資料讀取 ---
def load_events():
    if os.path.exists("events.json"):
        try:
            with open("events.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return []

# 檢查資料是否過期
def is_valid(event_date_str):
    try:
        return datetime.strptime(event_date_str, "%Y-%m-%d").date() >= date.today()
    except:
        return True # 格式錯誤則保留

# 讀取並過濾資料 (不在讀取時刪除檔案，避免衝突)
all_events = load_events()
# 篩選掉過期的內容
st.session_state.events = [e for e in all_events if is_valid(e["日期"])]

# --- 標題 ---
st.title("🎵 大竹國小兒童樂隊行事曆")

# --- 倒數計時 ---
today = date.today()
shows = [e for e in st.session_state.events if e["分類"] == "✨ 演出活動"]
if shows:
    upcoming = [e for e in shows if datetime.strptime(e["日期"], "%Y-%m-%d").date() >= today]
    if upcoming:
        next_show = sorted(upcoming, key=lambda x: x["日期"])[0]
        days = (datetime.strptime(next_show["日期"], "%Y-%m-%d").date() - today).days
        st.info(f"⏳ 下一個演出：{next_show['內容'].splitlines()[0]}，還有 {days} 天！")

# --- 主畫面 ---
col1, col2, col3 = st.columns(3)
colors = {"✨ 演出活動": "#E0F2FE", "🥁 每日進度": "#E2F0D9", "📢 通知事項": "#FCE8E6"}

for col, cat in zip([col1, col2, col3], ["✨ 演出活動", "🥁 每日進度", "📢 通知事項"]):
    with col:
        st.subheader(cat)
        for ev in sorted([e for e in st.session_state.events if e["分類"] == cat], key=lambda x: x["日期"]):
            st.markdown(f"""
                <div style="background-color: {colors.get(cat, '#f0f0f0')}; 
                            padding: 15px; border-radius: 10px; margin-bottom: 15px; 
                            border-left: 6px solid #555; color: #000000;">
                    <div style="font-size: 18px; font-weight: bold;">{ev['內容'].splitlines()[0]}</div>
                    <div style="font-size: 14px; margin-top: 5px;">📅 {ev['日期']} | ⏰ {ev['時間']}</div>
                </div>
            """, unsafe_allow_html=True)

# --- 側邊欄 ---
st.sidebar.markdown("### ⚙️ 管理員控制台")
if st.sidebar.text_input("🔑 請輸入管理密碼", type="password") == "dccb":
    st.sidebar.success("已登入")
    if st.sidebar.button("清除過期資料並存檔"):
        # 真正執行刪除存檔的動作
        with open("events.json", "w", encoding="utf-8") as f:
            json.dump(st.session_state.events, f, ensure_ascii=False, indent=4)
        st.sidebar.write("已清理完成！")
        st.rerun()
