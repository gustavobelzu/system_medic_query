import sqlite3, os, time
from PySide6.QtWidgets import (
    QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox
)
from PySide6.QtCore import QTimer
from desktop_gui.dashboard_window import DashboardWindow
from desktop_gui.usuarios_panel import UsuariosPanel
from .resultados_reportes import ResultadosReportes

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "emergencias.db")

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - System Medic Query")
        self.setFixedSize(350, 270)

        self.intentos = 0
        self.bloqueado_hasta = 0

        self.timer = QTimer()
        self.timer.setInterval(1000)  # 1 segundo
        self.timer.timeout.connect(self.actualizar_bloqueo)

        layout = QVBoxLayout()
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

        # Widgets
        self.lbl_user = QLabel("Usuario:")
        self.txt_user = QLineEdit()
        self.lbl_pass = QLabel("Contraseña:")
        self.txt_pass = QLineEdit()
        self.txt_pass.setEchoMode(QLineEdit.Password)
        self.btn_login = QPushButton("Ingresar")
        self.btn_registrar = QPushButton("Registrar nuevo usuario")
        self.lbl_bloqueo = QLabel("")  # Etiqueta para mostrar tiempo restante

        layout.addWidget(self.lbl_user)
        layout.addWidget(self.txt_user)
        layout.addWidget(self.lbl_pass)
        layout.addWidget(self.txt_pass)
        layout.addWidget(self.btn_login)
        layout.addWidget(self.btn_registrar)
        layout.addWidget(self.lbl_bloqueo)

        # Conexiones
        self.btn_login.clicked.connect(self.handle_login)
        self.btn_registrar.clicked.connect(self.registrar_usuario)

    def handle_login(self):
        if time.time() < self.bloqueado_hasta:
            remaining = int(self.bloqueado_hasta - time.time())
            self.lbl_bloqueo.setText(f"⏳ Bloqueado. Intente de nuevo en {remaining} segundos.")
            if not self.timer.isActive():
                self.timer.start()
            return

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
            self.intentos = 0
            self.lbl_bloqueo.setText("")
            self.timer.stop()
        else:
            self.intentos += 1
            if self.intentos >= 3:
                self.bloqueado_hasta = time.time() + 10  # bloquear 10 segundos
                self.lbl_bloqueo.setText(f"⏳ Demasiados intentos. Espere 10 segundos.")
                self.timer.start()
            else:
                QMessageBox.warning(self, "Error", f"Usuario o contraseña incorrectos ({self.intentos}/3)")

    def actualizar_bloqueo(self):
        remaining = int(self.bloqueado_hasta - time.time())
        if remaining > 0:
            self.lbl_bloqueo.setText(f"⏳ Bloqueado. Intente de nuevo en {remaining} segundos.")
        else:
            self.lbl_bloqueo.setText("")
            self.timer.stop()
            self.intentos = 0

    def registrar_usuario(self):
        from desktop_gui.usuarios_panel import UsuarioForm
        form = UsuarioForm(self)
        form.exec()

    def open_dashboard(self, user):
        self.dashboard = DashboardWindow(user)
        self.dashboard.show()
        self.close()
