import streamlit as st
import json
import os
from datetime import datetime, date

st.set_page_config(page_title="大竹國小兒童樂隊行事曆", layout="wide")

# --- 核心邏輯 ---
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

# 自動刪除過期行程的機制
def clean_expired_events(events):
    today = date.today()
    valid_events = [e for e in events if parse_date(e["日期"]) >= today]
    if len(valid_events) != len(events):
        with open("events.json", "w", encoding="utf-8") as f:
            json.dump(valid_events, f, ensure_ascii=False, indent=4)
    return valid_events

# 初始化與自動清理
if 'events' not in st.session_state:
    raw_events = load_events()
    st.session_state.events = clean_expired_events(raw_events)

# --- 標題 ---
st.title("🎵 大竹國小兒童樂隊行事曆")

# --- 側邊欄 (完整功能：新增、修改、刪除) ---
st.sidebar.markdown("### ⚙️ 管理員控制台")
if st.sidebar.text_input("🔑 請輸入管理密碼", type="password") == "dccb":
    st.sidebar.success("✅ 已登入")
    mode = st.sidebar.radio("操作項目", ["新增行程", "修改行程", "刪除行程"])
    
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

    elif mode == "修改行程":
        options = {f"{e['日期']} | {e['內容'][:10]}": e for e in st.session_state.events}
        selected = st.sidebar.selectbox("選擇要修改的行程", list(options.keys()))
        target = options[selected]
        with st.sidebar.form("edit_form"):
            new_cont = st.text_area("修改內容", target['內容'])
            if st.form_submit_button("儲存修改"):
                target['內容'] = new_cont
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

# --- 主畫面 ---
today = date.today()
col1, col2, col3 = st.columns(3)
colors = {"✨ 演出活動": "#E0F2FE", "🥁 每日進度": "#E2F0D9", "📢 通知事項": "#FCE8E6"}

for col, cat in zip([col1, col2, col3], ["✨ 演出活動", "🥁 每日進度", "📢 通知事項"]):
    with col:
        st.subheader(cat)
        # 顯示已過濾後的資料
        for ev in sorted([e for e in st.session_state.events if e["分類"] == cat], key=lambda x: x["日期"]):
            st.markdown(f"""
                <div style="background-color: {colors.get(cat, '#f0f0f0')}; padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 6px solid #555; color: #000000;">
                    <div style="font-size: 18px; font-weight: bold;">{ev.get('內容', '').replace('\n', '<br>')}</div>
                    <div style="font-size: 14px; margin-top: 8px;">📅 {ev['日期']} | ⏰ {ev['時間']}</div>
                </div>
            """, unsafe_allow_html=True)
