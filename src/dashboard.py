from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.progress import Progress, BarColumn, TextColumn
import sqlite3
import random
import time

# Importar funciones de tu módulo pacientes
from modules.pacientes import registrar_paciente

console = Console()

DB_PATH = "database/emergencias.db"

def conectar():
    return sqlite3.connect(DB_PATH)

# -----------------------------
# Funciones del dashboard
# -----------------------------

def make_layout() -> Layout:
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="body", ratio=1),
        Layout(name="footer", size=3)
    )
    layout["body"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="main", ratio=2),
        Layout(name="right", ratio=1)
    )
    return layout

def render_header() -> Panel:
    return Panel("[bold cyan]🏥 Sistema de Emergencias - Dashboard[/bold cyan]", expand=True)

def render_footer() -> Panel:
    return Panel("Presiona CTRL+C para salir | Menú: [1] Agregar Paciente", expand=True)

def render_pacientes_table() -> Table:
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.ci, p.nombre, p.edad, p.sexo, p.departamento, p.telefono, e.estado
        FROM Paciente p
        LEFT JOIN Estado e ON p.id_estado = e.id_estado
    """)
    pacientes = cursor.fetchall()
    conn.close()

    table = Table(title="Pacientes")
    table.add_column("CI", justify="center", style="cyan")
    table.add_column("Nombre", style="magenta")
    table.add_column("Edad", style="yellow")
    table.add_column("Sexo", style="green")
    table.add_column("Depto", style="blue")
    table.add_column("Tel", style="white")
    table.add_column("Estado", style="red")

    for p in pacientes:
        table.add_row(str(p[0]), p[1], str(p[2]), p[3], p[4], p[5], p[6] or "Sin estado")

    return table

def render_estadisticas() -> Panel:
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Paciente")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Paciente WHERE id_estado IS NOT NULL")
    con_estado = cursor.fetchone()[0]

    cursor.execute("SELECT estado, COUNT(*) FROM Paciente p JOIN Estado e ON p.id_estado = e.id_estado GROUP BY estado")
    estados = cursor.fetchall()
    conn.close()

    estado_texto = "\n".join(f"{estado}: [bold green]{cantidad}[/bold green]" for estado, cantidad in estados)
    texto = f"""
Total de pacientes: [bold cyan]{total}[/bold cyan]
Pacientes con estado asignado: [bold green]{con_estado}[/bold green]

Por estado:
{estado_texto or 'Sin datos'}
"""
    return Panel(texto, title="📊 Estadísticas", expand=True)

def render_emergencias() -> Panel:
    progress = Progress(
        TextColumn("[bold red]{task.fields[nombre]}", justify="right"),
        BarColumn(bar_width=None),
        TextColumn("{task.percentage:>3.0f}%"),
        expand=True
    )

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Nombre FROM Paciente p
        JOIN Estado e ON p.id_estado = e.id_estado
        WHERE e.estado='Crítico'
        LIMIT 3
    """)
    pacientes_criticos = cursor.fetchall()
    conn.close()

    if not pacientes_criticos:
        pacientes_criticos = [("Ninguno",)] * 3

    for p in pacientes_criticos:
        progress.add_task("", total=100, completed=random.randint(0,100), nombre=p[0])

    return Panel(progress, title="🚨 Emergencias Críticas", expand=True)

# -----------------------------
# Loop principal del TUI
# -----------------------------
def main():
    layout = make_layout()

    try:
        with Live(layout, refresh_per_second=2, screen=True):
            while True:
                layout["header"].update(render_header())
                layout["footer"].update(render_footer())
                layout["main"].update(render_pacientes_table())
                layout["right"].update(render_estadisticas())
                layout["left"].update(render_emergencias())

                # Permitir agregar pacientes sin salir del dashboard
                if console.input("\nPresiona [bold blue]1[/bold blue] para agregar paciente o Enter para continuar: ") == "1":
                    registrar_paciente()

                time.sleep(1)

    except KeyboardInterrupt:
        console.print("\n[bold red]Programa terminado por el usuario.[/bold red]")

if __name__ == "__main__":
    main()

