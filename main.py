import sys
import os

# Asegurar que Python vea la carpeta src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from desktop_gui.login_window import LoginWindow
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
