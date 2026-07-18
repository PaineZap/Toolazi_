import streamlit as st
import chat_api
import time

st.set_page_config(page_title="Phòng trò chuyện Đa tài khoản", page_icon="💬", layout="centered")

# --- KHỞI TẠO DỮ LIỆU TỪ GIST ---
if "accounts_loaded" not in st.session_state:
    chat_api.load_accounts()
    st.session_state.accounts_loaded = True
    st.session_state.accounts_data = chat_api.ACCOUNTS_CREDENTIALS

# Khởi tạo giá trị mặc định cho cấu hình động của từng Username
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

st.title("💬 Phòng trò chuyện Đa tài khoản")

# --- THANH ĐIỀU HƯỚNG SIDEBAR (THAY CHO CONTROL FRAME & POPUP) ---
st.sidebar.header("Cấu hình hệ thống")

if st.session_state.accounts_data:
    account_names = [f"Acc {i+1} ({acc.get('send_usename', '...')})" for i, acc in enumerate(st.session_state.accounts_data)]
    selected_acc_name = st.sidebar.selectbox("Chọn tài khoản hoạt động", account_names)
    
    # Lấy thông tin tài khoản đang chọn
    idx = account_names.index(selected_acc_name)
    cred = st.session_state.accounts_data[idx]
    username = cred.get('send_usename', 'unknown')
    
    # Trạng thái ẩn danh
    anonymous = st.sidebar.checkbox("Chế độ ẩn danh", value=True)
    
    # Nút đồng bộ thủ công từ Gist
    if st.sidebar.button("🔄 Đồng bộ dữ liệu Gist"):
        chat_api.load_accounts()
        st.session_state.accounts_data = chat_api.ACCOUNTS_CREDENTIALS
        st.rerun()
        
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Tùy chỉnh Payload")
    
    # Tạo các ô nhập liệu trực tiếp ở Sidebar thay thế cho Popup Toplevel cũ
    settings = st.session_state.account_settings[username]
    
    # Thiết lập tính năng xóa nhanh (Streamlit có sẵn nút x bên phải ô nhập liệu rất tiện)
    settings["send_name"] = st.text_input("Tên hiển thị:", value=settings["send_name"])
    settings["send_image"] = st.text_input("Link Avatar (URL):", value=settings["send_image"])
    settings["chanel_id"] = st.text_input("Chanel ID:", value=settings["chanel_id"])
    settings["type"] = st.text_input("Type:", value=settings["type"])
    settings["emoji_id"] = st.text_input("Emoji ID:", value=settings["emoji_id"])
    settings["attachments"] = st.text_input("Link đính kèm (File/Ảnh):", value=settings["attachments"])
    
    # Cập nhật lại vào bộ nhớ State
    st.session_state.account_settings[username] = settings
else:
    st.sidebar.error("Không tìm thấy dữ liệu tài khoản từ Gist!")
    st.stop()

# --- KHU VỰC HIỂN THỊ TIN NHẮN (STREAMLIT CHAT UI) ---
current_chanel = st.session_state.account_settings[username]["chanel_id"]
messages = chat_api.fetch_msgs(current_chanel)

# Khung chứa bong bóng chat
chat_container = st.container(height=450)
with chat_container:
    if messages:
        # Đảo ngược danh sách hoặc giữ nguyên tùy theo cấu trúc trả về của API Lazi để tin mới nằm dưới cùng
        for m in reversed(messages): 
            sender = m.get('sender_name', 'Ẩn danh')
            msg_text = m.get('message', '')
            
            # Phân biệt tin nhắn của mình gửi (bên phải) và người khác (bên trái)
            if username in sender or sender == st.session_state.account_settings[username]["send_name"]:
                with st.chat_message("user"):
                    st.write(f"**Bạn ({username}):** {msg_text}")
            else:
                with st.chat_message("assistant"):
                    st.write(f"**{sender}:** {msg_text}")
    else:
        st.info("Chưa có tin nhắn nào trong phòng này hoặc Chanel ID không hợp lệ.")

# --- Ô NHẬP TIN NHẮN CHUẨN WEB TELEGRAM ---
if msg_input := st.chat_input("Nhập tin nhắn và nhấn Enter..."):
    current_settings = st.session_state.account_settings[username]
    
    # Gửi payload ngầm lên hệ thống Lazi
    chat_api.send_msg(msg_input, cred, current_settings, anonymous)
    
    st.toast("🚀 Gửi tin nhắn thành công!")
    time.sleep(0.5) # Chờ một chút để API kịp cập nhật dữ liệu server
    st.rerun() # Tự động tải lại trang để kéo tin nhắn mới về
