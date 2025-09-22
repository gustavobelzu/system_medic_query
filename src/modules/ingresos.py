import sqlite3
from datetime import datetime

DB_PATH = "database/emergencias.db"

def conectar():
    return sqlite3.connect(DB_PATH)

# ==========================
# Registrar ingreso
# ==========================
def registrar_ingreso():
    conn = conectar()
    cursor = conn.cursor()

    print("\n=== Registro de Ingreso ===")

    ci = input("CI del paciente: ").strip()

    # Verificar si el paciente existe
    cursor.execute("SELECT nombre FROM Paciente WHERE ci = ?", (ci,))
    paciente = cursor.fetchone()
    if not paciente:
        print("❌ Error: No existe un paciente con ese CI.")
        conn.close()
        return
    
    print(f"Paciente encontrado: {paciente[0]}")

    fecha_ingreso = input("Fecha de ingreso (YYYY-MM-DD, ENTER para hoy): ").strip()
    if not fecha_ingreso:
        fecha_ingreso = datetime.now().strftime("%Y-%m-%d")

    hora_ingreso = input("Hora de ingreso (HH:MM, ENTER para ahora): ").strip()
    if not hora_ingreso:
        hora_ingreso = datetime.now().strftime("%H:%M")

    servicio = input("Servicio hospitalario (Ej: Emergencias, Terapia Intensiva): ").strip()
    cama = input("Número de cama: ").strip()

    try:
        cursor.execute("""
            INSERT INTO Ingreso (ci, fecha_ingreso, hora_ingreso, servicio_hospitalario, cama)
            VALUES (?, ?, ?, ?, ?)
        """, (ci, fecha_ingreso, hora_ingreso, servicio, cama))

        conn.commit()
        print("✅ Ingreso registrado con éxito.")
    except Exception as e:
        print("⚠️ Ocurrió un error:", e)
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
        print("⚠️ No hay ingresos registrados.")
        return
    
    print("\n=== Lista de Ingresos ===")
    for i in ingresos:
        print(f"ID: {i[0]} | Paciente: {i[1]} | Fecha: {i[2]} {i[3]} | Servicio: {i[4]} | Cama: {i[5]}")

# ==========================
# Actualizar ingreso
# ==========================
def actualizar_ingreso():
    listar_ingresos()
    id_ingreso = input("\nIngrese el ID del ingreso a modificar: ").strip()

    conn = conectar()
    cursor = conn.cursor()

    # Verificar si existe
    cursor.execute("SELECT fecha_ingreso, hora_ingreso, servicio_hospitalario, cama FROM Ingreso WHERE id_ingreso = ?", (id_ingreso,))
    ingreso = cursor.fetchone()
    if not ingreso:
        print("⚠️ No se encontró el ingreso con ese ID.")
        conn.close()
        return

    fecha_actual, hora_actual, servicio_actual, cama_actual = ingreso

    fecha_ingreso = input(f"Nuevo fecha de ingreso (ENTER para {fecha_actual}): ").strip() or fecha_actual
    hora_ingreso = input(f"Nuevo hora de ingreso (ENTER para {hora_actual}): ").strip() or hora_actual
    servicio = input(f"Nuevo servicio hospitalario (ENTER para {servicio_actual}): ").strip() or servicio_actual
    cama = input(f"Nuevo número de cama (ENTER para {cama_actual}): ").strip() or cama_actual

    try:
        cursor.execute("""
            UPDATE Ingreso
            SET fecha_ingreso = ?, hora_ingreso = ?, servicio_hospitalario = ?, cama = ?
            WHERE id_ingreso = ?
        """, (fecha_ingreso, hora_ingreso, servicio, cama, id_ingreso))
        conn.commit()
        print("✅ Ingreso actualizado con éxito.")
    except Exception as e:
        print("⚠️ Ocurrió un error:", e)
    finally:
        conn.close()

# ==========================
# Eliminar ingreso
# ==========================
def eliminar_ingreso():
    listar_ingresos()
    id_ingreso = input("\nIngrese el ID del ingreso a eliminar: ").strip()

    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM Ingreso WHERE id_ingreso = ?", (id_ingreso,))
        if cursor.rowcount == 0:
            print("⚠️ No se encontró el ingreso con ese ID.")
        else:
            conn.commit()
            print("✅ Ingreso eliminado con éxito.")
    except Exception as e:
        print("⚠️ Ocurrió un error:", e)
    finally:
        conn.close()

# ==========================
# Menú del módulo
# ==========================
def menu_ingresos():
    while True:
        print("\n--- MÓDULO INGRESOS ---")
        print("1. Registrar ingreso")
        print("2. Listar ingresos")
        print("3. Actualizar ingreso")
        print("4. Eliminar ingreso")
        print("0. Volver")

        opcion = input("Seleccione una opción: ").strip()

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
        else:
            print("❌ Opción inválida.")

# ==========================
# Ejecutar módulo directamente
# ==========================
if __name__ == "__main__":
    menu_ingresos()

