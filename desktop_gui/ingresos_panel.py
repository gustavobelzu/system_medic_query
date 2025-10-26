from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout
)
import sqlite3
from datetime import datetime

DB_PATH = "database/emergencias.db"

def conectar():
    return sqlite3.connect(DB_PATH)

class IngresosPanel(QWidget):
    def __init__(self, volver_callback=None):
        super().__init__()
        self.volver_callback = volver_callback

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Botones de acción
        self.buttons_layout = QHBoxLayout()
        self.btn_registrar = QPushButton("Registrar ingreso")
        self.btn_actualizar = QPushButton("Actualizar ingreso")
        self.btn_eliminar = QPushButton("Eliminar ingreso")
        self.btn_listar = QPushButton("Refrescar lista")
        self.btn_volver = QPushButton("Volver")

        self.buttons_layout.addWidget(self.btn_registrar)
        self.buttons_layout.addWidget(self.btn_actualizar)
        self.buttons_layout.addWidget(self.btn_eliminar)
        self.buttons_layout.addWidget(self.btn_listar)
        self.buttons_layout.addWidget(self.btn_volver)
        self.layout.addLayout(self.buttons_layout)

        # Tabla
        self.tabla = QTableWidget()
        self.layout.addWidget(self.tabla)

        # Conectar botones
        self.btn_listar.clicked.connect(self.cargar_tabla)
        self.btn_registrar.clicked.connect(self.registrar_ingreso)
        self.btn_actualizar.clicked.connect(self.actualizar_ingreso)
        self.btn_eliminar.clicked.connect(self.eliminar_ingreso)
        self.btn_volver.clicked.connect(self.volver)

        # Cargar datos al inicio
        self.cargar_tabla()

    def cargar_tabla(self):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.id_ingreso, p.nombre, i.fecha_ingreso, i.hora_ingreso, i.servicio_hospitalario, i.cama
            FROM Ingreso i
            JOIN Paciente p ON i.ci = p.ci
            ORDER BY i.fecha_ingreso DESC, i.hora_ingreso DESC
        """)
        ingresos = cursor.fetchall()
        conn.close()

        self.tabla.setRowCount(len(ingresos))
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["ID", "Paciente", "Fecha", "Hora", "Servicio", "Cama"])

        for row, ingreso in enumerate(ingresos):
            for col, value in enumerate(ingreso):
                self.tabla.setItem(row, col, QTableWidgetItem(str(value)))

    # =================================================================
    # Aquí puedes integrar tus funciones de registrar, actualizar y eliminar
    # usando ventanas emergentes (QInputDialog, QLineEdit, etc.)
    # =================================================================
    def registrar_ingreso(self):
        from PySide6.QtWidgets import QInputDialog
        # Ejemplo simple: pedir CI del paciente
        ci, ok = QInputDialog.getText(self, "Registrar Ingreso", "Ingrese CI del paciente:")
        if ok and ci:
            # Aquí llamas a la lógica de tu función registrar_ingreso()
            print(f"Registrar ingreso para CI: {ci}")
            self.cargar_tabla()

    def actualizar_ingreso(self):
        from PySide6.QtWidgets import QInputDialog
        id_ingreso, ok = QInputDialog.getText(self, "Actualizar Ingreso", "Ingrese ID del ingreso:")
        if ok and id_ingreso:
            print(f"Actualizar ingreso ID: {id_ingreso}")
            self.cargar_tabla()

    def eliminar_ingreso(self):
        from PySide6.QtWidgets import QInputDialog, QMessageBox
        id_ingreso, ok = QInputDialog.getText(self, "Eliminar Ingreso", "Ingrese ID del ingreso:")
        if ok and id_ingreso:
            reply = QMessageBox.question(self, "Confirmar", f"¿Eliminar ingreso {id_ingreso}?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                print(f"Eliminar ingreso ID: {id_ingreso}")
                self.cargar_tabla()

    def volver(self):
        if self.volver_callback:
            self.volver_callback()
