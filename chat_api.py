import requests
import json

session = requests.Session()

# Dán link của bạn vào đây
GIST_URL = "https://gist.githubusercontent.com/PaineZap/1f3c6112bca5515371b0ff02c5085918/raw/0b1794e370e85ccf6fbaa2de1386860adeae09fb/accounts.json" 

ACCOUNTS_CREDENTIALS = []

def load_accounts():
    """Tải dữ liệu tĩnh từ Gist với Header để tránh bị Github chặn"""
    global ACCOUNTS_CREDENTIALS
    
    # Bổ sung User-Agent giả lập trình duyệt để vượt qua hệ thống chặn bot của Github
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    
    try:
        print("Đang tải dữ liệu từ Gist...")
        response = requests.get(GIST_URL, headers=headers, timeout=10)
        
        if response.status_code == 200:
            try:
                ACCOUNTS_CREDENTIALS = response.json()
                print(f"✅ Tải thành công {len(ACCOUNTS_CREDENTIALS)} tài khoản!")
                return True
            except json.JSONDecodeError as json_err:
                print(f"❌ LỖI ĐỊNH DẠNG JSON TRÊN GIST: {json_err}")
                print("-> Vui lòng kiểm tra lại file Gist, chắc chắn rằng không có dấu phẩy dư ở cuối phần tử cuối cùng.")
        else:
            print(f"❌ LỖI TẢI FILE: Server trả về mã {response.status_code}")
            
    except Exception as e:
        print(f"❌ LỖI KẾT NỐI MẠNG: {e}")
        
    return False

def send_msg(message, account_cred, settings, anonymous):
    # ... [Giữ nguyên như cũ] ...
    payload = {
        "v": "0",
        "temp_id": "",
        "message": message,
        "anonymous": "1" if anonymous else "0", 
    }
    payload.update(account_cred)
    payload.update(settings)
    
    try:
        session.post("https://chat.lazi.vn/cores/code/sendg.php?v=0", data=payload, timeout=5)
    except: 
        pass

def fetch_msgs(chanel_id):
    # ... [Giữ nguyên như cũ] ...
    try:
        response = session.get(f"https://chat.lazi.vn/cores/code/get_messages.php?chanel_id={chanel_id}", timeout=5)
        return response.json() if response.status_code == 200 else []
    except: 
        return []
