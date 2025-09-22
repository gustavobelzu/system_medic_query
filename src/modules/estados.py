import sqlite3

DB_PATH = "database/emergencias.db"

def conectar():
    return sqlite3.connect(DB_PATH)

# ==========================
# Registrar estado
# ==========================
def registrar_estado():
    conn = conectar()
    cursor = conn.cursor()

    print("\n=== Registro de Estado ===")
    estado = input("Nombre del estado (Ej: Crítico, Estable, Grave): ").strip()
    condicion_especial = input("Condición especial (Opcional): ").strip()

    try:
        cursor.execute("""
            INSERT INTO Estado (estado, condicion_especial)
            VALUES (?, ?)
        """, (estado, condicion_especial if condicion_especial else None))

        conn.commit()
        print("✅ Estado registrado con éxito.")
    except sqlite3.IntegrityError:
        print("❌ Error: Ya existe un estado con ese nombre.")
    except Exception as e:
        print("⚠️ Ocurrió un error:", e)
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
        print("⚠️ No hay estados registrados.")
        return
    
    print("\n=== Lista de Estados ===")
    for e in estados:
        print(f"ID: {e[0]} | Estado: {e[1]} | Condición Especial: {e[2] if e[2] else 'N/A'}")

# ==========================
# Actualizar estado
# ==========================
def actualizar_estado():
    listar_estados()
    id_estado = input("\nIngrese el ID del estado a modificar: ").strip()

    conn = conectar()
    cursor = conn.cursor()

    nuevo_estado = input("Nuevo nombre del estado: ").strip()
    nueva_condicion = input("Nueva condición especial (dejar vacío si no cambia): ").strip()

    try:
        cursor.execute("""
            UPDATE Estado
            SET estado = ?, condicion_especial = ?
            WHERE id_estado = ?
        """, (nuevo_estado, nueva_condicion if nueva_condicion else None, id_estado))

        if cursor.rowcount == 0:
            print("⚠️ No se encontró el estado con ese ID.")
        else:
            conn.commit()
            print("✅ Estado actualizado con éxito.")
    except Exception as e:
        print("⚠️ Ocurrió un error:", e)
    finally:
        conn.close()

# ==========================
# Eliminar estado
# ==========================
def eliminar_estado():
    listar_estados()
    id_estado = input("\nIngrese el ID del estado a eliminar: ").strip()

    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM Estado WHERE id_estado = ?", (id_estado,))
        if cursor.rowcount == 0:
            print("⚠️ No se encontró el estado con ese ID.")
        else:
            conn.commit()
            print("✅ Estado eliminado con éxito.")
    except Exception as e:
        print("⚠️ Ocurrió un error:", e)
    finally:
        conn.close()

# ==========================
# Menú del módulo
# ==========================
def menu_estados():
    while True:
        print("\n--- MÓDULO ESTADOS ---")
        print("1. Registrar estado")
        print("2. Listar estados")
        print("3. Actualizar estado")
        print("4. Eliminar estado")
        print("0. Volver")

        opcion = input("Seleccione una opción: ").strip()

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
        else:
            print("❌ Opción inválida.")

if __name__ == "__main__":
    menu_estados()

