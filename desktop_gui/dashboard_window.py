from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import sys
import os

# Agregar tus módulos al path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "modules"))

from src.modules.estados import menu_estados
from src.modules.pacientes import menu_pacientes
from src.modules.usuarios import menu_usuarios
from src.modules.ingresos import menu_ingresos
from src.modules.egresos import menu_egresos
from src.modules.reportes import menu_reportes




class DashboardWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        loader = QUiLoader()
        ui_file = QFile("dashboard.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        self.user = user
        self.ui.lbl_user.setText(f"{user[1]} ({user[2]})")

        # Conectar botones
        self.ui.btn_estados.clicked.connect(lambda: self.abrir_modulo(menu_estados))
        self.ui.btn_pacientes.clicked.connect(lambda: self.abrir_modulo(menu_pacientes))
        self.ui.btn_usuarios.clicked.connect(lambda: self.abrir_modulo(menu_usuarios))
        self.ui.btn_ingresos.clicked.connect(lambda: self.abrir_modulo(menu_ingresos))
        self.ui.btn_egresos.clicked.connect(lambda: self.abrir_modulo(menu_egresos))
        self.ui.btn_reportes.clicked.connect(lambda: self.abrir_modulo(menu_reportes))
        self.ui.btn_salir.clicked.connect(self.close)

    def abrir_modulo(self, funcion):
        try:
            funcion(self.user)
        except TypeError:
            funcion()
        QMessageBox.information(self, "Módulo cerrado", "Regresando al panel principal.")
