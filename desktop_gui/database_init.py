import os
import sqlite3
import random
from faker import Faker
from datetime import datetime

# dentro de la lista de egresos
#fecha_ingreso = datetime.strptime(ingresos[i][1], "%Y-%m-%d").date()
#fecha_egreso = faker.date_between(start_date=fecha_ingreso, end_date='today').isoformat()


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "emergencias.db")
fake = Faker()

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
# DATOS FALSOS 1000 REGISTROS
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
    
    # Obtener IDs de estados
    cursor.execute("SELECT id_estado FROM Estado")
    estados_ids = [row[0] for row in cursor.fetchall()]

    # --- Usuarios ---
    usuarios = [(f"user{i}", f"pass{i}") for i in range(1, 1001)]
    cursor.executemany("INSERT INTO Usuario (username, password) VALUES (?, ?)", usuarios)
    cursor.execute("SELECT id_usuario FROM Usuario")
    usuarios_ids = [row[0] for row in cursor.fetchall()]

    # --- Personal ---
    cargos = ["Médico", "Enfermera", "Admin"]
    especialidades = [None, "Cardiología", "Pediatría", "Trauma", "Cirugía"]
    personal = [
        (usuarios_ids[i % 1000], fake.name(), random.choice(cargos), random.choice(especialidades))
        for i in range(1000)
    ]
    cursor.executemany("""
        INSERT INTO Personal (id_usuario, nombre, cargo, especialidad)
        VALUES (?, ?, ?, ?)
    """, personal)
    cursor.execute("SELECT id_personal FROM Personal")
    personal_ids = [row[0] for row in cursor.fetchall()]

    # --- Pacientes ---
    pacientes = [
        (str(1000+i), fake.name(), random.randint(1, 90),
         random.choice(["M", "F"]), fake.state(), random.randint(60000000, 79999999),
         random.choice(estados_ids))
        for i in range(1000)
    ]
    cursor.executemany("""
        INSERT INTO Paciente (ci, nombre, edad, sexo, departamento, telefono, id_estado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, pacientes)

    # --- Ingresos ---
    ingresos = [
        (
            pacientes[i][0],
            fake.date_between(start_date='-1y', end_date='today').isoformat(),
            f"{random.randint(0,23)}:{random.randint(0,59):02d}",
            f"Servicio_{random.randint(1,20)}",
            f"Cama_{random.randint(1,200)}"
        )
        for i in range(1000)
    ]

    cursor.executemany("""
        INSERT INTO Ingreso (ci, fecha_ingreso, hora_ingreso, servicio_hospitalario, cama)
        VALUES (?, ?, ?, ?, ?)
    """, ingresos)

    # --- Egresos ---
    egresos = []
    for i in range(len(ingresos)):
        # Convertir la fecha de ingreso (string) a objeto date
        fecha_ingreso_date = datetime.strptime(ingresos[i][1], "%Y-%m-%d").date()
        
        # Generar fecha de egreso entre fecha_ingreso y hoy
        fecha_egreso = fake.date_between(start_date=fecha_ingreso_date, end_date='today').isoformat()
        
        egresos.append((
            i+1,                     # id_ingreso
            pacientes[i][0],         # ci
            fecha_egreso,            # fecha_egreso
            f"{random.randint(0,23)}:{random.randint(0,59):02d}",  # hora_egreso
            random.randint(1,30),    # estancia
            random.choice(["Recuperado", "Derivado", "Fallecido"])
        ))

    cursor.executemany("""
        INSERT INTO Egreso (id_ingreso, ci, fecha_egreso, hora_egreso, estancia, estado_egreso)
        VALUES (?, ?, ?, ?, ?, ?)
    """, egresos)
    # --- Ingreso_Personal ---
    roles = ["Médico tratante", "Enfermera de guardia", "Asistente"]
    ingreso_personal = [
        ((i+1), random.choice(personal_ids), random.choice(roles))
        for i in range(1000)
    ]
    cursor.executemany("""
        INSERT INTO Ingreso_Personal (id_ingreso, id_personal, rol)
        VALUES (?, ?, ?)
    """, ingreso_personal)

    conn.commit()
    conn.close()
    print("✅ 1000 registros insertados correctamente")
