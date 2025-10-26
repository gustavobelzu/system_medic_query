import sqlite3, os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QLabel, QMessageBox, QLineEdit, QFormLayout, QDialog
)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "emergencias.db")

def conectar():
    return sqlite3.connect(DB_PATH)

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

class UsuarioForm(QDialog):
    def __init__(self, parent=None, usuario=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar/Editar Usuario")
        self.setFixedSize(400, 360)
        self.usuario = usuario

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # -------------------------
        # Campos de formulario
        # -------------------------
        self.txt_username = QLineEdit()
        self.lbl_error_usuario = QLabel("")
        self.lbl_error_usuario.setStyleSheet("color: red; font-size: 9pt")

        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.Password)

        self.txt_confirmar = QLineEdit()
        self.txt_confirmar.setEchoMode(QLineEdit.Password)

        self.btn_ver_password = QPushButton("👁")
        self.btn_ver_password.setFixedWidth(35)
        self.btn_ver_password.setToolTip("Mostrar/Ocultar contraseña")
        self.btn_ver_password.setCheckable(True)

        # Contenedor de contraseña + botón
        pass_layout = QHBoxLayout()
        pass_layout.addWidget(self.txt_password)
        pass_layout.addWidget(self.btn_ver_password)

        self.txt_nombre = QLineEdit()
        self.txt_cargo = QLineEdit()
        self.txt_especialidad = QLineEdit()

        form_layout.addRow("Usuario:", self.txt_username)
        form_layout.addRow("", self.lbl_error_usuario)
        form_layout.addRow("Contraseña:", pass_layout)
        form_layout.addRow("Confirmar contraseña:", self.txt_confirmar)
        form_layout.addRow("Nombre completo:", self.txt_nombre)
        form_layout.addRow("Cargo:", self.txt_cargo)
        form_layout.addRow("Especialidad:", self.txt_especialidad)

        layout.addLayout(form_layout)

        # -------------------------
        # Botones
        # -------------------------
        btn_layout = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar")
        self.btn_cancelar = QPushButton("Cancelar")
        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(self.btn_cancelar)
        layout.addLayout(btn_layout)

        # -------------------------
        # Conexiones
        # -------------------------
        self.btn_guardar.clicked.connect(self.guardar)
        self.btn_cancelar.clicked.connect(self.close)
        self.btn_ver_password.toggled.connect(self.toggle_password)
        self.txt_username.textChanged.connect(self.verificar_usuario)

        # -------------------------
        # Modo edición
        # -------------------------
        if usuario:
            self.txt_username.setText(usuario[0])
            self.txt_username.setEnabled(False)
            self.txt_nombre.setText(usuario[1])
            self.txt_cargo.setText(usuario[2])
            self.txt_especialidad.setText(usuario[3] if usuario[3] else "")

    # Mostrar/Ocultar contraseña
    def toggle_password(self, checked):
        modo = QLineEdit.Normal if checked else QLineEdit.Password
        self.txt_password.setEchoMode(modo)
        self.txt_confirmar.setEchoMode(modo)

    # Verifica si el usuario ya existe (solo al crear)
    def verificar_usuario(self):
        if self.usuario:  # Si está editando, no valida existencia
            return

        username = self.txt_username.text().strip()
        if not username:
            self.lbl_error_usuario.setText("")
            return

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM Usuario WHERE username=?", (username,))
        existe = cursor.fetchone()
        conn.close()

        if existe:
            self.lbl_error_usuario.setText("⚠️ El usuario ya existe")
        else:
            self.lbl_error_usuario.setText("")

    # Guardar usuario
    # Guardar usuario
    def guardar(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text().strip()
        confirmar = self.txt_confirmar.text().strip()
        nombre = self.txt_nombre.text().strip()
        cargo = self.txt_cargo.text().strip()
        especialidad = self.txt_especialidad.text().strip()

        if not all([username, nombre, cargo]):
            QMessageBox.warning(self, "Error", "Usuario, Nombre y Cargo son obligatorios")
            return

        if not self.usuario:  # Solo al crear
            if self.lbl_error_usuario.text():
                QMessageBox.warning(self, "Error", "El usuario ya existe.")
                return
            if not password:
                QMessageBox.warning(self, "Error", "Debe ingresar una contraseña.")
                return
            if password != confirmar:
                QMessageBox.warning(self, "Error", "Las contraseñas no coinciden.")
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
                mensaje = "Usuario actualizado exitosamente"
            else:
                cursor.execute("INSERT INTO Usuario (username, password) VALUES (?, ?)", (username, password))
                id_usuario = cursor.lastrowid
                cursor.execute("""
                    INSERT INTO Personal (id_usuario, nombre, cargo, especialidad) 
                    VALUES (?, ?, ?, ?)
                """, (id_usuario, nombre, cargo, especialidad if especialidad else None))
                mensaje = "Usuario registrado exitosamente"

            conn.commit()
            QMessageBox.information(self, "Éxito", mensaje)
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
