import sqlite3
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

DB_PATH = "database/emergencias.db"
console = Console()

def conectar():
    return sqlite3.connect(DB_PATH)

# ==========================
# Registrar ingreso
# ==========================
def registrar_ingreso():
    conn = conectar()
    cursor = conn.cursor()

    console.print("\n=== Registro de Ingreso ===", style="bold cyan")
    ci = Prompt.ask("CI del paciente").strip()

    # Verificar si el paciente existe
    cursor.execute("SELECT nombre FROM Paciente WHERE ci = ?", (ci,))
    paciente = cursor.fetchone()
    if not paciente:
        console.print("❌ No existe un paciente con ese CI.", style="red")
        conn.close()
        return
    console.print(f"Paciente encontrado: {paciente[0]}")

    fecha_ingreso = Prompt.ask("Fecha de ingreso (YYYY-MM-DD, ENTER para hoy)").strip() or datetime.now().strftime("%Y-%m-%d")
    hora_ingreso = Prompt.ask("Hora de ingreso (HH:MM, ENTER para ahora)").strip() or datetime.now().strftime("%H:%M")
    servicio = Prompt.ask("Servicio hospitalario (Ej: Emergencias, UCI)").strip()
    cama = Prompt.ask("Número de cama").strip()

    try:
        cursor.execute("""
            INSERT INTO Ingreso (ci, fecha_ingreso, hora_ingreso, servicio_hospitalario, cama)
            VALUES (?, ?, ?, ?, ?)
        """, (ci, fecha_ingreso, hora_ingreso, servicio, cama))
        conn.commit()
        console.print("✅ Ingreso registrado con éxito.", style="green")
    except Exception as e:
        console.print(f"⚠️ Ocurrió un error: {e}", style="red")
    finally:
        conn.close()

# ==========================
# Listar ingresos
# ==========================
def listar_ingresos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.id_ingreso, p.nombre, i.fecha_ingreso, i.hora_ingreso, i.servicio_hospitalario, i.cama
        FROM Ingreso i
        JOIN Paciente p ON i.ci = p.ci
        ORDER BY i.fecha_ingreso DESC, i.hora_ingreso DESC
    """)
    ingresos = cursor.fetchall()
    conn.close()

    if not ingresos:
        console.print("⚠️ No hay ingresos registrados.", style="red")
        return

    table = Table(title="Lista de Ingresos")
    table.add_column("ID", justify="center")
    table.add_column("Paciente")
    table.add_column("Fecha")
    table.add_column("Hora")
    table.add_column("Servicio")
    table.add_column("Cama")
    for i in ingresos:
        table.add_row(str(i[0]), i[1], i[2], i[3], i[4], i[5])
    console.print(table)

# ==========================
# Actualizar ingreso
# ==========================
def actualizar_ingreso():
    listar_ingresos()
    id_ingreso = Prompt.ask("Ingrese ID de ingreso a modificar").strip()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT ci, fecha_ingreso, hora_ingreso, servicio_hospitalario, cama FROM Ingreso WHERE id_ingreso = ?", (id_ingreso,))
    ingreso = cursor.fetchone()
    if not ingreso:
        console.print("⚠️ No se encontró el ingreso.", style="red")
        conn.close()
        return

    fecha_ingreso = Prompt.ask(f"Fecha (ENTER para {ingreso[1]})").strip() or ingreso[1]
    hora_ingreso = Prompt.ask(f"Hora (ENTER para {ingreso[2]})").strip() or ingreso[2]
    servicio = Prompt.ask(f"Servicio (ENTER para {ingreso[3]})").strip() or ingreso[3]
    cama = Prompt.ask(f"Cama (ENTER para {ingreso[4]})").strip() or ingreso[4]

    try:
        cursor.execute("""
            UPDATE Ingreso
            SET fecha_ingreso = ?, hora_ingreso = ?, servicio_hospitalario = ?, cama = ?
            WHERE id_ingreso = ?
        """, (fecha_ingreso, hora_ingreso, servicio, cama, id_ingreso))
        conn.commit()
        console.print("✅ Ingreso actualizado con éxito.", style="green")
    except Exception as e:
        console.print(f"⚠️ Ocurrió un error: {e}", style="red")
    finally:
        conn.close()

# ==========================
# Eliminar ingreso
# ==========================
def eliminar_ingreso():
    listar_ingresos()
    id_ingreso = Prompt.ask("Ingrese ID de ingreso a eliminar").strip()
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Ingreso WHERE id_ingreso = ?", (id_ingreso,))
        if cursor.rowcount == 0:
            console.print("⚠️ No se encontró el ingreso.", style="red")
        else:
            conn.commit()
            console.print("✅ Ingreso eliminado con éxito.", style="green")
    except Exception as e:
        console.print(f"⚠️ Ocurrió un error: {e}", style="red")
    finally:
        conn.close()

# ==========================
# Menú del módulo
# ==========================
def menu_ingresos():
    while True:
        console.print("\n--- MÓDULO INGRESOS ---", style="bold magenta")
        console.print("1. Registrar ingreso")
        console.print("2. Listar ingresos")
        console.print("3. Actualizar ingreso")
        console.print("4. Eliminar ingreso")
        console.print("0. Volver")
        opcion = Prompt.ask("Seleccione una opción", choices=["0","1","2","3","4"])
        if opcion == "1":
            registrar_ingreso()
        elif opcion == "2":
            listar_ingresos()
        elif opcion == "3":
            actualizar_ingreso()
        elif opcion == "4":
            eliminar_ingreso()
        elif opcion == "0":
            break

if __name__ == "__main__":
    menu_ingresos()


