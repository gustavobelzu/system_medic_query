import sqlite3

DB_PATH = "database/emergencias.db"

def conectar():
    return sqlite3.connect(DB_PATH)

# ==========================
# Registrar paciente
# ==========================
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
        print("⚠️ No hay estados registrados, agregue al menos uno en la tabla Estado.")
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

# ==========================
# Listar pacientes
# ==========================
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

# ==========================
# Actualizar paciente
# ==========================
def actualizar_paciente():
    listar_pacientes()
    ci = input("\nIngrese el CI del paciente a modificar: ").strip()

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT nombre, edad, sexo, departamento, telefono, id_estado FROM Paciente WHERE ci = ?", (ci,))
    paciente = cursor.fetchone()
    if not paciente:
        print("⚠️ No se encontró el paciente con ese CI.")
        conn.close()
        return

    nombre_actual, edad_actual, sexo_actual, depto_actual, tel_actual, id_estado_actual = paciente

    nombre = input(f"Nuevo nombre (ENTER para {nombre_actual}): ").strip() or nombre_actual
    edad = input(f"Nueva edad (ENTER para {edad_actual}): ").strip() or edad_actual
    sexo = input(f"Nuevo sexo (M/F, ENTER para {sexo_actual}): ").strip().upper() or sexo_actual
    departamento = input(f"Nuevo departamento (ENTER para {depto_actual}): ").strip() or depto_actual
    telefono = input(f"Nuevo teléfono (ENTER para {tel_actual}): ").strip() or tel_actual

    # Mostrar estados disponibles
    cursor.execute("SELECT * FROM Estado")
    estados = cursor.fetchall()
    print("\nEstados disponibles:")
    for e in estados:
        print(f"{e[0]} - {e[1]} ({e[2] if e[2] else 'Sin condición especial'})")
    id_estado = input(f"Nuevo id_estado (ENTER para {id_estado_actual}): ").strip() or id_estado_actual

    try:
        cursor.execute("""
            UPDATE Paciente
            SET nombre = ?, edad = ?, sexo = ?, departamento = ?, telefono = ?, id_estado = ?
            WHERE ci = ?
        """, (nombre, edad, sexo, departamento, telefono, id_estado, ci))
        conn.commit()
        print("✅ Paciente actualizado con éxito.")
    except Exception as e:
        print("⚠️ Ocurrió un error:", e)
    finally:
        conn.close()

# ==========================
# Eliminar paciente
# ==========================
def eliminar_paciente():
    listar_pacientes()
    ci = input("\nIngrese el CI del paciente a eliminar: ").strip()

    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM Paciente WHERE ci = ?", (ci,))
        if cursor.rowcount == 0:
            print("⚠️ No se encontró el paciente con ese CI.")
        else:
            conn.commit()
            print("✅ Paciente eliminado con éxito.")
    except Exception as e:
        print("⚠️ Ocurrió un error:", e)
    finally:
        conn.close()

# ==========================
# Menú del módulo
# ==========================
def menu_pacientes():
    while True:
        print("\n--- MÓDULO PACIENTES ---")
        print("1. Registrar paciente")
        print("2. Listar pacientes")
        print("3. Actualizar paciente")
        print("4. Eliminar paciente")
        print("0. Volver")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            registrar_paciente()
        elif opcion == "2":
            listar_pacientes()
        elif opcion == "3":
            actualizar_paciente()
        elif opcion == "4":
            eliminar_paciente()
        elif opcion == "0":
            break
        else:
            print("❌ Opción inválida.")

# ==========================
# Ejecutar módulo directamente
# ==========================
if __name__ == "__main__":
    menu_pacientes()
