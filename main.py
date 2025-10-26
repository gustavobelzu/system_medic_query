import sys
import os
from PySide6.QtWidgets import QApplication
from desktop_gui.login_window import LoginWindow

# Asegurar que src sea visible
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
