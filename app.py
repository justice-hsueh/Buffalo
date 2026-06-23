import streamlit as st
import json
import os
from datetime import datetime, date

st.set_page_config(page_title="大竹國小兒童樂隊行事曆", layout="wide")

# --- 核心函數 ---
def load_events():
    if os.path.exists("events.json"):
        try:
            with open("events.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return []

def parse_date(date_str):
    try: return datetime.strptime(str(date_str).strip()[:10], "%Y-%m-%d").date()
    except: return date(1900, 1, 1)

if 'events' not in st.session_state:
    st.session_state.events = load_events()

# --- 標題 ---
st.title("🎵 大竹國小兒童樂隊行事曆")

# --- 側邊欄 (完整功能版) ---
st.sidebar.markdown("### ⚙️ 管理員控制台")
if st.sidebar.text_input("🔑 請輸入管理密碼", type="password") == "dccb":
    st.sidebar.success("✅ 已登入")
    mode = st.sidebar.radio("操作項目", ["新增行程", "刪除行程"])
    
    if mode == "新增行程":
        with st.sidebar.form("add_form"):
            cat = st.selectbox("分類", ["✨ 演出活動", "🥁 每日進度", "📢 通知事項"])
            f_date = str(st.date_input("日期"))
            time_in = st.text_input("時間")
            cont = st.text_area("內容")
            if st.form_submit_button("新增"):
                new_ev = {"id": len(st.session_state.events)+1, "分類": cat, "日期": f_date, "時間": time_in, "內容": cont}
                st.session_state.events.append(new_ev)
                with open("events.json", "w", encoding="utf-8") as f:
                    json.dump(st.session_state.events, f, ensure_ascii=False, indent=4)
                st.rerun()

    elif mode == "刪除行程":
        to_del = st.sidebar.selectbox("選擇要刪除的行程", [f"{e['日期']} | {e['內容'][:10]}" for e in st.session_state.events])
        if st.sidebar.button("確認刪除"):
            st.session_state.events = [e for e in st.session_state.events if f"{e['日期']} | {e['內容'][:10]}" != to_del]
            with open("events.json", "w", encoding="utf-8") as f:
                json.dump(st.session_state.events, f, ensure_ascii=False, indent=4)
            st.rerun()

    if st.sidebar.button("清理所有過期行程"):
        today = date.today()
        st.session_state.events = [e for e in st.session_state.events if parse_date(e["日期"]) >= today]
        with open("events.json", "w", encoding="utf-8") as f:
            json.dump(st.session_state.events, f, ensure_ascii=False, indent=4)
        st.rerun()

# --- 主畫面 ---
today = date.today()
col1, col2, col3 = st.columns(3)
colors = {"✨ 演出活動": "#E0F2FE", "🥁 每日進度": "#E2F0D9", "📢 通知事項": "#FCE8E6"}

for col, cat in zip([col1, col2, col3], ["✨ 演出活動", "🥁 每日進度", "📢 通知事項"]):
    with col:
        st.subheader(cat)
        events = sorted([e for e in st.session_state.events if e["分類"] == cat and parse_date(e["日期"]) >= today], key=lambda x: x["日期"])
        for ev in events:
            st.markdown(f"""
                <div style="background-color: {colors.get(cat, '#f0f0f0')}; padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 6px solid #555; color: #000000;">
                    <div style="font-size: 18px; font-weight: bold;">{ev.get('內容', '').replace('\n', '<br>')}</div>
                    <div style="font-size: 14px; margin-top: 8px;">📅 {ev['日期']} | ⏰ {ev['時間']}</div>
                </div>
            """, unsafe_allow_html=True)
