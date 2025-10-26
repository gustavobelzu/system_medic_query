import os
DB_PATH = "database/emergencias.db"

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("✅ Base de datos eliminada")

# Luego puedes llamar a tu función inicializar_bd() para crear un archivo limpio
