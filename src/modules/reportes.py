# ========================================
# modules/reportes.py
# ========================================
import pandas as pd
import matplotlib.pyplot as plt
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table as PdfTable, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

console = Console()

# ========================================
# Función genérica para mostrar DataFrame
# ========================================
def mostrar_tabla(df: pd.DataFrame, titulo="Reporte"):
    if df.empty:
        console.print("⚠️ No hay datos disponibles.", style="bold yellow")
        return

    console.print(f"\n[bold cyan]{titulo}[/bold cyan]")
    tabla = Table(show_header=True, header_style="bold magenta")
    for col in df.columns:
        tabla.add_column(str(col))
    for _, row in df.iterrows():
        tabla.add_row(*[str(x) for x in row])
    console.print(tabla)

# ========================================
# Exportar a PDF
# ========================================
def exportar_pdf(df: pd.DataFrame, filename="reporte.pdf", titulo="Reporte"):
    if df.empty:
        console.print("⚠️ No hay datos para exportar.", style="bold yellow")
        return

    try:
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        elementos = []

        elementos.append(Paragraph(titulo, styles["Title"]))
        elementos.append(Spacer(1, 12))

        data = [list(df.columns)] + df.values.tolist()
        tabla = PdfTable(data)
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1976d2")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey)
        ]))

        elementos.append(tabla)
        doc.build(elementos)
        console.print(f"✅ Archivo PDF generado: {filename}", style="green")
    except Exception as e:
        console.print(f"❌ Error al exportar a PDF: {e}", style="bold red")

# ========================================
# Exportar a Excel (.xlsx)
# ========================================
def exportar_excel(df: pd.DataFrame, filename="reporte.xlsx"):
    if df.empty:
        console.print("⚠️ No hay datos para exportar.", style="bold yellow")
        return
    try:
        df.to_excel(filename, index=False)
        console.print(f"✅ Archivo Excel generado: {filename}", style="green")
    except Exception as e:
        console.print(f"❌ Error al exportar a Excel: {e}", style="bold red")

# ========================================
# Función principal de reportes
# ========================================
def consultas():
    console.print("\n[bold underline cyan]MENÚ DE REPORTES[/bold underline cyan]")
    console.print("1. Listar todos los pacientes")
    console.print("2. Reporte de medicamentos por categoría")
    console.print("3. Reporte de ventas mensuales")
    console.print("4. Gráfico de ventas por mes")
    console.print("0. Volver\n")

    opcion = Prompt.ask("Seleccione una opción", choices=["0","1","2","3","4"])

    # 1️⃣ Listar pacientes
    if opcion == "1":
        data = {
            "CI": ["1234567", "2345678", "3456789"],
            "Nombre": ["Ana Pérez", "Luis Rojas", "Carla Gómez"],
            "Edad": [30, 45, 25],
            "Sexo": ["F", "M", "F"]
        }
        df = pd.DataFrame(data)
        mostrar_tabla(df, "Lista de Pacientes")

        exportar = Prompt.ask("¿Exportar? (pdf/xlsx/n)", choices=["pdf","xlsx","n"])
        if exportar == "pdf":
            exportar_pdf(df, "pacientes.pdf", "Lista de Pacientes")
        elif exportar == "xlsx":
            exportar_excel(df, "pacientes.xlsx")

    # 2️⃣ Reporte de medicamentos por categoría
    elif opcion == "2":
        data = {
            "Categoría": ["Antibióticos", "Analgésicos", "Vitaminas"],
            "Cantidad": [120, 200, 150]
        }
        df = pd.DataFrame(data)
        mostrar_tabla(df, "Medicamentos por Categoría")

        exportar = Prompt.ask("¿Exportar? (pdf/xlsx/n)", choices=["pdf","xlsx","n"])
        if exportar == "pdf":
            exportar_pdf(df, "medicamentos.pdf", "Medicamentos por Categoría")
        elif exportar == "xlsx":
            exportar_excel(df, "medicamentos.xlsx")

    # 3️⃣ Reporte de ventas mensuales
    elif opcion == "3":
        data = {
            "Mes": ["Enero", "Febrero", "Marzo", "Abril"],
            "Ventas": [1500, 1800, 2100, 1950]
        }
        df = pd.DataFrame(data)
        mostrar_tabla(df, "Ventas Mensuales")

        exportar = Prompt.ask("¿Exportar? (pdf/xlsx/n)", choices=["pdf","xlsx","n"])
        if exportar == "pdf":
            exportar_pdf(df, "ventas.pdf", "Ventas Mensuales")
        elif exportar == "xlsx":
            exportar_excel(df, "ventas.xlsx")

    # 4️⃣ Gráfico de ventas
    elif opcion == "4":
        data = {
            "Mes": ["Enero", "Febrero", "Marzo", "Abril"],
            "Ventas": [1500, 1800, 2100, 1950]
        }
        df = pd.DataFrame(data)
        plt.bar(df["Mes"], df["Ventas"])
        plt.title("Ventas por Mes")
        plt.xlabel("Mes")
        plt.ylabel("Ventas (Bs)")
        plt.show()

    # 0️⃣ Volver
    elif opcion == "0":
        console.print("↩️ Volviendo al menú principal...", style="bold cyan")
