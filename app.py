import streamlit as st
import chat_api
import time

st.set_page_config(page_title="Phòng trò chuyện Đa tài khoản", page_icon="💬", layout="centered")

# --- KHỞI TẠO DỮ LIỆU TỪ GIST ---
if "accounts_loaded" not in st.session_state:
    chat_api.load_accounts()
    st.session_state.accounts_loaded = True
    st.session_state.accounts_data = chat_api.ACCOUNTS_CREDENTIALS

# Khởi tạo cấu hình động mặc định cho từng Username
if "account_settings" not in st.session_state:
    st.session_state.account_settings = {}
    for acc in st.session_state.accounts_data:
        username = acc.get('send_usename', 'unknown')
        st.session_state.account_settings[username] = {
            "send_name": "Doãn",
            "send_image": "",
            "chanel_id": "100000005",
            "type": "0",
            "emoji_id": "",
            "attachments": ""
        }

# Hộp chứa tin nhắn tạm thời hiển thị lập tức
if "temp_messages" not in st.session_state:
    st.session_state.temp_messages = []

# Khởi tạo danh sách bộ nhớ ẩn các tin nhắn đã nhấn Clear
if "cleared_messages" not in st.session_state:
    st.session_state.cleared_messages = set()

dark_mode = False

st.title("💬 Phòng trò chuyện Đa tài khoản")
st.markdown("---")

