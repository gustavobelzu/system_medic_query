import sqlite3, os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QLabel, QMessageBox, QLineEdit, QFormLayout, QDialog
)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "emergencias.db")

def conectar():
    return sqlite3.connect(DB_PATH)

# ==========================
# Formulario de Usuario
# ==========================
class UsuarioForm(QDialog):
    def __init__(self, parent=None, usuario=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar/Editar Usuario")
        self.setFixedSize(350, 300)
        self.usuario = usuario

        layout = QVBoxLayout()
        self.setLayout(layout)

        form_layout = QFormLayout()
        self.txt_username = QLineEdit()
        self.txt_password = QLineEdit()
        self.txt_nombre = QLineEdit()
        self.txt_cargo = QLineEdit()
        self.txt_especialidad = QLineEdit()

        form_layout.addRow("Usuario:", self.txt_username)
        form_layout.addRow("Contraseña:", self.txt_password)
        form_layout.addRow("Nombre completo:", self.txt_nombre)
        form_layout.addRow("Cargo:", self.txt_cargo)
        form_layout.addRow("Especialidad:", self.txt_especialidad)
        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar")
        self.btn_cancelar = QPushButton("Cancelar")
        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(self.btn_cancelar)
        layout.addLayout(btn_layout)

        self.btn_guardar.clicked.connect(self.guardar)
        self.btn_cancelar.clicked.connect(self.close)

        if usuario:
            self.txt_username.setText(usuario[0])
            self.txt_username.setEnabled(False)
            self.txt_nombre.setText(usuario[1])
            self.txt_cargo.setText(usuario[2])
            self.txt_especialidad.setText(usuario[3] if usuario[3] else "")

    def guardar(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text().strip()
        nombre = self.txt_nombre.text().strip()
        cargo = self.txt_cargo.text().strip()
        especialidad = self.txt_especialidad.text().strip()

        if not all([username, nombre, cargo]):
            QMessageBox.warning(self, "Error", "Usuario, Nombre y Cargo son obligatorios")
            return

        conn = conectar()
        cursor = conn.cursor()
        try:
            if self.usuario:
                # Actualizar Personal (no cambia username)
                cursor.execute("""
                    UPDATE Personal SET nombre=?, cargo=?, especialidad=? 
                    WHERE id_usuario=(SELECT id_usuario FROM Usuario WHERE username=?)
                """, (nombre, cargo, especialidad if especialidad else None, username))
                if password:
                    cursor.execute("UPDATE Usuario SET password=? WHERE username=?", (password, username))
            else:
                cursor.execute("INSERT INTO Usuario (username, password) VALUES (?, ?)", (username, password))
                id_usuario = cursor.lastrowid
                cursor.execute("INSERT INTO Personal (id_usuario, nombre, cargo, especialidad) VALUES (?, ?, ?, ?)",
                               (id_usuario, nombre, cargo, especialidad if especialidad else None))
            conn.commit()
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Ocurrió un error: {e}")
        finally:
            conn.close()

# ==========================
# Panel Usuarios
# ==========================
class UsuariosPanel(QWidget):
    def __init__(self, volver_callback=None):
        super().__init__()
        self.volver_callback = volver_callback
        self.setWindowTitle("Módulo Usuarios")
        self.setMinimumSize(700, 450)

        layout = QVBoxLayout()
        self.setLayout(layout)

        lbl_titulo = QLabel("Gestión de Usuarios")
        lbl_titulo.setStyleSheet("font-weight:bold; font-size:16pt")
        layout.addWidget(lbl_titulo)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Usuario","Nombre","Cargo","Especialidad"])
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setMinimumHeight(300)
        layout.addWidget(self.tabla, stretch=1)

        btn_layout = QHBoxLayout()
        self.btn_crear = QPushButton("Crear")
        self.btn_modificar = QPushButton("Modificar")
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_volver = QPushButton("Volver")
        btn_layout.addWidget(self.btn_crear)
        btn_layout.addWidget(self.btn_modificar)
        btn_layout.addWidget(self.btn_eliminar)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_volver)
        layout.addLayout(btn_layout)

        self.btn_crear.clicked.connect(self.agregar)
        self.btn_modificar.clicked.connect(self.editar)
        self.btn_eliminar.clicked.connect(self.eliminar)
        self.btn_volver.clicked.connect(self.volver)

        self.listar_usuarios()

    def listar_usuarios(self):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.username, p.nombre, p.cargo, p.especialidad
            FROM Usuario u JOIN Personal p ON u.id_usuario = p.id_usuario
        """)
        usuarios = cursor.fetchall()
        conn.close()

        self.tabla.setRowCount(0)
        for fila_idx, u in enumerate(usuarios):
            self.tabla.insertRow(fila_idx)
            for col_idx, valor in enumerate(u):
                self.tabla.setItem(fila_idx, col_idx, QTableWidgetItem(str(valor) if valor else "N/A"))

    def agregar(self):
        form = UsuarioForm(self)
        if form.exec():
            self.listar_usuarios()

    def editar(self):
        selected = self.tabla.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Error", "Seleccione un usuario para modificar")
            return
        username = selected[0].text()
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.username, p.nombre, p.cargo, p.especialidad
            FROM Usuario u JOIN Personal p ON u.id_usuario = p.id_usuario
            WHERE u.username=?
        """, (username,))
        usuario = cursor.fetchone()
        conn.close()
        form = UsuarioForm(self, usuario)
        if form.exec():
            self.listar_usuarios()

    def eliminar(self):
        selected = self.tabla.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Error", "Seleccione un usuario para eliminar")
            return
        username = selected[0].text()
        reply = QMessageBox.question(self, "Confirmar", f"Eliminar usuario {username}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT id_usuario FROM Usuario WHERE username=?", (username,))
            user = cursor.fetchone()
            if user:
                cursor.execute("DELETE FROM Personal WHERE id_usuario=?", (user[0],))
                cursor.execute("DELETE FROM Usuario WHERE id_usuario=?", (user[0],))
                conn.commit()
            conn.close()
            self.listar_usuarios()

    def volver(self):
        if self.volver_callback:
            self.volver_callback()
