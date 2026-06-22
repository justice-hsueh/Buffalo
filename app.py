import streamlit as st
import pandas as pd
from datetime import datetime, date

# 設定網頁標題與整體風格
st.set_page_config(page_title="大竹國小兒童樂隊行事曆", layout="wide")

# 套用自訂 CSS：全面放大字體與美化卡片風格
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
    .show-style { background-color: #E0F2FE; border-left: 6px solid #0EA5E9; color: #0369A1; }
    .progress-style { background-color: #E2F0D9; border-left: 6px solid #70AD47; color: #385723; }
    .notice-style { background-color: #FCE8E6; border-left: 6px solid #EA4335; color: #A51D12; }
    div[data-testid="stForm"] { background-color: #F3F4F6; padding: 20px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# 標題
st.title("🪗 大竹國小兒童樂隊行事曆")

# 初始化記憶體資料
if 'events' not in st.session_state:
    st.session_state.events = [
        {"id": 1, "日期": "2026-06-25", "分類": "✨ 演出活動", "時間": "13:30 - 15:30", "地點": "學校活動中心", "內容": "全團總排練（注意：分部樂譜需收齊）"},
        {"id": 2, "日期": "2026-06-26", "分類": "🥁 每日進度", "時間": "晨課時間", "地點": "音樂教室", "內容": "打擊與鍵盤分部練習基本功"},
        {"id": 3, "日期": "2026-06-27", "分類": "📢 通知事項", "時間": "全天", "地點": "各自家中", "內容": "請大家記得帶樂器與個人講義回家複習"},
    ]

if 'target_date' not in st.session_state:
    st.session_state.target_date = date(2026, 7, 10)
if 'target_title' not in st.session_state:
    st.session_state.target_title = "重要樂團活動"

# 重大活動倒數顯示
t_date = datetime.combine(st.session_state.target_date, datetime.min.time())
today = datetime.now()
days_left = (t_date - today).days + 1

if days_left >= 0:
    st.markdown(f'<div class="countdown-box">⏰ 距離 <span style="color: #1E3A8A;">{st.session_state.target_title}（{st.session_state.target_date.strftime("%Y/%m/%d")}）</span> 還有 <span style="font-size: 36px; color: #DC2626;">{days_left}</span> 天</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="countdown-box">🎉 {st.session_state.target_title} 已圓滿完成！</div>', unsafe_allow_html=True)

# 側邊欄密碼驗證鎖
st.sidebar.markdown("<h2>⚙️ 管理員控制台</h2>", unsafe_allow_html=True)

ADMIN_PASSWORD = "dzor" 
password_input = st.sidebar.text_input("🔑 請輸入管理密碼：", type="password")

if password_input == ADMIN_PASSWORD:
    st.sidebar.success("🔓 密碼正確！已開啟編輯權限")
    st.sidebar.markdown("---")
    
    # 設定倒數活動
    st.sidebar.markdown("<h3>🎯 設定倒數活動</h3>", unsafe_allow_html=True)
    with st.sidebar.form("countdown_form"):
        set_title = st.text_input("活動名稱", st.session_state.target_title)
        set_date = st.date_input("活動日期", st.session_state.target_date)
        save_cd = st.form_submit_button("儲存倒數設定")
        if save_cd:
            st.session_state.target_title = set_title
            st.session_state.target_date = set_date
            st.rerun()
            
    st.sidebar.markdown("---")
    mode = st.sidebar.radio("請選擇操作項目：", ["➕ 新增行程", "✏️ 修改行程", "🗑️ 刪除行程"])
    categories = ["✨ 演出活動", "🥁 每日進度", "📢 通知事項"]
    
    # 新增行程
    if mode == "➕ 新增行程":
        st.sidebar.markdown("<h3>➕ 新增新行程</h3>", unsafe_allow_html=True)
        with st.sidebar.form("add_form", clear_on_submit=True):
            new_date = st.date_input("選擇日期")
            new_category = st.selectbox("選擇分類", categories)
            new_time = st.text_input("輸入時間")
            new_location = st.text_input("輸入地點 (例如：音樂教室)")
            new_content = st.text_area("行程備忘 / 準備事項")
            submit_button = st.form_submit_button("確認加入行事曆")
            
            if submit_button and new_content:
                new_id = max([e["id"] for e in st.session_state.events]) + 1 if st.session_state.events else 1
                st.session_state.events.append({
                    "id": new_id, "日期": str(new_date), "分類": new_category, "時間": new_time, "地點": new_location if new_location else "未定", "內容": new_content
                })
                st.rerun()

    # 修改行程
    elif mode == "✏️ 修改行程":
        st.sidebar.markdown("<h3>✏️ 修改現有行程</h3>", unsafe_allow_html=True)
        if st.session_state.events:
            edit_options = {f"【{e['日期']}】{e['分類'][:2]} - {e['內容'][:10]}...": e for e in st.session_state.events}
            selected_text = st.sidebar.selectbox("請選擇要修改的行程：", list(edit_options.keys()))
            selected_event = edit_options[selected_text]
            
            with st.sidebar.form("edit_form"):
                curr_date = datetime.strptime(selected_event["["日期"]"], "%Y-%m-%d") if isinstance(selected_event["日期"], str) else selected_event["日期"]
                updated_date = st.date_input("修改日期", curr_date)
                curr_cat_idx = categories.index(selected_event["分類"]) if selected_event["分類"] in categories else 0
                updated_category = st.selectbox("修改分類", categories, index=curr_cat_idx)
                updated_time = st.text_input("修改時間", selected_event["時間"])
                updated_location = st.text_input("修改地點", selected_event.get("地點", ""))
                updated_content = st.text_area("修改行程備忘", selected_event["內容"])
                edit_submit = st.form_submit_button("💾 確認修改並儲存")
                
                if edit_submit:
                    for e in st.session_state.events:
                        if e["id"] == selected_event["id"]:
                            e["日期"] = str(updated_date)
                            e["分類"] = updated_category
                            e["時間"] = updated_time
                            e["地點"] = updated_location if updated_location else "未定"
                            e["內容"] = updated_content
                    st.rerun()
        else:
            st.sidebar.write("目前沒有行程可供修改")

    # 刪除行程
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
else:
    if password_input:
        st.sidebar.error("🔒 密碼錯誤，請重新輸入。")
    else:
        st.sidebar.info("💡 請在上方輸入密碼以解鎖修改與倒數自訂功能。未輸入密碼時，他人僅能瀏覽行程。")

# 右側主畫面：3 欄排列
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown("<h2>✨ 演出活動</h2>", unsafe_allow_html=True)
    show_events = [e for e in st.session_state.events if e["分類"] == "✨ 演出活動"]
    for ev in sorted(show_events, key=lambda x: x["日期"]):
        st.markdown(f'<div class="event-card show-style"><strong>📅 【{ev["日期"]}】</strong><br>⏰ <b>時間：</b>{ev["時間"]}<br>📍 <b>地點：</b>{ev.get("地點", "未定")}<br><hr style="margin: 8px 0; border: 0; border-top: 1px dashed #0EA5E9;">📌 {ev["內容"]}</div>', unsafe_allow_html=True)

with col2:
    st.markdown("<h2>🥁 每日進度</h2>", unsafe_allow_html=True)
    progress_events = [e for e in st.session_state.events if e["分類"] == "🥁 每日進度"]
    for ev in sorted(progress_events, key=lambda x: x["日期"]):
        st.markdown(f'<div class="event-card progress-style"><strong>📅 【{ev["日期"]}】</strong><br>⏰ <b>時間：</b>{ev["時間"]}<br>📍 <b>地點：</b>{ev.get("地點", "未定")}<br><hr style="margin: 8px 0; border: 0; border-top: 1px dashed #70AD47;">📌 {ev["內容"]}</div>', unsafe_allow_html=True)

with col3:
    st.markdown("<h2>📢 通知事項</h2>", unsafe_allow_html=True)
    notice_events = [e for e in st.session_state.events if e["分類"] == "📢 通知事項"]
    for ev in sorted(notice_events, key=lambda x: x["日期"]):
        st.markdown(f'<div class="event-card notice-style"><strong>📅 【{ev["日期"]}】</strong><br>⏰ <b>時間：</b>{ev["時間"]}<br>📍 <b>地點：</b>{ev.get("地點", "未定")}<br><hr style="margin: 8px 0; border: 0; border-top: 1px dashed #EA4335;">📌 {ev["內容"]}</div>', unsafe_allow_html=True)
