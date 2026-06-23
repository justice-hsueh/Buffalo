import streamlit as st
import json
import os
from datetime import datetime, date

st.set_page_config(page_title="大竹國小兒童樂隊行事曆", layout="wide")

# --- 設定配色 ---
COLORS = {
    "✨ 演出活動": {"bg": "#E0F2FE", "border": "#0EA5E9"},
    "🥁 每日進度": {"bg": "#E2F0D9", "border": "#70AD47"},
    "📢 通知事項": {"bg": "#FCE8E6", "border": "#EA4335"}
}

# --- 核心邏輯 ---
def load_events():
    if os.path.exists("events.json"):
        try:
            with open("events.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    if '地點' not in item: item['地點'] = ""
                return data
        except: return []
    return []

def parse_date(date_str):
    d = str(date_str).split("~")[0].strip()[:10]
    try: return datetime.strptime(d, "%Y-%m-%d").date()
    except: return date(1900, 1, 1)

# 初始化並自動清理過期資料
if 'events' not in st.session_state:
    st.session_state.events = load_events()
    today = date.today()
    st.session_state.events = [e for e in st.session_state.events if parse_date(e["日期"]) >= today]

# --- 標題 ---
st.markdown("""
    <div style="background: linear-gradient(to right, #E53E3E, #ED8936, #ECC94B, #48BB78, #3182CE, #000080, #9F7AEA);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                font-size: 40px; font-weight: bold; margin-bottom: 20px;">
        🎵 大竹國小兒童樂隊行事曆
    </div>
""", unsafe_allow_html=True)

# --- 側邊欄管理員控制台 ---
st.sidebar.markdown("### ⚙️ 管理員控制台")
if st.sidebar.text_input("🔑 請輸入管理密碼", type="password") == "dccb":
    mode = st.sidebar.radio("操作項目", ["新增行程", "修改行程", "刪除行程"])
    
    if mode == "新增行程":
        with st.sidebar.form("add_f"):
            cat = st.selectbox("分類", list(COLORS.keys()))
            d_start = st.date_input("開始日期")
            d_end = st.date_input("結束日期 (僅需一段時間時點選)")
            time_in = st.text_input("時間")
            loc_in = st.text_input("地點")
            cont = st.text_area("內容 (第一行標題，第二行起為詳細內容)")
            if st.form_submit_button("新增"):
                f_date = f"{d_start} ~ {d_end}" if d_start != d_end else str(d_start)
                st.session_state.events.append({"分類": cat, "日期": f_date, "時間": time_in, "地點": loc_in, "內容": cont})
                with open("events.json", "w", encoding="utf-8") as f:
                    json.dump(st.session_state.events, f, ensure_ascii=False, indent=4)
                st.rerun()

    elif mode == "修改行程":
        opts = {f"{e['日期']} | {e['內容'][:10]}": e for e in st.session_state.events}
        sel = st.sidebar.selectbox("選擇要修改的行程", list(opts.keys()))
        target = opts[sel]
        
        new_cat = st.sidebar.selectbox("修改分類", list(COLORS.keys()), index=list(COLORS.keys()).index(target['分類']))
        new_d = st.sidebar.text_input("修改日期", target['日期'])
        new_t = st.sidebar.text_input("修改時間", target.get('時間', ''))
        new_l = st.sidebar.text_input("修改地點", target.get('地點', ''))
        new_c = st.sidebar.text_area("修改內容", target['內容'])
        
        if st.sidebar.button("儲存修改"):
            target.update({'分類': new_cat, '日期': new_d, '時間': new_t, '地點': new_l, '內容': new_c})
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

# --- 主畫面渲染 ---
col1, col2, col3 = st.columns(3)
for col, cat in zip([col1, col2, col3], list(COLORS.keys())):
    with col:
        st.subheader(cat)
        for ev in sorted([e for e in st.session_state.events if e["分類"] == cat], key=lambda x: parse_date(x["日期"])):
            c = COLORS[cat]
            lines = ev.get('內容', '').splitlines()
            title = lines[0] if lines else "無標題"
            details = "<br>".join(lines[1:]) if len(lines) > 1 else ""
            details_html = f"<hr style='border: 0; border-top: 1px solid #aaa; margin: 8px 0;'><div style='font-size: 15px; color: #444;'>{details}</div>" if details else ""
            
            loc_val = ev.get('地點', '')
            location_html = f"<div style='font-size: 14px; margin-top: 3px;'>📍 {loc_val}</div>" if loc_val else ""
            
            st.markdown(f"""
                <div style="background-color: {c['bg']}; padding: 15px; border-radius: 8px; margin-bottom: 12px; 
                            border-left: 8px solid {c['border']}; color: #000000;">
                    <div style="font-size: 19px; font-weight: bold; margin-bottom: 5px;">{title}</div>
                    <hr style="border: 0; border-top: 1px solid #aaa; margin: 8px 0;">
                    <div style="font-size: 14px; font-weight: 600; color: #333;">
                        📅 {ev['日期']} | ⏰ {ev['時間']}
                    </div>
                    {location_html}
                    {details_html}
                </div>
            """, unsafe_allow_html=True)
