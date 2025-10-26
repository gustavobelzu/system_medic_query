import sys, os
from PySide6.QtWidgets import QApplication, QMessageBox
from desktop_gui.login_window import LoginWindow
from desktop_gui.database_init import inicializar_bd, hay_usuarios, poblar_datos_falsos
from desktop_gui.usuarios_panel import UsuarioForm

def resource_path(relative_path):
    """Devuelve la ruta válida tanto en desarrollo como en el .exe."""
    try:
        base_path = sys._MEIPASS  # Carpeta temporal usada por PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Inicializar la base de datos
inicializar_bd()

# Crear la aplicación **una sola vez**
app = QApplication(sys.argv)

# Crear primer usuario si no hay ninguno
if not hay_usuarios():
    QMessageBox.information(None, "Primera configuración",
                            "No hay usuarios registrados. Cree el primer usuario.")
    form = UsuarioForm()
    form.setWindowTitle("Crear primer usuario")
    if form.exec() != True:
        sys.exit()  # si cancela, salir

# Poblar datos falsos opcionalmente
poblar_datos_falsos()

# Cargar estilo
style_path = resource_path("desktop_gui/style.qss")
if os.path.exists(style_path):
    with open(style_path, "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())


# Abrir ventana de login / dashboard
window = LoginWindow()
window.show()

# Ejecutar la aplicación
sys.exit(app.exec())
