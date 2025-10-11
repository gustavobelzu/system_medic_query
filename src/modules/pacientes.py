import sqlite3
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

DB_PATH = "database/emergencias.db"
console = Console()

def conectar():
    return sqlite3.connect(DB_PATH)

# ==========================
# Mostrar tabla de pacientes
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
        console.print("⚠️ No hay pacientes registrados.", style="red")
        return []
    
    table = Table(title="Lista de Pacientes")
    table.add_column("CI", justify="center")
    table.add_column("Nombre")
    table.add_column("Edad", justify="center")
    table.add_column("Sexo", justify="center")
    table.add_column("Depto")
    table.add_column("Teléfono")
    table.add_column("Estado")
    for p in pacientes:
        table.add_row(str(p[0]), p[1], str(p[2]), p[3], p[4], str(p[5]), p[6] if p[6] else "N/A")
    console.print(table)
    return [str(p[0]) for p in pacientes]  # Lista de CIs existentes

# ==========================
# Registrar paciente
# ==========================
# ==========================
# Registrar paciente (ID estado obligatorio)
# ==========================
def registrar_paciente():
    console.print("\n=== Registro de Paciente ===", style="bold cyan")
    
    pacientes_existentes = listar_pacientes()
    console.print("Escriba 'c' para cancelar el registro en cualquier momento.", style="yellow")

    ci = Prompt.ask("CI").strip()
    if ci.lower() == "c":
        console.print("🔙 Registro cancelado.", style="yellow")
        return

    if ci in pacientes_existentes:
        console.print("❌ Ese CI ya existe.", style="red")
        return

    nombre = Prompt.ask("Nombre completo").strip()
    if nombre.lower() == "c":
        console.print("🔙 Registro cancelado.", style="yellow")
        return

    edad = Prompt.ask("Edad").strip()
    if edad.lower() == "c":
        console.print("🔙 Registro cancelado.", style="yellow")
        return

    sexo = Prompt.ask("Sexo (M/F)").strip().upper()
    if sexo.lower() == "c":
        console.print("🔙 Registro cancelado.", style="yellow")
        return

    departamento = Prompt.ask("Departamento").strip()
    if departamento.lower() == "c":
        console.print("🔙 Registro cancelado.", style="yellow")
        return

    telefono = Prompt.ask("Teléfono").strip()
    if telefono.lower() == "c":
        console.print("🔙 Registro cancelado.", style="yellow")
        return

    # Mostrar estados disponibles
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id_estado, estado FROM Estado")
    estados = cursor.fetchall()
    if not estados:
        console.print("⚠️ No hay estados registrados.", style="red")
        conn.close()
        return

    # Validación del ID de estado
    ids_estados = [str(e[0]) for e in estados]
    while True:
        console.print("\nEstados disponibles:")
        for e in estados:
            console.print(f"{e[0]} - {e[1]}")
        id_estado = Prompt.ask("Seleccione el ID del estado (obligatorio)").strip()
        if id_estado.lower() == "c":
            console.print("🔙 Registro cancelado.", style="yellow")
            conn.close()
            return
        if id_estado in ids_estados:
            break
        else:
            console.print("❌ ID inválido. Debe seleccionar un ID existente.", style="red")

    try:
        cursor.execute("""
            INSERT INTO Paciente (ci, nombre, edad, sexo, departamento, telefono, id_estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (ci, nombre, edad, sexo, departamento, telefono, id_estado))
        conn.commit()
        console.print("✅ Paciente registrado con éxito.", style="green")
    except Exception as e:
        console.print(f"⚠️ Ocurrió un error: {e}", style="red")
    finally:
        conn.close()


# ==========================
# Actualizar paciente (ID estado obligatorio)
# ==========================
def actualizar_paciente():
    pacientes_existentes = listar_pacientes()
    if not pacientes_existentes:
        return
    console.print("Escriba 'c' para cancelar la actualización.", style="yellow")
    
    ci = Prompt.ask("Ingrese el CI del paciente a modificar").strip()
    if ci.lower() == "c":
        console.print("🔙 Actualización cancelada.", style="yellow")
        return
    if ci not in pacientes_existentes:
        console.print("⚠️ Ese CI no existe.", style="red")
        return

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nombre, edad, sexo, departamento, telefono, id_estado
        FROM Paciente WHERE ci = ?
    """, (ci,))
    paciente = cursor.fetchone()

    nombre = Prompt.ask(f"Nombre (ENTER para {paciente[0]})").strip() or paciente[0]
    edad = Prompt.ask(f"Edad (ENTER para {paciente[1]})").strip() or paciente[1]
    sexo = Prompt.ask(f"Sexo (M/F) (ENTER para {paciente[2]})").strip().upper() or paciente[2]
    departamento = Prompt.ask(f"Departamento (ENTER para {paciente[3]})").strip() or paciente[3]
    telefono = Prompt.ask(f"Teléfono (ENTER para {paciente[4]})").strip() or paciente[4]

    # Estados
    cursor.execute("SELECT id_estado, estado FROM Estado")
    estados = cursor.fetchall()
    ids_estados = [str(e[0]) for e in estados]
    
    while True:
        console.print("\nEstados disponibles:")
        for e in estados:
            console.print(f"{e[0]} - {e[1]}")
        id_estado = Prompt.ask(f"ID Estado (ENTER para {paciente[5]})").strip() or str(paciente[5])
        if id_estado.lower() == "c":
            console.print("🔙 Actualización cancelada.", style="yellow")
            conn.close()
            return
        if id_estado in ids_estados:
            break
        else:
            console.print("❌ ID inválido. Debe seleccionar un ID existente.", style="red")

    try:
        cursor.execute("""
            UPDATE Paciente
            SET nombre = ?, edad = ?, sexo = ?, departamento = ?, telefono = ?, id_estado = ?
            WHERE ci = ?
        """, (nombre, edad, sexo, departamento, telefono, id_estado, ci))
        conn.commit()
        console.print("✅ Paciente actualizado con éxito.", style="green")
    except Exception as e:
        console.print(f"⚠️ Ocurrió un error: {e}", style="red")
    finally:
        conn.close()


# ==========================
# Eliminar paciente
# ==========================
def eliminar_paciente():
    pacientes_existentes = listar_pacientes()
    if not pacientes_existentes:
        return
    console.print("Escriba 'c' para cancelar la eliminación.", style="yellow")
    
    ci = Prompt.ask("Ingrese el CI del paciente a eliminar").strip()
    if ci.lower() == "c":
        console.print("🔙 Eliminación cancelada.", style="yellow")
        return
    if ci not in pacientes_existentes:
        console.print("⚠️ Ese CI no existe.", style="red")
        return

    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Paciente WHERE ci = ?", (ci,))
        conn.commit()
        console.print("✅ Paciente eliminado con éxito.", style="green")
    except Exception as e:
        console.print(f"⚠️ Ocurrió un error: {e}", style="red")
    finally:
        conn.close()

# ==========================
# Menú del módulo
# ==========================
def menu_pacientes(usuario=None):
    while True:
        console.print("\n--- MÓDULO PACIENTES ---", style="bold magenta")
        console.print("1. Registrar paciente")
        console.print("2. Listar pacientes")
        console.print("3. Actualizar paciente")
        console.print("4. Eliminar paciente")
        console.print("0. Volver")
        opcion = Prompt.ask("Seleccione una opción (0 para salir)", choices=["0","1","2","3","4"])
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

if __name__ == "__main__":
    menu_pacientes()
