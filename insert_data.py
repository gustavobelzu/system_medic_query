import sqlite3

conn = sqlite3.connect("database/emergencias.db")
cursor = conn.cursor()

# Insertar un estado
cursor.execute("INSERT INTO Estado (estado, condicion_especial) VALUES (?, ?)", 
               ("Crítico", "UCI"))
id_estado = cursor.lastrowid

# Insertar paciente con estado
cursor.execute("INSERT INTO Paciente (ci, nombre, edad, sexo, id_estado) VALUES (?, ?, ?, ?, ?)",
               ("123456", "Ana López", 32, "F", id_estado))

# Insertar usuario (médico)
cursor.execute("INSERT INTO Usuario (matricula, nombre, cargo, especialidad) VALUES (?, ?, ?, ?)",
               ("M001", "Dr. Pérez", "Médico", "Emergencias"))

# Insertar ingreso
cursor.execute("INSERT INTO Ingreso (ci, matricula, fecha_ingreso, hora_ingreso, servicio_hospitalario) VALUES (?, ?, ?, ?, ?)",
               ("123456", "M001", "2025-09-10", "08:30", "Emergencias"))

id_ingreso = cursor.lastrowid

# Insertar egreso
cursor.execute("INSERT INTO Egreso (id_ingreso, ci, fecha_egreso, hora_egreso, estancia, estado_egreso) VALUES (?, ?, ?, ?, ?, ?)",
               (id_ingreso, "123456", "2025-09-12", "15:00", 2, "Estable"))

conn.commit()
conn.close()

print("✅ Datos insertados correctamente")
