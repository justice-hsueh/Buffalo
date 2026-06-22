import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import base64
import json

# 設定網頁標題與整體風格
st.set_page_config(page_title="大竹國小兒童樂隊行事曆", layout="wide")

# 設定資料儲存的檔案路徑
DATA_FILE = "events.json"
CONFIG_FILE = "config.json"

# --- 密碼與設定檔管理機制（最高優先權防護版） ---
def load_admin_password():
    # 這裡直接鎖定老師手動修改的專屬密碼
    MY_PASSWORD = "dccb" 
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                file_pwd = config.get("admin_password", MY_PASSWORD)
                # 防呆：如果硬碟檔案裡是舊的 dzor，但程式碼已經改了，強制更新為老師的新密碼
                if file_pwd == "dzor" and MY_PASSWORD != "dzor":
                    return MY_PASSWORD
                return file_pwd
        except:
            pass
            
    # 如果檔案不存在，自動建立並寫入老師設定的密碼
    default_config = {"admin_password": MY_PASSWORD}
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)
    except:
        pass
    return MY_PASSWORD

def save_admin_password(new_password):
    config = {"admin_password": new_password}
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

# 載入當前鎖定的密碼
ADMIN_PASSWORD = load_admin_password()

# 讀取行程檔案資料的函式
def load_events():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    # 預設範例資料（這裡已先示範一個日期範圍的輸入樣式）
    return [
        {"id": 1, "日期": "2026-06-25", "分類": "✨ 演出活動", "時間": "13:30 - 15:30", "地點": "學校活動中心", "內容": "年度期末發表會\n注意：各分部樂譜需收齊\n請記得攜帶個人講義"},
        {"id": 2, "日期": "2026-06-26", "分類": "🥁 每日進度", "時間": "晨課時間", "內容": "打擊與鍵盤分部練習基本功\n加強弱奏節段的穩定度"},
        {"id": 3, "日期": "2026-06-29 ~ 2026-07-03", "分類": "📢 通知事項", "時間": "全天", "內容": "暑假自主複習週\n放學請大家把樂器和講義帶回家練習\n注意開學後的團練時間"},
    ]

# 儲存資料到檔案的函式
def save_events(events):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=4)

# 關鍵輔助函式：根據文字內容自動分配最適合的圖示
def get_smart_icon(text):
    text_lower = text.lower()
    if any(keyword in text_lower for keyword in ["譜", "歌", "樂譜", "演奏"]):
        return "🎼"
    elif any(keyword in text_lower for keyword in ["帶", "拿", "備", "準備", "攜帶"]):
        return "🎒"
    elif any(keyword in text_lower for keyword in ["注意", "務必", "記得", "重要", "切記"]):
        return "⚠️"
    elif any(keyword in text_lower for keyword in ["服", "穿", "衣", "團服"]):
        return "👕"
    else:
        return "📌"

# 關鍵輔助函式：將純文字清單渲染成精美的多項目 HTML 清單
def render_content_items(lines_list):
    html_output = ""
    for line in lines_list:
        if line.strip():
            icon = get_smart_icon(line)
            html_output += f'<div style="margin-bottom: 6px; display: flex; align-items: flex-start; gap: 8px;"><span>{icon}</span><span>{line}</span></div>'
    return html_output

# 排序輔助函式：不論是單一日期或日期範圍，一律抓最前面的那一天來當作排序基準
def get_sort_date(date_str):
    try:
        # 如果是範圍 "2026-06-29 ~ 2026-07-03"，切開並抓第一個
        first_part = date_str.split("~")[0].strip()
        return datetime.strptime(first_part, "%Y-%m-%d").date()
    except:
        return date.max

