import sqlite3

DB_PATH = "database/emergencias.db"

def conectar():
    return sqlite3.connect(DB_PATH)

# ==========================
# Registrar usuario
# ==========================
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

# ==========================
# Listar usuarios
# ==========================
def listar_usuarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id_usuario, u.username, p.nombre, p.cargo, p.especialidad
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
        print(f"ID: {u[0]}, Usuario: {u[1]}, Nombre: {u[2]}, Cargo: {u[3]}, Especialidad: {u[4] if u[4] else 'N/A'}")

# ==========================
# Actualizar usuario
# ==========================
def actualizar_usuario():
    listar_usuarios()
    id_usuario = input("\nIngrese el ID del usuario a modificar: ").strip()

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT u.username, u.password, p.nombre, p.cargo, p.especialidad
        FROM Usuario u
        JOIN Personal p ON u.id_usuario = p.id_usuario
        WHERE u.id_usuario = ?
    """, (id_usuario,))
    usuario = cursor.fetchone()

    if not usuario:
        print("⚠️ No se encontró el usuario con ese ID.")
        conn.close()
        return

    username_actual, password_actual, nombre_actual, cargo_actual, especialidad_actual = usuario

    username = input(f"Nuevo usuario (ENTER para {username_actual}): ").strip() or username_actual
    password = input(f"Nueva contraseña (ENTER para mantener): ").strip() or password_actual
    nombre = input(f"Nuevo nombre (ENTER para {nombre_actual}): ").strip() or nombre_actual
    cargo = input(f"Nuevo cargo (ENTER para {cargo_actual}): ").strip() or cargo_actual
    especialidad = input(f"Nueva especialidad (ENTER para {especialidad_actual if especialidad_actual else 'N/A'}): ").strip() or especialidad_actual

    try:
        cursor.execute("""
            UPDATE Usuario
            SET username = ?, password = ?
            WHERE id_usuario = ?
        """, (username, password, id_usuario))

        cursor.execute("""
            UPDATE Personal
            SET nombre = ?, cargo = ?, especialidad = ?
            WHERE id_usuario = ?
        """, (nombre, cargo, especialidad if especialidad else None, id_usuario))

        conn.commit()
        print("✅ Usuario actualizado con éxito.")
    except sqlite3.IntegrityError:
        print("❌ Error: El nombre de usuario ya existe.")
    except Exception as e:
        print("⚠️ Ocurrió un error:", e)
    finally:
        conn.close()

# ==========================
# Eliminar usuario
# ==========================
def eliminar_usuario():
    listar_usuarios()
    id_usuario = input("\nIngrese el ID del usuario a eliminar: ").strip()

    conn = conectar()
    cursor = conn.cursor()

    try:
        # Eliminar de Personal primero (por FK)
        cursor.execute("DELETE FROM Personal WHERE id_usuario = ?", (id_usuario,))
        # Luego eliminar de Usuario
        cursor.execute("DELETE FROM Usuario WHERE id_usuario = ?", (id_usuario,))

        if cursor.rowcount == 0:
            print("⚠️ No se encontró el usuario con ese ID.")
        else:
            conn.commit()
            print("✅ Usuario eliminado con éxito.")
    except Exception as e:
        print("⚠️ Ocurrió un error:", e)
    finally:
        conn.close()

# ==========================
# Menú del módulo
# ==========================
def menu_usuarios():
    while True:
        print("\n--- MÓDULO USUARIOS ---")
        print("1. Registrar usuario")
        print("2. Listar usuarios")
        print("3. Actualizar usuario")
        print("4. Eliminar usuario")
        print("0. Volver")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            registrar_usuario()
        elif opcion == "2":
            listar_usuarios()
        elif opcion == "3":
            actualizar_usuario()
        elif opcion == "4":
            eliminar_usuario()
        elif opcion == "0":
            break
        else:
            print("❌ Opción inválida.")

# ==========================
# Ejecutar módulo directamente
# ==========================
if __name__ == "__main__":
    menu_usuarios()
