import os
import sqlite3
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table as PdfTable, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import getpass

console = Console()

DB_PATH = "database/emergencias.db"

# ==============================
# Crear carpeta de reportes
# ==============================
def crear_carpeta_reportes():
    carpeta = os.path.join(os.getcwd(), "reportes")
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
    return carpeta

# ==============================
# Conectar a la base de datos
# ==============================
def conectar():
    return sqlite3.connect(DB_PATH)

# ==============================
# Listar tablas
# ==============================
def listar_tablas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tablas

# ==============================
# Listar columnas
# ==============================
def listar_columnas(tabla):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({tabla})")
    columnas = [row[1] for row in cursor.fetchall()]
    conn.close()
    return columnas

# ==============================
# Consultar datos
# ==============================
def consultar_tabla(tabla, columnas):
    cols = ", ".join(columnas)
    conn = conectar()
    df = pd.read_sql_query(f"SELECT {cols} FROM {tabla}", conn)
    conn.close()
    return df

# ==============================
# Mostrar tabla con Rich
# ==============================
def mostrar_tabla(df, titulo="Reporte"):
    if df.empty:
        console.print("⚠️ No hay datos", style="bold yellow")
        return
    table = Table(show_header=True, header_style="bold magenta")
    for col in df.columns:
        table.add_column(col)
    for _, row in df.iterrows():
        table.add_row(*[str(x) for x in row])
    console.print(table)

# ==============================
# Exportar a PDF
# ==============================
def exportar_pdf(df, base_name="reporte"):
    usuario = getpass.getuser()
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    filename = generar_nombre_archivo(base_name, "pdf")

    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Título
    elements.append(Paragraph(f"<b>Reporte: {base_name}</b>", styles['Title']))
    elements.append(Spacer(1, 12))

    # Tabla de datos
    data = [df.columns.tolist()] + df.values.tolist()
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1976d2')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 24))

    # Pie de página
    pie = f"Generado por {usuario} el {fecha_actual}"
    elements.append(Paragraph(pie, styles['Normal']))

    doc.build(elements)
    print(f"✅ PDF generado: {filename}")


# ==============================
# Exportar a Excel
# ==============================
def exportar_excel(df, base_name="reporte"):
    usuario = getpass.getuser()
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    filename = generar_nombre_archivo(base_name, "xlsx")

    # Crear el archivo
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Datos')

        # Agregar pie de página
        hoja = writer.sheets['Datos']
        fila = len(df) + 3
        hoja.cell(row=fila, column=1, value=f"Generado por {usuario} el {fecha_actual}")

    print(f"✅ Excel generado: {filename}")


# ==============================
# Menú dinámico
# ==============================
def menu_reportes():
    console.print("\n[bold underline cyan]MENÚ DINÁMICO DE REPORTES[/bold underline cyan]")

    tablas = listar_tablas()
    if not tablas:
        console.print("❌ No hay tablas disponibles en la base de datos.", style="bold red")
        return

    # Seleccionar tabla
    console.print("\nTablas disponibles:")
    for i, t in enumerate(tablas, start=1):
        console.print(f"{i}. {t}")
    t_idx = int(Prompt.ask("Seleccione la tabla", choices=[str(i) for i in range(1, len(tablas)+1)])) - 1
    tabla = tablas[t_idx]

    # Columnas
    columnas = listar_columnas(tabla)
    console.print(f"\nColumnas disponibles en {tabla}: {', '.join(columnas)}")
    col_indices = Prompt.ask(
        "Ingrese los números de las columnas a exportar (ej: 1,2,3) o Enter para todas",
        default=",".join([str(i+1) for i in range(len(columnas))])
    )
    col_seleccionadas = [columnas[int(i)-1] for i in col_indices.split(",")]

    # Consultar y mostrar datos
    df = consultar_tabla(tabla, col_seleccionadas)
    mostrar_tabla(df, f"Datos de {tabla}")

    # Exportar
    exportar = Prompt.ask("¿Exportar? (pdf/xlsx/n)", choices=["pdf","xlsx","n"])
    if exportar == "pdf":
        exportar_pdf(df, f"{tabla}.pdf", f"{tabla} - Reporte")
    elif exportar == "xlsx":
        exportar_excel(df, f"{tabla}.xlsx")

#Función para generar nombre del archivo
def generar_nombre_archivo(base_name, extension):
    usuario = getpass.getuser()
    fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{usuario}_{fecha_hora}.{extension}"