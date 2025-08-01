import sys
from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QVBoxLayout, QWidget,
    QMenuBar, QMenu, QStatusBar, QListWidget,
    QListWidgetItem, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon
from api.client_api import APIClient

class MainWindow(QMainWindow):
    def __init__(self, mobile: str):
        super().__init__()
        self.mobile = mobile
        self.token = None  # برای ذخیره توکن احراز هویت
        self.init_ui()
        self.setup_menu()
        self.show_welcome()

    def init_ui(self):
        """تنظیمات اولیه پنجره اصلی"""
        self.setWindowTitle(f"پدرام چت - {self.mobile}")
        self.setWindowIcon(QIcon("assets/icon.png"))  # مسیر آیکون برنامه
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(600, 400)

    def show_welcome(self):
        """نمایش صفحه خوشآمدگویی"""
        welcome_label = QLabel(
            f"سلام {self.mobile}!\nبه پیام‌رسان پدرام خوش آمدید\n\n"
            "از منوی بالا گزینه‌ها را انتخاب کنید"
        )
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setFont(QFont("Arial", 14))
        self.setCentralWidget(welcome_label)

    def setup_menu(self):
        """ایجاد منوهای اصلی"""
        menubar = self.menuBar()
        
        # منوی کاربر
        user_menu = menubar.addMenu("پروفایل")
        user_menu.addAction("مشاهده پروفایل", self.show_profile)
        user_menu.addAction("خروج", self.logout)

        # منوی دوستان
        friends_menu = menubar.addMenu("دوستان")
        friends_menu.addAction("لیست دوستان", self.show_friends_list)
        friends_menu.addAction("جستجوی دوستان", self.search_friends)
        friends_menu.addAction("درخواست‌های دوستی", self.show_friend_requests)

        # منوی چت
        chat_menu = menubar.addMenu("چت")
        chat_menu.addAction("چت جدید", self.new_chat)
        chat_menu.addAction("تاریخچه چت‌ها", self.chat_history)

        # نوار وضعیت
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status("آنلاین")

    def update_status(self, status: str):
        """به‌روزرسانی نوار وضعیت"""
        self.status_bar.showMessage(f"کاربر: {self.mobile} | وضعیت: {status}")

    def show_friends_list(self):
        """نمایش لیست دوستان با طراحی پیشرفته"""
        try:
            # دریافت داده از سرور
            friends_data = APIClient.get_friends(self.token) or [
                {"name": "پدرام", "mobile": "09123456789", "status": "آنلاین"},
                {"name": "علی", "mobile": "09121112222", "status": "آفلاین"}
            ]

            # ایجاد ویجت لیست
            friends_list = QListWidget()
            friends_list.setStyleSheet("""
                QListWidget {
                    background: #f9f9f9;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 5px;
                }
                QListWidget::item {
                    padding: 10px;
                    border-bottom: 1px solid #eee;
                }
                QListWidget::item:hover {
                    background: #e3f2fd;
                }
            """)

            for friend in friends_data:
                item = QListWidgetItem()
                item.setFont(QFont("Arial", 11))
                
                # ایجاد ویجت سفارشی برای هر آیتم
                widget = QWidget()
                layout = QVBoxLayout()
                
                name_label = QLabel(f"👤 {friend.get('name', 'بدون نام')}")
                name_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
                
                mobile_label = QLabel(f"📱 {friend['mobile']}")
                status_label = QLabel(f"● {friend.get('status', 'نامشخص')}")
                status_label.setStyleSheet(
                    "color: green;" if friend.get('status') == "آنلاین" else "color: gray;"
                )
                
                layout.addWidget(name_label)
                layout.addWidget(mobile_label)
                layout.addWidget(status_label)
                widget.setLayout(layout)
                
                item.setSizeHint(widget.sizeHint())
                friends_list.addItem(item)
                friends_list.setItemWidget(item, widget)

            # تنظیم به عنوان ویجت مرکزی
            central = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(QLabel("لیست دوستان", alignment=Qt.AlignmentFlag.AlignCenter))
            layout.addWidget(friends_list)
            central.setLayout(layout)
            
            self.setCentralWidget(central)

        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در دریافت لیست دوستان:\n{str(e)}")

    def show_profile(self):
        """نمایش پروفایل کاربر"""
        profile_data = {
            "name": "پدرام",
            "mobile": self.mobile,
            "status": "آنلاین",
            "bio": "عاشق برنامه‌نویسی!"
        }
        
        profile_widget = QWidget()
        layout = QVBoxLayout()
        
        # افزودن المان‌های پروفایل
        layout.addWidget(QLabel("پروفایل کاربر", 
                             font=QFont("Arial", 16, QFont.Weight.Bold),
                             alignment=Qt.AlignmentFlag.AlignCenter))
        
        for key, value in profile_data.items():
            row = QWidget()
            row_layout = QHBoxLayout()
            row_layout.addWidget(QLabel(f"{key.capitalize()}:", 
                               font=QFont("Arial", 12, QFont.Weight.Bold)))
            row_layout.addWidget(QLabel(str(value), font=QFont("Arial", 12)))
            row.setLayout(row_layout)
            layout.addWidget(row)
        
        profile_widget.setLayout(layout)
        self.setCentralWidget(profile_widget)

    def logout(self):
        """خروج از حساب کاربری"""
        reply = QMessageBox.question(
            self, "خروج",
            "آیا مطمئن هستید می‌خواهید خارج شوید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.close()
            # بازگشت به صفحه لاگین
            from ui.login_window import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()

    # سایر متدها (پیاده‌سازی بعدی)
    def search_friends(self): pass
    def show_friend_requests(self): pass
    def new_chat(self): pass
    def chat_history(self): pass


    def open_chat(self, contact_mobile: str):
        from ui.chat_window import ChatWindow
        self.chat_window = ChatWindow(
            contact_name=self.get_contact_name(contact_mobile),
            contact_mobile=contact_mobile
        )
        self.chat_window.message_sent.connect(
            lambda msg: self.send_message(contact_mobile, msg)
        )
        self.chat_window.show()
        
        # بارگیری تاریخچه چت
        messages = APIClient.get_messages(
            self.token, self.mobile, contact_mobile
        )
        self.display_messages(messages)

    def send_message(self, receiver: str, content: str):
        if APIClient.send_message(self.token, self.mobile, receiver, content):
            print("پیام با موفقیت ارسال شد")
        else:
            QMessageBox.warning(self, "خطا", "ارسال پیام ناموفق بود")