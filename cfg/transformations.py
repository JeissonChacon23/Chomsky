"""Algoritmos de depuración y transformación de una GLC a Forma Normal de Chomsky.

Cada función recibe una gramática, NO la modifica y devuelve un `Step` con:
gramática inicial de la etapa, elementos identificados, producciones eliminadas,
producciones agregadas y gramática resultante (RF18).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
from typing import Dict, List, Optional, Set, Tuple

from .grammar import EPSILON, Grammar, Production


# --------------------------------------------------------------------------- paso
@dataclass
class Step:
    key: str
    title: str
    description: str
    before: Grammar
    after: Grammar
    identified: List[Tuple[str, List[str]]] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    added: List[str] = field(default_factory=list)
    variables_removed: List[str] = field(default_factory=list)
    variables_added: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    status: Optional[str] = None  # 'ok' | 'error' (solo en la validación final)

    def to_dict(self) -> dict:
        sep = self.before.separator(self.after)
        return {
            "key": self.key,
            "title": self.title,
            "description": self.description,
            "before": self.before.to_dict(sep),
            "after": self.after.to_dict(sep),
            "identified": [{"label": label, "items": items} for label, items in self.identified],
            "removed": self.removed,
            "added": self.added,
            "variables_removed": self.variables_removed,
            "variables_added": self.variables_added,
            "notes": self.notes,
            "status": self.status,
        }


def _make_step(key: str, title: str, description: str, before: Grammar, after: Grammar,
               identified: List[Tuple[str, List[str]]], notes: Optional[List[str]] = None) -> Step:
    """Calcula producciones eliminadas/agregadas comparando antes y después."""
    sep = before.separator(after)
    before_set, after_set = set(before.all_productions()), set(after.all_productions())
    fmt = Grammar.production_text
    return Step(
        key=key, title=title, description=description, before=before, after=after,
        identified=identified,
        removed=[fmt(l, r, sep) for l, r in before.all_productions() if (l, r) not in after_set],
        added=[fmt(l, r, sep) for l, r in after.all_productions() if (l, r) not in before_set],
        variables_removed=[v for v in before.variables if v not in after.variables],
        variables_added=[v for v in after.variables if v not in before.variables],
        notes=notes or [],
    )


def _ordered(names: Set[str], grammar: Grammar) -> List[str]:
    """Ordena un conjunto de variables según el orden de declaración."""
    return [v for v in grammar.variables if v in names]


def _none_if_empty(items: List[str]) -> List[str]:
    return items if items else ["(ninguno)"]


# ---------------------------------------------------------- producciones nulas
def nullable_variables(g: Grammar) -> Set[str]:
    """Variables anulables: A es anulable si A =>* ε (punto fijo)."""
    nullable: Set[str] = set()
    changed = True
    while changed:
        changed = False
        for lhs, rhs in g.all_productions():
            if lhs not in nullable and all(s in nullable for s in rhs):  # rhs vacío => True
                nullable.add(lhs)
                changed = True
    return nullable


def eliminate_null_productions(g: Grammar) -> Step:
    """RF07 / RF08. Elimina A -> ε generando todas las variantes sin las variables anulables."""
    nullable = nullable_variables(g)
    sep = g.separator()
    null_prods = [Grammar.production_text(l, r, sep) for l, r in g.all_productions() if not r]
    identified = [
        ("Variables anulables", _none_if_empty(_ordered(nullable, g))),
        ("Producciones nulas", _none_if_empty(null_prods)),
    ]
    after = Grammar(g.variables, g.terminals, g.start)
    notes: List[str] = []

    for lhs in g.variables:
        for rhs in g.productions.get(lhs, []):
            if not rhs:
                continue  # las producciones nulas se eliminan
            positions = [i for i, s in enumerate(rhs) if s in nullable]
            # Para cada subconjunto de ocurrencias anulables se genera una variante.
            # La primera combinación (nada omitido) es la producción original.
            for omit_flags in product((False, True), repeat=len(positions)):
                omitted = {positions[k] for k, flag in enumerate(omit_flags) if flag}
                variant = tuple(s for i, s in enumerate(rhs) if i not in omitted)
                if variant:  # nunca se genera una nueva producción nula
                    after.add_production(lhs, variant)

    if g.start in nullable:
        # ε pertenece al lenguaje: tratamiento especial (RNF07).
        if after.start_in_right_side():
            new_start = after.fresh_start_symbol()
            after.add_variable(new_start, at_front=True)
            after.productions[new_start] = []
            after.add_production(new_start, (g.start,))
            after.add_production(new_start, ())
            after.start = new_start
            notes.append(
                f"El símbolo inicial {g.start} es anulable y aparece en lados derechos: se crea el nuevo "
                f"inicial {new_start} con {new_start} -> {g.start} | ε para conservar ε en el lenguaje."
            )
        else:
            after.add_production(g.start, ())
            notes.append(
                f"El símbolo inicial {g.start} es anulable: se conserva {g.start} -> ε "
                "(única producción nula permitida, pues el inicial no aparece en lados derechos)."
            )
    elif not nullable:
        notes.append("La gramática no tiene variables anulables: no hay cambios.")

    return _make_step(
        "nulas", "Eliminación de producciones nulas",
        "Se calculan las variables anulables y, por cada producción, se agregan las variantes que "
        "omiten combinaciones de variables anulables; luego se eliminan las producciones A -> ε.",
        g, after, identified, notes)


# ------------------------------------------------------- producciones unitarias
def unit_closure(g: Grammar) -> Dict[str, List[str]]:
    """Para cada A, las variables B tales que A =>* B usando solo producciones unitarias."""
    variables = g.variable_set()
    closure: Dict[str, List[str]] = {}
    for a in g.variables:
        reach = {a}
        stack = [a]
        while stack:
            x = stack.pop()
            for rhs in g.productions.get(x, []):
                if len(rhs) == 1 and rhs[0] in variables and rhs[0] not in reach:
                    reach.add(rhs[0])
                    stack.append(rhs[0])
        closure[a] = [a] + [v for v in g.variables if v in reach and v != a]
    return closure


def eliminate_unit_productions(g: Grammar) -> Step:
    """RF09 / RF10. Sustituye A -> B por las producciones no unitarias de B (y de su cierre)."""
    variables = g.variable_set()
    sep = g.separator()
    units = [Grammar.production_text(l, r, sep) for l, r in g.all_productions()
             if len(r) == 1 and r[0] in variables]
    closure = unit_closure(g)
    pairs = [f"{a} ⇒* {b}" for a in g.variables for b in closure[a] if b != a]
    identified = [
        ("Producciones unitarias", _none_if_empty(units)),
        ("Pares unitarios", _none_if_empty(pairs)),
    ]
    after = Grammar(g.variables, g.terminals, g.start)
    for a in g.variables:
        for b in closure[a]:
            for rhs in g.productions.get(b, []):
                if not (len(rhs) == 1 and rhs[0] in variables):
                    after.add_production(a, rhs)
    notes = [] if units else ["No hay producciones unitarias: no hay cambios."]
    return _make_step(
        "unitarias", "Eliminación de producciones unitarias",
        "Para cada par unitario A ⇒* B se copian a A todas las producciones no unitarias de B y se "
        "eliminan las producciones de la forma A -> B.",
        g, after, identified, notes)


# --------------------------------------------------------------- variables inútiles
def generating_variables(g: Grammar) -> Set[str]:
    """RF11. Variables que derivan alguna cadena de terminales (punto fijo)."""
    terminals = g.terminal_set()
    generating: Set[str] = set()
    changed = True
    while changed:
        changed = False
        for lhs, rhs in g.all_productions():
            if lhs not in generating and all(s in terminals or s in generating for s in rhs):
                generating.add(lhs)
                changed = True
    return generating


def eliminate_useless_variables(g: Grammar) -> Step:
    """RF12. Elimina variables no generadoras y las producciones donde aparecen."""
    generating = generating_variables(g)
    non_generating = set(g.variables) - generating
    identified = [
        ("Variables generadoras", _none_if_empty(_ordered(generating, g))),
        ("Variables no generadoras (inútiles)", _none_if_empty(_ordered(non_generating, g))),
    ]
    keep = [v for v in g.variables if v in generating]
    notes: List[str] = []
    if g.start not in generating:
        keep.insert(0, g.start)  # se conserva el inicial aunque el lenguaje sea vacío
        notes.append("El símbolo inicial no es generador: el lenguaje de la gramática es vacío (∅).")
    after = Grammar(keep, g.terminals, g.start)
    for lhs in keep:
        for rhs in g.productions.get(lhs, []):
            if lhs in generating and all(s not in non_generating for s in rhs):
                after.add_production(lhs, rhs)
    if not non_generating:
        notes.append("Todas las variables son generadoras: no hay cambios.")
    return _make_step(
        "inutiles", "Eliminación de variables inútiles (no generadoras)",
        "Se calculan las variables que pueden derivar cadenas de terminales; las demás se eliminan "
        "junto con toda producción que las use.",
        g, after, identified, notes)


# ---------------------------------------------------------- variables inalcanzables
def reachable_variables(g: Grammar) -> Set[str]:
    """RF13. Variables alcanzables desde el símbolo inicial (recorrido en anchura)."""
    variables = g.variable_set()
    reach = {g.start}
    queue = [g.start]
    while queue:
        x = queue.pop(0)
        for rhs in g.productions.get(x, []):
            for s in rhs:
                if s in variables and s not in reach:
                    reach.add(s)
                    queue.append(s)
    return reach


def eliminate_unreachable_variables(g: Grammar) -> Step:
    """RF14. Elimina variables no alcanzables desde S y sus producciones."""
    reach = reachable_variables(g)
    unreachable = set(g.variables) - reach
    identified = [
        ("Variables alcanzables", _none_if_empty(_ordered(reach, g))),
        ("Variables inalcanzables", _none_if_empty(_ordered(unreachable, g))),
    ]
    keep = [v for v in g.variables if v in reach]
    after = Grammar(keep, g.terminals, g.start)
    for lhs in keep:
        for rhs in g.productions.get(lhs, []):
            after.add_production(lhs, rhs)
    notes = [] if unreachable else ["Todas las variables son alcanzables: no hay cambios."]
    return _make_step(
        "inalcanzables", "Eliminación de variables inalcanzables",
        "Se recorre la gramática desde el símbolo inicial; las variables que no se visitan se eliminan "
        "junto con sus producciones.",
        g, after, identified, notes)


# ------------------------------------------------------------------ forma normal de Chomsky
def substitute_terminals(g: Grammar) -> Step:
    """RF15. En producciones de longitud >= 2 reemplaza cada terminal a por una variable Xi -> a."""
    terminals = g.terminal_set()
    after = Grammar(g.variables, g.terminals, g.start)
    mapping: Dict[str, str] = {}
    for lhs in g.variables:
        for rhs in g.productions.get(lhs, []):
            if len(rhs) < 2:
                after.add_production(lhs, rhs)
                continue
            new_rhs = []
            for s in rhs:
                if s in terminals:
                    if s not in mapping:
                        name = after.fresh_variable("X")
                        mapping[s] = name
                        after.add_variable(name)
                        after.add_production(name, (s,))
                    new_rhs.append(mapping[s])
                else:
                    new_rhs.append(s)
            after.add_production(lhs, tuple(new_rhs))
    identified = [
        ("Terminales sustituidos", _none_if_empty([f"{t} → {v}" for t, v in mapping.items()])),
    ]
    notes = [] if mapping else ["Ningún terminal aparece en producciones de longitud mayor a uno: no hay cambios."]
    return _make_step(
        "terminales", "Sustitución de terminales",
        "Cada terminal que aparece junto a otros símbolos se reemplaza por una variable auxiliar nueva "
        "que solo produce ese terminal.",
        g, after, identified, notes)


def reduce_long_productions(g: Grammar) -> Step:
    """RF16. Convierte A -> B1 B2 ... Bn (n > 2) en producciones binarias con variables auxiliares."""
    sep = g.separator()
    long_prods = [Grammar.production_text(l, r, sep) for l, r in g.all_productions() if len(r) > 2]
    after = Grammar(g.variables, g.terminals, g.start)
    cache: Dict[Tuple[str, ...], str] = {}  # cola de símbolos -> variable auxiliar (evita duplicados)
    created: List[str] = []
    for lhs in g.variables:
        for rhs in g.productions.get(lhs, []):
            if len(rhs) <= 2:
                after.add_production(lhs, rhs)
                continue
            current, symbols = lhs, list(rhs)
            while len(symbols) > 2:
                tail = tuple(symbols[1:])
                if tail in cache:  # la misma cola ya tiene su variable auxiliar
                    after.add_production(current, (symbols[0], cache[tail]))
                    symbols = []
                    break
                name = after.fresh_variable("X")
                cache[tail] = name
                created.append(name)
                after.add_variable(name)
                after.add_production(current, (symbols[0], name))
                current, symbols = name, symbols[1:]
            if symbols:
                after.add_production(current, tuple(symbols))
    identified = [
        ("Producciones con más de dos símbolos", _none_if_empty(long_prods)),
        ("Variables auxiliares creadas", _none_if_empty(created)),
    ]
    notes = [] if long_prods else ["No hay producciones de longitud mayor a dos: no hay cambios."]
    return _make_step(
        "largas", "Reducción de producciones largas",
        "Una producción A -> B1 B2 ... Bn se reemplaza por A -> B1 X1, X1 -> B2 X2, ..., "
        "X(n-2) -> B(n-1) Bn.",
        g, after, identified, notes)


# --------------------------------------------------------------------- validación final
def check_cnf(g: Grammar) -> List[str]:
    """Algoritmo de validación de FNC (RNF12). Devuelve la lista de violaciones (vacía = válida)."""
    variables, terminals = g.variable_set(), g.terminal_set()
    sep = g.separator()
    problems: List[str] = []
    for lhs, rhs in g.all_productions():
        text = Grammar.production_text(lhs, rhs, sep)
        if len(rhs) == 0:
            if lhs != g.start:
                problems.append(f"{text}: producción nula en una variable que no es el inicial.")
            elif g.start_in_right_side():
                problems.append(f"{text}: el inicial produce ε pero aparece en un lado derecho.")
        elif len(rhs) == 1:
            if rhs[0] not in terminals:
                problems.append(f"{text}: producción unitaria; debe ser A -> a.")
        elif len(rhs) == 2:
            if not all(s in variables for s in rhs):
                problems.append(f"{text}: contiene terminales; debe ser A -> BC.")
        else:
            problems.append(f"{text}: longitud mayor a dos; debe ser A -> BC.")
    return problems


def validate_cnf_step(g: Grammar) -> Step:
    problems = check_cnf(g)
    if problems:
        identified = [("La gramática NO está en FNC", problems)]
        notes = ["Ejecute primero la eliminación de nulas, unitarias, inútiles e inalcanzables."]
        status = "error"
    else:
        identified = [("Validación automática", ["✔ Todas las producciones son A -> BC, A -> a o S -> ε (inicial)."])]
        notes = []
        status = "ok"
        if () in g.productions.get(g.start, []):
            notes.append("La gramática genera ε: S -> ε es la única excepción permitida.")
    step = _make_step(
        "validacion", "Validación de la Forma Normal de Chomsky",
        "Se comprueba automáticamente que cada producción tenga la forma A -> BC o A -> a.",
        g, g.copy(), identified, notes)
    step.status = status
    return step
