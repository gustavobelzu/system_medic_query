import sqlite3
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QLabel, QMessageBox, QDialog, QFormLayout, QLineEdit, QComboBox
)
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "emergencias.db")

def conectar():
    return sqlite3.connect(DB_PATH)

# ==========================
# Formulario de Egreso
# ==========================
class EgresoForm(QDialog):
    def __init__(self, parent=None, egreso=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar/Editar Egreso")
        self.setFixedSize(350, 300)
        self.egreso = egreso

        layout = QVBoxLayout()
        self.setLayout(layout)

        form_layout = QFormLayout()

        # Ingreso a seleccionar
        self.cb_ingreso = QComboBox()
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.id_ingreso, p.ci, p.nombre, i.fecha_ingreso
            FROM Ingreso i
            JOIN Paciente p ON i.ci = p.ci
            LEFT JOIN Egreso e ON i.id_ingreso = e.id_ingreso
            WHERE e.id_egreso IS NULL
        """)
        ingresos = cursor.fetchall()
        conn.close()
        self.ingresos_dict = {f"{i[2]} ({i[1]}) - {i[3]}": i for i in ingresos}
        self.cb_ingreso.addItems(self.ingresos_dict.keys())

        self.txt_fecha = QLineEdit(datetime.now().strftime("%Y-%m-%d"))
        self.txt_hora = QLineEdit(datetime.now().strftime("%H:%M"))
        self.cb_estado = QComboBox()
        self.cb_estado.addItems(["Recuperado","Trasladado","Fallecido"])

        form_layout.addRow("Ingreso:", self.cb_ingreso)
        form_layout.addRow("Fecha de egreso:", self.txt_fecha)
        form_layout.addRow("Hora de egreso:", self.txt_hora)
        form_layout.addRow("Estado:", self.cb_estado)

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

        # Si es edición
        if egreso:
            self.cb_ingreso.setEnabled(False)
            self.cb_ingreso.addItem(f"{egreso[1]} ({egreso[2]}) - {egreso[3]}")
            self.cb_ingreso.setCurrentIndex(0)
            self.txt_fecha.setText(egreso[4])
            self.txt_hora.setText(egreso[5])
            self.cb_estado.setCurrentText(egreso[6])

    def guardar(self):
        ingreso_text = self.cb_ingreso.currentText()
        ingreso = self.ingresos_dict.get(ingreso_text) if not self.egreso else (None, self.egreso[2], self.egreso[1], self.egreso[3], self.egreso[4])
        if not ingreso and not self.egreso:
            QMessageBox.warning(self, "Error", "Debe seleccionar un ingreso válido")
            return

        id_ingreso = ingreso[0] if ingreso else self.egreso[0]
        ci = ingreso[1] if ingreso else self.egreso[2]
        fecha_ingreso = ingreso[3] if ingreso else self.egreso[3]

        fecha_egreso = self.txt_fecha.text().strip()
        hora_egreso = self.txt_hora.text().strip()
        estado_egreso = self.cb_estado.currentText()

        # Calcular estancia
        fecha_ingreso_dt = datetime.strptime(fecha_ingreso, "%Y-%m-%d")
        fecha_egreso_dt = datetime.strptime(fecha_egreso, "%Y-%m-%d")
        estancia = (fecha_egreso_dt - fecha_ingreso_dt).days

        conn = conectar()
        cursor = conn.cursor()
        try:
            if self.egreso:
                cursor.execute("""
                    UPDATE Egreso
                    SET fecha_egreso=?, hora_egreso=?, estado_egreso=?, estancia=?
                    WHERE id_egreso=?
                """, (fecha_egreso, hora_egreso, estado_egreso, estancia, self.egreso[0]))
            else:
                cursor.execute("""
                    INSERT INTO Egreso (id_ingreso, ci, fecha_egreso, hora_egreso, estancia, estado_egreso)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (id_ingreso, ci, fecha_egreso, hora_egreso, estancia, estado_egreso))
            conn.commit()
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Ocurrió un error: {e}")
        finally:
            conn.close()

# ==========================
# Panel Egresos
# ==========================
class EgresosPanel(QWidget):
    def __init__(self, volver_callback=None):
        super().__init__()
        self.volver_callback = volver_callback
        self.setWindowTitle("Módulo Egresos")
        self.setMinimumSize(750, 450)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        lbl_titulo = QLabel("Gestión de Egresos")
        lbl_titulo.setStyleSheet("font-weight:bold; font-size:16pt")
        main_layout.addWidget(lbl_titulo)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["ID","Paciente","Fecha","Hora","Estancia","Estado"])
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
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

        self.listar_egresos()

    def listar_egresos(self):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.id_egreso, p.nombre, e.fecha_egreso, e.hora_egreso, e.estancia, e.estado_egreso
            FROM Egreso e
            JOIN Paciente p ON e.ci = p.ci
            ORDER BY e.fecha_egreso DESC
        """)
        egresos = cursor.fetchall()
        conn.close()

        self.tabla.setRowCount(0)
        for fila_idx, e in enumerate(egresos):
            self.tabla.insertRow(fila_idx)
            for col_idx, valor in enumerate(e):
                self.tabla.setItem(fila_idx, col_idx, QTableWidgetItem(str(valor)))

    def agregar(self):
        form = EgresoForm(self)
        if form.exec():
            self.listar_egresos()

    def editar(self):
        selected = self.tabla.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Error", "Seleccione un egreso para modificar")
            return
        id_egreso = selected[0].text()
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT e.id_egreso, e.id_ingreso, e.ci, i.fecha_ingreso, e.fecha_egreso, e.hora_egreso, e.estado_egreso
        FROM Egreso e
        JOIN Ingreso i ON e.id_ingreso = i.id_ingreso
        WHERE e.id_egreso=?
        """, (id_egreso,))

        egreso = cursor.fetchone()
        conn.close()
        form = EgresoForm(self, egreso)
        if form.exec():
            self.listar_egresos()

    def eliminar(self):
        selected = self.tabla.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Error", "Seleccione un egreso para eliminar")
            return
        id_egreso = selected[0].text()
        reply = QMessageBox.question(self, "Confirmar", f"Eliminar egreso {id_egreso}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Egreso WHERE id_egreso=?", (id_egreso,))
            conn.commit()
            conn.close()
            self.listar_egresos()

    def volver(self):
        if self.volver_callback:
            self.volver_callback()
