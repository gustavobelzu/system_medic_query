import sqlite3
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QLabel, QMessageBox, QLineEdit, QFormLayout, QDialog, QComboBox
)

# ==========================
# CONFIGURACIÓN
# ==========================
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "emergencias.db")

DEPARTAMENTOS = [
    "La Paz", "Cochabamba", "Santa Cruz",
    "Oruro", "Potosí", "Chuquisaca",
    "Tarija", "Beni", "Pando"
]

def conectar():
    return sqlite3.connect(DB_PATH)

# ==========================
# FORMULARIO DE PACIENTE
# ==========================
class PacienteForm(QDialog):
    def __init__(self, parent=None, paciente=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar/Editar Paciente")
        self.setFixedSize(400, 420)
        self.paciente = paciente

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Formulario
        form_layout = QFormLayout()
        self.txt_ci = QLineEdit()
        self.lbl_error_ci = QLabel("")  # <-- etiqueta de error
        self.lbl_error_ci.setStyleSheet("color: red; font-size: 9pt")

        self.txt_nombre = QLineEdit()
        self.txt_edad = QLineEdit()
        self.txt_sexo = QLineEdit()
        self.cmb_departamento = QComboBox()
        self.cmb_departamento.addItems(DEPARTAMENTOS)
        self.txt_telefono = QLineEdit()
        self.cmb_estado = QComboBox()

        # Cargar estados desde la BD
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id_estado, estado FROM Estado")
        self.estados = cursor.fetchall()
        conn.close()
        for e in self.estados:
            self.cmb_estado.addItem(e[1], e[0])

        form_layout.addRow("CI:", self.txt_ci)
        form_layout.addRow("", self.lbl_error_ci)  # <-- mostrar mensaje aquí
        form_layout.addRow("Nombre:", self.txt_nombre)
        form_layout.addRow("Edad:", self.txt_edad)
        form_layout.addRow("Sexo (M/F):", self.txt_sexo)
        form_layout.addRow("Departamento:", self.cmb_departamento)
        form_layout.addRow("Teléfono:", self.txt_telefono)
        form_layout.addRow("Estado:", self.cmb_estado)
        layout.addLayout(form_layout)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar")
        self.btn_cancelar = QPushButton("Cancelar")
        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(self.btn_cancelar)
        layout.addLayout(btn_layout)

        self.btn_guardar.clicked.connect(self.guardar)
        self.btn_cancelar.clicked.connect(self.close)

        # Si se pasa paciente, cargar datos
        if paciente:
            self.txt_ci.setText(str(paciente[0]))
            self.txt_ci.setEnabled(False)
            self.txt_nombre.setText(paciente[1])
            self.txt_edad.setText(str(paciente[2]))
            self.txt_sexo.setText(paciente[3])
            self.cmb_departamento.setCurrentText(paciente[4])
            self.txt_telefono.setText(str(paciente[5]))
            # Buscar índice del estado
            estado_id = paciente[6]
            for i in range(self.cmb_estado.count()):
                if self.cmb_estado.itemData(i) == estado_id:
                    self.cmb_estado.setCurrentIndex(i)
                    break

        # Validar CI en tiempo real
        self.txt_ci.textChanged.connect(self.verificar_ci)

    # -------------------------
    # Validación CI
    # -------------------------
    def verificar_ci(self):
        if self.paciente:  # Si estamos editando, no validar
            self.lbl_error_ci.setText("")
            return
        ci = self.txt_ci.text().strip()
        if not ci:
            self.lbl_error_ci.setText("")
            return
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM Paciente WHERE ci=?", (ci,))
        existe = cursor.fetchone()
        conn.close()
        if existe:
            self.lbl_error_ci.setText("⚠️ Este CI ya está registrado")
        else:
            self.lbl_error_ci.setText("")

    # -------------------------
    # Guardar paciente
    # -------------------------
    def guardar(self):
        ci = self.txt_ci.text().strip()
        nombre = self.txt_nombre.text().strip()
        edad = self.txt_edad.text().strip()
        sexo = self.txt_sexo.text().strip().upper()
        departamento = self.cmb_departamento.currentText()
        telefono = self.txt_telefono.text().strip()
        id_estado = self.cmb_estado.currentData()

        if not all([ci, nombre, edad, sexo, departamento, telefono, id_estado]):
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios.")
            return

        if sexo not in ["M", "F"]:
            QMessageBox.warning(self, "Error", "El sexo debe ser 'M' o 'F'.")
            return

        # Validación final de CI duplicado
        if not self.paciente:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM Paciente WHERE ci=?", (ci,))
            if cursor.fetchone():
                self.lbl_error_ci.setText("⚠️ Este CI ya está registrado")
                conn.close()
                return
            conn.close()

        conn = conectar()
        cursor = conn.cursor()
        try:
            if self.paciente:
                cursor.execute("""
                    UPDATE Paciente
                    SET nombre=?, edad=?, sexo=?, departamento=?, telefono=?, id_estado=?
                    WHERE ci=?
                """, (nombre, edad, sexo, departamento, telefono, id_estado, ci))
            else:
                cursor.execute("""
                    INSERT INTO Paciente (ci,nombre,edad,sexo,departamento,telefono,id_estado)
                    VALUES (?,?,?,?,?,?,?)
                """, (ci, nombre, edad, sexo, departamento, telefono, id_estado))
            conn.commit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error: {e}")
        finally:
            conn.close()


# ==========================
# PANEL PACIENTES
# ==========================
class PacientesPanel(QWidget):
    def __init__(self, volver_callback=None):
        super().__init__()
        self.volver_callback = volver_callback
        self.setWindowTitle("Módulo Pacientes")
        self.setMinimumSize(750, 450)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Título
        lbl_titulo = QLabel("Gestión de Pacientes")
        lbl_titulo.setStyleSheet("font-weight:bold; font-size:16pt")
        main_layout.addWidget(lbl_titulo)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels(["CI","Nombre","Edad","Sexo","Depto","Teléfono","Estado"])
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setMinimumHeight(300)
        main_layout.addWidget(self.tabla, stretch=1)

        # Botones
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
        main_layout.addLayout(btn_layout)

        # Conectar botones
        self.btn_crear.clicked.connect(self.agregar)
        self.btn_modificar.clicked.connect(self.editar)
        self.btn_eliminar.clicked.connect(self.eliminar)
        self.btn_volver.clicked.connect(self.volver)

        self.listar_pacientes()

    def listar_pacientes(self):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.ci, p.nombre, p.edad, p.sexo, p.departamento, p.telefono, e.estado
            FROM Paciente p
            LEFT JOIN Estado e ON p.id_estado = e.id_estado
        """)
        pacientes = cursor.fetchall()
        conn.close()

        self.tabla.setRowCount(0)
        for fila_idx, p in enumerate(pacientes):
            self.tabla.insertRow(fila_idx)
            for col_idx, valor in enumerate(p):
                self.tabla.setItem(fila_idx, col_idx, QTableWidgetItem(str(valor) if valor else "N/A"))

    def agregar(self):
        form = PacienteForm(self)
        if form.exec():
            self.listar_pacientes()

    def editar(self):
        selected = self.tabla.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Error", "Seleccione un paciente para modificar.")
            return
        ci = selected[0].text()
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ci,nombre,edad,sexo,departamento,telefono,id_estado
            FROM Paciente WHERE ci=?
        """, (ci,))
        paciente = cursor.fetchone()
        conn.close()
        form = PacienteForm(self, paciente)
        if form.exec():
            self.listar_pacientes()

    def eliminar(self):
        selected = self.tabla.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Error", "Seleccione un paciente para eliminar.")
            return
        ci = selected[0].text()
        reply = QMessageBox.question(self, "Confirmar", f"¿Eliminar paciente {ci}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Paciente WHERE ci=?", (ci,))
            conn.commit()
            conn.close()
            self.listar_pacientes()

    def volver(self):
        if self.volver_callback:
            self.volver_callback()
