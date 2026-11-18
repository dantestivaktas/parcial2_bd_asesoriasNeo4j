from conexion import conectar_bd, cerrar_bd
from seed import cargar_datos_iniciales
import operaciones as op


# Mostrar el menu principal en consola
def mostrar_menu():
    print("\n--- MENU PRINCIPAL ---")
    print("1. Reiniciar datos iniciales (Seed)")
    print("2. Crear estudiante o materia")
    print("3. Registrar curso o colaboracion")
    print("4. Listar estudiantes y materias")
    print("5. Ver historial de un estudiante")
    print("6. Actualizar semestre o calificacion")
    print("7. Eliminar estudiante o dar de baja curso")
    print("8. Recomendar asesores para una materia")
    print("9. Camino mas corto entre dos estudiantes")
    print("0. Salir")


def main():
    driver = conectar_bd()
    if driver is None:
        return

    try:
        while True:
            mostrar_menu()
            opcion = input("Opcion: ").strip()

            if opcion == "1":
                if input("Reiniciar datos en la nube? (s/n): ").strip().lower() == "s":
                    cargar_datos_iniciales(driver)

            elif opcion == "2":
                sub = input("1. Estudiante | 2. Materia: ").strip()
                if sub == "1":
                    mat = input("Matricula: ")
                    nom = input("Nombre: ")
                    car = input("Carrera: ")
                    sem = input("Semestre: ")
                    _, msg = op.crear_estudiante(driver, mat, nom, car, sem)
                    print(msg)
                elif sub == "2":
                    cod = input("Codigo: ")
                    nom = input("Nombre: ")
                    area = input("Area: ")
                    _, msg = op.crear_materia(driver, cod, nom, area)
                    print(msg)

            elif opcion == "3":
                sub = input("1. Curso | 2. Colaboracion: ").strip()
                if sub == "1":
                    mat = input("Matricula: ")
                    cod = input("Codigo materia: ")
                    cal = input("Calificacion: ")
                    per = input("Periodo (ej. 2026-1): ")
                    _, msg = op.registrar_curso(driver, mat, cod, cal, per)
                    print(msg)
                elif sub == "2":
                    m1 = input("Matricula 1: ")
                    m2 = input("Matricula 2: ")
                    proy = input("Proyecto: ")
                    _, msg = op.registrar_colaboracion(driver, m1, m2, proy)
                    print(msg)

            elif opcion == "4":
                print("--- ESTUDIANTES ---")
                for e in op.listar_estudiantes(driver):
                    print(e["matricula"], "|", e["nombre"], "|", e["carrera"], "| Sem:", e["semestre"])
                print("--- MATERIAS ---")
                for m in op.listar_materias(driver):
                    print(m["codigo"], "|", m["nombre"], "| Area:", m["area"])

            elif opcion == "5":
                mat = input("Matricula: ")
                ok, msg, datos = op.consultar_historial(driver, mat)
                if not ok:
                    print(msg)
                else:
                    est = datos["estudiante"]
                    print("Estudiante:", est["nombre"], "-", est["matricula"], "| Semestre:", est["semestre"])
                    print("Cursos:")
                    for c in datos["cursos"]:
                        print(" -", c["codigo"], c["materia"], "| Calif:", c["calificacion"], "| Periodo:", c["periodo"])
                    print("Colaboraciones:")
                    for col in datos["colaboraciones"]:
                        print(" -", col["nombre"], "(", col["matricula"], ") | Proyecto:", col["proyecto"])

            elif opcion == "6":
                sub = input("1. Semestre | 2. Calificacion: ").strip()
                if sub == "1":
                    mat = input("Matricula: ")
                    sem = input("Nuevo semestre: ")
                    _, msg = op.actualizar_semestre(driver, mat, sem)
                    print(msg)
                elif sub == "2":
                    mat = input("Matricula: ")
                    cod = input("Codigo materia: ")
                    per = input("Periodo (opcional): ")
                    cal = input("Nueva calificacion: ")
                    _, msg = op.actualizar_calificacion(driver, mat, cod, cal, per)
                    print(msg)

            elif opcion == "7":
                sub = input("1. Eliminar estudiante | 2. Dar de baja curso: ").strip()
                if sub == "1":
                    mat = input("Matricula: ")
                    _, msg = op.eliminar_estudiante(driver, mat)
                    print(msg)
                elif sub == "2":
                    mat = input("Matricula: ")
                    cod = input("Codigo materia: ")
                    per = input("Periodo (opcional): ")
                    _, msg = op.eliminar_curso(driver, mat, cod, per)
                    print(msg)

            elif opcion == "8":
                mat = input("Tu matricula: ")
                cod = input("Codigo materia: ")
                ok, msg, datos = op.recomendar_asesores(driver, mat, cod)
                if not ok:
                    print(msg)
                else:
                    print("Asesores para", datos["materia"], ":")
                    for a in datos["asesores"]:
                        print(" -", a["nombre"], "(", a["matricula"], ") | Calif:", a["calificacion"], "|", a["estado"])

            elif opcion == "9":
                origen = input("Matricula origen: ")
                destino = input("Matricula destino: ")
                ok, msg, datos = op.buscar_camino_mas_corto(driver, origen, destino)
                if not ok:
                    print(msg)
                else:
                    print("Saltos:", datos["saltos"])
                    for p in datos["pasos"]:
                        print(" Paso", p["numero"], ":", p["desde_nombre"], "--", p["relacion"], "-->", p["hacia_nombre"])

            elif opcion == "0":
                print("Saliendo...")
                break
            else:
                print("Opcion no valida.")
    finally:
        cerrar_bd(driver)


if __name__ == "__main__":
    main()
