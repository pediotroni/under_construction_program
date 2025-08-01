import sys
from PyQt6.QtWidgets import QApplication
from ui.login_window import LoginWindow
from utils.file_manager import load_user_data
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    if user_data := load_user_data():
        window = MainWindow(user_data["mobile"])
    else:
        window = LoginWindow()

    window.show()
    sys.exit(app.exec())
