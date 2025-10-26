from PySide6.QtWidgets import QMainWindow, QWidget, QLabel, QPushButton, QGridLayout, QMessageBox
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from modules.estados import menu_estados
from modules.pacientes import menu_pacientes
from modules.usuarios import menu_usuarios
from modules.ingresos import menu_ingresos
from modules.egresos import menu_egresos
from modules.reportes import menu_reportes

class DashboardWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.setWindowTitle("Dashboard - System Medic Query")
        self.setFixedSize(600, 400)
        self.user = user

        central = QWidget()
        layout = QGridLayout()
        central.setLayout(layout)
        self.setCentralWidget(central)

        lbl_user = QLabel(f"Usuario: {user[1]} ({user[2]})")
        lbl_user.setStyleSheet("font-weight:bold; font-size:14pt; color:#333")
        layout.addWidget(lbl_user, 0, 0, 1, 3)

        botones = [
            ("Gestión de Estados", menu_estados),
            ("Gestión de Pacientes", menu_pacientes),
            ("Gestión de Usuarios", menu_usuarios),
            ("Gestión de Ingresos", menu_ingresos),
            ("Gestión de Egresos", menu_egresos),
            ("Reportes", menu_reportes)
        ]

        fila, col = 1, 0
        for texto, funcion in botones:
            btn = QPushButton(texto)
            btn.setMinimumSize(180, 80)
            btn.setStyleSheet("background-color:#0078d7; color:white; border-radius:8px; font-weight:bold; font-size:12pt;")
            btn.clicked.connect(lambda checked, f=funcion: self.abrir_modulo(f))
            layout.addWidget(btn, fila, col)
            col += 1
            if col > 2:
                col = 0
                fila += 1

        btn_salir = QPushButton("Salir")
        btn_salir.setStyleSheet("background-color:#d9534f; color:white; font-weight:bold; font-size:12pt;")
        btn_salir.clicked.connect(self.close)
        layout.addWidget(btn_salir, fila+1, 0, 1, 3)

    def abrir_modulo(self, funcion):
        try:
            funcion(self.user)
        except TypeError:
            funcion()
        QMessageBox.information(self, "Módulo cerrado", "Regresando al panel principal.")