# 套用自訂 CSS
st.markdown("""
    <style>
    html, body, [data-testid="stWidgetLabel"] p, .stSelectbox, .stDateInput {
        font-size: 20px !important; font-weight: 500 !important;
    }
    h2 { font-size: 32px !important; font-weight: bold !important; color: #0D9488; }
    h3 { font-size: 26px !important; font-weight: bold !important; }
    .stButton>button { font-size: 22px !important; padding: 10px 24px !important; color: white !important; }
    .countdown-box {
        background-color: #FEF3C7; padding: 20px; border-radius: 12px; border-left: 8px solid #F59E0B;
        font-size: 28px !important; font-weight: bold; margin-bottom: 25px;
    }
    .event-card { padding: 15px 20px; border-radius: 8px; margin-bottom: 12px; font-size: 22px !important; }
    .show-style { background-color: #E0F2FE; border-left: 6px solid #0EA5E9; color: #0369A1; }
    .progress-style { background-color: #E2F0D9; border-left: 6px solid #70AD47; color: #385723; }
    .notice-style { background-color: #FCE8E6; border-left: 6px solid #EA4335; color: #A51D12; }
    div[data-testid="stForm"] { background-color: #F3F4F6; padding: 20px; border-radius: 10px; }
    
    .custom-title-container { display: flex; align-items: flex-end; gap: 15px; margin-top: 10px; margin-bottom: 30px; padding-bottom: 5px; }
    .custom-title-logo { width: 80px; height: auto; display: block; transform: translateY(6px); }
    .rainbow-text {
        font-size: 42px !important; font-weight: bold !important; line-height: 1.0 !important;
        margin: 0 !important; padding: 0 !important;
        background: linear-gradient(to right, #E53E3E, #ED8936, #ECC94B, #48BB78, #3182CE, #000080, #9F7AEA);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; color: transparent;
    }
    .show-title-text { font-size: 24px !important; font-weight: bold !important; color: #1E40AF; margin-bottom: 8px; }
    .show-meta-text { font-size: 19px !important; color: #475569; line-height: 1.5; }
    </style>
""", unsafe_allow_html=True)

# 檢查 Logo
logo_file = None
for name in ["logo.jpg", "logo.JPG", "logo.png", "logo.PNG", "logo.jpeg"]:
    if os.path.exists(name):
        logo_file = name
        break

# --- 標題與 Logo 渲染 ---
if logo_file:
    try:
        with open(logo_file, "rb") as f:
            data = f.read()
            encoded = base64.b64encode(data).decode()
        st.markdown(f"""
            <div class="custom-title-container">
                <img class="custom-title-logo" src="data:image/jpeg;base64,{encoded}">
                <span class="rainbow-text">大竹國小兒童樂隊行事曆</span>
            </div>
        """, unsafe_allow_html=True)
    except:
        st.markdown('<h1 class="rainbow-text">大竹國小兒童樂隊行事曆</h1>', unsafe_allow_html=True)
else:
    st.markdown("""
        <div class="custom-title-container">
            <span style="font-size: 42px; line-height: 1; transform: translateY(2px);">🎵</span>
            <span class="rainbow-text">大竹國小兒童樂隊行事曆</span>
        </div>
    """, unsafe_allow_html=True)

# 載入最新行程
if 'events' not in st.session_state:
    st.session_state.events = load_events()

if 'target_date' not in st.session_state:
    st.session_state.target_date = date(2026, 7, 10)
if 'target_title' not in st.session_state:
    st.session_state.target_title = "重要樂團活動"

# 倒數顯示
t_date = datetime.combine(st.session_state.target_date, datetime.min.time())
today = datetime.now()
days_left = (t_date - today).days + 1

if days_left >= 0:
    st.markdown(f'<div class="countdown-box">⏰ 距離 <span style="color: #1E3A8A;">{st.session_state.target_title}（{st.session_state.target_date.strftime("%Y/%m/%d")}）</span> 還有 <span style="font-size: 36px; color: #DC2626;">{days_left}</span> 天</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="countdown-box">🎉 {st.session_state.target_title} 已圓滿完成！</div>', unsafe_allow_html=True)

# 管理控制台
st.sidebar.markdown("<h2>⚙️ 管理員控制台</h2>", unsafe_allow_html=True)
password_input = st.sidebar.text_input("🔑 請輸入管理密碼：", type="password")

