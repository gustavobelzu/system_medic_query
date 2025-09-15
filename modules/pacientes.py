import sqlite3

DB_PATH = "database/emergencias.db"

def conectar():
    return sqlite3.connect(DB_PATH)

def registrar_paciente():
    conn = conectar()
    cursor = conn.cursor()

    print("\n=== Registro de Paciente ===")

    ci = input("CI: ").strip()
    nombre = input("Nombre completo: ").strip()
    edad = input("Edad: ").strip()
    sexo = input("Sexo (M/F): ").strip().upper()
    departamento = input("Departamento: ").strip()
    telefono = input("Teléfono: ").strip()

    # Mostrar estados disponibles
    cursor.execute("SELECT * FROM Estado")
    estados = cursor.fetchall()
    if not estados:
        print("⚠️ No hay estados registrados, debe agregar al menos uno en la tabla Estado.")
        conn.close()
        return
    
    print("\nEstados disponibles:")
    for e in estados:
        print(f"{e[0]} - {e[1]} ({e[2] if e[2] else 'Sin condición especial'})")

    id_estado = input("Seleccione el id_estado: ").strip()

    try:
        cursor.execute("""
            INSERT INTO Paciente (ci, nombre, edad, sexo, departamento, telefono, id_estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (ci, nombre, edad, sexo, departamento, telefono, id_estado))

        conn.commit()
        print("✅ Paciente registrado con éxito.")
    except sqlite3.IntegrityError:
        print("❌ Error: Ya existe un paciente con ese CI.")
    except Exception as e:
        print("⚠️ Ocurrió un error:", e)
    finally:
        conn.close()


def listar_pacientes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.ci, p.nombre, p.edad, p.sexo, p.departamento, p.telefono, e.estado
        FROM Paciente p
        LEFT JOIN Estado e ON p.id_estado = e.id_estado
    """)
    pacientes = cursor.fetchall()
    conn.close()

    if not pacientes:
        print("⚠️ No hay pacientes registrados.")
        return
    
    print("\n=== Lista de Pacientes ===")
    for p in pacientes:
        print(f"CI: {p[0]}, Nombre: {p[1]}, Edad: {p[2]}, Sexo: {p[3]}, "
              f"Depto: {p[4]}, Tel: {p[5]}, Estado: {p[6]}")


# Menú del módulo
def menu_pacientes():
    while True:
        print("\n--- MÓDULO PACIENTES ---")
        print("1. Registrar paciente")
        print("2. Listar pacientes")
        print("3. Salir")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            registrar_paciente()
        elif opcion == "2":
            listar_pacientes()
        elif opcion == "3":
            break
        else:
            print("❌ Opción inválida.")


if __name__ == "__main__":
    menu_pacientes()
