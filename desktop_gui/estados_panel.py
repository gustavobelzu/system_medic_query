import sqlite3
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QLabel, QMessageBox, QLineEdit, QFormLayout, QDialog
)
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "emergencias.db")

def conectar():
    return sqlite3.connect(DB_PATH)

# ==========================
# Formulario de Estado
# ==========================
class EstadoForm(QDialog):
    def __init__(self, parent=None, estado=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar/Editar Estado")
        self.setFixedSize(350, 250)  # aumentar ancho y alto
        self.estado = estado

        layout = QVBoxLayout()
        self.setLayout(layout)

        form_layout = QFormLayout()
        self.txt_estado = QLineEdit()

        self.lbl_error_estado = QLabel("")  # etiqueta de error
        self.lbl_error_estado.setStyleSheet("color: red; font-size: 10pt")
        self.lbl_error_estado.setWordWrap(True)  # permitir que el texto se rompa
        self.lbl_error_estado.setMinimumHeight(20)  # altura mínima para que sea visible

        self.txt_condicion = QLineEdit()

        form_layout.addRow("Estado:", self.txt_estado)
        form_layout.addRow("", self.lbl_error_estado)
        form_layout.addRow("Condición especial:", self.txt_condicion)
        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar")
        self.btn_cancelar = QPushButton("Cancelar")
        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(self.btn_cancelar)
        layout.addLayout(btn_layout)

        self.btn_guardar.clicked.connect(self.guardar)
        self.btn_cancelar.clicked.connect(self.close)

        if estado:
            self.txt_estado.setText(estado[1])
            self.txt_condicion.setText(estado[2] if estado[2] else "")

        self.txt_estado.textChanged.connect(self.verificar_estado)


    # -------------------------
    # Validación de duplicados
    # -------------------------
    def verificar_estado(self):
        if self.estado:  # Si estamos editando, no validar
            self.lbl_error_estado.setText("")
            return
        estado_text = self.txt_estado.text().strip()
        if not estado_text:
            self.lbl_error_estado.setText("")
            return
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM Estado WHERE estado=?", (estado_text,))
        existe = cursor.fetchone()
        conn.close()
        if existe:
            self.lbl_error_estado.setText("⚠️ Este estado ya existe")
        else:
            self.lbl_error_estado.setText("")

    # -------------------------
    # Guardar estado
    # -------------------------
    def guardar(self):
        estado_text = self.txt_estado.text().strip()
        condicion = self.txt_condicion.text().strip()

        if not estado_text:
            QMessageBox.warning(self, "Error", "El campo Estado es obligatorio")
            return

        # Validación final de duplicado
        if not self.estado:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM Estado WHERE estado=?", (estado_text,))
            if cursor.fetchone():
                self.lbl_error_estado.setText("⚠️ Este estado ya existe")
                conn.close()
                return
            conn.close()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            if self.estado:
                cursor.execute(
                    "UPDATE Estado SET estado=?, condicion_especial=? WHERE id_estado=?",
                    (estado_text, condicion if condicion else None, self.estado[0])
                )
            else:
                cursor.execute(
                    "INSERT INTO Estado (estado, condicion_especial) VALUES (?, ?)",
                    (estado_text, condicion if condicion else None)
                )
            conn.commit()
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Ocurrió un error: {e}")
        finally:
            conn.close()


# ==========================
# Panel Estados
# ==========================
class EstadosPanel(QWidget):
    def __init__(self, volver_callback=None):
        super().__init__()
        self.volver_callback = volver_callback
        self.setWindowTitle("Módulo Estados")
        self.setMinimumSize(600, 400)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        lbl_titulo = QLabel("Gestión de Estados")
        lbl_titulo.setStyleSheet("font-weight:bold; font-size:16pt")
        main_layout.addWidget(lbl_titulo)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["ID", "Estado", "Condición Especial"])
        self.tabla.setColumnWidth(0, 60)    # ID
        self.tabla.setColumnWidth(1, 200)   # Estado
        self.tabla.setColumnWidth(2, 300)   # Condición Especial
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setMinimumHeight(250)
        main_layout.addWidget(self.tabla, stretch=1)


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

        self.btn_crear.clicked.connect(self.agregar)
        self.btn_modificar.clicked.connect(self.editar)
        self.btn_eliminar.clicked.connect(self.eliminar)
        self.btn_volver.clicked.connect(self.volver)

        self.listar_estados()
        self.tabla.resizeColumnsToContents()

    def listar_estados(self):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id_estado, estado, condicion_especial FROM Estado")
        estados = cursor.fetchall()
        conn.close()

        self.tabla.setRowCount(0)
        for i, e in enumerate(estados):
            self.tabla.insertRow(i)
            for j, val in enumerate(e):
                self.tabla.setItem(i, j, QTableWidgetItem(str(val) if val else "N/A"))

    def agregar(self):
        form = EstadoForm(self)
        if form.exec():
            self.listar_estados()

    def editar(self):
        selected = self.tabla.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Error", "Seleccione un estado para modificar")
            return
        id_estado = selected[0].text()
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Estado WHERE id_estado=?", (id_estado,))
        estado = cursor.fetchone()
        conn.close()
        form = EstadoForm(self, estado)
        if form.exec():
            self.listar_estados()

    def eliminar(self):
        selected = self.tabla.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Error", "Seleccione un estado para eliminar")
            return
        id_estado = selected[0].text()
        reply = QMessageBox.question(self, "Confirmar", f"Eliminar estado {id_estado}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Estado WHERE id_estado=?", (id_estado,))
            conn.commit()
            conn.close()
            self.listar_estados()

    def volver(self):
        if self.volver_callback:
            self.volver_callback()