if password_input == ADMIN_PASSWORD:
    st.sidebar.success("🔓 密碼正確！已開啟編輯權限")
    st.sidebar.markdown("---")
    
    st.sidebar.markdown("<h3>🔐 安全設定</h3>", unsafe_allow_html=True)
    with st.sidebar.form("password_form"):
        new_pwd_input = st.text_input("設定全新管理密碼", type="password")
        confirm_pwd_button = st.form_submit_button("💾 確認變更密碼")
        if confirm_pwd_button and new_pwd_input:
            save_admin_password(new_pwd_input)
            st.sidebar.success("密碼已安全寫入資料庫！將自動重新載入...")
            st.rerun()

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
        
        # 核心改動：讓老師自己決定是要選單一日子，還是點擊按鈕切換成文字輸入一段期間
        date_mode = st.sidebar.selectbox("日期輸入方式：", ["📅 選擇單一日曆天", "✍️ 手動輸入日期範圍 (例如一段時間)"])
        
        with st.sidebar.form("add_form", clear_on_submit=True):
            if date_mode == "📅 選擇單一日曆天":
                chosen_date = st.date_input("選擇日期")
                final_date_str = str(chosen_date)
            else:
                final_date_str = st.text_input("請輸入日期範圍說明", placeholder="例如：2026-06-29 ~ 2026-07-03")
                
            new_category = st.selectbox("選擇分類", categories)
            new_time = st.text_input("輸入時間")
            new_location = st.text_input("🏠 輸入演出地點 (例如：演藝廳)") if new_category == "✨ 演出活動" else ""
            
            if new_category == "✨ 演出活動":
                new_content = st.text_area("行程備忘（注意：第一行會自動變成演出大標題）：")
            else:
                new_content = st.text_area("行程備忘 / 準備事項（換行可分成多個圖示項目）：")
                
            submit_button = st.form_submit_button("確認加入行事曆")
            
            if submit_button and new_content and final_date_str:
                new_id = max([e["id"] for e in st.session_state.events]) + 1 if st.session_state.events else 1
                event_data = {"id": new_id, "日期": final_date_str, "分類": new_category, "時間": new_time, "內容": new_content}
                if new_category == "✨ 演出活動":
                    event_data["地點"] = new_location if new_location else "未定"
                
                st.session_state.events.append(event_data)
                save_events(st.session_state.events)
                st.rerun()

    # 修改行程
    elif mode == "✏️ 修改行程":
        st.sidebar.markdown("<h3>✏️ 修改現有行程</h3>", unsafe_allow_html=True)
        if st.session_state.events:
            edit_options = {f"【{e['日期']}】{e['分類'][:2]} - {e['內容'].splitlines()[0][:10]}...": e for e in st.session_state.events}
            selected_text = st.sidebar.selectbox("請選擇要修改的行程：", list(edit_options.keys()))
            selected_event = edit_options[selected_text]
            
            with st.sidebar.form("edit_form"):
                updated_date_str = st.text_input("修改日期 / 範圍說明", selected_event["日期"])
                curr_cat_idx = categories.index(selected_event["分類"]) if selected_event["分類"] in categories else 0
                updated_category = st.selectbox("修改分類", categories, index=curr_cat_idx)
                updated_time = st.text_input("修改時間", selected_event["時間"])
                updated_location = st.text_input("🏠 修改演出地點", selected_event.get("地點", "未定")) if updated_category == "✨ 演出活動" else ""
                updated_content = st.text_area("修改行程備忘", selected_event["內容"])
                edit_submit = st.form_submit_button("💾 確認修改並儲存")
                
                if edit_submit:
                    for e in st.session_state.events:
                        if e["id"] == selected_event["id"]:
                            e["日期"] = updated_date_str
                            e["分類"] = updated_category
                            e["時間"] = updated_time
                            e["內容"] = updated_content
                            if updated_category == "✨ 演出活動":
                                e["地點"] = updated_location if updated_location else "未定"
                            elif "地點" in e:
                                del e["地點"]
                    save_events(st.session_state.events)
                    st.rerun()
        else:
            st.sidebar.write("目前沒有行程可供修改")

    # 刪除行程
    elif mode == "🗑️ 刪除行程":
        st.sidebar.markdown("<h3>🗑️ 刪除現有行程</h3>", unsafe_allow_html=True)
        if st.session_state.events:
            delete_options = {f"【{e['日期']}】{e['時間']} - {e['內容'].splitlines()[0][:10]}...": e["id"] for e in st.session_state.events}
            selected_del_text = st.sidebar.selectbox("請選擇要刪除的行程：", list(delete_options.keys()))
            delete_button = st.sidebar.button("❌ 確定刪除這筆行程", use_container_width=True)
            
            if delete_button:
                target_id = delete_options[selected_del_text]
                st.session_state.events = [e for e in st.session_state.events if e["id"] != target_id]
                save_events(st.session_state.events)
                st.rerun()
