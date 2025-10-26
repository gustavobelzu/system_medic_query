import sqlite3, os
import pandas as pd
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox
)
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "emergencias.db")
REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "reportes")

def conectar():
    return sqlite3.connect(DB_PATH)

def asegurar_directorio():
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)

class ReportesPanel(QWidget):
    def __init__(self, volver_callback=None):
        super().__init__()
        self.volver_callback = volver_callback
        self.setWindowTitle("Módulo Reportes")
        self.setMinimumSize(800, 500)

        layout = QVBoxLayout()
        self.setLayout(layout)

        lbl_titulo = QLabel("📊 Reportes y Consultas")
        lbl_titulo.setStyleSheet("font-weight:bold; font-size:16pt")
        layout.addWidget(lbl_titulo)

        # Combo de tablas
        self.combo_tablas = QComboBox()
        layout.addWidget(QLabel("Seleccione una tabla:"))
        layout.addWidget(self.combo_tablas)

        # Input columnas
        layout.addWidget(QLabel("Columnas (coma separadas, * para todas):"))
        self.txt_columnas = QLineEdit("*")
        layout.addWidget(self.txt_columnas)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_consultar = QPushButton("Consultar")
        self.btn_exportar_pdf = QPushButton("Exportar PDF")
        self.btn_exportar_excel = QPushButton("Exportar Excel")
        self.btn_volver = QPushButton("Volver")
        btn_layout.addWidget(self.btn_consultar)
        btn_layout.addWidget(self.btn_exportar_pdf)
        btn_layout.addWidget(self.btn_exportar_excel)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_volver)
        layout.addLayout(btn_layout)

        # Tabla de resultados
        self.tabla = QTableWidget()
        layout.addWidget(self.tabla, stretch=1)

        self.btn_consultar.clicked.connect(self.consultar)
        self.btn_exportar_pdf.clicked.connect(self.exportar_pdf)
        self.btn_exportar_excel.clicked.connect(self.exportar_excel)
        self.btn_volver.clicked.connect(self.volver)

        self.df_resultado = pd.DataFrame()
        self.cargar_tablas()

    def cargar_tablas(self):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = [t[0] for t in cursor.fetchall()]
        conn.close()
        self.combo_tablas.addItems(tablas)

    def consultar(self):
        tabla = self.combo_tablas.currentText()
        columnas = self.txt_columnas.text().strip()
        if columnas == "":
            columnas = "*"
        query = f"SELECT {columnas} FROM {tabla}"
        try:
            conn = conectar()
            self.df_resultado = pd.read_sql_query(query, conn)
            conn.close()
            if self.df_resultado.empty:
                QMessageBox.information(self, "Info", "No se encontraron registros")
                self.tabla.setRowCount(0)
                self.tabla.setColumnCount(0)
                return
            self.mostrar_tabla()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Ocurrió un error:\n{e}")

    def mostrar_tabla(self):
        self.tabla.setColumnCount(len(self.df_resultado.columns))
        self.tabla.setHorizontalHeaderLabels(self.df_resultado.columns.tolist())
        self.tabla.setRowCount(len(self.df_resultado))
        for i, row in self.df_resultado.iterrows():
            for j, val in enumerate(row):
                self.tabla.setItem(i, j, QTableWidgetItem(str(val)))

    def exportar_pdf(self):
        if self.df_resultado.empty:
            QMessageBox.warning(self, "Error", "Primero realice una consulta")
            return
        asegurar_directorio()
        filename = f"{self.combo_tablas.currentText()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        ruta = os.path.join(REPORT_DIR, filename)
        doc = SimpleDocTemplate(ruta, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        elements.append(Paragraph(f"Reporte de {self.combo_tablas.currentText()}", styles["Title"]))
        elements.append(Spacer(1, 12))
        data = [self.df_resultado.columns.tolist()] + self.df_resultado.values.tolist()
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0), colors.HexColor("#1976d2")),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
            ('GRID',(0,0),(-1,-1),0.5,colors.grey)
        ]))
        elements.append(table)
        doc.build(elements)
        QMessageBox.information(self, "Éxito", f"PDF generado:\n{ruta}")

    def exportar_excel(self):
        if self.df_resultado.empty:
            QMessageBox.warning(self, "Error", "Primero realice una consulta")
            return
        asegurar_directorio()
        filename = f"{self.combo_tablas.currentText()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        ruta = os.path.join(REPORT_DIR, filename)
        self.df_resultado.to_excel(ruta, index=False)
        QMessageBox.information(self, "Éxito", f"Excel generado:\n{ruta}")

    def volver(self):
        if self.volver_callback:
            self.volver_callback()
