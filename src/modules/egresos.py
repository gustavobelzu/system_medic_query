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
# Registrar egreso
# ==========================
def registrar_egreso():
    conn = conectar()
    cursor = conn.cursor()

    console.print("\n=== Registro de Egreso ===", style="bold cyan")

    # Mostrar ingresos activos (sin egreso)
    cursor.execute("""
        SELECT i.id_ingreso, p.ci, p.nombre, i.fecha_ingreso, i.hora_ingreso, i.servicio_hospitalario
        FROM Ingreso i
        JOIN Paciente p ON i.ci = p.ci
        LEFT JOIN Egreso e ON i.id_ingreso = e.id_ingreso
        WHERE e.id_egreso IS NULL
    """)
    ingresos = cursor.fetchall()
    if not ingresos:
        console.print("⚠️ No hay ingresos activos para egreso.", style="red")
        conn.close()
        return

    table = Table(title="Ingresos Activos")
    table.add_column("ID Ingreso", justify="center")
    table.add_column("CI")
    table.add_column("Paciente")
    table.add_column("Fecha")
    table.add_column("Hora")
    table.add_column("Servicio")
    for i in ingresos:
        table.add_row(str(i[0]), str(i[1]), i[2], i[3], i[4], i[5])
    console.print(table)

    id_ingreso = Prompt.ask("Seleccione ID de ingreso para egreso (o 'C' para cancelar)").strip()
    if id_ingreso.upper() == "C":
        console.print("❌ Registro cancelado.", style="yellow")
        conn.close()
        return

    ingreso_ids = [str(i[0]) for i in ingresos]
    if id_ingreso not in ingreso_ids:
        console.print("❌ Ingreso inválido. Ingrese un ID existente.", style="red")
        conn.close()
        return

    # Obtener CI y fecha de ingreso
    cursor.execute("SELECT ci, fecha_ingreso FROM Ingreso WHERE id_ingreso = ?", (id_ingreso,))
    ci, fecha_ingreso = cursor.fetchone()

    fecha_egreso = Prompt.ask("Fecha de egreso (YYYY-MM-DD, ENTER para hoy)").strip() or datetime.now().strftime("%Y-%m-%d")
    hora_egreso = Prompt.ask("Hora de egreso (HH:MM, ENTER para ahora)").strip() or datetime.now().strftime("%H:%M")
    estado_egreso = Prompt.ask("Estado de egreso (Recuperado, Trasladado, Fallecido, o 'C' para cancelar)").strip()
    if estado_egreso.upper() == "C":
        console.print("❌ Registro cancelado.", style="yellow")
        conn.close()
        return

    # Calcular estancia en días
    fecha_ingreso_dt = datetime.strptime(fecha_ingreso, "%Y-%m-%d")
    fecha_egreso_dt = datetime.strptime(fecha_egreso, "%Y-%m-%d")
    estancia = (fecha_egreso_dt - fecha_ingreso_dt).days

    try:
        cursor.execute("""
            INSERT INTO Egreso (id_ingreso, ci, fecha_egreso, hora_egreso, estancia, estado_egreso)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id_ingreso, ci, fecha_egreso, hora_egreso, estancia, estado_egreso))
        conn.commit()
        console.print("✅ Egreso registrado con éxito.", style="green")
    except Exception as e:
        console.print(f"⚠️ Ocurrió un error: {e}", style="red")
    finally:
        conn.close()

# ==========================
# Listar egresos
# ==========================
def listar_egresos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.id_egreso, p.nombre, e.fecha_egreso, e.hora_egreso, e.estancia, e.estado_egreso
        FROM Egreso e
        JOIN Paciente p ON e.ci = p.ci
        ORDER BY e.fecha_egreso DESC
    """)
    egresos = cursor.fetchall()
    conn.close()

    if not egresos:
        console.print("⚠️ No hay egresos registrados.", style="red")
        return

    table = Table(title="Lista de Egresos")
    table.add_column("ID", justify="center")
    table.add_column("Paciente")
    table.add_column("Fecha")
    table.add_column("Hora")
    table.add_column("Estancia (días)")
    table.add_column("Estado")
    for e in egresos:
        table.add_row(str(e[0]), e[1], e[2], e[3], str(e[4]), e[5])
    console.print(table)

# ==========================
# Actualizar egreso
# ==========================
def actualizar_egreso():
    listar_egresos()
    id_egreso = Prompt.ask("Ingrese ID de egreso a modificar (o 'C' para cancelar)").strip()
    if id_egreso.upper() == "C":
        console.print("❌ Actualización cancelada.", style="yellow")
        return

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT fecha_egreso, hora_egreso, estado_egreso FROM Egreso WHERE id_egreso = ?", (id_egreso,))
    egreso = cursor.fetchone()
    if not egreso:
        console.print("⚠️ No se encontró el egreso. Ingrese un ID existente.", style="red")
        conn.close()
        return

    fecha_egreso = Prompt.ask(f"Fecha (ENTER para {egreso[0]})").strip() or egreso[0]
    hora_egreso = Prompt.ask(f"Hora (ENTER para {egreso[1]})").strip() or egreso[1]
    estado_egreso = Prompt.ask(f"Estado (ENTER para {egreso[2]})").strip() or egreso[2]

    try:
        cursor.execute("""
            UPDATE Egreso
            SET fecha_egreso = ?, hora_egreso = ?, estado_egreso = ?
            WHERE id_egreso = ?
        """, (fecha_egreso, hora_egreso, estado_egreso, id_egreso))
        conn.commit()
        console.print("✅ Egreso actualizado con éxito.", style="green")
    except Exception as e:
        console.print(f"⚠️ Ocurrió un error: {e}", style="red")
    finally:
        conn.close()

# ==========================
# Eliminar egreso
# ==========================
def eliminar_egreso():
    listar_egresos()
    id_egreso = Prompt.ask("Ingrese ID de egreso a eliminar (o 'C' para cancelar)").strip()
    if id_egreso.upper() == "C":
        console.print("❌ Eliminación cancelada.", style="yellow")
        return

    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Egreso WHERE id_egreso = ?", (id_egreso,))
        if cursor.rowcount == 0:
            console.print("⚠️ No se encontró el egreso. Ingrese un ID existente.", style="red")
        else:
            conn.commit()
            console.print("✅ Egreso eliminado con éxito.", style="green")
    except Exception as e:
        console.print(f"⚠️ Ocurrió un error: {e}", style="red")
    finally:
        conn.close()


# ==========================
# Menú del módulo
# ==========================
def menu_egresos(usuario=None):
    while True:
        console.print("\n--- MÓDULO EGRESOS ---", style="bold magenta")
        console.print("1. Registrar egreso")
        console.print("2. Listar egresos")
        console.print("3. Actualizar egreso")
        console.print("4. Eliminar egreso")
        console.print("0. Volver")
        opcion = Prompt.ask("Seleccione una opción (0 para salir)", choices=["0","1","2","3","4"])
        if opcion == "1":
            registrar_egreso()
        elif opcion == "2":
            listar_egresos()
        elif opcion == "3":
            actualizar_egreso()
        elif opcion == "4":
            eliminar_egreso()
        elif opcion == "0":
            break

if __name__ == "__main__":
    menu_egresos()

