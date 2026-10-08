# GLC → Forma Normal de Chomsky

Microproyecto #1 – Teoría de la Computación. Valida una Gramática Libre de Contexto, la depura
(nulas, unitarias, variables inútiles e inalcanzables) y la convierte a Forma Normal de Chomsky,
mostrando cada etapa. Incluye interfaz web (Flask, desplegable en Vercel) y menú de consola.

## Ejecutar en local
```bash
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py              # web en http://127.0.0.1:5000
python main.py             # menú de consola (sección 12 del lineamiento)
python -m unittest tests.test_cfg -v    # pruebas
```
El menú de consola y el paquete `cfg` solo usan la biblioteca estándar; Flask se necesita únicamente para la web.

## Desplegar en Vercel
1. Suba esta carpeta a un repositorio de GitHub (`app.py` y `requirements.txt` deben quedar en la raíz).
2. En vercel.com: *Add New → Project*, importe el repositorio y pulse *Deploy*. Vercel detecta Flask solo.
3. O con la CLI: `npm i -g vercel && vercel` (y `vercel --prod` para producción).

## Estructura
| Archivo | Contenido |
|---|---|
| `cfg/grammar.py` | Clase `Grammar` (V, T, P, S), nombres nuevos X1, X2… sin colisiones |
| `cfg/parser.py` | Lectura de la entrada y validación inicial (sección 8) |
| `cfg/transformations.py` | Algoritmos: anulables, unitarias, generadoras, alcanzables, terminales, producciones largas, validación FNC |
| `cfg/converter.py` | Ejecución paso a paso / automática e historial |
| `cfg/report.py` | Texto de cada etapa para la consola |
| `main.py` | Menú de consola |
| `app.py`, `webui.py` | API Flask e interfaz web |
| `tests/test_cfg.py` | Pruebas (incluye 300 gramáticas aleatorias que comparan el lenguaje antes y después) |

## Decisiones de diseño
- **Orden del proceso completo:** nulas → unitarias → inútiles (no generadoras) → inalcanzables → FNC (terminales, producciones largas, validación).
- **Cadena vacía:** si ε ∈ L(G) se conserva `S -> ε` como única excepción; si el inicial aparece en un lado derecho se crea un nuevo inicial `S0 -> S | ε`.
- **Lenguaje vacío:** si el inicial no es generador se avisa y la gramática queda sin producciones.
- **Reproducibilidad:** todo se recorre en orden de declaración, así una misma gramática da siempre el mismo resultado.
- **Entrada:** `S -> A S B | ε`. Se acepta `->`, `→` o `::=`; ε se puede escribir `ε`, `λ`, `epsilon` o `&`.
