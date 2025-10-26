import os
import pandas as pd
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "reportes")

def asegurar_directorio():
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)

class ResultadosReportes(QWidget):
    def __init__(self, df, nombre_tabla="", usuario="", volver_callback=None):
        super().__init__()
        self.df = df
        self.nombre_tabla = nombre_tabla
        self.usuario = usuario
        self.volver_callback = volver_callback
        self.setWindowTitle("Resultados del Reporte")
        self.setMinimumSize(900, 550)

        layout = QVBoxLayout(self)
        lbl = QLabel(f"📄 Resultados de: {self.nombre_tabla}")
        lbl.setStyleSheet("font-weight:bold; font-size:16pt; color:#1976d2")
        layout.addWidget(lbl)

        # Tabla
        self.tabla = QTableWidget()
        layout.addWidget(self.tabla)
        self.mostrar_tabla()

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_pdf = QPushButton("Exportar PDF")
        self.btn_excel = QPushButton("Exportar Excel")
        self.btn_volver = QPushButton("Volver")
        btn_layout.addWidget(self.btn_pdf)
        btn_layout.addWidget(self.btn_excel)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_volver)
        layout.addLayout(btn_layout)

        self.btn_pdf.clicked.connect(self.exportar_pdf)
        self.btn_excel.clicked.connect(self.exportar_excel)
        self.btn_volver.clicked.connect(self.volver)

    def mostrar_tabla(self):
        self.tabla.setColumnCount(len(self.df.columns))
        self.tabla.setRowCount(len(self.df))
        self.tabla.setHorizontalHeaderLabels(self.df.columns.tolist())
        for i, row in self.df.iterrows():
            for j, val in enumerate(row):
                self.tabla.setItem(i, j, QTableWidgetItem(str(val)))

    def exportar_pdf(self):
        if self.df.empty:
            QMessageBox.warning(self, "Error", "No hay datos para exportar")
            return
        asegurar_directorio()
        filename = f"{self.nombre_tabla}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        ruta = os.path.join(REPORT_DIR, filename)

        doc = SimpleDocTemplate(ruta, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Título de tabla en color
        elements.append(Paragraph(f"Reporte: {self.nombre_tabla}", styles["Title"]))
        elements.append(Spacer(1,12))

        # Datos
        data = [self.df.columns.tolist()] + self.df.values.tolist()
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0), colors.HexColor("#1976d2")),
            ('TEXTCOLOR',(0,0),(-1,0), colors.white),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
            ('GRID',(0,0),(-1,-1),0.5, colors.grey)
        ]))
        elements.append(table)
        elements.append(Spacer(1,12))

        # Info de usuario y fecha
        export_info = f"Usuario: {self.usuario} | Fecha de exportación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        elements.append(Paragraph(export_info, styles["Normal"]))

        doc.build(elements)
        QMessageBox.information(self, "Éxito", f"PDF generado:\n{ruta}")

    def exportar_excel(self):
        if self.df.empty:
            QMessageBox.warning(self, "Error", "No hay datos para exportar")
            return
        asegurar_directorio()
        filename = f"{self.nombre_tabla}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        ruta = os.path.join(REPORT_DIR, filename)

        # Crear un DataFrame con encabezados adicionales
        df_export = self.df.copy()
        # Agregar info de usuario y fecha al final
        info = pd.DataFrame({
            "": ["Usuario:", "Fecha de exportación:"],
            "Valor": [self.usuario, datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        })
        with pd.ExcelWriter(ruta, engine="openpyxl") as writer:
            df_export.to_excel(writer, index=False, sheet_name="Datos")
            info.to_excel(writer, index=False, sheet_name="Datos", startrow=len(df_export)+2)

        QMessageBox.information(self, "Éxito", f"Excel generado:\n{ruta}")

    def volver(self):
        self.close()
        if self.volver_callback:
            self.volver_callback()
   
