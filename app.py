import streamlit as st
import json
import os
from datetime import datetime, date

st.set_page_config(page_title="大竹國小兒童樂隊行事曆", layout="wide")

COLORS = {
    "✨ 演出活動": {"bg": "#E0F2FE", "border": "#0EA5E9"},
    "🥁 每日進度": {"bg": "#E2F0D9", "border": "#70AD47"},
    "📢 通知事項": {"bg": "#FCE8E6", "border": "#EA4335"}
}

def load_events():
    if os.path.exists("events.json"):
        try:
            with open("events.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return []

def parse_date(date_str):
    # 處理區間格式 (取 ~ 前面的日期進行排序)
    d = str(date_str).split("~")[0].strip()[:10]
    try: return datetime.strptime(d, "%Y-%m-%d").date()
    except: return date(1900, 1, 1)

if 'events' not in st.session_state:
    raw = load_events()
    today = date.today()
    st.session_state.events = [e for e in raw if parse_date(e["日期"]) >= today]

# --- 標題 ---
st.markdown("""
    <div style="background: linear-gradient(to right, #E53E3E, #ED8936, #ECC94B, #48BB78, #3182CE, #000080, #9F7AEA);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                font-size: 42px; font-weight: bold; margin-bottom: 20px;">
        🎵 大竹國小兒童樂隊行事曆
    </div>
""", unsafe_allow_html=True)

# --- 側邊欄 ---
st.sidebar.markdown("### ⚙️ 管理員控制台")
if st.sidebar.text_input("🔑 請輸入管理密碼", type="password") == "dccb":
    mode = st.sidebar.radio("操作項目", ["新增行程", "修改行程", "刪除行程"])
    
    if mode == "新增行程":
        with st.sidebar.form("add_f"):
            cat = st.selectbox("分類", list(COLORS.keys()))
            # 讓老師自行決定輸入格式
            f_date = st.text_input("日期 (單一日期請填 YYYY-MM-DD，區間請填 YYYY-MM-DD ~ YYYY-MM-DD)")
            time_in = st.text_input("時間")
            cont = st.text_area("內容")
            if st.form_submit_button("新增"):
                st.session_state.events.append({"分類": cat, "日期": f_date, "時間": time_in, "內容": cont})
                with open("events.json", "w", encoding="utf-8") as f:
                    json.dump(st.session_state.events, f, ensure_ascii=False, indent=4)
                st.rerun()
    elif mode == "修改行程":
        opts = {f"{e['日期']} | {e['內容'][:10]}": e for e in st.session_state.events}
        sel = st.sidebar.selectbox("選行程", list(opts.keys()))
        new_d = st.sidebar.text_input("修改日期", opts[sel]['日期'])
        new_c = st.sidebar.text_area("修改內容", opts[sel]['內容'])
        if st.sidebar.button("儲存修改"):
            opts[sel]['日期'] = new_d
            opts[sel]['內容'] = new_c
            with open("events.json", "w", encoding="utf-8") as f:
                json.dump(st.session_state.events, f, ensure_ascii=False, indent=4)
            st.rerun()
    elif mode == "刪除行程":
        to_del = st.sidebar.selectbox("選行程", [f"{e['日期']} | {e['內容'][:10]}" for e in st.session_state.events])
        if st.sidebar.button("確認刪除"):
            st.session_state.events = [e for e in st.session_state.events if f"{e['日期']} | {e['內容'][:10]}" != to_del]
            with open("events.json", "w", encoding="utf-8") as f:
                json.dump(st.session_state.events, f, ensure_ascii=False, indent=4)
            st.rerun()

# --- 主畫面 ---
col1, col2, col3 = st.columns(3)
for col, cat in zip([col1, col2, col3], list(COLORS.keys())):
    with col:
        st.subheader(cat)
        for ev in sorted([e for e in st.session_state.events if e["分類"] == cat], key=lambda x: parse_date(x["日期"])):
            c = COLORS[cat]
            st.markdown(f"""
                <div style="background-color: {c['bg']}; padding: 15px; border-radius: 8px; margin-bottom: 12px; 
                            border-left: 8px solid {c['border']}; color: #000000;">
                    <div style="font-size: 18px; font-weight: bold;">{ev.get('內容', '').replace('\n', '<br>')}</div>
                    <div style="font-size: 14px; margin-top: 8px; opacity: 0.8;">📅 {ev['日期']} | ⏰ {ev['時間']}</div>
                </div>
            """, unsafe_allow_html=True)