# --- KHU VỰC ĐIỀU KHIỂN CHÍNH (Ở GIỮA) ---
if st.session_state.accounts_data:
    account_names = [f"Acc {i+1} ({acc.get('send_usename', '...')})" for i, acc in enumerate(st.session_state.accounts_data)]
    
    # Chia thêm cột col5 để đặt nút Clear tin nhắn
    col1, col2, col3, col4, col5 = st.columns([3.5, 1.2, 1.8, 0.7, 0.7])
    
    with col1:
        selected_acc_name = st.selectbox("Chọn tài khoản hoạt động:", account_names)
        idx = account_names.index(selected_acc_name)
        cred = st.session_state.accounts_data[idx]
        username = cred.get('send_usename', 'unknown')
        current_chanel = st.session_state.account_settings[username]["chanel_id"]
        
    with col2:
        st.markdown("<div style='padding-top: 35px;'></div>", unsafe_allow_html=True)
        anonymous = st.checkbox("Ẩn danh", value=True)
        
    with col3:
        st.markdown("<div style='padding-top: 35px;'></div>", unsafe_allow_html=True)
        dark_mode = st.checkbox("Chế độ tối 🌙", value=False)
        
    with col4:
        st.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🔄", help="Đồng bộ dữ liệu mới từ Gist"):
            chat_api.load_accounts()
            st.session_state.accounts_data = chat_api.ACCOUNTS_CREDENTIALS
            st.rerun()

    with col5:
        st.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🗑️", help="Xóa sạch toàn bộ tin nhắn trên màn hình hiện tại"):
            # Lấy toàn bộ tin nhắn hiện tại để đưa vào danh sách đen cần ẩn đi
            current_msgs = chat_api.fetch_msgs(current_chanel)
            for m in current_msgs:
                msg_key = f"{m.get('sender_name', '')}_{m.get('message', '')}"
                st.session_state.cleared_messages.add(msg_key)
            # Xóa luôn cả tin nhắn tạm thời đang chờ
            st.session_state.temp_messages = []
            st.toast("🧹 Đã làm sạch màn hình trò chuyện!")
            time.sleep(0.5)
            st.rerun()

    # --- THANH CÀI ĐẶT BÊN TRÁI (SIDEBAR) GỌN GÀNG NGOẠI CỠ ---
    with st.sidebar:
        st.subheader(f"⚙️ Cài đặt Payload ({username})")
        
        current_settings = st.session_state.account_settings[username]
        
        with st.form("payload_form"):
            new_name = st.text_input("Tên hiển thị:", value=current_settings["send_name"])
            new_image = st.text_input("Link Avatar (URL):", value=current_settings["send_image"])
            new_chanel = st.text_input("Chanel ID:", value=current_settings["chanel_id"])
            new_type = st.text_input("Type:", value=current_settings["type"])
            new_emoji = st.text_input("Emoji ID:", value=current_settings["emoji_id"])
            new_attachments = st.text_input("Link hình ảnh/File đính kèm:", value=current_settings["attachments"])
            
            submit_button = st.form_submit_button("Áp dụng thay đổi 💾", use_container_width=True)
            
            if submit_button:
                st.session_state.account_settings[username] = {
                    "send_name": new_name,
                    "send_image": new_image,
                    "chanel_id": new_chanel,
                    "type": new_type,
                    "emoji_id": new_emoji,
                    "attachments": new_attachments
                }
                st.toast("🎯 Đã áp dụng cấu hình mới thành công!")
                time.sleep(0.5)
                st.rerun()

    # --- ĐOẠN ĐIỀU CHỈNH KÍCH THƯỚC SIDEBAR TOÀN CỤC ---
    st.markdown("""
        <style>
        /* Mở rộng chiều rộng Sidebar sang bên phải thành 400px */
        section[data-testid="stSidebar"] {
            width: 400px !important;
            min-width: 400px !important;
        }
        /* Đẩy nội dung Sidebar lên sát đỉnh */
        div[data-testid="stSidebarUserContent"] {
            padding-top: 0.8rem !important;
            padding-bottom: 0rem !important;
        }
        /* Nén khoảng cách các ô nhập trong Form */
        div[data-testid="stForm"] {
            padding: 10px !important;
        }
        div[data-testid="stForm"] [data-testid="stVerticalBlock"] > div {
            padding-bottom: 2px !important;
            margin-bottom: 0px !important;
        }
        div[data-testid="stForm"] label {
            margin-bottom: 1px !important;
            padding-bottom: 0px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- ÁP DỤNG MÀU SẮC KHI BẬT CHẾ ĐỘ TỐI ---
    if dark_mode:
        st.markdown("""
            <style>
            html, body, .stApp, 
            div[data-testid="stAppViewContainer"], 
            section[data-testid="stMain"], 
            section[data-testid="stSidebar"],
            section[data-testid="stSidebar"] > div {
                background-color: #0E1117 !important;
                color: #C9D1D9 !important;
            }
            h1, h2, h3, label, summary, section[data-testid="stSidebar"] stMarkdown {
                color: #F0F6FC !important;
            }
            div[data-testid="stForm"], input, select {
                background-color: #161B22 !important;
                color: #F0F6FC !important;
                border: 1px solid #30363D !important;
            }
            
            /* Sửa nút bấm Áp dụng trong Form tối màu rõ chữ */
            div[data-testid="stForm"] button, 
            button[data-testid*="FormSubmit"], 
            button[data-testid*="secondaryFormSubmit"] {
                background-color: #21262D !important;
                color: #F0F6FC !important;
                border: 1px solid #30363D !important;
            }
            div[data-testid="stForm"] button:hover {
                background-color: #30363D !important;
                border-color: #8b949e !important;
            }
            
            /* ÉP KHUNG CHAT VÀ TIN NHẮN GIỮ MÀU SÁNG */
            div[data-testid="stChatMessage"] {
                background-color: #F0F2F6 !important;
                border: 1px solid #E2E8F0 !important;
                border-radius: 8px !important;
            }
            div[data-testid="stChatMessage"] *, 
            div[data-testid="stChatMessage"] p, 
            div[data-testid="stChatMessage"] span,
            div[data-testid="stChatMessage"] strong {
                color: #1E293B !important;
            }
            
            /* ÉP DẢI BĂNG ĐÁY MÀU TỐI - XÓA NỀN TRẮNG RÌA */
            div[data-testid="stBottom"], 
            div[data-testid="stBottom"] > div, 
            div[data-testid="stBottomBlockContainer"] {
                background-color: #0E1117 !important;
                background: #0E1117 !important;
            }
            
            /* KHUNG Ô NHẬP LIỆU GIỮ MÀU SÁNG */
            div[data-testid="stChatInput"] {
                background-color: #FFFFFF !important;
                border: 1px solid #CBD5E1 !important;
            }
            div[data-testid="stChatInput"] textarea {
                color: #0F172A !important;
            }
            div[data-testid="stChatInput"] button {
                background-color: #F1F5F9 !important;
                color: #0F172A !important;
            }
            </style>
        """, unsafe_allow_html=True)

else:
    st.error("Không tìm thấy dữ liệu tài khoản từ Gist!")
    st.stop()

st.markdown("---")

# --- KHU VỰC HIỂN THỊ TIN NHẮN TỰ ĐỘNG CẬP NHẬT REAL-TIME ---
@st.fragment(run_every="3s")
def render_chat_window(chanel_id, my_username, my_send_name):
    messages = chat_api.fetch_msgs(chanel_id)
    
    # [TÍNH NĂNG 2] Lọc bỏ các tin nhắn cũ đã nằm trong danh sách bấm nút Clear
    messages = [m for m in messages if f"{m.get('sender_name', '')}_{m.get('message', '')}" not in st.session_state.cleared_messages]
    
    # [TÍNH NĂNG 1] TỰ ĐỘNG CẮT BỚT: Chỉ giữ lại đúng 30 tin nhắn mới nhất để chống lag web
    messages = messages[-30:]
    
    server_texts = [m.get('message', '') for m in messages]
    st.session_state.temp_messages = [t for t in st.session_state.temp_messages if t['message'] not in server_texts]
    
    chat_container = st.container(height=400)
    with chat_container:
        if messages:
            for m in reversed(messages): 
                sender = m.get('sender_name', 'Ẩn danh')
                msg_text = m.get('message', '')
                
                if my_username in sender or sender == my_send_name:
                    with st.chat_message("user"):
                        st.write(f"**Bạn ({my_username}):** {msg_text}")
                else:
                    with st.chat_message("assistant"):
                        st.write(f"**{sender}:** {msg_text}")
        
        for t in st.session_state.temp_messages:
            if t['username'] == my_username:
                with st.chat_message("user"):
                    st.write(f"**Bạn ({my_username}):** {t['message']}")
                    
        if not messages and not st.session_state.temp_messages:
            st.info("Chưa có tin nhắn nào hoặc màn hình vừa được dọn sạch.")

# Gọi hàm hiển thị khung chat
current_chanel = st.session_state.account_settings[username]["chanel_id"]
render_chat_window(current_chanel, username, st.session_state.account_settings[username]["send_name"])

# --- Ô NHẬP TIN NHẮN CHUẨN WEB TELEGRAM ---
if msg_input := st.chat_input("Nhập tin nhắn và nhấn Enter..."):
    current_settings = st.session_state.account_settings[username]
    
    st.session_state.temp_messages.append({
        "username": username,
        "message": msg_input
    })
    
    chat_api.send_msg(msg_input, cred, current_settings, anonymous)
    
    st.toast("🚀 Gửi tin nhắn thành công!")
    st.rerun()
