import sqlite3, os
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QLabel, QMessageBox, QDialog, QFormLayout,
    QComboBox, QDateEdit, QTimeEdit
)
from PySide6.QtCore import QDate, QTime

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
        self.setFixedSize(400, 300)
        self.egreso = egreso

        layout = QVBoxLayout()
        self.setLayout(layout)
        form_layout = QFormLayout()

        # Pacientes ingresados
        self.cb_ingreso = QComboBox()
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.id_ingreso, p.ci, p.nombre, i.fecha_ingreso
            FROM Ingreso i
            JOIN Paciente p ON i.ci = p.ci
            ORDER BY i.fecha_ingreso DESC
        """)
        ingresos = cursor.fetchall()
        self.ingresos_dict = {}
        for i in ingresos:
            text = f"{i[2]} ({i[1]}) - {i[3]}"
            self.cb_ingreso.addItem(text)
            self.ingresos_dict[text] = i

        # Fecha y hora
        from PySide6.QtWidgets import QDateEdit, QTimeEdit
        from PySide6.QtCore import QDate, QTime
        self.date_egreso = QDateEdit(QDate.currentDate())
        self.date_egreso.setCalendarPopup(True)
        self.time_egreso = QTimeEdit(QTime.currentTime())

        # Estados: cargar desde tabla Estado
        self.cb_estado = QComboBox()
        cursor.execute("SELECT id_estado, estado FROM Estado ORDER BY estado")
        self.estados = cursor.fetchall()  # lista de tuplas (id_estado, nombre)
        for e in self.estados:
            self.cb_estado.addItem(e[1], e[0])
        conn.close()

        form_layout.addRow("Ingreso:", self.cb_ingreso)
        form_layout.addRow("Fecha de egreso:", self.date_egreso)
        form_layout.addRow("Hora de egreso:", self.time_egreso)
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
            # Seleccionar ingreso correspondiente
            ingreso_text = f"{egreso[2]} ({egreso[1]}) - {egreso[3]}"
            index = self.cb_ingreso.findText(ingreso_text)
            if index >= 0:
                self.cb_ingreso.setCurrentIndex(index)
            self.cb_ingreso.setEnabled(False)

            self.date_egreso.setDate(QDate.fromString(egreso[4], "yyyy-MM-dd"))
            self.time_egreso.setTime(QTime.fromString(egreso[5], "HH:mm"))

            # Seleccionar estado según id_estado
            estado_id = egreso[6]  # suponer que egreso[6] es id_estado
            for i in range(self.cb_estado.count()):
                if self.cb_estado.itemData(i) == estado_id:
                    self.cb_estado.setCurrentIndex(i)
                    break

    def guardar(self):
        ingreso_text = self.cb_ingreso.currentText()
        ingreso = self.ingresos_dict.get(ingreso_text)
        if not ingreso and not self.egreso:
            QMessageBox.warning(self, "Error", "Seleccione un ingreso válido")
            return

        id_ingreso = ingreso[0] if ingreso else self.egreso[0]
        ci = ingreso[1] if ingreso else self.egreso[2]
        fecha_ingreso = ingreso[3] if ingreso else self.egreso[3]

        fecha_egreso = self.date_egreso.date().toString("yyyy-MM-dd")
        hora_egreso = self.time_egreso.time().toString("HH:mm")
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
            SELECT e.id_egreso, e.id_ingreso, e.ci, i.fecha_ingreso, e.fecha_egreso, e.hora_egreso, e.estado_egreso,
                   p.nombre
            FROM Egreso e
            JOIN Ingreso i ON e.id_ingreso = i.id_ingreso
            JOIN Paciente p ON e.ci = p.ci
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
