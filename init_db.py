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
    id_estado INTEGER,
    FOREIGN KEY (id_estado) REFERENCES Estado(id_estado)
)
""")

# ==========================
# TABLA: Usuario
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS Usuario (
    matricula TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    cargo TEXT,
    especialidad TEXT
)
""")

# ==========================
# TABLA: Ingreso
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS Ingreso (
    id_ingreso INTEGER PRIMARY KEY AUTOINCREMENT,
    ci TEXT NOT NULL,
    matricula TEXT NOT NULL,
    fecha_ingreso TEXT,
    hora_ingreso TEXT,
    servicio_hospitalario TEXT,
    FOREIGN KEY (ci) REFERENCES Paciente(ci),
    FOREIGN KEY (matricula) REFERENCES Usuario(matricula)
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

print("✅ Base de datos emergencias.db creada con relaciones entre tablas")
