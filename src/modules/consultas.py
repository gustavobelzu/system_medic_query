from datetime import datetime

from pathlib import Path

# ==========================
# Exportar a PDF con opción de ruta
# ==========================
def exportar_pdf(headers, rows, title="Consulta"):
    # Preguntar ruta completa al usuario
    ruta = Prompt.ask("Ruta completa para guardar el PDF (ej: C:/Users/Usuario/Desktop/consulta.pdf)")
    ruta = Path(ruta)  # Convierte a Path
    ruta.parent.mkdir(parents=True, exist_ok=True)  # Crea carpeta si no existe

    c = canvas.Canvas(str(ruta), pagesize=letter)
    width, height = letter
    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, title)
    y -= 30

    c.setFont("Helvetica-Bold", 12)
    for i, h in enumerate(headers):
        c.drawString(50 + i*100, y, h)
    y -= 20

    c.setFont("Helvetica", 10)
    for row in rows:
        for i, r in enumerate(row):
            c.drawString(50 + i*100, y, str(r))
        y -= 20
        if y < 50:
            c.showPage()
            y = height - 50

    c.save()
    console.print(f"✅ PDF generado en: {ruta}", style="green")


def consultas(user=None):
    conn = conectar()
    cursor = conn.cursor()

    tablas_disponibles = ["Paciente", "Estado", "Ingreso", "Egreso", "Usuario", "Personal", "Ingreso_Personal"]

    while True:
        console.print("\n--- MÓDULO CONSULTAS INTERACTIVAS ---", style="bold magenta")
        console.print("Tablas disponibles:", ", ".join(tablas_disponibles))
        console.print("0 - Salir")
        tabla = Prompt.ask("Ingrese la tabla que desea consultar").strip()

        if tabla == "0":
            break
        if tabla not in tablas_disponibles:
            console.print("❌ Tabla inválida.", style="red")
            continue

        # Columnas disponibles
        cursor.execute(f"PRAGMA table_info({tabla})")
        columnas = [info[1] for info in cursor.fetchall()]
        console.print("Columnas disponibles:", ", ".join(columnas))

        cols_input = Prompt.ask("Columnas a mostrar (separadas por coma, * para todas)", default="*").strip()
        columnas_a_mostrar = "*" if cols_input == "*" else [c.strip() for c in cols_input.split(",")]

        filtro = Prompt.ask("Filtro SQL opcional (ej: edad > 30) o ENTER para ninguno", default="").strip()
        query = f"SELECT {', '.join(columnas) if columnas_a_mostrar == '*' else ', '.join(columnas_a_mostrar)} FROM {tabla}"
        if filtro:
            query += f" WHERE {filtro}"

        try:
            cursor.execute(query)
            rows = cursor.fetchall()

            # Obtener fecha, hora y usuario actual
            fecha_actual = datetime.now().strftime("%Y-%m-%d")
            hora_actual = datetime.now().strftime("%H:%M")
            usuario_actual = user[1] if user else "N/A"

            # Mostrar tabla
            mostrar_tabla(
                columns=(columnas_a_mostrar if columnas_a_mostrar != "*" else columnas) + ["Fecha", "Hora", "Usuario"],
                rows=[list(r) + [fecha_actual, hora_actual, usuario_actual] for r in rows],
                title=f"Consulta: {tabla}"
            )

            # Exportar a PDF si desea
            if rows and Prompt.ask("¿Exportar a PDF? (s/n)", choices=["s","n"], default="n") == "s":
                    exportar_pdf(
                            headers=(columnas_a_mostrar if columnas_a_mostrar != "*" else columnas) + ["Fecha", "Hora", "Usuario"],
                            rows=[list(r) + [fecha_actual, hora_actual, usuario_actual] for r in rows],
                            title=f"Consulta: {tabla}"
                    )


        except Exception as e:
            console.print(f"❌ Error en la consulta: {e}", style="red")

    conn.close()
