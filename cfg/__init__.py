"""Paquete cfg: depuración y conversión de GLC a Forma Normal de Chomsky."""
from .grammar import EPSILON, Grammar
from .parser import build_grammar
from .converter import Converter, FULL_PROCESS, STAGES
from .transformations import check_cnf

__all__ = ["EPSILON", "Grammar", "build_grammar", "Converter", "FULL_PROCESS", "STAGES", "check_cnf"]
