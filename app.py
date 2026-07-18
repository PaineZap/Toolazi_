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

st.title("💬 Phòng trò chuyện Đa tài khoản")
st.markdown("---")

# --- KHU VỰC ĐIỀU KHIỂN CHÍNH (Ở GIỮA) ---
if st.session_state.accounts_data:
    account_names = [f"Acc {i+1} ({acc.get('send_usename', '...')})" for i, acc in enumerate(st.session_state.accounts_data)]
    
    # Rút gọn lại thành 4 cột gọn gàng sau khi bỏ Chế độ tối
    col1, col2, col3, col4 = st.columns([5.0, 1.5, 0.7, 0.7])
    
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
        st.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🔄", help="Đồng bộ dữ liệu mới từ Gist"):
            chat_api.load_accounts()
            st.session_state.accounts_data = chat_api.ACCOUNTS_CREDENTIALS
            st.rerun()

    with col4:
        st.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🗑️", help="Xóa sạch toàn bộ tin nhắn trên màn hình hiện tại"):
            current_msgs = chat_api.fetch_msgs(current_chanel)
            for m in current_msgs:
                msg_key = f"{m.get('sender_name', '')}_{m.get('message', '')}"
                st.session_state.cleared_messages.add(msg_key)
            st.session_state.temp_messages = []
            st.toast("🧹 Đã làm sạch màn hình trò chuyện!")
            time.sleep(0.5)
            st.rerun()

    # --- THANH CÀI ĐẶT BÊN TRÁI (SIDEBAR) GIỮ NGUYÊN LAYOUT TỐI ƯU ---
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

    # --- ĐIỀU CHỈNH KÍCH THƯỚC BỐ CỤC SIDEBAR (CHỈ GIỮ LẠI ĐỘ RỘNG VÀ CỰ LY, KHÔNG ÉP MÀU) ---
    st.markdown("""
        <style>
        /* Mở rộng chiều rộng Sidebar sang bên phải thành 400px để dễ nhìn */
        section[data-testid="stSidebar"] {
            width: 400px !important;
            min-width: 400px !important;
        }
        /* Đẩy nội dung Sidebar lên sát đỉnh để không cần cuộn chuột */
        div[data-testid="stSidebarUserContent"] {
            padding-top: 0.8rem !important;
            padding-bottom: 0rem !important;
        }
        /* Nén khoảng cách các ô nhập trong Form và kéo nút Áp dụng lên cao */
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

else:
    st.error("Không tìm thấy dữ liệu tài khoản từ Gist!")
    st.stop()

st.markdown("---")

# --- KHU VỰC HIỂN THỊ TIN NHẮN TỰ ĐỘNG CẬP NHẬT REAL-TIME ---
@st.fragment(run_every="3s")
def render_chat_window(chanel_id, my_username, my_send_name):
    messages = chat_api.fetch_msgs(chanel_id)
    
    # Lọc bỏ các tin nhắn cũ đã nằm trong danh sách bấm nút Clear
    messages = [m for m in messages if f"{m.get('sender_name', '')}_{m.get('message', '')}" not in st.session_state.cleared_messages]
    
    # TỰ ĐỘNG CẮT BỚT: Chỉ giữ lại đúng 30 tin nhắn mới nhất để chống lag web
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
