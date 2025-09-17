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
    """Muestra todos los registros de la tabla elegida"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM {tabla}")
        registros = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]

        if registros:
            table = Table(title=f"Registros en {tabla}")
            for col in columnas:
                table.add_column(col, style="bold white")
            for row in registros:
                table.add_row(*[str(r) for r in row])
            console.print(table)
        else:
            console.print("⚠️ No hay registros en la tabla.", style="bold red")
    except Exception as e:
        console.print(f"❌ Error al mostrar la tabla: {e}", style="bold red")
    finally:
        conn.close()

def obtener_columnas(tabla):
    """Devuelve lista de columnas válidas de la tabla"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    columnas = []
    try:
        cursor.execute(f"PRAGMA table_info({tabla})")
        columnas = [col[1] for col in cursor.fetchall()]
    except Exception as e:
        console.print(f"❌ Error al obtener columnas: {e}", style="bold red")
    finally:
        conn.close()
    return columnas

def modificar_registro():
    console.print(Panel("✏️ MODIFICAR REGISTRO", style="bold green"))

    tabla = Prompt.ask("Ingrese el nombre de la tabla (ej: Paciente, Estado, Usuario) o [0] para cancelar")
    if tabla == "0":
        console.print("❌ Operación cancelada", style="yellow")
        return

    columnas = obtener_columnas(tabla)
    if not columnas:
        console.print("⚠️ Tabla no encontrada.", style="red")
        return

    mostrar_tabla(tabla)

    id_col = Prompt.ask(f"Ingrese el nombre de la columna ID (opciones: {', '.join(columnas)}) o [0] para cancelar")
    if id_col == "0":
        console.print("❌ Operación cancelada", style="yellow")
        return
    if id_col not in columnas:
        console.print("⚠️ Columna ID inválida.", style="red")
        return

    id_val = Prompt.ask(f"Ingrese el valor del {id_col} a modificar o [0] para cancelar")
    if id_val == "0":
        console.print("❌ Operación cancelada", style="yellow")
        return

    campo = Prompt.ask(f"Ingrese el campo a modificar (opciones: {', '.join(columnas)}) o [0] para cancelar")
    if campo == "0":
        console.print("❌ Operación cancelada", style="yellow")
        return
    if campo not in columnas:
        console.print("⚠️ Columna inválida. Solo puede elegir entre sus datos registrados.", style="red")
        return

    nuevo_valor = Prompt.ask("Ingrese el nuevo valor o [0] para cancelar")
    if nuevo_valor == "0":
        console.print("❌ Operación cancelada", style="yellow")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(f"UPDATE {tabla} SET {campo} = ? WHERE {id_col} = ?", (nuevo_valor, id_val))
        if cursor.rowcount == 0:
            console.print("⚠️ No se encontró ningún registro con ese ID.", style="yellow")
        else:
            conn.commit()
            console.print("✅ Registro actualizado correctamente", style="bold green")
    except Exception as e:
        console.print(f"❌ Error al modificar: {e}", style="bold red")
    finally:
        conn.close()

def eliminar_registro():
    console.print(Panel("🗑️ ELIMINAR REGISTRO", style="bold red"))

    tabla = Prompt.ask("Ingrese el nombre de la tabla (ej: Paciente, Estado, Usuario) o [0] para cancelar")
    if tabla == "0":
        console.print("❌ Operación cancelada", style="yellow")
        return

    columnas = obtener_columnas(tabla)
    if not columnas:
        console.print("⚠️ Tabla no encontrada.", style="red")
        return

    mostrar_tabla(tabla)

    id_col = Prompt.ask(f"Ingrese el nombre de la columna ID (opciones: {', '.join(columnas)}) o [0] para cancelar")
    if id_col == "0":
        console.print("❌ Operación cancelada", style="yellow")
        return
    if id_col not in columnas:
        console.print("⚠️ Columna ID inválida.", style="red")
        return

    id_val = Prompt.ask(f"Ingrese el valor del {id_col} a eliminar o [0] para cancelar")
    if id_val == "0":
        console.print("❌ Operación cancelada", style="yellow")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(f"DELETE FROM {tabla} WHERE {id_col} = ?", (id_val,))
        if cursor.rowcount == 0:
            console.print("⚠️ No se encontró ningún registro con ese ID.", style="yellow")
        else:
            conn.commit()
            console.print("✅ Registro eliminado correctamente", style="bold green")
    except Exception as e:
        console.print(f"❌ Error al eliminar: {e}", style="bold red")
    finally:
        conn.close()

