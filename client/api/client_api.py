import requests
from PyQt6.QtWidgets import QMessageBox
import websockets
from PyQt6.QtCore import QObject, pyqtSignal

BASE_URL = "http://127.0.0.1:8000"

class APIClient:
    @staticmethod
    def login(mobile: str, password: str):
        try:
            print(f"در حال ارسال درخواست برای موبایل: {mobile}")  # لاگ دیباگ
            response = requests.post(
                f"{BASE_URL}/token/",
                json={"mobile": mobile, "password": password}  # تغییر از data به json
            )
            print(f"پاسخ سرور: {response.status_code}, {response.text}")  # لاگ دیباگ
            if response.status_code == 200:
                return response.json()["access_token"]
            QMessageBox.warning(None, "خطا", "موبایل یا رمز عبور اشتباه")
        except Exception as e:
            print(f"خطای اتصال: {str(e)}")  # لاگ دیباگ
            QMessageBox.critical(None, "خطا", f"اتصال به سرور ممکن نیست: {str(e)}")
        return None

    @staticmethod
    def get_friends(token: str):
        try:
            response = requests.get(
                f"{BASE_URL}/friends/",
                headers={"Authorization": f"Bearer {token}"}
            )
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            print(f"Error fetching friends: {e}")
            return []

    @staticmethod
    def send_message(token: str, sender: str, receiver: str, content: str):
        try:
            response = requests.post(
                f"{BASE_URL}/messages/send/",
                json={
                    "sender": sender,
                    "receiver": receiver,
                    "content": content
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            return response.status_code == 200
        except:
            return False

    @staticmethod
    def get_messages(token: str, user_mobile: str, contact_mobile: str):
        try:
            response = requests.get(
                f"{BASE_URL}/messages/{user_mobile}/",
                params={"contact_mobile": contact_mobile},
                headers={"Authorization": f"Bearer {token}"}
            )
            return response.json() if response.status_code == 200 else []
        except:
            return []

class WebSocketClient(QObject):
    message_received = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.websocket = None

    async def connect(self, mobile: str, token: str):
        self.websocket = await websockets.connect(
            f"ws://localhost:8000/ws/{mobile}",
            extra_headers={"Authorization": f"Bearer {token}"}
        )
        
        while True:
            message = await self.websocket.recv()
            self.message_received.emit(message)

    async def send_message(self, message: str):
        if self.websocket:
            await self.websocket.send(message)


@staticmethod
async def upload_file(token: str, file_path: str, sender: str, receiver: str):
    """ارسال فایل به سرور"""
    try:
        with open(file_path, "rb") as file:
            files = {"file": (os.path.basename(file_path), file)}
            data = {"sender": sender, "receiver": receiver}
            
            response = requests.post(
                f"{BASE_URL}/uploadfile/",
                files=files,
                data=data,
                headers={"Authorization": f"Bearer {token}"}
            )
            return response.json()
    except Exception as e:
        print(f"خطا در آپلود فایل: {e}")
        return None

@staticmethod
def get_file_url(filename: str):
    """دریافت لینک دانلود فایل"""
    return f"{BASE_URL}/download/{filename}"