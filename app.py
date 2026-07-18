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

# Hộp chứa tin nhắn tạm thời để hiển thị LẬP TỨC lên màn hình khi vừa nhấn Enter
if "temp_messages" not in st.session_state:
    st.session_state.temp_messages = []

st.title("💬 Phòng trò chuyện Đa tài khoản")
st.markdown("---")

# --- KHU VỰC ĐIỀU KHIỂN CHÍNH TRÊN TRANG CHÍNH ---
if st.session_state.accounts_data:
    account_names = [f"Acc {i+1} ({acc.get('send_usename', '...')})" for i, acc in enumerate(st.session_state.accounts_data)]
    
    col1, col2, col3 = st.columns([5, 2, 1])
    
    with col1:
        selected_acc_name = st.selectbox("Chọn tài khoản hoạt động:", account_names)
        idx = account_names.index(selected_acc_name)
        cred = st.session_state.accounts_data[idx]
        username = cred.get('send_usename', 'unknown')
        
    with col2:
        st.markdown("<div style='padding-top: 35px;'></div>", unsafe_allow_html=True)
        anonymous = st.checkbox("Ẩn danh", value=True)
        
    with col3:
        st.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🔄", help="Đồng bộ dữ liệu mới từ Gist"):
            chat_api.load_accounts()
            st.session_state.accounts_data = chat_api.ACCOUNTS_CREDENTIALS
            st.rerun()

    # --- HỘP THOẠI CÀI ĐẶT PAYLOAD ---
    with st.expander("⚙️ Tùy chỉnh nâng cao Payload (Tên, Ảnh, Chanel, File đính kèm...)"):
        settings = st.session_state.account_settings[username]
        
        settings["send_name"] = st.text_input("Tên hiển thị:", value=settings["send_name"])
        settings["send_image"] = st.text_input("Link Avatar (URL):", value=settings["send_image"])
        settings["chanel_id"] = st.text_input("Chanel ID:", value=settings["chanel_id"])
        settings["type"] = st.text_input("Type:", value=settings["type"])
        settings["emoji_id"] = st.text_input("Emoji ID:", value=settings["emoji_id"])
        settings["attachments"] = st.text_input("Link hình ảnh/File đính kèm:", value=settings["attachments"])
        
        st.session_state.account_settings[username] = settings
else:
    st.error("Không tìm thấy dữ liệu tài khoản từ Gist!")
    st.stop()

st.markdown("---")

# --- KHU VỰC HIỂN THỊ TIN NHẮN TỰ ĐỘNG CẬP NHẬT REAL-TIME ---
@st.fragment(run_every="3s")
def render_chat_window(chanel_id, my_username, my_send_name):
    # Lấy dữ liệu tin nhắn mới từ Lazi
    messages = chat_api.fetch_msgs(chanel_id)
    
    # Kiểm tra xem tin nhắn tạm thời nào đã được Lazi cập nhật thành công thì xóa khỏi hàng đợi tạm
    server_texts = [m.get('message', '') for m in messages]
    st.session_state.temp_messages = [t for t in st.session_state.temp_messages if t['message'] not in server_texts]
    
    chat_container = st.container(height=400)
    with chat_container:
        # 1. Hiển thị tin nhắn chính thức tải từ server về
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
        
        # 2. Hiển thị NGAY LẬP TỨC tin nhắn vừa ấn gửi (Trong khi chờ server Lazi load xong)
        for t in st.session_state.temp_messages:
            if t['username'] == my_username:
                with st.chat_message("user"):
                    st.write(f"**Bạn ({my_username}):** {t['message']}")
                    
        if not messages and not st.session_state.temp_messages:
            st.info("Chưa có tin nhắn nào hoặc Chanel ID không hợp lệ.")

# Gọi hàm hiển thị khung chat
current_chanel = st.session_state.account_settings[username]["chanel_id"]
render_chat_window(current_chanel, username, st.session_state.account_settings[username]["send_name"])

# --- Ô NHẬP TIN NHẮN CHUẨN WEB TELEGRAM ---
if msg_input := st.chat_input("Nhập tin nhắn và nhấn Enter..."):
    current_settings = st.session_state.account_settings[username]
    
    # Đút tin nhắn vào hàng đợi hiển thị tạm thời để UI cập nhật ngay tức thì
    st.session_state.temp_messages.append({
        "username": username,
        "message": msg_input
    })
    
    # Tiến hành gửi payload ngầm lên hệ thống Lazi
    chat_api.send_msg(msg_input, cred, current_settings, anonymous)
    
    st.toast("🚀 Gửi tin nhắn thành công!")
    st.rerun() # Kích hoạt vẽ lại màn hình để hiện tin nhắn tạm ngay lập tức
