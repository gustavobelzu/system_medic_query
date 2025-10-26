import sqlite3
from PySide6.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox
from desktop_gui.dashboard_window import DashboardWindow
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "emergencias.db")

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - System Medic Query")
        self.setFixedSize(300, 200)

        # Widgets
        layout = QVBoxLayout()
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

        self.lbl_user = QLabel("Usuario:")
        self.txt_user = QLineEdit()
        self.lbl_pass = QLabel("Contraseña:")
        self.txt_pass = QLineEdit()
        self.txt_pass.setEchoMode(QLineEdit.Password)
        self.btn_login = QPushButton("Ingresar")

        # Agregar al layout
        layout.addWidget(self.lbl_user)
        layout.addWidget(self.txt_user)
        layout.addWidget(self.lbl_pass)
        layout.addWidget(self.txt_pass)
        layout.addWidget(self.btn_login)

        # Conectar botón
        self.btn_login.clicked.connect(self.handle_login)

    def handle_login(self):
        username = self.txt_user.text().strip()
        password = self.txt_pass.text().strip()

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
