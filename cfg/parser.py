"""Lectura y validación inicial de la gramática (sección 8 del lineamiento).

Formato de entrada:
    Variables:   S, A, B            (separadas por coma o espacio)
    Terminales:  a, b
    Inicial:     S
    Producciones (una por línea, alternativas con '|'):
        S -> A S B | ε
        A -> a A S | a
    La cadena vacía se escribe ε (también se acepta: λ, epsilon, lambda, &).
    Los nombres de símbolos pueden tener varios caracteres (p. ej. X1);
    si se pegan varios símbolos sin espacios se reconocen por el nombre más largo.
"""
from __future__ import annotations

import re
from typing import List, Optional, Tuple

from .grammar import Grammar

EPSILON_ALIASES = {"ε", "ϵ", "λ", "epsilon", "lambda", "eps", "&"}
ARROWS = ("->", "→", "::=", "=>")

RawProduction = Tuple[str, Tuple[str, ...], str]  # (lhs, rhs, texto original)


def split_list(text: str) -> List[str]:
    """Convierte 'S, A B; C' en ['S','A','B','C'] sin repetidos y conservando el orden."""
    items: List[str] = []
    for token in re.split(r"[,;\s]+", text or ""):
        token = token.strip()
        if token and token not in items:
            items.append(token)
    return items


def _tokenize(chunk: str, known: List[str]) -> List[str]:
    """Parte una cadena en símbolos usando el nombre declarado más largo posible."""
    tokens: List[str] = []
    i = 0
    while i < len(chunk):
        for symbol in known:  # 'known' viene ordenado de mayor a menor longitud
            if chunk.startswith(symbol, i):
                tokens.append(symbol)
                i += len(symbol)
                break
        else:  # símbolo desconocido: se conserva para reportarlo en la validación
            tokens.append(chunk[i])
            i += 1
    return tokens


def _split_arrow(line: str) -> Optional[Tuple[int, str]]:
    best: Optional[Tuple[int, str]] = None
    for arrow in ARROWS:
        idx = line.find(arrow)
        if idx != -1 and (best is None or idx < best[0]):
            best = (idx, arrow)
    return best


def parse_productions(text: str, known: List[str], errors: List[str]) -> List[RawProduction]:
    """Convierte el texto de producciones en tuplas (lhs, rhs, texto)."""
    result: List[RawProduction] = []
    for number, raw_line in enumerate((text or "").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        found = _split_arrow(line)
        if found is None:
            errors.append(f"Error: la línea {number} «{line}» no tiene flecha '->' (estructura de producción inválida).")
            continue
        idx, arrow = found
        lhs = line[:idx].strip()
        rhs_text = line[idx + len(arrow):].strip()
        for alt in rhs_text.split("|"):
            alt = alt.strip()
            shown = f"{lhs} -> {alt}"
            if alt == "":
                errors.append(f"Error: la producción «{lhs} -> {rhs_text}» tiene una alternativa vacía; use ε para la cadena vacía.")
                continue
            chunks = alt.split()
            if any(c in EPSILON_ALIASES for c in chunks):
                if len(chunks) == 1:
                    result.append((lhs, (), shown))
                else:
                    errors.append(f"Error: en la producción «{shown}» ε no puede combinarse con otros símbolos.")
                continue
            tokens: List[str] = []
            for chunk in chunks:
                tokens += _tokenize(chunk, known)
            result.append((lhs, tuple(tokens), shown))
    return result


def build_grammar(variables_text: str, terminals_text: str, start_text: str,
                  productions_text: str) -> Tuple[Optional[Grammar], List[str]]:
    """Construye y valida la gramática. Devuelve (gramática, errores).

    Si hay errores la gramática es None y el proceso de conversión no debe iniciar.
    """
    errors: List[str] = []
    variables = split_list(variables_text)
    terminals = split_list(terminals_text)
    start = (start_text or "").strip()

    if not variables:
        errors.append("Error: debe existir al menos una variable.")
    if not terminals:
        errors.append("Error: debe existir al menos un terminal.")
    if not start:
        errors.append("Error: no se definió el símbolo inicial.")
    elif start not in variables:
        errors.append(f"Error: el símbolo inicial {start} no pertenece al conjunto de variables.")
    for symbol in variables:
        if symbol in terminals:
            errors.append(f"Error: el símbolo {symbol} fue declarado como variable y como terminal.")
        if symbol in EPSILON_ALIASES:
            errors.append(f"Error: {symbol} está reservado para la cadena vacía y no puede ser una variable.")
    for symbol in terminals:
        if symbol in EPSILON_ALIASES:
            errors.append(f"Error: {symbol} está reservado para la cadena vacía y no puede ser un terminal.")
        if symbol == "|":
            errors.append("Error: '|' está reservado como separador de alternativas y no puede ser un terminal.")

    known = sorted(set(variables) | set(terminals), key=lambda s: (-len(s), s))
    raw = parse_productions(productions_text, known, errors)
    if not raw and not any("línea" in e or "alternativa" in e for e in errors):
        errors.append("Error: no se registró ninguna producción.")

    declared_vars, declared_terms = set(variables), set(terminals)
    for lhs, rhs, text in raw:
        if lhs not in declared_vars:
            if lhs in declared_terms:
                errors.append(f"Error: el lado izquierdo de la producción {text} es el terminal {lhs}; debe ser una variable.")
            elif lhs == "" or re.search(r"\s", lhs):
                errors.append(f"Error: la producción {text} debe tener una única variable en el lado izquierdo.")
            else:
                errors.append(f"Error: la variable {lhs} utilizada en la producción {text} no fue declarada.")
        for symbol in rhs:
            if symbol in declared_vars or symbol in declared_terms:
                continue
            if symbol.isalpha() and symbol.isupper():
                errors.append(f"Error: la variable {symbol} utilizada en la producción {text} no fue declarada.")
            else:
                errors.append(f"Error: el símbolo {symbol} no fue declarado como terminal (producción {text}).")

    errors = list(dict.fromkeys(errors))  # sin mensajes repetidos, mismo orden
    if errors:
        return None, errors

    grammar = Grammar(variables, terminals, start)
    for lhs, rhs, _ in raw:
        grammar.add_production(lhs, rhs)
    return grammar, []
