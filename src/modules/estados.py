import sqlite3
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

DB_PATH = "database/emergencias.db"
console = Console()

def conectar():
    return sqlite3.connect(DB_PATH)

# ==========================
# Registrar estado
# ==========================
def registrar_estado():
    conn = conectar()
    cursor = conn.cursor()

    console.print("\n=== Registro de Estado ===", style="bold cyan")
    estado = Prompt.ask("Nombre del estado (Ej: Crítico, Estable, Grave)").strip()
    condicion_especial = Prompt.ask("Condición especial (Opcional)").strip()

    try:
        cursor.execute("""
            INSERT INTO Estado (estado, condicion_especial)
            VALUES (?, ?)
        """, (estado, condicion_especial if condicion_especial else None))
        conn.commit()
        console.print("✅ Estado registrado con éxito.", style="green")
    except sqlite3.IntegrityError:
        console.print("❌ Error: Ya existe un estado con ese nombre.", style="red")
    except Exception as e:
        console.print(f"⚠️ Ocurrió un error: {e}", style="red")
    finally:
        conn.close()

# ==========================
# Listar estados
# ==========================
def listar_estados():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id_estado, estado, condicion_especial FROM Estado")
    estados = cursor.fetchall()
    conn.close()

    if not estados:
        console.print("⚠️ No hay estados registrados.", style="red")
        return
    
    table = Table(title="Lista de Estados")
    table.add_column("ID", justify="center")
    table.add_column("Estado", justify="center")
    table.add_column("Condición Especial", justify="center")
    for e in estados:
        table.add_row(str(e[0]), e[1], e[2] if e[2] else "N/A")
    console.print(table)

# ==========================
# Actualizar estado
# ==========================
def actualizar_estado():
    listar_estados()
    id_estado = Prompt.ask("Ingrese el ID del estado a modificar").strip()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT estado, condicion_especial FROM Estado WHERE id_estado = ?", (id_estado,))
    estado = cursor.fetchone()
    if not estado:
        console.print("⚠️ No se encontró el estado.", style="red")
        conn.close()
        return

    nuevo_estado = Prompt.ask(f"Nuevo estado (ENTER para {estado[0]})").strip() or estado[0]
    nueva_condicion = Prompt.ask(f"Nueva condición (ENTER para {estado[1] if estado[1] else 'N/A'})").strip() or estado[1]

    try:
        cursor.execute("UPDATE Estado SET estado = ?, condicion_especial = ? WHERE id_estado = ?",
                       (nuevo_estado, nueva_condicion, id_estado))
        conn.commit()
        console.print("✅ Estado actualizado con éxito.", style="green")
    except Exception as e:
        console.print(f"⚠️ Ocurrió un error: {e}", style="red")
    finally:
        conn.close()

# ==========================
# Eliminar estado
# ==========================
def eliminar_estado():
    listar_estados()
    id_estado = Prompt.ask("Ingrese el ID del estado a eliminar").strip()
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Estado WHERE id_estado = ?", (id_estado,))
        if cursor.rowcount == 0:
            console.print("⚠️ No se encontró el estado.", style="red")
        else:
            conn.commit()
            console.print("✅ Estado eliminado con éxito.", style="green")
    except Exception as e:
        console.print(f"⚠️ Ocurrió un error: {e}", style="red")
    finally:
        conn.close()

# ==========================
# Menú del módulo
# ==========================
def menu_estados():
    while True:
        console.print("\n--- MÓDULO ESTADOS ---", style="bold magenta")
        console.print("1. Registrar estado")
        console.print("2. Listar estados")
        console.print("3. Actualizar estado")
        console.print("4. Eliminar estado")
        console.print("0. Volver")
        opcion = Prompt.ask("Seleccione una opción", choices=["0","1","2","3","4"])
        if opcion == "1":
            registrar_estado()
        elif opcion == "2":
            listar_estados()
        elif opcion == "3":
            actualizar_estado()
        elif opcion == "4":
            eliminar_estado()
        elif opcion == "0":
            break

if __name__ == "__main__":
    menu_estados()


