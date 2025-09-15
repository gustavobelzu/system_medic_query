from db import conectar

# ======================
# PACIENTES
# ======================
def registrar_paciente(ci, nombre, edad, sexo, id_estado):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO Paciente (ci, nombre, edad, sexo, id_estado)
        VALUES (?, ?, ?, ?, ?)
        """, (ci, nombre, edad, sexo, id_estado))
        conn.commit()
        print("✅ Paciente registrado correctamente")
    except Exception as e:
        print("❌ Error:", e)
    finally:
        conn.close()

def listar_pacientes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT p.ci, p.nombre, p.edad, p.sexo, e.estado
    FROM Paciente p
    LEFT JOIN Estado e ON p.id_estado = e.id_estado
    """)
    pacientes = cursor.fetchall()
    conn.close()

    print("\n📋 LISTA DE PACIENTES")
    for p in pacientes:
        print(f"CI: {p[0]} | Nombre: {p[1]} | Edad: {p[2]} | Sexo: {p[3]} | Estado: {p[4]}")
