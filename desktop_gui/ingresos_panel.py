from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QLabel, QMessageBox, QLineEdit, QFormLayout, QDialog, QComboBox,
    QDateEdit, QTimeEdit
)
from PySide6.QtCore import QDate, QTime
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "emergencias.db")

def conectar():
    return sqlite3.connect(DB_PATH)

# ==========================
# Formulario de Ingreso
# ==========================
class IngresoForm(QDialog):
    def __init__(self, parent=None, ingreso=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar / Editar Ingreso")
        self.setFixedSize(400, 320)
        self.ingreso = ingreso

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        # ComboBox Paciente
        self.combo_paciente = QComboBox()
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT ci, nombre FROM Paciente ORDER BY nombre")
        self.pacientes = cursor.fetchall()
        conn.close()

        for ci, nombre in self.pacientes:
            self.combo_paciente.addItem(f"{nombre} ({ci})", ci)

        # Campos fecha y hora con selectores
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())

        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())

        # Otros campos
        self.txt_servicio = QLineEdit()
        self.txt_cama = QLineEdit()

        form_layout.addRow("Paciente:", self.combo_paciente)
        form_layout.addRow("Fecha:", self.date_edit)
        form_layout.addRow("Hora:", self.time_edit)
        form_layout.addRow("Servicio:", self.txt_servicio)
        form_layout.addRow("Cama:", self.txt_cama)

        layout.addLayout(form_layout)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar")
        self.btn_cancelar = QPushButton("Cancelar")
        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(self.btn_cancelar)
        layout.addLayout(btn_layout)

        self.btn_guardar.clicked.connect(self.guardar)
        self.btn_cancelar.clicked.connect(self.close)

        # Si se pasa un ingreso, cargar datos
        if ingreso:
            self.cargar_datos(ingreso)

    def cargar_datos(self, ingreso):
        """
        ingreso = (id_ingreso, ci, nombre, fecha, hora, servicio, cama)
        """
        ci = ingreso[1]
        index = self.combo_paciente.findData(ci)
        if index >= 0:
            self.combo_paciente.setCurrentIndex(index)

        # Parsear fecha y hora correctamente
        try:
            fecha = datetime.strptime(ingreso[3], "%Y-%m-%d").date()
            hora = datetime.strptime(ingreso[4], "%H:%M").time()
            self.date_edit.setDate(QDate(fecha.year, fecha.month, fecha.day))
            self.time_edit.setTime(QTime(hora.hour, hora.minute))
        except Exception:
            pass  # En caso de datos corruptos

        self.txt_servicio.setText(ingreso[5])
        self.txt_cama.setText(str(ingreso[6]))

    def guardar(self):
        ci = self.combo_paciente.currentData()
        fecha = self.date_edit.date().toString("yyyy-MM-dd")
        hora = self.time_edit.time().toString("HH:mm")
        servicio = self.txt_servicio.text().strip()
        cama = self.txt_cama.text().strip()

        if not all([ci, servicio, cama]):
            QMessageBox.warning(self, "Error", "Complete todos los campos obligatorios.")
            return

        conn = conectar()
        cursor = conn.cursor()
        try:
            if self.ingreso:
                cursor.execute("""
                    UPDATE Ingreso
                    SET ci=?, fecha_ingreso=?, hora_ingreso=?, servicio_hospitalario=?, cama=?
                    WHERE id_ingreso=?
                """, (ci, fecha, hora, servicio, cama, self.ingreso[0]))
            else:
                cursor.execute("""
                    INSERT INTO Ingreso (ci, fecha_ingreso, hora_ingreso, servicio_hospitalario, cama)
                    VALUES (?,?,?,?,?)
                """, (ci, fecha, hora, servicio, cama))
            conn.commit()
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Ocurrió un error: {e}")
        finally:
            conn.close()


# ==========================
# Panel Ingresos
# ==========================
class IngresosPanel(QWidget):
    def __init__(self, volver_callback=None):
        super().__init__()
        self.volver_callback = volver_callback
        self.setWindowTitle("Módulo Ingresos")
        self.setMinimumSize(750, 450)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Título
        lbl_titulo = QLabel("Gestión de Ingresos")
        lbl_titulo.setStyleSheet("font-weight:bold; font-size:16pt")
        main_layout.addWidget(lbl_titulo)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["ID","Paciente","Fecha","Hora","Servicio","Cama"])
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setMinimumHeight(300)
        main_layout.addWidget(self.tabla, stretch=1)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_crear = QPushButton("Crear")
        self.btn_modificar = QPushButton("Modificar")
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_volver = QPushButton("Volver")
        btn_layout.addWidget(self.btn_crear)
        btn_layout.addWidget(self.btn_modificar)
        btn_layout.addWidget(self.btn_eliminar)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_volver)
        main_layout.addLayout(btn_layout)

        # Conectar botones
        self.btn_crear.clicked.connect(self.agregar)
        self.btn_modificar.clicked.connect(self.editar)
        self.btn_eliminar.clicked.connect(self.eliminar)
        self.btn_volver.clicked.connect(self.volver)

        self.listar_ingresos()

    def listar_ingresos(self):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.id_ingreso, p.ci, p.nombre, i.fecha_ingreso, i.hora_ingreso, i.servicio_hospitalario, i.cama
            FROM Ingreso i
            JOIN Paciente p ON i.ci = p.ci
            ORDER BY i.fecha_ingreso DESC, i.hora_ingreso DESC
        """)
        ingresos = cursor.fetchall()
        conn.close()

        self.tabla.setRowCount(0)
        for fila_idx, i in enumerate(ingresos):
            self.tabla.insertRow(fila_idx)
            self.tabla.setItem(fila_idx, 0, QTableWidgetItem(str(i[0])))
            self.tabla.setItem(fila_idx, 1, QTableWidgetItem(f"{i[2]} ({i[1]})"))  # Nombre (CI)
            self.tabla.setItem(fila_idx, 2, QTableWidgetItem(i[3]))
            self.tabla.setItem(fila_idx, 3, QTableWidgetItem(i[4]))
            self.tabla.setItem(fila_idx, 4, QTableWidgetItem(i[5]))
            self.tabla.setItem(fila_idx, 5, QTableWidgetItem(str(i[6])))

    def agregar(self):
        form = IngresoForm(self)
        if form.exec():
            self.listar_ingresos()

    def editar(self):
        selected = self.tabla.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Error", "Seleccione un ingreso para modificar")
            return
        id_ingreso = int(selected[0].text())
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT i.id_ingreso, i.ci, p.nombre, i.fecha_ingreso, i.hora_ingreso, i.servicio_hospitalario, i.cama
        FROM Ingreso i
        JOIN Paciente p ON i.ci = p.ci
        WHERE i.id_ingreso=?
        """, (id_ingreso,))

        ingreso = cursor.fetchone()
        conn.close()
        form = IngresoForm(self, ingreso)
        if form.exec():
            self.listar_ingresos()

    def eliminar(self):
        selected = self.tabla.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Error", "Seleccione un ingreso para eliminar")
            return
        id_ingreso = int(selected[0].text())
        reply = QMessageBox.question(self, "Confirmar", f"Eliminar ingreso {id_ingreso}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Ingreso WHERE id_ingreso=?", (id_ingreso,))
            conn.commit()
            conn.close()
            self.listar_ingresos()

    def volver(self):
        if self.volver_callback:
            self.volver_callback()
