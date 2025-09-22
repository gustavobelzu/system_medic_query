# src/modules/consultas.py
import sqlite3
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from pathlib import Path

DB_PATH = "database/emergencias.db"
console = Console()

# ==========================
# Conexión a la base de datos
# ==========================
def conectar():
    return sqlite3.connect(DB_PATH)

# ==========================
# Mostrar tabla con Rich + auditoría
# ==========================
def mostrar_tabla(headers, rows, title="Consulta", usuario=None, fecha=None, hora=None):
    table = Table(title=title)
    for h in headers:
        table.add_column(h)
    for row in rows:
        table.add_row(*[str(r) if r is not None else "" for r in row])
    console.print(table)

    # Auditoría al final
    if usuario and fecha and hora:
        console.print(f"[bold]Reporte generado por:[/bold] {usuario} | [bold]Fecha:[/bold] {fecha} | [bold]Hora:[/bold] {hora}", style="cyan")

# ==========================
# Exportar a PDF + auditoría
# ==========================
def exportar_pdf(headers, rows, title="Consulta", usuario=None, fecha=None, hora=None):
    ruta = Prompt.ask("Ruta completa para guardar el PDF (ej: C:/Users/Usuario/Desktop/consulta.pdf)")
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)  # Crear carpeta si no existe

    c = canvas.Canvas(str(ruta), pagesize=letter)
    width, height = letter
    y = height - 50

    # Encabezado
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, title)
    y -= 30

    # Columnas
    c.setFont("Helvetica-Bold", 12)
    for i, h in enumerate(headers):
        c.drawString(50 + i*100, y, h)
    y -= 20

    # Filas
    c.setFont("Helvetica", 10)
    for row in rows:
        for i, r in enumerate(row):
            c.drawString(50 + i*100, y, str(r))
        y -= 20
        if y < 70:  # dejar espacio para auditoría
            c.showPage()
            y = height - 50
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, y, title)
            y -= 30
            c.setFont("Helvetica-Bold", 12)
            for i, h in enumerate(headers):
                c.drawString(50 + i*100, y, h)
            y -= 20
            c.setFont("Helvetica", 10)

    # Auditoría al final
    if usuario and fecha and hora:
        y -= 10
        if y < 50:
            c.showPage()
            y = height - 50
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"Reporte generado por: {usuario} | Fecha: {fecha} | Hora: {hora}")

    c.save()
    console.print(f"✅ PDF generado en: {ruta}", style="green")

# ==========================
# Función principal de consultas
# ==========================
def consultas(user=None):
    conn = conectar()
    cursor = conn.cursor()
    tablas_disponibles = ["Paciente", "Estado", "Ingreso", "Egreso", "Usuario", "Personal", "Ingreso_Personal"]

    while True:
        console.print("\n--- MÓDULO CONSULTAS INTERACTIVAS ---", style="bold magenta")
        console.print("Tablas disponibles:", ", ".join(tablas_disponibles))
        console.print("0 - Salir")
        tabla = Prompt.ask("Ingrese la tabla que desea consultar").strip()

        if tabla == "0":
            break
        if tabla not in tablas_disponibles:
            console.print("❌ Tabla inválida.", style="red")
            continue

        # Columnas disponibles
        cursor.execute(f"PRAGMA table_info({tabla})")
        columnas = [info[1] for info in cursor.fetchall()]
        console.print("Columnas disponibles:", ", ".join(columnas))

        cols_input = Prompt.ask("Columnas a mostrar (separadas por coma, * para todas)", default="*").strip()
        columnas_a_mostrar = "*" if cols_input == "*" else [c.strip() for c in cols_input.split(",")]

        filtro = Prompt.ask("Filtro SQL opcional (ej: edad > 30) o ENTER para ninguno", default="").strip()
        query = f"SELECT {', '.join(columnas) if columnas_a_mostrar == '*' else ', '.join(columnas_a_mostrar)} FROM {tabla}"
        if filtro:
            query += f" WHERE {filtro}"

        try:
            cursor.execute(query)
            rows = cursor.fetchall()

            # Auditoría
            fecha_actual = datetime.now().strftime("%Y-%m-%d")
            hora_actual = datetime.now().strftime("%H:%M")
            usuario_actual = user[1] if user else "N/A"

            # Mostrar tabla en consola con auditoría única
            mostrar_tabla(
                headers=columnas_a_mostrar if columnas_a_mostrar != "*" else columnas,
                rows=rows,
                title=f"Consulta: {tabla}",
                usuario=usuario_actual,
                fecha=fecha_actual,
                hora=hora_actual
            )

            # Exportar a PDF
            if rows and Prompt.ask("¿Exportar a PDF? (s/n)", choices=["s","n"], default="n") == "s":
                exportar_pdf(
                    headers=columnas_a_mostrar if columnas_a_mostrar != "*" else columnas,
                    rows=rows,
                    title=f"Consulta: {tabla}",
                    usuario=usuario_actual,
                    fecha=fecha_actual,
                    hora=hora_actual
                )

        except Exception as e:
            console.print(f"❌ Error en la consulta: {e}", style="red")

    conn.close()
