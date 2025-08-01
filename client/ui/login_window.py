from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox
)
from api.client_api import APIClient
from ui.main_window import MainWindow
from utils.file_manager import save_user_data

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ورود به پدرام چت")
        self.setup_ui()

    def setup_connections(self):
        self.password_input.returnPressed.connect(self.handle_login)
        
    def setup_ui(self):
        layout = QVBoxLayout()

        self.mobile_input = QLineEdit()
        self.mobile_input.setPlaceholderText("شماره موبایل")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("رمز عبور")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        login_btn = QPushButton("ورود")
        login_btn.clicked.connect(self.handle_login)

        layout.addWidget(QLabel("ورود به حساب کاربری"))
        layout.addWidget(self.mobile_input)
        layout.addWidget(self.password_input)
        layout.addWidget(login_btn)
        
        self.setLayout(layout)

    def handle_login(self):
        mobile = self.mobile_input.text()
        password = self.password_input.text()
        
        if not mobile or not password:
            QMessageBox.warning(self, "خطا", "لطفاً همه فیلدها را پر کنید")
        else:
            # TODO: ارتباط با سرور
            QMessageBox.information(self, "موفق", f"خوش آمدید {mobile}")
            
    def handle_login(self):
            mobile = self.mobile_input.text()
            password = self.password_input.text()
            
            if not mobile or not password:
                QMessageBox.warning(self, "خطا", "لطفاً همه فیلدها را پر کنید")
                return

            token = APIClient.login(mobile, password)
            if token:
                self.close()
                # بعداً پنجره اصلی رو اینجا باز می‌کنیم
                QMessageBox.information(self, "موفق", "ورود با موفقیت انجام شد!")
                
    def handle_login(self):
        mobile = self.mobile_input.text()
        password = self.password_input.text()
        
        token = APIClient.login(mobile, password)
        if token:
            save_user_data(mobile, token)  # ذخیره توکن
            self.close()
            self.main_window = MainWindow(mobile)  # باز کردن پنجره اصلی
            self.main_window.show()


