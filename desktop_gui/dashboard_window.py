import os
import sys
from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

# Agregar src al path para poder importar módulos
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

        # Cargar UI
        ui_path = os.path.join(os.path.dirname(__file__), "dashboard.ui")
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
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
