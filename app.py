from modules.estados import menu_estados
from modules.pacientes import menu_pacientes
from modules.usuarios import menu_usuarios
from modules.ingresos import menu_ingresos
from modules.egresos import menu_egresos
import sqlite3

DB_PATH = "database/emergencias.db"

# ==========================
# Función de login
# ==========================
def login():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n=== LOGIN DEL SISTEMA ===")
    username = input("Usuario: ").strip()
    password = input("Contraseña: ").strip()

    cursor.execute("""
        SELECT u.id_usuario, p.nombre, p.cargo
        FROM Usuario u
        JOIN Personal p ON u.id_usuario = p.id_usuario
        WHERE u.username = ? AND u.password = ?
    """, (username, password))

    user = cursor.fetchone()
    conn.close()

    if user:
        print(f"\n✅ Bienvenido {user[1]} ({user[2]})")
        return user  # id_usuario, nombre, cargo
    else:
        print("❌ Usuario o contraseña incorrectos.")
        return None

# ==========================
# Función para mostrar registros
# ==========================
def ver_datos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tablas = ["Estado", "Paciente", "Usuario", "Personal", "Ingreso", "Egreso", "Ingreso_Personal"]

    print("\n=== DATOS INSERTADOS EN LA BASE ===")
    for tabla in tablas:
        print(f"\n📌 Tabla: {tabla}")
        try:
            cursor.execute(f"SELECT * FROM {tabla}")
            filas = cursor.fetchall()
            if filas:
                for fila in filas:
                    print(fila)
            else:
                print("   (sin registros)")
        except Exception as e:
            print(f"   ⚠️ Error al consultar {tabla}: {e}")

    conn.close()

# ==========================
# Menú principal
# ==========================
def menu_principal(user):
    while True:
        print("\n=== SISTEMA DE CONTROL DE EMERGENCIAS - CLÍNICA LA FUENTE ===")
        print(f"Usuario conectado: {user[1]} ({user[2]})")
        print("1. Gestión de Estados")
        print("2. Gestión de Pacientes")
        print("3. Gestión de Usuarios")
        print("4. Gestión de Ingresos")
        print("5. Gestión de Egresos")
        print("6. Ver datos insertados")  # <--- Nueva opción
        print("0. Salir")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            menu_estados()
        elif opcion == "2":
            menu_pacientes()
        elif opcion == "3":
            menu_usuarios()
        elif opcion == "4":
            menu_ingresos()
        elif opcion == "5":
            menu_egresos()
        elif opcion == "6":
            ver_datos()
        elif opcion == "0":
            print("👋 Saliendo del sistema...")
            break
        else:
            print("❌ Opción inválida. Intente nuevamente.")

# ==========================
# Inicio del programa
# ==========================
if __name__ == "__main__":
    intentos = 3
    usuario = None

    while intentos > 0 and not usuario:
        usuario = login()
        if not usuario:
            intentos -= 1
            print(f"Intentos restantes: {intentos}")

    if usuario:
        menu_principal(usuario)
    else:
        print("⚠️ Se han agotado los intentos. Saliendo del sistema.")
