import sqlite3
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

DB_PATH = "database/emergencias.db"
console = Console()

def conectar():
    return sqlite3.connect(DB_PATH)

# ==========================
# Mostrar resultados en Rich Table
# ==========================
def mostrar_tabla(headers, rows, title="Reporte"):
    table = Table(title=title)
    for h in headers:
        table.add_column(h)
    for row in rows:
        table.add_row(*[str(r) if r is not None else "" for r in row])
    console.print(table)

# ==========================
# Exportar a PDF
# ==========================
def exportar_pdf(headers, rows, filename="reporte.pdf", title="Reporte"):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, title)
    y -= 30

    c.setFont("Helvetica-Bold", 12)
    for i, h in enumerate(headers):
        c.drawString(50 + i*100, y, h)
    y -= 20

    c.setFont("Helvetica", 10)
    for row in rows:
        for i, r in enumerate(row):
            c.drawString(50 + i*100, y, str(r))
        y -= 20
        if y < 50:
            c.showPage()
            y = height - 50
    c.save()
    console.print(f"✅ PDF generado: {filename}", style="green")

# ==========================
# Consultas disponibles
# ==========================
def consultas():
    conn = conectar()
    cursor = conn.cursor()

    while True:
        console.print("\n--- MÓDULO CONSULTAS Y REPORTES ---", style="bold magenta")
        console.print("1. Listar todos los pacientes")
        console.print("2. Ingresos por paciente")
        console.print("3. Egresos por paciente")
        console.print("4. Pacientes activos (ingresados y sin egreso)")
        console.print("5. Volver")
        opcion = Prompt.ask("Seleccione una opción", choices=["1","2","3","4","5"])

        if opcion == "1":
            cursor.execute("""
                SELECT p.ci, p.nombre, p.edad, p.sexo, p.departamento, p.telefono, e.estado
                FROM Paciente p
                LEFT JOIN Estado e ON p.id_estado = e.id_estado
            """)
            rows = cursor.fetchall()
            headers = ["CI","Nombre","Edad","Sexo","Depto","Tel","Estado"]
            mostrar_tabla(headers, rows, title="Todos los Pacientes")
            if Prompt.ask("¿Exportar a PDF? (s/n)", choices=["s","n"]) == "s":
                exportar_pdf(headers, rows, filename="pacientes.pdf", title="Todos los Pacientes")

        elif opcion == "2":
            ci = Prompt.ask("Ingrese CI del paciente").strip()
            cursor.execute("""
                SELECT i.id_ingreso, i.fecha_ingreso, i.hora_ingreso, i.servicio_hospitalario, i.cama
                FROM Ingreso i
                WHERE i.ci = ?
            """, (ci,))
            rows = cursor.fetchall()
            headers = ["ID Ingreso","Fecha","Hora","Servicio","Cama"]
            mostrar_tabla(headers, rows, title=f"Ingresos del Paciente {ci}")
            if rows and Prompt.ask("¿Exportar a PDF? (s/n)", choices=["s","n"]) == "s":
                exportar_pdf(headers, rows, filename=f"ingresos_{ci}.pdf", title=f"Ingresos del Paciente {ci}")

        elif opcion == "3":
            ci = Prompt.ask("Ingrese CI del paciente").strip()
            cursor.execute("""
                SELECT e.id_egreso, e.fecha_egreso, e.hora_egreso, e.estancia, e.estado_egreso
                FROM Egreso e
                WHERE e.ci = ?
            """, (ci,))
            rows = cursor.fetchall()
            headers = ["ID Egreso","Fecha","Hora","Estancia","Estado"]
            mostrar_tabla(headers, rows, title=f"Egresos del Paciente {ci}")
            if rows and Prompt.ask("¿Exportar a PDF? (s/n)", choices=["s","n"]) == "s":
                exportar_pdf(headers, rows, filename=f"egresos_{ci}.pdf", title=f"Egresos del Paciente {ci}")

        elif opcion == "4":
            cursor.execute("""
                SELECT i.id_ingreso, p.nombre, i.fecha_ingreso, i.hora_ingreso, i.servicio_hospitalario
                FROM Ingreso i
                JOIN Paciente p ON i.ci = p.ci
                LEFT JOIN Egreso e ON i.id_ingreso = e.id_ingreso
                WHERE e.id_egreso IS NULL
            """)
            rows = cursor.fetchall()
            headers = ["ID Ingreso","Paciente","Fecha","Hora","Servicio"]
            mostrar_tabla(headers, rows, title="Pacientes Activos")
            if rows and Prompt.ask("¿Exportar a PDF? (s/n)", choices=["s","n"]) == "s":
                exportar_pdf(headers, rows, filename="pacientes_activos.pdf", title="Pacientes Activos")

        elif opcion == "5":
            break

    conn.close()

if __name__ == "__main__":
    consultas()
