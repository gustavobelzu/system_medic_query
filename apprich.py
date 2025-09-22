import sys
import os
import sqlite3 

# Agregar la carpeta src al path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from modules.estados import menu_estados
from modules.pacientes import menu_pacientes
from modules.usuarios import menu_usuarios
from modules.ingresos import menu_ingresos
from modules.egresos import menu_egresos
from modules.reportes import consultas as menu_reportes
from modules.consultas import consultas as menu_consultas
import sqlite3
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from getpass import getpass

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
# Función para mostrar listas con Rich Table
# ==========================
def mostrar_tabla(titulo, columnas, filas):
    if not filas:
        console.print(f"⚠️ No hay {titulo.lower()}.", style="bold red")
        return
    table = Table(title=titulo, style="cyan")
    for col in columnas:
        table.add_column(col, justify="center")
    for fila in filas:
        table.add_row(*[str(f) if f is not None else "N/A" for f in fila])
    console.print(table)

# ==========================
# Menú principal
# ==========================
def menu_principal(user):
    while True:
        console.print(Panel(f"SISTEMA DE CONTROL DE EMERGENCIAS - CLÍNICA LA FUENTE\n[bold]Usuario conectado:[/bold] {user[1]} ({user[2]})", style="magenta"))

        console.print("[cyan]1.[/cyan] Gestión de Estados")
        console.print("[cyan]2.[/cyan] Gestión de Pacientes")
        console.print("[cyan]3.[/cyan] Gestión de Usuarios")
        console.print("[cyan]4.[/cyan] Gestión de Ingresos")
        console.print("[cyan]5.[/cyan] Gestión de Egresos")
        console.print("[cyan]6.[/cyan] Consultas y Reportes")
        console.print("[cyan]0.[/cyan] Salir")

        opcion = Prompt.ask("Seleccione una opción", choices=["0","1","2","3","4","5","6"])

        if opcion == "1":
            menu_estados()
        elif opcion == "2":
            menu_pacientes()
        elif opcion == "3":
            menu_usuarios()
        elif opcion == "4":
            menu_ingresos()
        elif opcion == "5":
            menu_egresos()
        elif opcion == "6":
            menu_consultas(usuario)
        elif opcion == "0":
            console.print("👋 Saliendo del sistema...", style="bold yellow")
            break

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
