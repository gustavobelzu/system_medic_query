import sqlite3
from datetime import datetime

DB_PATH = "database/emergencias.db"

def conectar():
    return sqlite3.connect(DB_PATH)

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


# Menú del módulo
def menu_ingresos():
    while True:
        print("\n--- MÓDULO INGRESOS ---")
        print("1. Registrar ingreso")
        print("2. Listar ingresos")
        print("3. Salir")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            registrar_ingreso()
        elif opcion == "2":
            listar_ingresos()
        elif opcion == "3":
            break
        else:
            print("❌ Opción inválida.")


if __name__ == "__main__":
    menu_ingresos()
