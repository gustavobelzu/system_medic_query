import sqlite3
import random

# Conectar a la base de datos
conn = sqlite3.connect("database/emergencias.db")
cursor = conn.cursor()

# ==========================
# DATOS DE EJEMPLO
# ==========================

# Estados
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

# Pacientes
pacientes = [
    (f"{1000+i}", f"Paciente_{i}", random.randint(1, 90),
     random.choice(["M", "F"]), f"Depto_{i}", 70000000+i, (i % 10)+1)
    for i in range(1, 11)
]

# Usuarios
usuarios = [(f"user{i}", f"pass{i}") for i in range(1, 11)]

# Personal
personal = [
    (i, f"Personal_{i}", random.choice(["Médico", "Enfermera", "Admin"]),
     random.choice([None, "Cardiología", "Pediatría", "Trauma", "Cirugía"]))
    for i in range(1, 11)
]

# Ingresos
ingresos = [
    (pacientes[i][0], f"2025-09-{10+i}", f"{8+i}:00",
     f"Servicio_{i}", f"Cama_{i}")
    for i in range(10)
]

# Egresos
egresos = [
    (i+1, pacientes[i][0], f"2025-09-{15+i}", f"{12+i}:30",
     random.randint(1, 15), random.choice(["Recuperado", "Derivado", "Fallecido"]))
    for i in range(10)
]

# Ingreso_Personal (asignamos personal aleatorio a cada ingreso)
ingreso_personal = [
    (i+1, (i % 10)+1, random.choice(["Médico tratante", "Enfermera de guardia", "Asistente"]))
    for i in range(10)
]

# ==========================
# INSERCIONES
# ==========================

# Estado
cursor.executemany("INSERT INTO Estado (estado, condicion_especial) VALUES (?, ?)", estados)

# Paciente
cursor.executemany("""
INSERT INTO Paciente (ci, nombre, edad, sexo, departamento, telefono, id_estado)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", pacientes)

# Usuario
cursor.executemany("INSERT INTO Usuario (username, password) VALUES (?, ?)", usuarios)

# Personal
cursor.executemany("""
INSERT INTO Personal (id_usuario, nombre, cargo, especialidad)
VALUES (?, ?, ?, ?)
""", personal)

# Ingreso
cursor.executemany("""
INSERT INTO Ingreso (ci, fecha_ingreso, hora_ingreso, servicio_hospitalario, cama)
VALUES (?, ?, ?, ?, ?)
""", ingresos)

# Egreso
cursor.executemany("""
INSERT INTO Egreso (id_ingreso, ci, fecha_egreso, hora_egreso, estancia, estado_egreso)
VALUES (?, ?, ?, ?, ?, ?)
""", egresos)

# Ingreso_Personal
cursor.executemany("""
INSERT INTO Ingreso_Personal (id_ingreso, id_personal, rol)
VALUES (?, ?, ?)
""", ingreso_personal)

# Guardar cambios
conn.commit()
conn.close()

print("✅ 10 registros insertados en cada tabla correctamente.")
