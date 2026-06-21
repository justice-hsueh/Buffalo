import streamlit as st
import pandas as pd
from datetime import datetime

# 設定網頁標題與整體風格
st.set_page_config(page_title="我的專屬大字體行事曆", layout="wide")

# 套用自訂 CSS：全面放大字體與美化表單
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
    .band-style { background-color: #E0F2FE; border-left: 6px solid #0EA5E9; color: #0369A1; }
    .personal-style { background-color: #FFEDD5; border-left: 6px solid #F97316; color: #C2410C; }
    div[data-testid="stForm"] { background-color: #F3F4F6; padding: 20px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("📅 我的專屬大字體行行事曆")

# 倒數計時
target_date = datetime(2026, 7, 10)
today = datetime.now()
days_left = (target_date - today).days

if days_left >= 0:
    st.markdown(f"""
        <div class="countdown-box">
            ⏰ 距離 重要活動（2026/07/10） 還有 <span style="font-size: 36px; color: #DC2626;">{days_left}</span> 天
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown('<div class="countdown-box">🎉 活動已圓滿完成！</div>', unsafe_allow_html=True)

# 初始預設行程（修正此處的語法小錯誤）
if 'events' not in st.session_state:
    st.session_state.events = [
        {"id": 1, "日期": "2026-06-25", "分類": "🎵 樂團事務", "時間": "13:30 - 15:30", "內容": "全團總排練（注意：分部樂譜需收齊）"},
        {"id": 2, "日期": "2026-06-25", "分類": "🏡 個人生活", "時間": "18:00", "內容": "與家人聚餐"},
    ]

# 側邊欄控制台（點選左上角 >> 展開）
st.sidebar.markdown("<h2>⚙️ 行事曆控制台</h2>", unsafe_allow_html=True)

# 功能切換：新增、修改、刪除
mode = st.sidebar.radio("請選擇操作項目：", ["➕ 新增行程", "✏️ 修改行程", "🗑️ 刪除行程"])

st.sidebar.markdown("---")

# 【1. 新增行程模式】
if mode == "➕ 新增行程":
    st.sidebar.markdown("<h3>➕ 新增新行程</h3>", unsafe_allow_html=True)
    with st.sidebar.form("add_form", clear_on_submit=True):
        new_date = st.date_input("選擇日期")
        new_category = st.selectbox("選擇分類", ["🎵 樂團事務", "🏡 個人生活"])
        new_time = st.text_input("輸入時間")
        new_content = st.text_area("行程備忘 / 準備事項")
        submit_button = st.form_submit_button("確認加入行事曆")
        
        if submit_button and new_content:
            new_id = max([e["id"] for e in st.session_state.events]) + 1 if st.session_state.events else 1
            st.session_state.events.append({
                "id": new_id,
                "日期": str(new_date),
                "分類": new_category,
                "時間": new_time,
                "內容": new_content
            })
            st.rerun()

# 【2. 修改行程模式】
elif mode == "✏️ 修改行程":
    st.sidebar.markdown("<h3>✏️ 修改現有行程</h3>", unsafe_allow_html=True)
    if st.session_state.events:
        edit_options = {f"【{e['日期']}】{e['分類'][:2]} - {e['內容'][:10]}...": e for e in st.session_state.events}
        selected_text = st.sidebar.selectbox("請選擇要修改的行程：", list(edit_options.keys()))
        selected_event = edit_options[selected_text]
        
        # 帶入原本數值的修改表單
        with st.sidebar.form("edit_form"):
            curr_date = datetime.strptime(selected_event["日期"], "%Y-%m-%d")
            updated_date = st.date_input("修改日期", curr_date)
            
            cat_list = ["🎵 樂團事務", "🏡 個人生活"]
            curr_cat_idx = cat_list.index(selected_event["分類"]) if selected_event["分類"] in cat_list else 0
            updated_category = st.selectbox("修改分類", cat_list, index=curr_cat_idx)
            
            updated_time = st.text_input("修改時間", selected_event["時間"])
            updated_content = st.text_area("修改行程備忘", selected_event["內容"])
            
            edit_submit = st.form_submit_button("💾 確認修改並儲存")
            
            if edit_submit:
                for e in st.session_state.events:
                    if e["id"] == selected_event["id"]:
                        e["日期"] = str(updated_date)
                        e["分類"] = updated_category
                        e["時間"] = updated_time
                        e["內容"] = updated_content
                st.rerun()
    else:
        st.sidebar.write("目前沒有行程可供修改")

# 【3. 刪除行程模式】
elif mode == "🗑️ 刪除行程":
    st.sidebar.markdown("<h3>🗑️ 刪除現有行程</h3>", unsafe_allow_html=True)
    if st.session_state.events:
        delete_options = {f"【{e['日期']}】{e['時間']} - {e['內容'][:10]}...": e["id"] for e in st.session_state.events}
        selected_del_text = st.sidebar.selectbox("請選擇要刪除的行程：", list(delete_options.keys()))
        delete_button = st.sidebar.button("❌ 確定刪除這筆行程", use_container_width=True)
        
        if delete_button:
            target_id = delete_options[selected_del_text]
            st.session_state.events = [e for e in st.session_state.events if e["id"] != target_id]
            st.rerun()
    else:
        st.sidebar.write("目前沒有行程可供刪除")


# 右側主畫面：分類顯示行事曆
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("<h2>🎵 樂團事務行程</h2>", unsafe_allow_html=True)
    for ev in sorted([e for e in st.session_state.events if e["分類"] == "🎵 樂團事務"], key=lambda x: x["日期"]):
        st.markdown(f'<div class="event-card band-style"><strong>【{ev["日期"]}】 {ev["時間"]}</strong><br>📌 {ev["內容"]}</div>', unsafe_allow_html=True)

with col2:
    st.markdown("<h2>🏡 個人生活行程</h2>", unsafe_allow_html=True)
    for ev in sorted([e for e in st.session_state.events if e["分類"] == "🏡 個人生活"], key=lambda x: x["日期"]):
        st.markdown(f'<div class="event-card personal-style"><strong>【{ev["日期"]}】 {ev["時間"]}</strong><br>📌 {ev["內容"]}</div>', unsafe_allow_html=True)
