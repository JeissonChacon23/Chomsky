"""Orquestador del proceso: ejecuta etapas individuales o el proceso completo y guarda el historial."""
from __future__ import annotations

from typing import Callable, Dict, List

from .grammar import Grammar
from .transformations import (
    Step,
    eliminate_null_productions,
    eliminate_unit_productions,
    eliminate_useless_variables,
    eliminate_unreachable_variables,
    reduce_long_productions,
    substitute_terminals,
    validate_cnf_step,
)

# Etapas individuales disponibles (modo paso a paso).
STAGES: Dict[str, Callable[[Grammar], Step]] = {
    "nulas": eliminate_null_productions,
    "unitarias": eliminate_unit_productions,
    "inutiles": eliminate_useless_variables,
    "inalcanzables": eliminate_unreachable_variables,
    "terminales": substitute_terminals,
    "largas": reduce_long_productions,
    "validacion": validate_cnf_step,
}

# Orden correcto del proceso completo (el de la guía y el que preserva el lenguaje).
FULL_PROCESS = ["nulas", "unitarias", "inutiles", "inalcanzables", "fnc"]


class Converter:
    """Mantiene la gramática actual y el historial paso a paso (RNF10)."""

    def __init__(self, grammar: Grammar):
        self.original = grammar.copy()
        self.current = grammar.copy()
        self.history: List[Step] = []

    def apply(self, key: str) -> List[Step]:
        """Ejecuta una etapa. 'fnc' agrupa sustitución de terminales + reducción + validación."""
        keys = ["terminales", "largas", "validacion"] if key == "fnc" else [key]
        produced: List[Step] = []
        for k in keys:
            if k not in STAGES:
                raise ValueError(f"Etapa desconocida: {k}")
            step = STAGES[k](self.current)
            self.current = step.after
            self.history.append(step)
            produced.append(step)
        return produced

    def run_all(self) -> List[Step]:
        """Modo automático: ejecuta todas las etapas consecutivamente."""
        produced: List[Step] = []
        for key in FULL_PROCESS:
            produced += self.apply(key)
        return produced
