import sqlite3

DB_PATH = "database/emergencias.db"

def conectar():
    return sqlite3.connect(DB_PATH)

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


# Menú del módulo
def menu_estados():
    while True:
        print("\n--- MÓDULO ESTADOS ---")
        print("1. Registrar estado")
        print("2. Listar estados")
        print("3. Salir")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            registrar_estado()
        elif opcion == "2":
            listar_estados()
        elif opcion == "3":
            break
        else:
            print("❌ Opción inválida.")


if __name__ == "__main__":
    menu_estados()
