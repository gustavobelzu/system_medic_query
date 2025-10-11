import sqlite3
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

DB_PATH = "database/emergencias.db"
console = Console()

def conectar():
    return sqlite3.connect(DB_PATH)

# ==========================
# Mostrar tabla de estados
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
    return [str(e[0]) for e in estados]  # Devuelve lista de IDs existentes

# ==========================
# Registrar estado con cancelar
# ==========================
def registrar_estado():
    ids = listar_estados()
    console.print("\n=== Registro de Estado ===", style="bold cyan")
    console.print("Escriba 'c' para cancelar el registro en cualquier momento.", style="yellow")
    
    estado = Prompt.ask("Nombre del estado (Ej: Crítico, Estable, Grave)").strip()
    if estado.lower() == "c":
        console.print("🔙 Registro cancelado.", style="yellow")
        return
    
    condicion_especial = Prompt.ask("Condición especial (Opcional)").strip()
    if condicion_especial.lower() == "c":
        console.print("🔙 Registro cancelado.", style="yellow")
        return

    try:
        conn = conectar()
        cursor = conn.cursor()
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
# Actualizar estado con cancelar y validación
# ==========================
def actualizar_estado():
    ids = listar_estados()
    if not ids:
        return
    console.print("Escriba 'c' para cancelar la actualización.", style="yellow")
    
    id_estado = Prompt.ask("Ingrese el ID del estado a modificar").strip()
    if id_estado.lower() == "c":
        console.print("🔙 Actualización cancelada.", style="yellow")
        return
    if id_estado not in ids:
        console.print("⚠️ Ese ID no existe. Por favor ingrese un ID válido.", style="red")
        return

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT estado, condicion_especial FROM Estado WHERE id_estado = ?", (id_estado,))
    estado = cursor.fetchone()

    nuevo_estado = Prompt.ask(f"Nuevo estado (ENTER para {estado[0]})").strip() or estado[0]
    if nuevo_estado.lower() == "c":
        console.print("🔙 Actualización cancelada.", style="yellow")
        conn.close()
        return

    nueva_condicion = Prompt.ask(f"Nueva condición (ENTER para {estado[1] if estado[1] else 'N/A'})").strip() or estado[1]
    if nueva_condicion.lower() == "c":
        console.print("🔙 Actualización cancelada.", style="yellow")
        conn.close()
        return

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
# Eliminar estado con cancelar y validación
# ==========================
def eliminar_estado():
    ids = listar_estados()
    if not ids:
        return
    console.print("Escriba 'c' para cancelar la eliminación.", style="yellow")
    
    id_estado = Prompt.ask("Ingrese el ID del estado a eliminar").strip()
    if id_estado.lower() == "c":
        console.print("🔙 Eliminación cancelada.", style="yellow")
        return
    if id_estado not in ids:
        console.print("⚠️ Ese ID no existe. Por favor ingrese un ID válido.", style="red")
        return

    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Estado WHERE id_estado = ?", (id_estado,))
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
