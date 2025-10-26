from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton, QGridLayout, QVBoxLayout, QStackedWidget
)
import sys, os

# Ajustar path a src si es necesario
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

# Importar los paneles de cada módulo
from desktop_gui.pacientes_panel import PacientesPanel
from desktop_gui.estados_panel import EstadosPanel
from desktop_gui.usuarios_panel import UsuariosPanel
from desktop_gui.ingresos_panel import IngresosPanel
from desktop_gui.egresos_panel import EgresosPanel
from desktop_gui.reportes_panel import ReportesPanel

class DashboardWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.setWindowTitle("Dashboard - System Medic Query")
        self.setFixedSize(900, 600)
        self.user = user

        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout()
        central.setLayout(self.main_layout)

        # Usuario conectado
        self.lbl_user = QLabel(f"Usuario: {user[1]} ({user[2]})")
        self.lbl_user.setStyleSheet("font-weight:bold; font-size:14pt; color:#333")
        self.main_layout.addWidget(self.lbl_user)

        # Panel de botones de módulos
        self.grid_btns = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_btns.setLayout(self.grid_layout)
        self.main_layout.addWidget(self.grid_btns)

        # Stacked widget para subpaneles
        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack, stretch=1)

        # Botones de módulos
        self.botones = {
            "Pacientes": PacientesPanel,
            "Estados": EstadosPanel,
            "Usuarios": UsuariosPanel,
            "Ingresos": IngresosPanel,
            "Egresos": EgresosPanel,
            "Reportes": ReportesPanel
        }

        fila, col = 0, 0
        for nombre, panel_class in self.botones.items():
            btn = QPushButton(nombre)
            btn.setMinimumSize(180, 60)
            btn.clicked.connect(lambda checked, cls=panel_class: self.abrir_panel(cls))
            self.grid_layout.addWidget(btn, fila, col)
            col += 1
            if col > 2:
                col = 0
                fila += 1

        # Botón salir
        self.btn_salir = QPushButton("Salir")
        self.btn_salir.clicked.connect(self.close)
        self.grid_layout.addWidget(self.btn_salir, fila+1, 0, 1, 3)

    def abrir_panel(self, panel_class):
        """Mostrar el subpanel en el stack"""
        panel = panel_class(volver_callback=self.volver_a_menu)
        self.stack.addWidget(panel)
        self.stack.setCurrentWidget(panel)
        self.grid_btns.hide()  # ocultar botones del dashboard

    def volver_a_menu(self):
        """Volver al dashboard principal"""
        self.grid_btns.show()
        self.stack.setCurrentIndex(-1)  # oculta cualquier panel activo

# ==========================
# Ejemplo de inicio
# ==========================
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    # Simular usuario conectado
    usuario = (1, "Admin", "Administrador")

    app = QApplication(sys.argv)
    window = DashboardWindow(usuario)
    window.show()
    sys.exit(app.exec())
