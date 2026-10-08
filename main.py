"""Menú de consola: DEPURACIÓN Y FORMA NORMAL DE CHOMSKY (sección 12 del lineamiento).

Uso:  python main.py
Modo paso a paso: opciones 4 a 8.  Modo automático: opción 9.
"""
from cfg import Converter, build_grammar
from cfg.report import format_history, format_step
from cfg.transformations import check_cnf

MENU = """
DEPURACIÓN Y FORMA NORMAL DE CHOMSKY
 1. Ingresar gramática
 2. Mostrar gramática original
 3. Validar gramática
 4. Eliminar producciones nulas
 5. Eliminar producciones unitarias
 6. Eliminar variables inútiles
 7. Eliminar variables inalcanzables
 8. Convertir a Forma Normal de Chomsky
 9. Ejecutar proceso completo
10. Mostrar historial de transformaciones
11. Mostrar gramática final
12. Ingresar nueva gramática
13. Salir
"""
STEP_OPTIONS = {"4": "nulas", "5": "unitarias", "6": "inutiles", "7": "inalcanzables", "8": "fnc"}


def read_grammar():
    """Pide los datos de la gramática (RF01-RF05). Devuelve el Converter o None si hay errores."""
    variables = input("Variables (separadas por coma o espacio): ")
    terminals = input("Terminales: ")
    start = input("Símbolo inicial: ")
    print("Producciones, una por línea (ej. S -> A B | a | ε). Línea vacía para terminar:")
    lines = []
    while True:
        line = input()
        if not line.strip():
            break
        lines.append(line)
    grammar, errors = build_grammar(variables, terminals, start, "\n".join(lines))
    if errors:
        print("\nLa gramática tiene errores; corríjalos antes de continuar:")
        print("\n".join(errors))
        return None
    print("\nGramática registrada y validada correctamente.")
    return Converter(grammar)


def main():
    converter = None
    while True:
        print(MENU)
        option = input("Seleccione una opción: ").strip()
        if option in ("1", "12"):
            converter = read_grammar()  # RF20: reemplaza la gramática anterior
        elif option == "13":
            print("Hasta luego.")
            break
        elif converter is None:
            print("Primero debe ingresar una gramática válida (opción 1).")
        elif option == "2":
            print(converter.original.format())
        elif option == "3":
            print("La gramática está correctamente definida." if converter else "")
        elif option in STEP_OPTIONS:
            for step in converter.apply(STEP_OPTIONS[option]):
                print(format_step(step, len(converter.history)))
        elif option == "9":
            converter = Converter(converter.original)  # reinicia el historial
            print(format_history(converter.run_all()))
        elif option == "10":
            print(format_history(converter.history))
        elif option == "11":
            problems = check_cnf(converter.current)
            print(converter.current.format())
            print("\n✔ Está en Forma Normal de Chomsky." if not problems else
                  "\nAún NO está en FNC:\n" + "\n".join(problems))
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()