else:
    if password_input:
        st.sidebar.error("🔒 密碼錯誤，請重新輸入。")
    else:
        st.sidebar.info("💡 請在上方輸入密碼以解鎖修改功能。")

# 右側主畫面呈現（導入智慧排序）
col1, col2, col3 = st.columns([1, 1, 1])

# --- 欄位 1：✨ 演出活動 ---
with col1:
    st.markdown("<h2>✨ 演出活動</h2>", unsafe_allow_html=True)
    show_events = [e for e in st.session_state.events if e["分類"] == "✨ 演出活動"]
    for ev in sorted(show_events, key=lambda x: get_sort_date(x["日期"])):
        lines = [line.strip() for line in ev["內容"].split("\n") if line.strip()]
        act_name = lines[0] if lines else "未命名活動"
        desc_lines = lines[1:] if len(lines) > 1 else []
        items_html = render_content_items(desc_lines)
        
        st.markdown(f"""
            <div class="event-card show-style">
                <div class="show-title-text">🎵 {act_name}</div>
                <div class="show-meta-text">
                    📅 <b>日期：</b>{ev["日期"]}<br>
                    ⏰ <b>時間：</b>{ev["時間"]}<br>
                    🏠 <b>地點：</b>{ev.get("地點", "未定")}
                </div>
                <hr style="margin: 12px 0; border: 0; border-top: 1px dashed #0EA5E9;">
                <div>{items_html}</div>
            </div>
        """, unsafe_allow_html=True)

# --- 欄位 2：🥁 每日進度 ---
with col2:
    st.markdown("<h2>🥁 每日進度</h2>", unsafe_allow_html=True)
    prog_events = [e for e in st.session_state.events if e["分類"] == "🥁 每日進度"]
    for ev in sorted(prog_events, key=lambda x: get_sort_date(x["日期"])):
        lines = [line.strip() for line in ev["內容"].split("\n") if line.strip()]
        items_html = render_content_items(lines)
        st.markdown(f'<div class="event-card progress-style"><strong>📅 【{ev["日期"]}】</strong><br>⏰ <b>時間：</b>{ev["時間"]}<br><hr style="margin: 8px 0; border: 0; border-top: 1px dashed #70AD47;">{items_html}</div>', unsafe_allow_html=True)

# --- 欄位 3：📢 通知事項 ---
with col3:
    st.markdown("<h2>📢 通知事項</h2>", unsafe_allow_html=True)
    notice_events = [e for e in st.session_state.events if e["分類"] == "📢 通知事項"]
    for ev in sorted(notice_events, key=lambda x: get_sort_date(x["日期"])):
        lines = [line.strip() for line in ev["內容"].split("\n") if line.strip()]
        items_html = render_content_items(lines)
        st.markdown(f'<div class="event-card notice-style"><strong>📅 【{ev["日期"]}】</strong><br>⏰ <b>時間：</b>{ev["時間"]}<br><hr style="margin: 8px 0; border: 0; border-top: 1px dashed #EA4335;">{items_html}</div>', unsafe_allow_html=True)
