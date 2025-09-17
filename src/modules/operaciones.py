import sqlite3
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel

DB_PATH = "database/emergencias.db"
console = Console()

def menu_operaciones():
    while True:
        console.clear()
        console.print(Panel("🔧 MÓDULO DE OPERACIONES", style="bold cyan"))

        opciones = {
            "1": "Modificar registro",
            "2": "Eliminar registro",
            "0": "Volver al menú principal"
        }

        for k, v in opciones.items():
            console.print(f"[bold cyan]{k}[/bold cyan]. {v}")

        opcion = Prompt.ask("\nSeleccione una opción", choices=list(opciones.keys()))

        if opcion == "1":
            modificar_registro()
        elif opcion == "2":
            eliminar_registro()
        elif opcion == "0":
            break

def mostrar_tabla(tabla):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {tabla}")
    registros = cursor.fetchall()
    columnas = [desc[0] for desc in cursor.description]
    conn.close()

    if registros:
        table = Table(title=f"Registros en {tabla}")
        for col in columnas:
            table.add_column(col, style="bold white")
        for row in registros:
            table.add_row(*[str(r) for r in row])
        console.print(table)
    else:
        console.print("⚠️ No hay registros en la tabla.", style="bold red")

def modificar_registro():
    console.print(Panel("✏️ MODIFICAR REGISTRO", style="bold green"))
    tabla = Prompt.ask("Ingrese el nombre de la tabla a modificar (ej: Paciente, Estado, Usuario)")
    mostrar_tabla(tabla)

    id_col = Prompt.ask("Ingrese el nombre de la columna ID (ej: id_paciente, id_estado, id_usuario)")
    id_val = Prompt.ask(f"Ingrese el valor del {id_col} a modificar")
    campo = Prompt.ask("Ingrese el nombre del campo a modificar")
    nuevo_valor = Prompt.ask("Ingrese el nuevo valor")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(f"UPDATE {tabla} SET {campo} = ? WHERE {id_col} = ?", (nuevo_valor, id_val))
        conn.commit()
        console.print("✅ Registro actualizado correctamente", style="bold green")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="bold red")
    conn.close()

def eliminar_registro():
    console.print(Panel("🗑️ ELIMINAR REGISTRO", style="bold red"))
    tabla = Prompt.ask("Ingrese el nombre de la tabla a eliminar (ej: Paciente, Estado, Usuario)")
    mostrar_tabla(tabla)

    id_col = Prompt.ask("Ingrese el nombre de la columna ID (ej: id_paciente, id_estado, id_usuario)")
    id_val = Prompt.ask(f"Ingrese el valor del {id_col} a eliminar")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(f"DELETE FROM {tabla} WHERE {id_col} = ?", (id_val,))
        conn.commit()
        console.print("✅ Registro eliminado correctamente", style="bold green")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="bold red")
    conn.close()
