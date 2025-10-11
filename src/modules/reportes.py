import sqlite3
import pandas as pd
import getpass
from datetime import datetime
from rich.console import Console
from rich.table import Table as RichTable
from rich.prompt import Prompt
from rich.panel import Panel
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os

DB_PATH = "database/emergencias.db"
REPORT_DIR = "reportes"
console = Console()

# ==========================
# Crear carpeta de reportes si no existe
# ==========================
def asegurar_directorio():
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)

# ==========================
# Conexión a la base de datos
# ==========================
def conectar():
    return sqlite3.connect(DB_PATH)

# ==========================
# Mostrar tabla en consola
# ==========================
def mostrar_tabla(df, titulo="Reporte"):
    table = RichTable(title=titulo)
    for col in df.columns:
        table.add_column(col)
    for row in df.itertuples(index=False):
        table.add_row(*[str(x) for x in row])
    console.print(table)

# ==========================
# Exportar a PDF
# ==========================
def exportar_pdf(df, usuario_nombre, filename=None, titulo="Reporte"):
    asegurar_directorio()
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    if filename is None:
        filename = f"{titulo.replace(' ', '_')}.pdf"

    ruta_completa = os.path.join(REPORT_DIR, filename)
    doc = SimpleDocTemplate(ruta_completa, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Título
    elements.append(Paragraph(f"<b>{titulo}</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    # Tabla de datos
    data = [df.columns.tolist()] + df.values.tolist()

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1976d2")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 24))

    # Pie de página
    pie = f"Generado por {usuario_nombre} el {fecha_actual}"
    elements.append(Paragraph(pie, styles["Normal"]))

    doc.build(elements)
    console.print(f"✅ PDF generado: {ruta_completa}", style="green")

# ==========================
# Exportar a Excel
# ==========================
def exportar_excel(df, usuario_nombre, filename=None):
    asegurar_directorio()
    fecha_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if filename is None:
        filename = f"reporte_{fecha_actual}.xlsx"

    ruta_completa = os.path.join(REPORT_DIR, filename)
    df.to_excel(ruta_completa, index=False)
    console.print(f"✅ Archivo Excel generado: {ruta_completa}", style="green")

# ==========================
# Módulo principal de reportes
# ==========================
def menu_reportes(usuario=None):
    conn = conectar()
    cursor = conn.cursor()

    nombre_usuario = usuario[1] if usuario else getpass.getuser()
    console.print(Panel(f"📊 MÓDULO DE REPORTES Y CONSULTAS\n[bold]Usuario conectado:[/bold] {nombre_usuario}", style="bold cyan"))

    # Obtener todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = [t[0] for t in cursor.fetchall()]

    if not tablas:
        console.print("⚠️ No se encontraron tablas en la base de datos.", style="bold red")
        return

    while True:
        console.print("\nTablas disponibles:")
        for i, t in enumerate(tablas, 1):
            console.print(f"{i}. {t}")

        console.print(f"{len(tablas)+1}. Volver al menú principal")

        opcion = Prompt.ask("Seleccione una tabla", choices=[str(i) for i in range(1, len(tablas)+2)])

        if int(opcion) == len(tablas) + 1:
            break

        tabla = tablas[int(opcion)-1]

        # Obtener columnas de la tabla
        cursor.execute(f"PRAGMA table_info({tabla})")
        columnas = [c[1] for c in cursor.fetchall()]
        console.print("\nCampos disponibles:", style="bold yellow")
        console.print(", ".join(columnas))

        campos = Prompt.ask("Ingrese los campos separados por coma (o * para todos)").strip()
        if campos == "*":
            query = f"SELECT * FROM {tabla}"
        else:
            query = f"SELECT {campos} FROM {tabla}"

        try:
            df = pd.read_sql_query(query, conn)
            if df.empty:
                console.print("⚠️ No se encontraron registros.", style="bold red")
                continue

            mostrar_tabla(df, titulo=f"Reporte de {tabla}")

            exportar = Prompt.ask("¿Exportar? (pdf/xlsx/n)", choices=["pdf", "xlsx", "n"])
            if exportar == "pdf":
                exportar_pdf(df, nombre_usuario, f"{tabla}.pdf", f"Reporte de {tabla}")
            elif exportar == "xlsx":
                exportar_excel(df, nombre_usuario, f"{tabla}.xlsx")

        except Exception as e:
            console.print(f"❌ Error en la consulta: {e}", style="bold red")

    conn.close()

# ==========================
# Ejecución independiente
# ==========================
if __name__ == "__main__":
    menu_reportes()
