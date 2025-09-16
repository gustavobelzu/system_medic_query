from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.progress import Progress, BarColumn, TextColumn
import sqlite3
import time
import random

console = Console()

# Conexión a la base de datos
conn = sqlite3.connect("database/emergencias.db")
cursor = conn.cursor()

def make_layout() -> Layout:
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="body", ratio=1),
        Layout(name="footer", size=3),
    )
    layout["body"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="main", ratio=2),
        Layout(name="right", ratio=1),
    )
    return layout

def render_header() -> Panel:
    return Panel("[bold cyan]🏥 Sistema de Emergencias - Dashboard[/bold cyan]", expand=True)

def render_footer() -> Panel:
    return Panel("Presiona [bold green]CTRL+C[/bold green] para salir", expand=True)

def render_pacientes_table() -> Table:
    table = Table(title="Pacientes")
    table.add_column("ID", style="cyan", justify="center")
    table.add_column("Nombre", style="magenta")
    table.add_column("Edad", style="yellow")
    table.add_column("Sexo", style="green")
    table.add_column("Estado", style="red")

    cursor.execute("""
        SELECT p.Ci, p.Nombre, p.Edad, p.Sexo, e.estado
        FROM Paciente p
        LEFT JOIN Estado e ON p.id_estado = e.id_estado
    """)
    pacientes = cursor.fetchall()

    for paciente in pacientes:
        table.add_row(
            str(paciente[0]),
            paciente[1],
            str(paciente[2]),
            paciente[3],
            paciente[4] or "Sin estado"
        )
    
    return table

def render_estadisticas() -> Panel:
    cursor.execute("SELECT COUNT(*) FROM Paciente")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Paciente WHERE id_estado IS NOT NULL")
    con_estado = cursor.fetchone()[0]

    cursor.execute("SELECT estado, COUNT(*) FROM Paciente p JOIN Estado e ON p.id_estado = e.id_estado GROUP BY estado")
    estados = cursor.fetchall()

    estado_texto = "\n".join(f"{estado}: [bold green]{cantidad}[/bold green]" for estado, cantidad in estados)

    texto = f"""
Total de pacientes: [bold cyan]{total}[/bold cyan]
Pacientes con estado asignado: [bold green]{con_estado}[/bold green]

Por estado:
{estado_texto or 'Sin datos'}
"""
    return Panel(texto, title="📊 Estadísticas", expand=True)

def render_emergencias() -> Panel:
    # Simulamos 3 emergencias críticas con barra de progreso
    progress = Progress(
        TextColumn("[bold red]{task.fields[nombre]}", justify="right"),
        BarColumn(bar_width=None),
        TextColumn("{task.percentage:>3.0f}%"),
        expand=True
    )

    pacientes_criticos = [
        {"nombre": "Paciente A", "progreso": random.randint(0, 100)},
        {"nombre": "Paciente B", "progreso": random.randint(0, 100)},
        {"nombre": "Paciente C", "progreso": random.randint(0, 100)},
    ]

    for paciente in pacientes_criticos:
        task = progress.add_task("", total=100, completed=paciente["progreso"], nombre=paciente["nombre"])

    return Panel(progress, title="🚨 Emergencias Críticas", expand=True)

def main():
    layout = make_layout()

    with Live(layout, refresh_per_second=2, screen=True):
        while True:
            layout["header"].update(render_header())
            layout["footer"].update(render_footer())
            layout["main"].update(render_pacientes_table())
            layout["right"].update(render_estadisticas())
            layout["left"].update(render_emergencias())

            time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Programa terminado por el usuario.[/bold red]")
