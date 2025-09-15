from modulo_paciente import menu_pacientes
from modulo_usuario import menu_usuarios
from modulo_ingreso import menu_ingresos
from modulo_egreso import menu_egresos

def menu_principal():
    while True:
        print("\n=== SISTEMA DE CONTROL DE EMERGENCIAS - CLÍNICA LA FUENTE ===")
        print("1. Gestión de Pacientes")
        print("2. Gestión de Usuarios")
        print("3. Gestión de Ingresos")
        print("4. Gestión de Egresos")
        print("0. Salir")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            menu_pacientes()
        elif opcion == "2":
            menu_usuarios()
        elif opcion == "3":
            menu_ingresos()
        elif opcion == "4":
            menu_egresos()
        elif opcion == "0":
            print("👋 Saliendo del sistema...")
            break
        else:
            print("❌ Opción inválida. Intente nuevamente.")

if __name__ == "__main__":
    menu_principal()
