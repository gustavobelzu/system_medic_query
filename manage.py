import sys
import os
import sqlite3 

# Agregar la carpeta src al path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
# ==========================
# Ajustar path para importar modules
# ==========================
from modules.estados import menu_estados
from modules.pacientes import menu_pacientes
from modules.usuarios import menu_usuarios
from modules.ingresos import menu_ingresos
from modules.egresos import menu_egresos
from modules.reportes import menu_reportes as menu_reportes
from modules.consultas import consultas as menu_consultas

import sqlite3
from getpass import getpass
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

DB_PATH = "database/emergencias.db"
console = Console()

# ==========================
# Función de login
# ==========================
def login():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    console.print(Panel("LOGIN DEL SISTEMA", style="bold cyan"))
    username = Prompt.ask("Usuario")
    password = getpass("Contraseña: ")

    cursor.execute("""
        SELECT u.id_usuario, p.nombre, p.cargo
        FROM Usuario u
        JOIN Personal p ON u.id_usuario = p.id_usuario
        WHERE u.username = ? AND u.password = ?
    """, (username, password))

    user = cursor.fetchone()
    conn.close()

    if user:
        console.print(f"✅ Bienvenido [green]{user[1]}[/green] ([yellow]{user[2]}[/yellow])")
        return user
    else:
        console.print("❌ Usuario o contraseña incorrectos.", style="bold red")
        return None

# ==========================
# Dashboard estilo grid (2 filas x 3 columnas)
# ==========================
def menu_principal(user):
    opciones = [
        ("1", "Gestión de Estados", menu_estados),
        ("2", "Gestión de Pacientes", menu_pacientes),
        ("3", "Gestión de Usuarios", menu_usuarios),
        ("4", "Gestión de Ingresos", menu_ingresos),
        ("5", "Gestión de Egresos", menu_egresos),
        ("6", "Reportes", menu_reportes),
        ("0", "Salir", None)
    ]

    while True:
        console.clear()
        console.print(Panel(f"SISTEMA DE CONTROL DE EMERGENCIAS\n[bold]Usuario conectado:[/bold] {user[1]} ({user[2]})", style="magenta"))

        # Grid de 2 filas x 3 columnas
        table = Table.grid(expand=True)
        table.add_column(ratio=1)
        table.add_column(ratio=1)
        table.add_column(ratio=1)

        row_panels = []
        for key, title, _ in opciones:
            style = "bold white on blue" if key != "0" else "bold white on red"
            row_panels.append(Panel(f"[bold]{key}[/bold]\n{title}", style=style, expand=True))

        # Mostrar filas en grid
        table.add_row(*row_panels[:3])
        table.add_row(*row_panels[3:6])
        if len(row_panels) > 6:
            table.add_row(*row_panels[6:])

        console.print(table)

        opcion = Prompt.ask("Seleccione una opción", choices=[str(op[0]) for op in opciones])

        if opcion == "0":
            console.print("👋 Saliendo del sistema...", style="bold yellow")
            break
        else:
            for key, _, func in opciones:
                if key == opcion and func:
                # Pasar el usuario al módulo si acepta argumento
                    try:
                        func(user)
                    except TypeError:
                        func()
                    break


        console.print("\nPresione Enter para volver al panel de control...")
        input()

# ==========================
# Inicio del programa
# ==========================
if __name__ == "__main__":
    intentos = 3
    usuario = None

    while intentos > 0 and not usuario:
        usuario = login()
        if not usuario:
            intentos -= 1
            console.print(f"Intentos restantes: {intentos}", style="bold red")

    if usuario:
        menu_principal(usuario)
    else:
        console.print("⚠️ Se han agotado los intentos. Saliendo del sistema.", style="bold red")
