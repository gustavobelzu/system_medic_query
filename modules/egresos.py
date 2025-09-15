import sqlite3
from datetime import datetime

DB_PATH = "database/emergencias.db"

def conectar():
    return sqlite3.connect(DB_PATH)

def registrar_egreso():
    conn = conectar()
    cursor = conn.cursor()

    print("\n=== Registro de Egreso ===")

    # Seleccionar ingreso activo
    cursor.execute("""
        SELECT i.id_ingreso, p.nombre, i.fecha_ingreso, i.hora_ingreso, i.servicio_hospitalario
        FROM Ingreso i
        JOIN Paciente p ON i.ci = p.ci
        LEFT JOIN Egreso e ON i.id_ingreso = e.id_ingreso
        WHERE e.id_egreso IS NULL
    """)
    ingresos = cursor.fetchall()

    if not ingresos:
        print("⚠️ No hay ingresos activos para egreso.")
        conn.close()
        return

    print("\nIngresos activos:")
    for i in ingresos:
        print(f"ID Ingreso: {i[0]} | Paciente: {i[1]} | Fecha: {i[2]} {i[3]} | Servicio: {i[4]}")

    id_ingreso = input("Seleccione ID de ingreso para egreso: ").strip()

    # Verificar que el ingreso exista
    ingreso_ids = [str(i[0]) for i in ingresos]
    if id_ingreso not in ingreso_ids:
        print("❌ Ingreso inválido.")
        conn.close()
        return

    fecha_egreso = input("Fecha de egreso (YYYY-MM-DD, ENTER para hoy): ").strip()
    if not fecha_egreso:
        fecha_egreso = datetime.now().strftime("%Y-%m-%d")

    hora_egreso = input("Hora de egreso (HH:MM, ENTER para ahora): ").strip()
    if not hora_egreso:
        hora_egreso = datetime.now().strftime("%H:%M")

    # Obtener CI del ingreso
    cursor.execute("SELECT ci, fecha_ingreso FROM Ingreso WHERE id_ingreso = ?", (id_ingreso,))
    ci, fecha_ingreso = cursor.fetchone()

    # Calcular estancia en días
    fecha_ingreso_dt = datetime.strptime(fecha_ingreso, "%Y-%m-%d")
    fecha_egreso_dt = datetime.strptime(fecha_egreso, "%Y-%m-%d")
    estancia = (fecha_egreso_dt - fecha_ingreso_dt).days

    estado_egreso = input("Estado de egreso (Recuperado, Trasladado, Fallecido): ").strip()

    try:
        cursor.execute("""
            INSERT INTO Egreso (id_ingreso, ci, fecha_egreso, hora_egreso, estancia, estado_egreso)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id_ingreso, ci, fecha_egreso, hora_egreso, estancia, estado_egreso))

        conn.commit()
        print("✅ Egreso registrado con éxito.")
    except Exception as e:
        print("⚠️ Ocurrió un error:", e)
    finally:
        conn.close()


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
        print("⚠️ No hay egresos registrados.")
        return
    
    print("\n=== Lista de Egresos ===")
    for e in egresos:
        print(f"ID: {e[0]} | Paciente: {e[1]} | Fecha: {e[2]} {e[3]} | Estancia: {e[4]} días | Estado: {e[5]}")


# Menú del módulo
def menu_egresos():
    while True:
        print("\n--- MÓDULO EGRESOS ---")
        print("1. Registrar egreso")
        print("2. Listar egresos")
        print("3. Salir")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            registrar_egreso()
        elif opcion == "2":
            listar_egresos()
        elif opcion == "3":
            break
        else:
            print("❌ Opción inválida.")


if __name__ == "__main__":
    menu_egresos()
