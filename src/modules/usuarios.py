import sqlite3
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

DB_PATH = "database/emergencias.db"
console = Console()

def conectar():
    return sqlite3.connect(DB_PATH)

# ==========================
# Registrar usuario
# ==========================
def registrar_usuario():
    conn = conectar()
    cursor = conn.cursor()

    console.print("\n=== Registro de Usuario ===", style="bold cyan")
    console.print("Escriba 'c' en cualquier momento para cancelar.", style="yellow")

    while True:
        username = Prompt.ask("Nombre de usuario (login)").strip()
        if username.lower() == "c":
            console.print("🔙 Registro cancelado.", style="yellow")
            conn.close()
            return

        # Verificar si ya existe
        cursor.execute("SELECT 1 FROM Usuario WHERE username = ?", (username,))
        if cursor.fetchone():
            console.print("❌ Ese nombre de usuario ya existe.", style="red")
        else:
            break

    # Contraseña doble
    while True:
        password = Prompt.ask("Contraseña").strip()
        if password.lower() == "c":
            console.print("🔙 Registro cancelado.", style="yellow")
            conn.close()
            return
        password2 = Prompt.ask("Repita la contraseña").strip()
        if password2.lower() == "c":
            console.print("🔙 Registro cancelado.", style="yellow")
            conn.close()
            return
        if password != password2:
            console.print("❌ Las contraseñas no coinciden. Intente nuevamente.", style="red")
        else:
            break

    nombre = Prompt.ask("Nombre completo").strip()
    if nombre.lower() == "c":
        console.print("🔙 Registro cancelado.", style="yellow")
        conn.close()
        return

    cargo = Prompt.ask("Cargo (Médico, Enfermera, Administrativo)").strip()
    if cargo.lower() == "c":
        console.print("🔙 Registro cancelado.", style="yellow")
        conn.close()
        return

    especialidad = Prompt.ask("Especialidad (si aplica, caso contrario dejar vacío)").strip()
    if especialidad.lower() == "c":
        console.print("🔙 Registro cancelado.", style="yellow")
        conn.close()
        return

    try:
        cursor.execute("INSERT INTO Usuario (username, password) VALUES (?, ?)", (username, password))
        id_usuario = cursor.lastrowid
        cursor.execute("INSERT INTO Personal (id_usuario, nombre, cargo, especialidad) VALUES (?, ?, ?, ?)",
                       (id_usuario, nombre, cargo, especialidad if especialidad else None))
        conn.commit()
        console.print("✅ Usuario registrado con éxito.", style="green")
    except Exception as e:
        console.print(f"⚠️ Ocurrió un error: {e}", style="red")
    finally:
        conn.close()


# ==========================
# Listar usuarios
# ==========================
def listar_usuarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT u.username, p.nombre, p.cargo, p.especialidad FROM Usuario u JOIN Personal p ON u.id_usuario = p.id_usuario")
    usuarios = cursor.fetchall()
    conn.close()

    if not usuarios:
        console.print("⚠️ No hay usuarios registrados.", style="red")
        return

    table = Table(title="Lista de Usuarios")
    table.add_column("Usuario")
    table.add_column("Nombre")
    table.add_column("Cargo")
    table.add_column("Especialidad")
    for u in usuarios:
        table.add_row(u[0], u[1], u[2], u[3] if u[3] else "N/A")
    console.print(table)

# ==========================
# Actualizar usuario
# ==========================
def actualizar_usuario():
    listar_usuarios()
    console.print("Escriba 'c' para cancelar la actualización.", style="yellow")
    username = Prompt.ask("Ingrese el nombre de usuario a modificar").strip()
    if username.lower() == "c":
        console.print("🔙 Actualización cancelada.", style="yellow")
        return

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT u.id_usuario, p.nombre, p.cargo, p.especialidad FROM Usuario u JOIN Personal p ON u.id_usuario = p.id_usuario WHERE u.username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        console.print("❌ No se encontró el usuario.", style="red")
        conn.close()
        return

    nuevo_username = Prompt.ask(f"Nuevo usuario (ENTER para {username})").strip() or username
    nombre = Prompt.ask(f"Nombre completo (ENTER para {user[1]})").strip() or user[1]
    cargo = Prompt.ask(f"Cargo (ENTER para {user[2]})").strip() or user[2]
    especialidad = Prompt.ask(f"Especialidad (ENTER para {user[3] if user[3] else 'N/A'})").strip() or user[3]

    try:
        cursor.execute("UPDATE Usuario SET username = ? WHERE id_usuario = ?", (nuevo_username, user[0]))
        cursor.execute("UPDATE Personal SET nombre = ?, cargo = ?, especialidad = ? WHERE id_usuario = ?",
                       (nombre, cargo, especialidad, user[0]))
        conn.commit()
        console.print("✅ Usuario actualizado con éxito.", style="green")
    except Exception as e:
        console.print(f"⚠️ Ocurrió un error: {e}", style="red")
    finally:
        conn.close()

# ==========================
# Eliminar usuario con doble confirmación
# ==========================
def eliminar_usuario():
    listar_usuarios()
    console.print("Escriba 'c' para cancelar la eliminación.", style="yellow")
    username = Prompt.ask("Ingrese el nombre de usuario a eliminar").strip()
    if username.lower() == "c":
        console.print("🔙 Eliminación cancelada.", style="yellow")
        return

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id_usuario FROM Usuario WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        console.print("❌ No se encontró el usuario.", style="red")
        conn.close()
        return

    confirm = Prompt.ask(f"¿Está seguro que desea eliminar el usuario '{username}'? (s/n)").strip().lower()
    if confirm != "s":
        console.print("🔙 Eliminación cancelada.", style="yellow")
        conn.close()
        return

    try:
        cursor.execute("DELETE FROM Personal WHERE id_usuario = ?", (user[0],))
        cursor.execute("DELETE FROM Usuario WHERE id_usuario = ?", (user[0],))
        conn.commit()
        console.print("✅ Usuario eliminado con éxito.", style="green")
    except Exception as e:
        console.print(f"⚠️ Ocurrió un error: {e}", style="red")
    finally:
        conn.close()

# ==========================
# Menú del módulo
# ==========================
def menu_usuarios(usuario=None):
    while True:
        console.print("\n--- MÓDULO USUARIOS ---", style="bold magenta")
        console.print("1. Registrar usuario")
        console.print("2. Listar usuarios")
        console.print("3. Actualizar usuario")
        console.print("4. Eliminar usuario")
        console.print("0. Volver")
        opcion = Prompt.ask("Seleccione una opción (0 para salir)", choices=["0","1","2","3","4"])
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

if __name__ == "__main__":
    menu_usuarios()

