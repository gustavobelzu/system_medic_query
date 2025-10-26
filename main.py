import sys, os
from PySide6.QtWidgets import QApplication
from desktop_gui.login_window import LoginWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Cargar estilo
    style_path = os.path.join(os.path.dirname(__file__), "desktop_gui", "style.qss")
    if os.path.exists(style_path):
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
