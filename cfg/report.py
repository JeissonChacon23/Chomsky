"""Presentación en texto de las etapas (usada por el menú de consola)."""
from __future__ import annotations

from typing import List

from .transformations import Step


def _block(title: str, lines: List[str]) -> str:
    return f"{title}\n" + "\n".join(f"  {line}" for line in lines)


def format_step(step: Step, number: int = 0) -> str:
    """RF18: gramática inicial, identificados, eliminadas, agregadas y resultante."""
    head = f"=== Paso {number}: {step.title} ===" if number else f"=== {step.title} ==="
    parts = [head, step.description, "", _block("Gramática inicial de la etapa:", step.before.lines(step.before.separator(step.after)))]
    for label, items in step.identified:
        parts.append(_block(f"{label}:", items))
    parts.append(_block("Producciones eliminadas:", step.removed or ["(ninguna)"]))
    parts.append(_block("Producciones agregadas:", step.added or ["(ninguna)"]))
    if step.variables_removed:
        parts.append(_block("Variables eliminadas:", [", ".join(step.variables_removed)]))
    if step.variables_added:
        parts.append(_block("Variables nuevas:", [", ".join(step.variables_added)]))
    for note in step.notes:
        parts.append(f"Nota: {note}")
    parts.append(_block("Gramática resultante:", step.after.lines(step.before.separator(step.after))))
    return "\n".join(parts) + "\n"


def format_history(steps: List[Step]) -> str:
    if not steps:
        return "El historial está vacío: aún no se ha ejecutado ninguna transformación."
    return "\n".join(format_step(s, i) for i, s in enumerate(steps, start=1))
