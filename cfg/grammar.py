"""Modelo de datos de una Gramática Libre de Contexto G = (V, T, P, S).

Las producciones se guardan como diccionario ordenado:
    variable -> lista de alternativas, cada alternativa es una tupla de símbolos.
La cadena vacía (ε) se representa con la tupla vacía ().
El orden de inserción se conserva siempre, de modo que una misma gramática
produce siempre la misma transformación (RNF11).
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Set, Tuple

EPSILON = "ε"
Production = Tuple[str, ...]


class Grammar:
    """Gramática libre de contexto con orden determinista."""

    def __init__(self, variables: Iterable[str], terminals: Iterable[str], start: str):
        self.variables: List[str] = list(variables)
        self.terminals: List[str] = list(terminals)
        self.start: str = start
        self.productions: Dict[str, List[Production]] = {v: [] for v in self.variables}

    # ------------------------------------------------------------------ edición
    def add_variable(self, name: str, at_front: bool = False) -> None:
        """Agrega una variable nueva (si no existe)."""
        if name in self.productions:
            return
        if at_front:
            self.variables.insert(0, name)
        else:
            self.variables.append(name)
        self.productions[name] = []

    def add_production(self, lhs: str, rhs: Iterable[str]) -> bool:
        """Agrega una producción evitando duplicados (RNF08). True si fue nueva."""
        rhs = tuple(rhs)
        bucket = self.productions.setdefault(lhs, [])
        if rhs in bucket:
            return False
        bucket.append(rhs)
        return True

    def copy(self) -> "Grammar":
        clone = Grammar(self.variables, self.terminals, self.start)
        for lhs in self.variables:
            clone.productions[lhs] = list(self.productions.get(lhs, []))
        return clone

    # ---------------------------------------------------------------- consultas
    def all_productions(self) -> List[Tuple[str, Production]]:
        """Todas las producciones en orden determinista."""
        return [(v, rhs) for v in self.variables for rhs in self.productions.get(v, [])]

    def variable_set(self) -> Set[str]:
        return set(self.variables)

    def terminal_set(self) -> Set[str]:
        return set(self.terminals)

    def start_in_right_side(self) -> bool:
        return any(self.start in rhs for _, rhs in self.all_productions())

    def fresh_variable(self, prefix: str = "X") -> str:
        """Nombre nuevo (X1, X2, ...) que no choca con ningún símbolo existente (RF17, RNF09)."""
        used = set(self.variables) | set(self.terminals)
        n = 1
        while f"{prefix}{n}" in used:
            n += 1
        return f"{prefix}{n}"

    def fresh_start_symbol(self) -> str:
        """Nombre para un nuevo símbolo inicial (S -> S0)."""
        used = set(self.variables) | set(self.terminals)
        candidate = self.start + "0"
        while candidate in used:
            candidate += "0"
        return candidate

    # ----------------------------------------------------------------- formato
    def separator(self, *others: "Grammar") -> str:
        """Separa símbolos con espacio si algún nombre tiene más de un carácter."""
        symbols = list(self.variables) + list(self.terminals)
        for other in others:
            symbols += list(other.variables) + list(other.terminals)
        return " " if any(len(s) > 1 for s in symbols) else ""

    @staticmethod
    def production_text(lhs: str, rhs: Production, sep: str = "") -> str:
        body = sep.join(rhs) if rhs else EPSILON
        return f"{lhs} -> {body}"

    def lines(self, sep: Optional[str] = None) -> List[str]:
        """Una línea por variable: 'A -> BC | a | ε'."""
        sep = self.separator() if sep is None else sep
        out = []
        for lhs in self.variables:
            alts = self.productions.get(lhs, [])
            if not alts:
                out.append(f"{lhs} -> ∅")
                continue
            out.append(f"{lhs} -> " + " | ".join(sep.join(r) if r else EPSILON for r in alts))
        return out

    def format(self) -> str:
        head = (
            f"V = {{{', '.join(self.variables)}}}\n"
            f"T = {{{', '.join(self.terminals)}}}\n"
            f"S = {self.start}\n"
            "P:\n"
        )
        return head + "\n".join("  " + line for line in self.lines())

    # ----------------------------------------------------------- serialización
    def to_dict(self, sep: Optional[str] = None) -> dict:
        return {
            "variables": list(self.variables),
            "terminals": list(self.terminals),
            "start": self.start,
            "productions": {v: [list(r) for r in self.productions.get(v, [])] for v in self.variables},
            "lines": self.lines(sep),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Grammar":
        g = cls(data["variables"], data["terminals"], data["start"])
        for lhs in g.variables:
            for rhs in data.get("productions", {}).get(lhs, []):
                g.add_production(lhs, rhs)
        return g
