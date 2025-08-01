from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLineEdit, 
    QPushButton, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtCore import QThread
import asyncio

class WebSocketThread(QThread):
    def __init__(self, mobile: str, token: str):
        super().__init__()
        self.mobile = mobile
        self.token = token
        self.client = WebSocketClient()

    def run(self):
        asyncio.run(self.client.connect(self.mobile, self.token))

class ChatWindow(QWidget):
    message_sent = pyqtSignal(str)  # سیگنال ارسال پیام

    def __init__(self, contact_name: str, contact_mobile: str, user_mobile: str, token: str):
        super().__init__()
        self.contact_mobile = contact_mobile
        self.user_mobile = user_mobile
        self.token = token
        self.setup_ui(contact_name)
        self.setup_websocket()
        

    def setup_websocket(self):
        self.ws_thread = WebSocketThread(self.user_mobile, self.token)
        self.ws_thread.client.message_received.connect(self.handle_ws_message)
        self.ws_thread.start()

    def handle_ws_message(self, message: str):
        self.chat_history.append(f"دوستم: {message}")


    def setup_ui(self, contact_name):
        self.setWindowTitle(f"چت با {contact_name}")
        self.setGeometry(200, 200, 500, 600)

        layout = QVBoxLayout()

        # نمایش تاریخچه چت
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        layout.addWidget(self.chat_history)

        # ورودی پیام جدید
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("پیام خود را بنویسید... (حداکثر 500 کاراکتر)")
        layout.addWidget(self.message_input)

        # دکمه ارسال
        send_btn = QPushButton("ارسال")
        send_btn.clicked.connect(self.send_message)
        layout.addWidget(send_btn)

        self.setLayout(layout)

    def send_message(self):
        message = self.message_input.text()
        if message:
            self.message_sent.emit(message)
            self.message_input.clear()

    from ui.file_uploader import FileUploader
    self.file_uploader = FileUploader()
    self.file_uploader.file_selected.connect(self.handle_file_selected)
    layout.addWidget(self.file_uploader)

    def handle_file_selected(self, file_path):
        """مدیریت فایل انتخاب شده"""
        result = APIClient.upload_file(
            self.token,
            file_path,
            self.user_mobile,
            self.contact_mobile
        )
        
        if result:
            self.chat_history.append(f"شما فایل ارسال کردید: {result['filename']}")
            # نمایش پیش‌نمایش فایل (برای تصاویر)
            if result['filename'].split(".")[-1].lower() in ["png", "jpg", "jpeg"]:
                self.show_image_preview(result['saved_as'])

    def show_image_preview(self, filename):
        """نمایش پیش‌نمایش تصویر"""
        from PyQt6.QtGui import QPixmap
        from PyQt6.QtWidgets import QLabel
        
        image_url = APIClient.get_file_url(filename)
        # TODO: دانلود و نمایش تصویر


