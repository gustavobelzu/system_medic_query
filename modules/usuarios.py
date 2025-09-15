import sqlite3

DB_PATH = "database/emergencias.db"

def conectar():
    return sqlite3.connect(DB_PATH)

def registrar_usuario():
    conn = conectar()
    cursor = conn.cursor()

    print("\n=== Registro de Usuario ===")

    username = input("Nombre de usuario (login): ").strip()
    password = input("Contraseña: ").strip()
    nombre = input("Nombre completo: ").strip()
    cargo = input("Cargo (Médico, Enfermera, Administrativo): ").strip()
    especialidad = input("Especialidad (si aplica, caso contrario dejar vacío): ").strip()

    try:
        # Insertar en Usuario
        cursor.execute("""
            INSERT INTO Usuario (username, password) 
            VALUES (?, ?)
        """, (username, password))
        id_usuario = cursor.lastrowid

        # Insertar en Personal
        cursor.execute("""
            INSERT INTO Personal (id_usuario, nombre, cargo, especialidad)
            VALUES (?, ?, ?, ?)
        """, (id_usuario, nombre, cargo, especialidad if especialidad else None))

        conn.commit()
        print("✅ Usuario registrado con éxito.")
    except sqlite3.IntegrityError:
        print("❌ Error: Ese nombre de usuario ya existe.")
    except Exception as e:
        print("⚠️ Ocurrió un error:", e)
    finally:
        conn.close()


def listar_usuarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.username, p.nombre, p.cargo, p.especialidad
        FROM Usuario u
        JOIN Personal p ON u.id_usuario = p.id_usuario
    """)
    usuarios = cursor.fetchall()
    conn.close()

    if not usuarios:
        print("⚠️ No hay usuarios registrados.")
        return
    
    print("\n=== Lista de Usuarios ===")
    for u in usuarios:
        print(f"Usuario: {u[0]}, Nombre: {u[1]}, Cargo: {u[2]}, Especialidad: {u[3] if u[3] else 'N/A'}")


# Menú del módulo
def menu_usuarios():
    while True:
        print("\n--- MÓDULO USUARIOS ---")
        print("1. Registrar usuario")
        print("2. Listar usuarios")
        print("3. Salir")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            registrar_usuario()
        elif opcion == "2":
            listar_usuarios()
        elif opcion == "3":
            break
        else:
            print("❌ Opción inválida.")


if __name__ == "__main__":
    menu_usuarios()
