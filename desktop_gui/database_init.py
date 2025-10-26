import os
import sqlite3
import random
from faker import Faker

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "emergencias.db")

# ==========================
# INICIALIZACIÓN BD
# ==========================
def inicializar_bd():
    if not os.path.exists(DB_PATH):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Crear tablas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuario (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Personal (
            id_personal INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER,
            nombre TEXT NOT NULL,
            cargo TEXT NOT NULL,
            especialidad TEXT,
            FOREIGN KEY(id_usuario) REFERENCES Usuario(id_usuario)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Estado (
            id_estado INTEGER PRIMARY KEY AUTOINCREMENT,
            estado TEXT NOT NULL,
            condicion_especial TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Paciente (
            ci TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            edad INTEGER,
            sexo TEXT,
            departamento TEXT,
            telefono INTEGER,
            id_estado INTEGER,
            FOREIGN KEY(id_estado) REFERENCES Estado(id_estado)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Ingreso (
            id_ingreso INTEGER PRIMARY KEY AUTOINCREMENT,
            ci TEXT,
            fecha_ingreso TEXT,
            hora_ingreso TEXT,
            servicio_hospitalario TEXT,
            cama TEXT,
            FOREIGN KEY(ci) REFERENCES Paciente(ci)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Egreso (
            id_egreso INTEGER PRIMARY KEY AUTOINCREMENT,
            id_ingreso INTEGER,
            ci TEXT,
            fecha_egreso TEXT,
            hora_egreso TEXT,
            estancia INTEGER,
            estado_egreso TEXT,
            FOREIGN KEY(id_ingreso) REFERENCES Ingreso(id_ingreso),
            FOREIGN KEY(ci) REFERENCES Paciente(ci)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Ingreso_Personal (
            id_ingreso INTEGER,
            id_personal INTEGER,
            rol TEXT,
            FOREIGN KEY(id_ingreso) REFERENCES Ingreso(id_ingreso),
            FOREIGN KEY(id_personal) REFERENCES Personal(id_personal)
        )
    """)
    conn.commit()
    conn.close()

# ==========================
# VERIFICAR USUARIOS
# ==========================
def hay_usuarios():
    if not os.path.exists(DB_PATH):
        return False
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Usuario")
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

# ==========================
# DATOS FALSOS
# ==========================
def poblar_datos_falsos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Revisar si hay pacientes
    cursor.execute("SELECT COUNT(*) FROM Paciente")
    if cursor.fetchone()[0] > 0:
        print("⚠️ Datos ya existen, no se insertan duplicados")
        conn.close()
        return

    # --- Estados ---
    estados = [
        ("Estable", "Ninguna"),
        ("Crítico", "UTI"),
        ("Observación", "24h"),
        ("Fallecido", None),
        ("Recuperado", None),
        ("Estable", "Aislamiento"),
        ("Crítico", "Cirugía urgente"),
        ("Recuperación", "Sala común"),
        ("Derivado", "Otro hospital"),
        ("Alta médica", None)
    ]
    cursor.executemany("INSERT INTO Estado (estado, condicion_especial) VALUES (?, ?)", estados)

    # --- Pacientes ---
    pacientes = [
        (f"{1000+i}", f"Paciente_{i}", random.randint(1, 90),
         random.choice(["M", "F"]), f"Depto_{i}", 70000000+i, (i % 10)+1)
        for i in range(1, 11)
    ]
    cursor.executemany("""
        INSERT INTO Paciente (ci, nombre, edad, sexo, departamento, telefono, id_estado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, pacientes)

    # --- Usuarios ---
    usuarios = [(f"user{i}", f"pass{i}") for i in range(1, 11)]
    cursor.executemany("INSERT INTO Usuario (username, password) VALUES (?, ?)", usuarios)

    # --- Personal ---
    personal = [
        (i, f"Personal_{i}", random.choice(["Médico", "Enfermera", "Admin"]),
         random.choice([None, "Cardiología", "Pediatría", "Trauma", "Cirugía"]))
        for i in range(1, 11)
    ]
    cursor.executemany("""
        INSERT INTO Personal (id_usuario, nombre, cargo, especialidad)
        VALUES (?, ?, ?, ?)
    """, personal)

    # --- Ingresos ---
    ingresos = [
        (pacientes[i][0], f"2025-09-{10+i}", f"{8+i}:00",
         f"Servicio_{i}", f"Cama_{i}")
        for i in range(10)
    ]
    cursor.executemany("""
        INSERT INTO Ingreso (ci, fecha_ingreso, hora_ingreso, servicio_hospitalario, cama)
        VALUES (?, ?, ?, ?, ?)
    """, ingresos)

    # --- Egresos ---
    egresos = [
        (i+1, pacientes[i][0], f"2025-09-{15+i}", f"{12+i}:30",
         random.randint(1, 15), random.choice(["Recuperado", "Derivado", "Fallecido"]))
        for i in range(10)
    ]
    cursor.executemany("""
        INSERT INTO Egreso (id_ingreso, ci, fecha_egreso, hora_egreso, estancia, estado_egreso)
        VALUES (?, ?, ?, ?, ?, ?)
    """, egresos)

    # --- Ingreso_Personal ---
    ingreso_personal = [
        (i+1, (i % 10)+1, random.choice(["Médico tratante", "Enfermera de guardia", "Asistente"]))
        for i in range(10)
    ]
    cursor.executemany("""
        INSERT INTO Ingreso_Personal (id_ingreso, id_personal, rol)
        VALUES (?, ?, ?)
    """, ingreso_personal)

    conn.commit()
    conn.close()
    print("✅ Datos falsos insertados correctamente")
