from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, 
    QLabel, QFileDialog
)
from PyQt6.QtCore import pyqtSignal

class FileUploader(QWidget):
    file_selected = pyqtSignal(str)  # سیگنال انتخاب فایل

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.btn_select = QPushButton("انتخاب فایل")
        self.btn_select.clicked.connect(self.select_file)
        layout.addWidget(self.btn_select)
        
        self.lbl_status = QLabel("هیچ فایلی انتخاب نشده")
        layout.addWidget(self.lbl_status)
        
        self.setLayout(layout)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "انتخاب فایل",
            "",
            "همه فایل‌ها (*);;تصاویر (*.png *.jpg *.jpeg);;اسناد (*.pdf *.docx)"
        )
        
        if file_path:
            self.lbl_status.setText(f"فایل انتخاب شده: {os.path.basename(file_path)}")
            self.file_selected.emit(file_path)