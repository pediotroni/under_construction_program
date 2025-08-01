from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

class FriendsList(QListWidget):
    def __init__(self, friends_data):
        super().__init__()
        self.setStyleSheet("""
            QListWidget {
                background-color: #f0f0f0;
                border-radius: 10px;
                padding: 10px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ddd;
            }
        """)
        self.setup_ui(friends_data)

    def setup_ui(self, friends_data):
        self.clear()
        self.setMinimumSize(QSize(400, 300))
        
        for friend in friends_data:
            item = QListWidgetItem(f"👤 {friend['name']}\n📱 {friend['mobile']}")
            item.setFont(QFont("Arial", 12))
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.addItem(item)