import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

DB_PATH = "database/emergencias.db"
console = Console()

# ==============================
# Función de conexión a la base
# ==============================
def conectar():
    return sqlite3.connect(DB_PATH)

# ==============================
# Mostrar tabla en Rich
# ==============================
def mostrar_tabla(df: pd.DataFrame, title="Reporte"):
    if df.empty:
        console.print("⚠️ No hay datos disponibles.", style="bold yellow")
        return
    table = Table(title=title)
    for col in df.columns:
        table.add_column(str(col))
    for _, row in df.iterrows():
        table.add_row(*[str(x) if x is not None else "" for x in row])
    console.print(table)

# ==============================
# Exportar a PDF
# ==============================
def exportar_pdf(df: pd.DataFrame, filename="reporte.pdf", title="Reporte"):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, title)
    y -= 30

    c.setFont("Helvetica-Bold", 12)
    for i, col in enumerate(df.columns):
        c.drawString(50 + i * 100, y, str(col))
    y -= 20

    c.setFont("Helvetica", 10)
    for _, row in df.iterrows():
        for i, val in enumerate(row):
            c.drawString(50 + i * 100, y, str(val))
        y -= 20
        if y < 50:
            c.showPage()
            y = height - 50

    c.save()
    console.print(f"✅ PDF generado: {filename}", style="green")

# ==============================
# Graficar con pandas y matplotlib
# ==============================
def graficar(df, columna, titulo="Gráfico de Datos"):
    if df.empty or columna not in df.columns:
        console.print("⚠️ No hay datos o columna inválida para graficar.", style="yellow")
        return
    df[columna].value_counts().plot(kind="bar", color="skyblue", edgecolor="black")
    plt.title(titulo)
    plt.xlabel(columna)
    plt.ylabel("Cantidad")
    plt.tight_layout()
    plt.show()

# ==============================
# Módulo principal de reportes
# ==============================
def consultas():
    conn = conectar()
    console.print("\n[bold magenta]=== MÓDULO DE REPORTES Y CONSULTAS ===[/bold magenta]")

    while True:
        console.print("""
1. Listar todos los pacientes
2. Ingresos por paciente
3. Egresos por paciente
4. Pacientes activos
5. Gráfico: Pacientes por estado
6. Volver al menú principal
""")
        opcion = Prompt.ask("Seleccione una opción", choices=["1", "2", "3", "4", "5", "6"])

        if opcion == "1":
            df = pd.read_sql_query("""
                SELECT p.ci, p.nombre, p.edad, p.sexo, p.departamento, p.telefono, e.estado
                FROM Paciente p
                LEFT JOIN Estado e ON p.id_estado = e.id_estado
            """, conn)
            mostrar_tabla(df, "Todos los Pacientes")
            if Prompt.ask("¿Exportar a PDF? (s/n)", choices=["s","n"]) == "s":
                exportar_pdf(df, "pacientes.pdf", "Todos los Pacientes")

        elif opcion == "2":
            ci = Prompt.ask("Ingrese CI del paciente").strip()
            df = pd.read_sql_query("""
                SELECT i.id_ingreso, i.fecha_ingreso, i.hora_ingreso, i.servicio_hospitalario, i.cama
                FROM Ingreso i
                WHERE i.ci = ?
            """, conn, params=(ci,))
            mostrar_tabla(df, f"Ingresos del Paciente {ci}")
            if not df.empty and Prompt.ask("¿Exportar a PDF? (s/n)", choices=["s","n"]) == "s":
                exportar_pdf(df, f"ingresos_{ci}.pdf", f"Ingresos del Paciente {ci}")

        elif opcion == "3":
            ci = Prompt.ask("Ingrese CI del paciente").strip()
            df = pd.read_sql_query("""
                SELECT e.id_egreso, e.fecha_egreso, e.hora_egreso, e.estancia, e.estado_egreso
                FROM Egreso e
                WHERE e.ci = ?
            """, conn, params=(ci,))
            mostrar_tabla(df, f"Egresos del Paciente {ci}")
            if not df.empty and Prompt.ask("¿Exportar a PDF? (s/n)", choices=["s","n"]) == "s":
                exportar_pdf(df, f"egresos_{ci}.pdf", f"Egresos del Paciente {ci}")

        elif opcion == "4":
            df = pd.read_sql_query("""
                SELECT i.id_ingreso, p.nombre, i.fecha_ingreso, i.hora_ingreso, i.servicio_hospitalario
                FROM Ingreso i
                JOIN Paciente p ON i.ci = p.ci
                LEFT JOIN Egreso e ON i.id_ingreso = e.id_ingreso
                WHERE e.id_egreso IS NULL
            """, conn)
            mostrar_tabla(df, "Pacientes Activos")
            if not df.empty and Prompt.ask("¿Exportar a PDF? (s/n)", choices=["s","n"]) == "s":
                exportar_pdf(df, "pacientes_activos.pdf", "Pacientes Activos")

        elif opcion == "5":
            df = pd.read_sql_query("""
                SELECT e.estado, COUNT(*) as cantidad
                FROM Paciente p
                LEFT JOIN Estado e ON p.id_estado = e.id_estado
                GROUP BY e.estado
            """, conn)
            mostrar_tabla(df, "Pacientes por Estado")
            graficar(df, "estado", "Pacientes por Estado")

        elif opcion == "6":
            break

    conn.close()
