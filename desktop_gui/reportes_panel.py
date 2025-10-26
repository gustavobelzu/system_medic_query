import sqlite3, os
import pandas as pd
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QCheckBox, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QGridLayout
from PySide6.QtCore import QDate
from datetime import datetime
from .resultados_reportes import ResultadosReportes

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "emergencias.db")

def conectar():
    return sqlite3.connect(DB_PATH)

class ReportesPanel(QWidget):
    def __init__(self, volver_callback=None):
        super().__init__()
        self.volver_callback = volver_callback
        self.setWindowTitle("Módulo Reportes")
        self.setMinimumSize(900, 600)

        layout = QVBoxLayout()
        self.setLayout(layout)

        lbl_titulo = QLabel("📊 Reportes y Consultas")
        lbl_titulo.setStyleSheet("font-weight:bold; font-size:16pt")
        layout.addWidget(lbl_titulo)

        # Selección de tabla
        self.combo_tablas = QComboBox()
        layout.addWidget(QLabel("Seleccione una tabla:"))
        layout.addWidget(self.combo_tablas)
        self.combo_tablas.currentTextChanged.connect(self.cargar_columnas_tabla)

        # Columnas
        self.columnas_layout = QGridLayout()
        layout.addLayout(self.columnas_layout)

        # Pacientes
        self.combo_pacientes = QComboBox()
        self.combo_pacientes.addItem("Todos", None)
        layout.addWidget(QLabel("Filtrar por paciente:"))
        layout.addWidget(self.combo_pacientes)
        self.cargar_pacientes()

        # --- En la sección de fechas ---
        fechas_layout = QHBoxLayout()
        self.date_inicio = QDateEdit(QDate.currentDate().addMonths(-1))
        self.date_inicio.setCalendarPopup(True)
        self.date_fin = QDateEdit(QDate.currentDate())
        self.date_fin.setCalendarPopup(True)
        fechas_layout.addWidget(QLabel("Fecha de ingreso de pacientes:"))
        fechas_layout.addWidget(self.date_inicio)
        fechas_layout.addSpacing(20)
        fechas_layout.addWidget(QLabel("hasta"))
        fechas_layout.addWidget(self.date_fin)

        # Ordenar asc/desc
        self.cmb_orden = QComboBox()
        self.cmb_orden.addItems(["ASC", "DESC"])
        fechas_layout.addSpacing(20)
        fechas_layout.addWidget(QLabel("Orden:"))
        fechas_layout.addWidget(self.cmb_orden)

        layout.addLayout(fechas_layout)


        # Botones
        btn_layout = QHBoxLayout()
        self.btn_consultar = QPushButton("Consultar")
        self.btn_volver = QPushButton("Volver")
        btn_layout.addWidget(self.btn_consultar)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_volver)
        layout.addLayout(btn_layout)

        # Conexiones
        self.btn_consultar.clicked.connect(self.consultar)
        self.btn_volver.clicked.connect(self.volver)

        # Tabla previsualización opcional
        self.tabla = QTableWidget()
        layout.addWidget(self.tabla, stretch=1)

        self.df_resultado = pd.DataFrame()
        self.cargar_tablas()

    def cargar_tablas(self):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name!='sqlite_sequence';")
        tablas = [t[0] for t in cursor.fetchall()]
        conn.close()
        self.combo_tablas.addItems(tablas)

    def cargar_pacientes(self):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT ci, nombre FROM Paciente")
        for ci, nombre in cursor.fetchall():
            self.combo_pacientes.addItem(f"{nombre} ({ci})", ci)
        conn.close()

    def cargar_columnas_tabla(self):
        for i in reversed(range(self.columnas_layout.count())):
            widget = self.columnas_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        tabla = self.combo_tablas.currentText()
        if not tabla:
            return

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({tabla})")
        columnas = [col[1] for col in cursor.fetchall()]
        conn.close()

        self.columnas_checkboxes = []
        col_count = 3
        for idx, col in enumerate(columnas):
            cb = QCheckBox(col)
            cb.setChecked(True)
            row, col_idx = divmod(idx, col_count)
            self.columnas_layout.addWidget(cb, row, col_idx)
            self.columnas_checkboxes.append(cb)

    def consultar(self):
        tabla = self.combo_tablas.currentText()
        columnas = [cb.text() for cb in self.columnas_checkboxes if cb.isChecked()]
        if not columnas:
            QMessageBox.warning(self, "Error", "Seleccione al menos una columna")
            return

        columnas_sql = ", ".join(columnas)
        query = f"SELECT {columnas_sql} FROM {tabla} WHERE 1=1"

        ci = self.combo_pacientes.currentData()
        if ci:
            query += f" AND ci='{ci}'"

        f_inicio = self.date_inicio.date().toString("yyyy-MM-dd")
        f_fin = self.date_fin.date().toString("yyyy-MM-dd")
        if "fecha_ingreso" in columnas:  # filtro por rango de ingreso
            query += f" AND fecha_ingreso BETWEEN '{f_inicio}' AND '{f_fin}'"

        # Ordenar por nombre de paciente
        if "nombre" in columnas:  # suponiendo que la columna se llama 'nombre'
            query += f" ORDER BY nombre {self.cmb_orden.currentText()}"

        try:
            conn = conectar()
            df = pd.read_sql_query(query, conn)
            conn.close()

            if df.empty:
                QMessageBox.information(self, "Info", "No se encontraron registros")
                return

            usuario_actual = "Admin"
           # dentro de ReportesPanel.consultar()
            self.resultados_window = ResultadosReportes(
                df,
                nombre_tabla=tabla,
                usuario=usuario_actual,
                volver_callback=self.volver_al_panel_reportes  # <-- callback
            )
            self.resultados_window.show()


        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def volver(self):
        if self.volver_callback:
            self.volver_callback()
    
    def volver_al_panel_reportes(self):
         self.show()  # Muestra de nuevo el panel de reportes si lo habías ocultado
