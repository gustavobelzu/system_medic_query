from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton, QGridLayout, QVBoxLayout, QStackedWidget
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QSize
import os
import sys
from PySide6.QtWidgets import QMessageBox

# Ajustar path a src si es necesario
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from desktop_gui.pacientes_panel import PacientesPanel
from desktop_gui.estados_panel import EstadosPanel
from desktop_gui.usuarios_panel import UsuariosPanel
from desktop_gui.ingresos_panel import IngresosPanel
from desktop_gui.egresos_panel import EgresosPanel
from desktop_gui.reportes_panel import ReportesPanel

class DashboardWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.setWindowTitle("SISTEMA DE CONTROL DE PACIENTES - CLINICA LA FUENTE")
        self.setFixedSize(1000, 650)
        self.user = user
        self.centrar_ventana()

        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout()
        central.setLayout(self.main_layout)

        # --------------------------
        # Título grande estilizado
        # --------------------------
        lbl_titulo = QLabel("SISTEMA DE CONTROL DE PACIENTES\nCLINICA LA FUENTE")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        lbl_titulo.setStyleSheet("""
            color: #1976d2;
            font-weight: bold;
            font-size: 28pt;
            font-family: Arial;
        """)
        self.main_layout.addWidget(lbl_titulo)

        # Usuario conectado
        self.lbl_user = QLabel(f"Usuario: {user[1]} ({user[2]})")
        self.lbl_user.setAlignment(Qt.AlignRight)
        self.lbl_user.setStyleSheet("font-weight:bold; font-size:12pt; color:#333")
        self.main_layout.addWidget(self.lbl_user)

        # --------------------------
        # Panel de botones con imágenes
        # --------------------------
        self.grid_btns = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_btns.setLayout(self.grid_layout)
        self.main_layout.addWidget(self.grid_btns)

        # Stacked widget para subpaneles
        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack, stretch=1)

        # Botones de módulos con iconos
        self.botones = {
            "Pacientes": ("pacientes.png", PacientesPanel),
            "Estados": ("estados.png", EstadosPanel),
            "Usuarios": ("usuarios.png", UsuariosPanel),
            "Ingresos": ("ingresos.png", IngresosPanel),
            "Egresos": ("egresos.png", EgresosPanel),
            "Reportes": ("reportes.png", ReportesPanel)
        }

        fila, col = 0, 0
        icon_size = 64  # tamaño de icono en px
        for nombre, (icon_file, panel_class) in self.botones.items():
            btn = QPushButton(nombre)
            btn.setMinimumSize(180, 100)

            # Cargar imagen si existe
            icon_path = os.path.join(os.path.dirname(__file__), "icons", icon_file)
            if os.path.exists(icon_path):
                btn.setIcon(QIcon(icon_path))
                btn.setIconSize(QSize(icon_size, icon_size))

            # Estilo texto debajo del icono
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 12pt;
                    text-align: bottom center;
                    padding-top: 70px;
                }
            """)
            btn.clicked.connect(lambda checked, cls=panel_class: self.abrir_panel(cls))
            self.grid_layout.addWidget(btn, fila, col)
            col += 1
            if col > 2:
                col = 0
                fila += 1

        # Botón salir
        self.btn_salir = QPushButton("Salir")
        self.btn_salir.setMinimumHeight(50)
        self.grid_layout.addWidget(self.btn_salir, fila+1, 0, 1, 3)
        self.btn_salir.clicked.disconnect()
        self.btn_salir.clicked.connect(self.salir_sistema)

    # --------------------------
    # Métodos
    # --------------------------
    def abrir_panel(self, panel_class):
        panel = panel_class(volver_callback=self.volver_a_menu)
        self.stack.addWidget(panel)
        self.stack.setCurrentWidget(panel)
        self.grid_btns.hide()  # ocultar botones

    def volver_a_menu(self):
        self.grid_btns.show()
        # Limpiar el stack
        while self.stack.count():
            widget = self.stack.widget(0)
            self.stack.removeWidget(widget)
            widget.deleteLater()

    def centrar_ventana(self):
        screen = self.screen().availableGeometry()  # tamaño disponible de la pantalla
        size = self.geometry()  # tamaño de la ventana
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)
    # Nuevo método
    def salir_sistema(self):
        QMessageBox.information(
            self,
            "Gracias",
            "Gracias por usar el sistema. ¡Vuelva pronto!",
            QMessageBox.Ok
        )
        self.close()

    def closeEvent(self, event):
        # Solo acepta el cierre sin mensaje
        event.accept()

# ==========================
# Ejemplo de inicio
# ==========================
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    usuario = (1, "Admin", "Administrador")
    app = QApplication(sys.argv)
    window = DashboardWindow(usuario)
    window.show()
    sys.exit(app.exec())
