from operaciones import registrar_paciente, listar_pacientes

def menu_principal():
    while True:
        print("\n=== SISTEMA DE EMERGENCIAS - CLÍNICA LA FUENTE ===")
        print("1. Gestión de Pacientes")
        print("2. Gestión de Usuarios")
        print("3. Ingresos")
        print("4. Egresos")
        print("0. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            menu_pacientes()
        elif opcion == "0":
            print("👋 Saliendo del sistema...")
            break
        else:
            print("⚠️ Opción inválida")

def menu_pacientes():
    while True:
        print("\n--- MENÚ PACIENTES ---")
        print("1. Registrar Paciente")
        print("2. Listar Pacientes")
        print("0. Volver")

        opcion = input("Seleccione: ")

        if opcion == "1":
            ci = input("CI: ")
            nombre = input("Nombre: ")
            edad = int(input("Edad: "))
            sexo = input("Sexo (M/F): ")
            id_estado = input("ID Estado (opcional, ENTER=Null): ")
            id_estado = int(id_estado) if id_estado else None
            registrar_paciente(ci, nombre, edad, sexo, id_estado)
        elif opcion == "2":
            listar_pacientes()
        elif opcion == "0":
            break
        else:
            print("⚠️ Opción inválida")
