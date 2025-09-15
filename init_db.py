import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect("database/emergencias.db")
cursor = conn.cursor()

# ==========================
# TABLA: Estado
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS Estado (
    id_estado INTEGER PRIMARY KEY AUTOINCREMENT,
    estado TEXT NOT NULL,
    condicion_especial TEXT
)
""")

# ==========================
# TABLA: Paciente
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS Paciente (
    ci TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    edad INTEGER,
    sexo TEXT CHECK(sexo IN ('M','F')),
    departamento TEXT NOT NULL,
    telefono INTEGER,
    id_estado INTEGER,
    FOREIGN KEY (id_estado) REFERENCES Estado(id_estado)
)
""")
# ==========================
# TABLA: Ingreso
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS Ingreso (
    id_ingreso INTEGER PRIMARY KEY AUTOINCREMENT,
    ci TEXT NOT NULL,
    fecha_ingreso TEXT,
    hora_ingreso TEXT,
    servicio_hospitalario TEXT,
    cama TEXT,
    FOREIGN KEY (ci) REFERENCES Paciente(ci)
)
""")
# ==========================
# TABLA: Usuario (login)
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS Usuario (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
""")
# ==========================
# TABLA: Personal (información del trabajador)
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS Personal (
    id_personal INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER UNIQUE, -- Relación 1 a 1 con Usuario
    nombre TEXT NOT NULL,
    cargo TEXT NOT NULL,       -- Ej: Médico, Enfermera, Administrativo
    especialidad TEXT,         -- Solo aplica a médicos/enfermeras
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
)
""")
# ==========================
# TABLA: Egreso
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS Egreso (
    id_egreso INTEGER PRIMARY KEY AUTOINCREMENT,
    id_ingreso INTEGER NOT NULL,
    ci TEXT NOT NULL,
    fecha_egreso TEXT,
    hora_egreso TEXT,
    estancia INTEGER,
    estado_egreso TEXT,
    FOREIGN KEY (id_ingreso) REFERENCES Ingreso(id_ingreso),
    FOREIGN KEY (ci) REFERENCES Paciente(ci)
)
""")

conn.commit()
conn.close()

print("✅ Base de datos emergencias.db creada con tabla intermedia Ingreso_Personal")

