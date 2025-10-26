import sqlite3
from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from desktop_gui.dashboard_window import DashboardWindow

DB_PATH = "../database/emergencias.db"

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loader = QUiLoader()
        ui_file = QFile("login.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        self.ui.btn_login.clicked.connect(self.handle_login)

    def handle_login(self):
        username = self.ui.txt_user.text().strip()
        password = self.ui.txt_password.text().strip()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id_usuario, p.nombre, p.cargo
            FROM Usuario u
            JOIN Personal p ON u.id_usuario = p.id_usuario
            WHERE u.username = ? AND u.password = ?
        """, (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            QMessageBox.information(self, "Bienvenido", f"Hola {user[1]} ({user[2]})")
            self.open_dashboard(user)
        else:
            QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos.")

    def open_dashboard(self, user):
        self.dashboard = DashboardWindow(user)
        self.dashboard.show()
        self.close()
